#!/usr/bin/env node
import fs from "node:fs";
import { execFileSync } from "node:child_process";
import { createRequire } from "node:module";
import { pathToFileURL } from "node:url";

const require = createRequire(import.meta.url);

function valueMatches(fields, predicate) {
	return fields.filter((field) => field?.value && predicate(field));
}

export function selectCredentialField(
	fields,
	{ id, purpose, labels, displayName },
) {
	const byId = valueMatches(fields, (field) => field.id === id);
	if (byId.length === 1) return String(byId[0].value);
	if (byId.length > 1) throw new Error(`ambiguous canonical ${displayName} fields`);

	const byPurpose = valueMatches(fields, (field) => field.purpose === purpose);
	if (byPurpose.length === 1) return String(byPurpose[0].value);
	if (byPurpose.length > 1) throw new Error(`ambiguous ${displayName} purpose fields`);

	const acceptedLabels = new Set(labels.map((label) => label.toLowerCase()));
	const byLabel = valueMatches(fields, (field) =>
		acceptedLabels.has(String(field.label ?? "").toLowerCase()),
	);
	if (byLabel.length === 1) return String(byLabel[0].value);
	if (byLabel.length > 1) throw new Error(`ambiguous ${displayName} label fields`);
	throw new Error(`missing ${displayName} field`);
}

export function extractNpmCredentials(item) {
	const fields = Array.isArray(item?.fields) ? item.fields : [];
	return {
		username: selectCredentialField(fields, {
			id: "username",
			purpose: "USERNAME",
			labels: ["username", "name"],
			displayName: "username",
		}),
		password: selectCredentialField(fields, {
			id: "password",
			purpose: "PASSWORD",
			labels: ["password"],
			displayName: "password",
		}),
	};
}

function npmProfileCandidates() {
	const roots = [];
	try {
		roots.push(execFileSync("npm", ["root", "-g"], { encoding: "utf8" }).trim());
	} catch {}
	roots.push("/opt/homebrew/lib/node_modules", "/usr/local/lib/node_modules");
	return roots.flatMap((root) => [
		`${root}/npm/node_modules/npm-profile`,
		`${root}/npm-profile`,
	]);
}

function loadLoginCouch() {
	for (const candidate of npmProfileCandidates()) {
		try {
			return require(candidate).loginCouch;
		} catch {}
	}
	throw new Error("could not load npm-profile loginCouch from npm installation");
}

async function main() {
	const otp = process.env.NPM_OTP ?? "";
	const npmrc = process.env.NPMRC ?? "";
	const registry = process.env.REGISTRY ?? "https://registry.npmjs.org/";
	if (!/^\d{6}$/.test(otp)) throw new Error("npm OTP must be six digits");
	if (!npmrc) throw new Error("NPMRC path is required");

	const input = fs.readFileSync(0, "utf8");
	const { username, password } = extractNpmCredentials(JSON.parse(input));
	const result = await loadLoginCouch()(username, password, { registry, otp });
	if (!result?.token) throw new Error("registry did not return an npm token");

	const authHost = new URL(registry).host;
	fs.writeFileSync(npmrc, `//${authHost}/:_authToken=${result.token}\n`, {
		mode: 0o600,
	});
	console.log(`npm registry session created for ${result.username || username}`);
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
	main().catch((error) => {
		console.error(error?.code ? `${error.code}: ${error.message}` : error.message);
		if (error?.body) {
			console.error(String(error.body).replace(/\b\d{6}\b/g, "OTP_REDACTED"));
		}
		process.exit(1);
	});
}
