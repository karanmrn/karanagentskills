import assert from "node:assert/strict";
import test from "node:test";
import {
	registryTokenFromNpmrc,
	registryTokenMatches,
	updateRegistryToken,
} from "./npm-auth-cache.mjs";

test("extracts the exact registry token without truncating equals signs", () => {
	const token = registryTokenFromNpmrc(
		"//registry.npmjs.org/:_authToken=new-token==\n",
		"https://registry.npmjs.org/",
	);
	assert.equal(token, "new-token==");
});

test("updates only the unique registry token field", () => {
	const item = {
		fields: [
			{ id: "username", label: "username", value: "owner" },
			{ id: "cache", label: "registry_token", type: "CONCEALED", value: "old" },
		],
	};
	const updated = updateRegistryToken(structuredClone(item), "new");
	assert.equal(updated.fields[0].value, "owner");
	assert.equal(updated.fields[1].value, "new");
	assert.equal(updated.fields[1].type, "CONCEALED");
	assert.equal(registryTokenMatches(updated, "new"), true);
});

test("rejects missing or duplicate registry token fields", () => {
	assert.throws(() => updateRegistryToken({ fields: [] }, "new"), /exactly one/);
	assert.throws(
		() =>
			updateRegistryToken(
				{
					fields: [
						{ label: "registry_token", value: "one" },
						{ label: "registry_token", value: "two" },
					],
				},
				"new",
			),
		/exactly one/,
	);
});
