#!/usr/bin/env node

import { readFileSync } from "node:fs";
import { pathToFileURL } from "node:url";

const DENY_MESSAGE =
  "Action blocked by the repository's fail-closed agent policy.";

function normalize(value) {
  return String(value ?? "")
    .replaceAll("\\", "/")
    .replace(/^file:\/\//, "")
    .replace(/\/+/g, "/");
}

function basename(value) {
  return normalize(value).split("/").at(-1) ?? "";
}

export function isSecretPath(value) {
  const path = normalize(value);
  const name = basename(path);

  if (
    /^\.env(?:\.|$)/i.test(name) &&
    !/^\.env\.(?:example|sample|template)$/i.test(name)
  ) {
    return true;
  }

  return (
    /\.(?:pem|key|p12|pfx)$/i.test(name) ||
    /^(?:credentials?|secrets?)\.json$/i.test(name) ||
    /^id_(?:rsa|ed25519|ecdsa|dsa)$/i.test(name) ||
    /(^|\/)\.aws\/credentials$/i.test(path) ||
    /(^|\/)\.config\/gcloud\/application_default_credentials\.json$/i.test(
      path,
    ) ||
    /(^|\/)\.docker\/config\.json$/i.test(path) ||
    /(^|\/)(?:\.netrc|\.npmrc|\.pypirc)$/i.test(path)
  );
}

const protectedPathPatterns = [
  /(^|\/)AGENTS\.md$/i,
  /(^|\/)\.cursor\/AGENTS\.md$/i,
  /(^|\/)\.cursor\/INSTRUCTIONS\.md$/i,
  /(^|\/)\.cursor\/instructions\/ROLES\.md$/i,
  /(^|\/)\.cursor\/agents(?:\/|$)/i,
  /(^|\/)\.cursor\/rules(?:\/|$)/i,
  /(^|\/)\.cursor\/hooks(?:\.json|\/|$)/i,
  /(^|\/)\.cursor\/(?:cli|sandbox|permissions|mcp)\.json$/i,
  /(^|\/)\.cursor\/scripts\/(?:bootstrap\.sh|validate-agent-config\.mjs)$/i,
  /(^|\/)\.github\/workflows\/agent-governance\.yml$/i,
  /(^|\/)\.cursorignore$/i,
];

export function isProtectedPath(value) {
  const path = normalize(value);
  return protectedPathPatterns.some((pattern) => pattern.test(path));
}

function collectPathFields(value, paths = [], parentKey = "") {
  if (value === null || value === undefined) return paths;

  if (Array.isArray(value)) {
    for (const child of value) collectPathFields(child, paths, parentKey);
    return paths;
  }

  if (typeof value !== "object") return paths;

  for (const [key, child] of Object.entries(value)) {
    const compoundKey = `${parentKey}.${key}`;
    if (
      typeof child === "string" &&
      /(?:^|_)(?:path|file|filename|target|source|destination|notebook)$/i.test(
        key,
      )
    ) {
      paths.push(child);
    } else if (typeof child === "object") {
      collectPathFields(child, paths, compoundKey);
    }
  }

  return paths;
}

function shellReferencesSecret(command) {
  const value = String(command ?? "");
  const withoutTemplates = value
    .replace(/\.env\.(?:example|sample|template)\b/gi, "")
    .replace(/\bid_(?:rsa|ed25519|ecdsa|dsa)\.pub\b/gi, "");

  return (
    /(^|[\s"'=:/\\])\.env(?:\.[\w.-]+)?\b/i.test(withoutTemplates) ||
    /\.(?:pem|key|p12|pfx)\b/i.test(value) ||
    /\b(?:credentials?|secrets?)\.json\b/i.test(value) ||
    /(?:^|[\s"'=:/\\])(?:\.netrc|\.npmrc|\.pypirc)\b/i.test(value) ||
    /\.aws[\\/]credentials\b/i.test(value) ||
    /application_default_credentials\.json\b/i.test(value)
  );
}

export function isDestructiveGit(command) {
  const value = String(command ?? "");
  return [
    /\bgit\s+reset\b[^;&|\n]*--hard\b/i,
    /\bgit\s+clean\b[^;&|\n]*\s-[^\s;&|]*f/i,
    /\bgit\s+checkout\s+--(?:\s|$)/i,
    /\bgit\s+restore\b(?![^;&|\n]*--staged\b)/i,
    /\bgit\s+branch\b[^;&|\n]*\s-D(?:\s|$)/i,
    /\bgit\s+push\b[^;&|\n]*(?:--force(?:-with-lease)?|-f(?:\s|$))/i,
    /\bgit\s+(?:filter-repo|filter-branch)\b/i,
    /\bgit\s+reflog\s+expire\b/i,
    /\bgit\s+gc\b[^;&|\n]*--prune(?:=|\s+)now\b/i,
  ].some((pattern) => pattern.test(value));
}

export function isProductionMutation(command) {
  const value = String(command ?? "");
  return [
    /\b(?:vercel|vc|npx\s+(?:--yes\s+)?vercel(?:@\S+)?)\b[^;&|\n]*--prod\b/i,
    /\bvercel\s+(?:promote|rollback|remove)\b/i,
    /\b(?:supabase|npx\s+(?:--yes\s+)?supabase(?:@\S+)?)\s+db\s+(?:push|reset)\b/i,
    /\b(?:supabase|npx\s+(?:--yes\s+)?supabase(?:@\S+)?)\s+migration\s+repair\b/i,
    /\b(?:supabase|npx\s+(?:--yes\s+)?supabase(?:@\S+)?)\s+(?:functions\s+deploy|secrets?\s+set)\b/i,
    /\bterraform\s+(?:apply|destroy|import)\b/i,
    /\bkubectl\s+(?:apply|create|delete|patch|replace|rollout|scale|set)\b/i,
    /\b(?:firebase|netlify|railway|flyctl)\s+(?:deploy|up|release)\b/i,
    /\bgcloud\s+(?:run\s+deploy|app\s+deploy|functions\s+deploy)\b/i,
  ].some((pattern) => pattern.test(value));
}

function shellMutatesProtectedPath(command) {
  const value = normalize(command);
  const pathCandidates = value
    .split(/[\s"'`=<>|;&(),]+/)
    .map((candidate) => candidate.replace(/^\.\//, ""))
    .filter(Boolean);

  if (!pathCandidates.some((candidate) => isProtectedPath(candidate))) {
    return false;
  }

  return [
    /(^|[;&|]\s*|\s)(?:rm|mv|cp|install|truncate|touch|unlink)\s/i,
    /\b(?:chmod|chown)\b/i,
    /\b(?:sed|perl)\b[^;&|\n]*(?:-i|-pi)\b/i,
    /\b(?:apply_patch|patch|rsync)\b/i,
    /\bdd\b[^;&|\n]*\bof=/i,
    /\btar\b[^;&|\n]*\s-x/i,
    /\btee\b/i,
    /(?:^|[^<])>{1,2}(?!>)/,
    /\b(?:python|python3|node|ruby)\b[^;&|\n]*(?:writeFile|write_text|unlink|rename|remove|rmtree)/i,
    /\bgit\s+(?:checkout|restore)\b/i,
  ].some((pattern) => pattern.test(value));
}

function mutationTool(toolName) {
  return /(?:^|:|\s)(?:write|delete|edit|applypatch|move|rename|createfile)(?:$|:|\s)/i.test(
    String(toolName ?? ""),
  );
}

function stateChangingMcp(input) {
  const toolName = String(input.tool_name ?? input.name ?? "").toLowerCase();
  const toolInput =
    typeof input.tool_input === "string"
      ? input.tool_input
      : JSON.stringify(input.tool_input ?? {});

  return (
    /(?:^|[_:\-\s])(?:create|update|delete|remove|move|rename|edit|write|deploy|release|publish|push|apply|execute|promote|rollback|repair|migrate|merge|send|reply|purchase|buy|install|launch|stop|set|click|tap|type|fill|select|press|drag|gesture|swipe)(?:$|[_:\-\s])/i.test(
      toolName,
    ) ||
    /(?:^|[_:\-\s])run_sql(?:$|[_:\-\s])/i.test(toolName) ||
    /\b(?:insert|update|delete|drop|alter|create|truncate|grant|revoke|merge)\b/i.test(
      toolInput,
    )
  );
}

function denied(event, reason) {
  const result = {
    permission: "deny",
    user_message: `${DENY_MESSAGE} ${reason}`,
  };

  if (
    event === "preToolUse" ||
    event === "beforeShellExecution" ||
    event === "beforeMCPExecution"
  ) {
    result.agent_message = reason;
  }

  return result;
}

function allowed() {
  return { permission: "allow" };
}

export function evaluate(input) {
  const event = String(input?.hook_event_name ?? "");

  if (event === "beforeReadFile") {
    const path = input.file_path ?? input.path ?? "";
    if (isSecretPath(path)) {
      return denied(event, "Secret-bearing files are unavailable to agents.");
    }
    return allowed();
  }

  if (event === "preToolUse") {
    const toolName = String(input.tool_name ?? "");
    const paths = collectPathFields(input.tool_input);

    for (const path of paths) {
      if (isSecretPath(path)) {
        return denied(
          event,
          "Reading, writing, moving, or deleting secret-bearing files is blocked.",
        );
      }
      if (mutationTool(toolName) && isProtectedPath(path)) {
        return denied(
          event,
          "Agent modification of protected governance and enforcement files is blocked.",
        );
      }
    }

    if (/^MCP(?::|\s|$)/i.test(toolName) && stateChangingMcp(input)) {
      return denied(
        event,
        "State-changing MCP tools require an owner-controlled or CI workflow.",
      );
    }

    return allowed();
  }

  if (event === "beforeShellExecution") {
    const command = String(input.command ?? "");

    if (shellReferencesSecret(command)) {
      return denied(event, "Shell access to secret-bearing paths is blocked.");
    }
    if (isDestructiveGit(command)) {
      return denied(
        event,
        "Destructive Git and force-push operations are blocked.",
      );
    }
    if (isProductionMutation(command)) {
      return denied(
        event,
        "Direct production, infrastructure, and remote database mutations are blocked.",
      );
    }
    if (shellMutatesProtectedPath(command)) {
      return denied(
        event,
        "Shell mutation of protected governance and enforcement files is blocked.",
      );
    }

    return allowed();
  }

  if (event === "beforeMCPExecution") {
    if (stateChangingMcp(input)) {
      return denied(
        event,
        "State-changing MCP tools require an owner-controlled or CI workflow.",
      );
    }
    return allowed();
  }

  if (event === "subagentStart") {
    const task = String(input.task ?? "");
    const productionTask =
      /\b(?:deploy|promote|release|publish|production|db\s+push|migration\s+repair|terraform\s+apply|kubectl\s+apply)\b/i.test(
        task,
      );
    const reviewOnly =
      /\b(?:review|audit|plan|inspect|verify|explain|research|dry[- ]run|read[- ]only)\b/i.test(
        task,
      );

    if (productionTask && !reviewOnly) {
      return denied(
        event,
        "Production mutation tasks may not be delegated to subagents.",
      );
    }
    return allowed();
  }

  return allowed();
}

function main() {
  let input;

  try {
    input = JSON.parse(readFileSync(0, "utf8"));
  } catch {
    process.stdout.write(
      `${JSON.stringify(
        denied("preToolUse", "Policy input was missing or malformed."),
      )}\n`,
    );
    process.exit(0);
  }

  process.stdout.write(`${JSON.stringify(evaluate(input))}\n`);
}

if (
  process.argv[1] &&
  import.meta.url === pathToFileURL(process.argv[1]).href
) {
  main();
}
