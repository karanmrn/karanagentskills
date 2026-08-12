#!/usr/bin/env node
import fs from "node:fs";
import { pathToFileURL } from "node:url";

export function registryTokenFromNpmrc(npmrc, registry) {
	const authKey = `//${new URL(registry).host}/:_authToken`;
	const matches = npmrc
		.split("\n")
		.map((line) => line.trim())
		.filter((line) => line && !line.startsWith("#") && !line.startsWith(";"))
		.map((line) => {
			const separator = line.indexOf("=");
			return separator === -1
				? [line, ""]
				: [line.slice(0, separator).trim(), line.slice(separator + 1).trim()];
		})
		.filter(([key]) => key === authKey);
	if (matches.length !== 1 || !matches[0][1]) {
		throw new Error(`temporary npmrc must contain exactly one token for ${new URL(registry).host}`);
	}
	return matches[0][1];
}

export function updateRegistryToken(item, token) {
	const matches = (item.fields ?? []).filter((field) => field.label === "registry_token");
	if (matches.length !== 1) {
		throw new Error("1Password item must contain exactly one registry_token field");
	}
	matches[0].value = token;
	return item;
}

export function registryTokenMatches(item, token) {
	const matches = (item.fields ?? []).filter((field) => field.label === "registry_token");
	return matches.length === 1 && matches[0].value === token;
}

async function main() {
	const [mode, npmrcPath, registry = "https://registry.npmjs.org/"] = process.argv.slice(2);
	if (!npmrcPath || !["update", "verify"].includes(mode)) {
		throw new Error("usage: npm-auth-cache.mjs <update|verify> <npmrc> [registry]");
	}
	const token = registryTokenFromNpmrc(fs.readFileSync(npmrcPath, "utf8"), registry);
	const input = await new Promise((resolve, reject) => {
		let text = "";
		process.stdin.setEncoding("utf8");
		process.stdin.on("data", (chunk) => (text += chunk));
		process.stdin.on("end", () => resolve(text));
		process.stdin.on("error", reject);
	});
	const item = JSON.parse(input);
	if (mode === "update") {
		process.stdout.write(JSON.stringify(updateRegistryToken(item, token)));
	} else if (!registryTokenMatches(item, token)) {
		throw new Error("cached registry token does not match the new npm session");
	}
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
	main().catch((error) => {
		console.error(error.message);
		process.exit(1);
	});
}
