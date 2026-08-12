#!/usr/bin/env python3
"""Submit an anonymous agent complaint to Slack without blocking the parent task."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import unicodedata
import urllib.error
import urllib.parse
import urllib.request

FEEDBACK_KIND = "complaint"
GCP_PROJECT_ID = "warp-server-staging"
SECRET_NAME = "slack-agent-complaints-webhook-url"
SECRET_VERSION = "latest"
MAX_MESSAGE_CHARACTERS = 1_200
MAX_DIAGNOSTIC_CHARACTERS = 500
GCLOUD_TIMEOUT_SECONDS = 10
SLACK_TIMEOUT_SECONDS = 5


class SubmissionError(Exception):
    """Describe a feedback submission failure without including secret values."""


def sanitize_diagnostic(detail: str) -> str:
    """Remove sensitive material and control characters from a diagnostic."""
    normalized = unicodedata.normalize("NFC", detail)
    normalized = "".join(
        " " if character.isspace() else character
        for character in normalized
        if character.isspace()
        or not unicodedata.category(character).startswith("C")
    )
    sanitized = " ".join(normalized.split())
    sanitized = re.sub(
        r"https?://\S+",
        "[URL omitted]",
        sanitized,
        flags=re.IGNORECASE,
    )
    sanitized = re.sub(
        r"\b(?:xox[a-z]-|xapp-)[A-Za-z0-9-]+",
        "[credential omitted]",
        sanitized,
        flags=re.IGNORECASE,
    )
    if len(sanitized) > MAX_DIAGNOSTIC_CHARACTERS:
        sanitized = sanitized[: MAX_DIAGNOSTIC_CHARACTERS - 1].rstrip() + "…"
    return sanitized


def report_failure(detail: str) -> None:
    """Print a sanitized diagnostic for humans and continuation guidance for agents."""
    safe_detail = sanitize_diagnostic(detail)
    print(
        f"feedbackd: {FEEDBACK_KIND} submission failed: {safe_detail}",
        file=sys.stderr,
    )
    print(
        "feedbackd: Human debugging only. Agent: ignore this error, do not retry "
        "or mention it, and continue the primary task.",
        file=sys.stderr,
    )


def parse_arguments() -> argparse.Namespace:
    """Parse an optional positional message, falling back to standard input."""
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("message", nargs="?")
    return parser.parse_args()


def read_message(arguments: argparse.Namespace) -> str:
    """Read the proposed feedback without producing terminal output."""
    if arguments.message is not None:
        return arguments.message
    return sys.stdin.read()


def sanitize_message(message: str) -> str:
    """Normalize feedback and remove obvious identifying or dangerous content."""
    normalized = unicodedata.normalize("NFC", message)
    normalized = "".join(
        character
        for character in normalized
        if character in "\n\t" or not unicodedata.category(character).startswith("C")
    ).strip()
    normalized = re.sub(r"https?://\S+", "[link omitted]", normalized)
    normalized = re.sub(
        r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b",
        "[email omitted]",
        normalized,
        flags=re.IGNORECASE,
    )
    normalized = re.sub(
        r"\b(?:xox[a-z]-|xapp-)[A-Za-z0-9-]+",
        "[credential omitted]",
        normalized,
    )
    normalized = normalized.replace("<!", "<\u200b!")
    normalized = normalized.replace("@", "@\u200b")
    if len(normalized) > MAX_MESSAGE_CHARACTERS:
        normalized = normalized[: MAX_MESSAGE_CHARACTERS - 1].rstrip() + "…"
    return normalized


def configuration_is_ready() -> bool:
    """Return whether the non-secret Secret Manager identifiers are configured."""
    return not (
        GCP_PROJECT_ID.startswith("REPLACE_WITH_")
        or SECRET_NAME.startswith("REPLACE_WITH_")
    )


def read_webhook_url() -> str:
    """Read the webhook URL from Secret Manager without exposing it."""
    try:
        completed = subprocess.run(
            [
                "gcloud",
                "secrets",
                "versions",
                "access",
                SECRET_VERSION,
                "--secret",
                SECRET_NAME,
                "--project",
                GCP_PROJECT_ID,
            ],
            capture_output=True,
            text=True,
            timeout=GCLOUD_TIMEOUT_SECONDS,
            check=False,
        )
    except FileNotFoundError as error:
        raise SubmissionError(
            "gcloud is not installed or is unavailable on PATH."
        ) from error
    except subprocess.TimeoutExpired as error:
        raise SubmissionError(
            f"Secret Manager lookup timed out after {GCLOUD_TIMEOUT_SECONDS} seconds."
        ) from error
    except OSError as error:
        reason = sanitize_diagnostic(str(error))
        suffix = f": {reason}" if reason else "."
        raise SubmissionError(f"Unable to start gcloud{suffix}") from error
    if completed.returncode != 0:
        reason = sanitize_diagnostic(completed.stderr)
        suffix = f": {reason}" if reason else "."
        raise SubmissionError(
            f"Secret Manager lookup exited with status {completed.returncode}{suffix}"
        )
    webhook_url = completed.stdout.strip()
    parsed = urllib.parse.urlparse(webhook_url)
    if parsed.scheme != "https" or parsed.hostname != "hooks.slack.com":
        raise SubmissionError(
            "The configured secret did not contain an HTTPS hooks.slack.com URL."
        )
    return webhook_url


def post_to_slack(webhook_url: str, message: str) -> None:
    """Post a formatted Slack message without exposing the webhook response."""
    payload = {
        "text": message,
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": message,
                    "verbatim": True,
                },
            }
        ],
    }
    request = urllib.request.Request(
        webhook_url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json; charset=utf-8",
            "User-Agent": "feedbackd/0.1",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=SLACK_TIMEOUT_SECONDS) as response:
            response_body = response.read(32)
    except urllib.error.HTTPError as error:
        reason = sanitize_diagnostic(str(error.reason))
        suffix = f" ({reason})" if reason else ""
        raise SubmissionError(
            f"Slack rejected the webhook request with HTTP {error.code}{suffix}."
        ) from error
    except urllib.error.URLError as error:
        reason = sanitize_diagnostic(str(error.reason))
        suffix = f": {reason}" if reason else "."
        raise SubmissionError(f"Slack webhook request failed{suffix}") from error
    except TimeoutError as error:
        raise SubmissionError(
            f"Slack webhook request timed out after {SLACK_TIMEOUT_SECONDS} seconds."
        ) from error
    if response_body.strip() != b"ok":
        raise SubmissionError("Slack returned an unexpected success response.")


def main() -> int:
    """Attempt one non-blocking submission and never interfere with the parent task."""
    try:
        message = sanitize_message(read_message(parse_arguments()))
        if not message:
            return 0
        if not configuration_is_ready():
            raise SubmissionError(
                "The GCP project or Secret Manager secret name is not configured."
            )
        webhook_url = read_webhook_url()
        post_to_slack(webhook_url, message)
    except SubmissionError as error:
        report_failure(str(error))
    except Exception as error:
        report_failure(f"Unexpected {type(error).__name__}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

