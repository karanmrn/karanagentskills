#!/usr/bin/env ruby
# frozen_string_literal: true

require "json"
require "open3"
require "optparse"
require "shellwords"

MODELS = %w[gpt-5.6-sol gpt-5.6-terra gpt-5.6-luna].freeze
CONTEXT_WINDOW = 922_000
AUTO_COMPACT_TOKEN_LIMIT = 700_000
AUTO_COMPACT_TOKEN_LIMIT_SCOPE = "total"

class PreflightError < StandardError; end

def strip_toml_comment(line)
  quote = nil
  escaped = false

  line.each_char.with_index do |character, index|
    if quote == '"'
      if escaped
        escaped = false
      elsif character == "\\"
        escaped = true
      elsif character == quote
        quote = nil
      end
    elsif quote == "'"
      quote = nil if character == quote
    elsif character == '"' || character == "'"
      quote = character
    elsif character == "#"
      return line[0...index]
    end
  end

  line
end

def parse_toml_value(raw_value)
  value = raw_value.strip
  return JSON.parse(value) if value.start_with?('"') && value.end_with?('"')
  return value[1...-1] if value.start_with?("'") && value.end_with?("'")
  return true if value == "true"
  return false if value == "false"
  return Integer(value.delete("_"), 10) if value.match?(/\A[+-]?[0-9][0-9_]*\z/)

  value
rescue JSON::ParserError, ArgumentError
  raise PreflightError, "could not parse a required value in config.toml"
end

def read_config(path)
  raise PreflightError, "config not found: #{path}" unless File.file?(path)

  sections = Hash.new { |hash, key| hash[key] = {} }
  section = "root"

  File.foreach(path) do |raw_line|
    line = strip_toml_comment(raw_line).strip
    next if line.empty?

    if (match = line.match(/\A\[([^\]]+)\]\z/))
      section = match[1]
      next
    end

    match = line.match(/\A([A-Za-z0-9_-]+)\s*=\s*(.+)\z/)
    next unless match

    sections[section][match[1]] = parse_toml_value(match[2])
  end

  sections
end

def require_value(actual, expected, label)
  return if actual == expected

  raise PreflightError, "#{label} must be #{expected.inspect}"
end

def validate_config(sections)
  root = sections["root"]
  provider = sections["model_providers.openai_api_direct"]
  auth = sections["model_providers.openai_api_direct.auth"]

  raise PreflightError, "model must be one of the 1M catalogue models" unless MODELS.include?(root["model"])

  require_value(root["model_provider"], "openai_api_direct", "model_provider")
  require_value(root["model_context_window"], CONTEXT_WINDOW, "model_context_window")
  require_value(
    root["model_auto_compact_token_limit"],
    AUTO_COMPACT_TOKEN_LIMIT,
    "model_auto_compact_token_limit",
  )
  require_value(
    root["model_auto_compact_token_limit_scope"],
    AUTO_COMPACT_TOKEN_LIMIT_SCOPE,
    "model_auto_compact_token_limit_scope",
  )

  require_value(provider["base_url"], "https://api.openai.com/v1", "openai_api_direct.base_url")
  require_value(provider["wire_api"], "responses", "openai_api_direct.wire_api")
  require_value(provider["requires_openai_auth"], false, "openai_api_direct.requires_openai_auth")
  require_value(auth["timeout_ms"], 5000, "openai_api_direct.auth.timeout_ms")
  require_value(auth["refresh_interval_ms"], 300_000, "openai_api_direct.auth.refresh_interval_ms")

  catalog_path = root["model_catalog_json"]
  raise PreflightError, "model_catalog_json is missing" unless catalog_path.is_a?(String) && !catalog_path.empty?

  command = auth["command"]
  raise PreflightError, "openai_api_direct.auth.command is missing" unless command.is_a?(String) && !command.empty?

  [File.expand_path(catalog_path), command, auth["timeout_ms"]]
end

def validate_catalog(path)
  raise PreflightError, "model catalogue not found: #{path}" unless File.file?(path)

  document = JSON.parse(File.read(path, encoding: "UTF-8"))
  models = document["models"]
  raise PreflightError, "model catalogue has no models array" unless models.is_a?(Array)

  MODELS.each do |slug|
    model = models.find { |entry| entry.is_a?(Hash) && entry["slug"] == slug }
    raise PreflightError, "model catalogue is missing #{slug}" unless model

    require_value(model["context_window"], CONTEXT_WINDOW, "#{slug}.context_window")
    require_value(model["max_context_window"], CONTEXT_WINDOW, "#{slug}.max_context_window")
    require_value(
      model["auto_compact_token_limit"],
      AUTO_COMPACT_TOKEN_LIMIT,
      "#{slug}.auto_compact_token_limit",
    )
    if model.key?("effective_context_window_percent")
      effective_percent = model["effective_context_window_percent"]
      unless effective_percent.is_a?(Integer) && effective_percent == 95
        raise PreflightError, "#{slug}.effective_context_window_percent must be omitted or integer 95"
      end
    end
  end
rescue JSON::ParserError
  raise PreflightError, "model catalogue is not valid JSON"
end

def run_auth_helper(command, timeout_ms)
  arguments = Shellwords.split(command)
  unless arguments.length == 1
    raise PreflightError, "auth command must be one executable path with no arguments"
  end

  helper = File.expand_path(arguments.first)
  raise PreflightError, "auth helper is not executable: #{helper}" unless File.executable?(helper)

  stdin, stdout, stderr, wait_thread = Open3.popen3([helper, helper])
  stdin.close
  stdout_reader = Thread.new { stdout.read }
  stderr_reader = Thread.new { stderr.read }

  unless wait_thread.join(timeout_ms / 1000.0)
    Process.kill("TERM", wait_thread.pid)
    unless wait_thread.join(0.5)
      Process.kill("KILL", wait_thread.pid)
      wait_thread.join
    end
    stdout_reader.join
    stderr_reader.join
    raise PreflightError, "auth helper timed out; unlock the login Keychain from the local graphical session"
  end

  auth_output = stdout_reader.value
  error_output = stderr_reader.value
  success = wait_thread.value.success?
  delivered = !auth_output.strip.empty?

  auth_output.clear
  error_output.clear

  unless success
    raise PreflightError, "auth helper failed; install or repair the dedicated Keychain delivery copy"
  end
  raise PreflightError, "auth helper returned no credential" unless delivered
rescue Errno::ENOENT
  raise PreflightError, "auth helper could not be launched"
ensure
  stdout&.close unless stdout&.closed?
  stderr&.close unless stderr&.closed?
end

config_path = File.expand_path("~/.codex/config.toml")
OptionParser.new do |options|
  options.banner = "Usage: preflight.rb [--config PATH]"
  options.on("--config PATH", "Codex config.toml to check") { |path| config_path = File.expand_path(path) }
end.parse!

begin
  sections = read_config(config_path)
  catalog_path, auth_command, timeout_ms = validate_config(sections)
  validate_catalog(catalog_path)
  run_auth_helper(auth_command, timeout_ms)

  puts "Codex direct API safe-context preflight: ok"
  warn "Note: GITHUB_PAT_TOKEN is unset; GitHub MCP may fail independently." if ENV.fetch("GITHUB_PAT_TOKEN", "").empty?
rescue PreflightError => error
  warn "Codex direct API safe-context preflight failed: #{error.message}"
  exit 1
end
