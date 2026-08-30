import assert from "node:assert/strict";
import test from "node:test";

import {
  evaluate,
  isDestructiveGit,
  isProductionMutation,
  isProtectedPath,
  isSecretPath,
} from "./policy.mjs";

const decision = (input) => evaluate(input).permission;

test("recognizes secrets while allowing templates", () => {
  assert.equal(isSecretPath(".env"), true);
  assert.equal(isSecretPath("apps/web/.env.production"), true);
  assert.equal(isSecretPath("/Users/example/.aws/credentials"), true);
  assert.equal(isSecretPath("certs/service.pem"), true);
  assert.equal(isSecretPath(".env.example"), false);
  assert.equal(isSecretPath("id_ed25519.pub"), false);
});

test("recognizes protected governance paths", () => {
  assert.equal(isProtectedPath("AGENTS.md"), true);
  assert.equal(isProtectedPath(".cursor/hooks.json"), true);
  assert.equal(isProtectedPath(".cursor/hooks/policy.mjs"), true);
  assert.equal(isProtectedPath(".cursor/instructions/ROLES.md"), true);
  assert.equal(isProtectedPath(".cursor/STATE.md"), false);
  assert.equal(isProtectedPath("src/app.ts"), false);
});

test("blocks secret reads and allows public templates", () => {
  assert.equal(
    decision({ hook_event_name: "beforeReadFile", file_path: ".env.local" }),
    "deny",
  );
  assert.equal(
    decision({
      hook_event_name: "beforeReadFile",
      file_path: ".env.example",
    }),
    "allow",
  );
});

test("blocks tool writes to policy and secret paths", () => {
  assert.equal(
    decision({
      hook_event_name: "preToolUse",
      tool_name: "Write",
      tool_input: { path: ".cursor/hooks/policy.mjs" },
    }),
    "deny",
  );
  assert.equal(
    decision({
      hook_event_name: "preToolUse",
      tool_name: "Write",
      tool_input: { file_path: "apps/web/.env.local" },
    }),
    "deny",
  );
  assert.equal(
    decision({
      hook_event_name: "preToolUse",
      tool_name: "Read",
      tool_input: { path: ".cursor/hooks/policy.mjs" },
    }),
    "allow",
  );
  assert.equal(
    decision({
      hook_event_name: "preToolUse",
      tool_name: "Write",
      tool_input: { path: "src/app.ts" },
    }),
    "allow",
  );
});

test("blocks destructive Git while allowing inspection and staging", () => {
  const blocked = [
    "git reset --hard HEAD~1",
    "git clean -fd",
    "git checkout -- src/app.ts",
    "git restore src/app.ts",
    "git branch -D old-work",
    "git push --force-with-lease origin main",
    "git filter-repo --path secrets.txt --invert-paths",
  ];

  for (const command of blocked) {
    assert.equal(isDestructiveGit(command), true, command);
    assert.equal(
      decision({ hook_event_name: "beforeShellExecution", command }),
      "deny",
      command,
    );
  }

  for (const command of [
    "git status --short",
    "git diff --check",
    "git add .cursor/hooks.json",
    "git restore --staged src/app.ts",
  ]) {
    assert.equal(
      decision({ hook_event_name: "beforeShellExecution", command }),
      "allow",
      command,
    );
  }
});

test("blocks production mutations while allowing previews and local files", () => {
  const blocked = [
    "vercel --prod",
    "npx --yes vercel@latest deploy --prod",
    "supabase db push --linked --yes",
    "supabase migration repair --status reverted 123",
    "terraform apply plan.tfplan",
    "kubectl apply -f deployment.yml",
  ];

  for (const command of blocked) {
    assert.equal(isProductionMutation(command), true, command);
    assert.equal(
      decision({ hook_event_name: "beforeShellExecution", command }),
      "deny",
      command,
    );
  }

  for (const command of [
    "vercel",
    "supabase migration new add_profiles",
    "npm test",
    "node --test .cursor/hooks/policy.test.mjs",
  ]) {
    assert.equal(
      decision({ hook_event_name: "beforeShellExecution", command }),
      "allow",
      command,
    );
  }
});

test("blocks shell mutation of policy while allowing validation", () => {
  for (const command of [
    "rm .cursor/hooks.json",
    "rm -- ./.cursor/hooks.json",
    "mv replacement .cursor/instructions/ROLES.md",
    "python3 -c 'Path(\".cursor/hooks.json\").write_text(\"{}\")'",
    "sed -i '' 's/deny/allow/' .cursor/hooks/policy.mjs",
    "echo '{}' > .cursor/permissions.json",
    "apply_patch < policy-bypass.patch .cursor/hooks/policy.mjs",
    "dd if=replacement of=.cursor/cli.json",
    "git restore .cursor/hooks/policy.mjs",
  ]) {
    assert.equal(
      decision({ hook_event_name: "beforeShellExecution", command }),
      "deny",
      command,
    );
  }

  assert.equal(
    decision({
      hook_event_name: "beforeShellExecution",
      command: "node .cursor/scripts/validate-agent-config.mjs",
    }),
    "allow",
  );
});

test("blocks state-changing MCP and allows read-only discovery", () => {
  for (const tool_name of [
    "create_issue",
    "update_project",
    "deploy_to_vercel",
    "database:run_sql",
    "send_message",
    "browser_click",
    "filesystem:move_file",
  ]) {
    assert.equal(
      decision({
        hook_event_name: "beforeMCPExecution",
        tool_name,
        tool_input: "{}",
      }),
      "deny",
      tool_name,
    );
  }

  for (const tool_name of [
    "search_repositories",
    "get_project",
    "list_deployments",
    "query_analytics",
    "browser_snapshot",
  ]) {
    assert.equal(
      decision({
        hook_event_name: "beforeMCPExecution",
        tool_name,
        tool_input: "{}",
      }),
      "allow",
      tool_name,
    );
  }

  assert.equal(
    decision({
      hook_event_name: "beforeMCPExecution",
      tool_name: "run_sql",
      tool_input: '{"query":"DELETE FROM users"}',
    }),
    "deny",
  );
});

test("blocks delegated production tasks but allows review", () => {
  assert.equal(
    decision({
      hook_event_name: "subagentStart",
      task: "Deploy the current branch to production",
    }),
    "deny",
  );
  assert.equal(
    decision({
      hook_event_name: "subagentStart",
      task: "Audit the production deployment plan in read-only mode",
    }),
    "allow",
  );
});

test("allows unknown events without granting extra authority", () => {
  assert.deepEqual(evaluate({ hook_event_name: "sessionStart" }), {
    permission: "allow",
  });
});
