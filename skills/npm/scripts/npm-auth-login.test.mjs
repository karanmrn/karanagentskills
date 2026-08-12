import assert from "node:assert/strict";
import test from "node:test";
import {
	extractNpmCredentials,
	selectCredentialField,
} from "./npm-auth-login.mjs";

test("canonical IDs beat earlier duplicate labels", () => {
	const credentials = extractNpmCredentials({
		fields: [
			{ label: "password", type: "STRING", value: "stale-password" },
			{ id: "username", label: "name", purpose: "USERNAME", value: "owner" },
			{
				id: "password",
				label: "password",
				purpose: "PASSWORD",
				type: "CONCEALED",
				value: "current-password",
			},
		],
	});

	assert.deepEqual(credentials, {
		username: "owner",
		password: "current-password",
	});
});

test("purpose beats labels when canonical IDs are absent", () => {
	const value = selectCredentialField(
		[
			{ label: "password", value: "legacy" },
			{ label: "login secret", purpose: "PASSWORD", value: "current" },
		],
		{
			id: "password",
			purpose: "PASSWORD",
			labels: ["password"],
			displayName: "password",
		},
	);

	assert.equal(value, "current");
});

test("duplicate label-only fields are rejected", () => {
	assert.throws(
		() =>
			selectCredentialField(
				[
					{ label: "password", value: "one" },
					{ label: "password", value: "two" },
				],
				{
					id: "password",
					purpose: "PASSWORD",
					labels: ["password"],
					displayName: "password",
				},
			),
		/ambiguous password label fields/,
	);
});
