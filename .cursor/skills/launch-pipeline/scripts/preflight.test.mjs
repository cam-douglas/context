import test from "node:test";
import assert from "node:assert/strict";

import {
  classifyLifecycleMode,
  collectPreflight,
  extractSection,
  inferModeHint,
  summarizeState,
} from "./preflight.mjs";

const baseState = `# STATE.md

## Current Status

- In progress.

## Active Plan

- None.

## Active Workstream

- None.

## Active Role and Gate

- None.

## Pending Remediation

- None recorded.

## Owner Decision

- None.
`;

test("extracts state sections without consuming later headings", () => {
  assert.equal(extractSection(baseState, "Active Plan"), "- None.");
  assert.equal(
    extractSection(baseState, "Pending Remediation"),
    "- None recorded.",
  );
});

test("summarizes inactive state and leaves mode undetermined", () => {
  const state = summarizeState(baseState);
  assert.equal(state.active_plan, null);
  assert.equal(state.active_workstream, null);
  assert.equal(state.pending_remediation, null);
  assert.equal(inferModeHint(state), "undetermined");
});

test("prioritizes remediation over resume", () => {
  const state = summarizeState(
    baseState
      .replace("- None.\n\n## Active Role", "- docs/plans/phase_1.md\n\n## Active Role")
      .replace("- None recorded.", "- SEC-04 requires re-verification."),
  );
  assert.equal(inferModeHint(state), "remediation");
});

test("detects resume and closure hints from active work", () => {
  const resumeState = {
    ...summarizeState(baseState),
    active_workstream: "docs/workstreams/20260818-example/",
  };
  assert.equal(inferModeHint(resumeState), "resume");

  const closureState = {
    ...resumeState,
    current_status: "Ready for owner review.",
    owner_decision: "Owner decision required.",
  };
  assert.equal(inferModeHint(closureState), "closure");
});

test("classifies every explicit launch mode", () => {
  assert.equal(
    classifyLifecycleMode("Launch a new app for volunteer coordinators"),
    "new-idea",
  );
  assert.equal(
    classifyLifecycleMode("Plan a major feature and platform migration"),
    "major-change",
  );
  assert.equal(
    classifyLifecycleMode("Resume the active workstream"),
    "resume",
  );
  assert.equal(
    classifyLifecycleMode("Remediate the failed security gate and re-verify"),
    "remediation",
  );
  assert.equal(
    classifyLifecycleMode("Prepare release readiness and the owner handoff"),
    "closure",
  );
});

test("uses recorded state when request text does not select a mode", () => {
  assert.equal(
    classifyLifecycleMode("Please proceed", {
      active_workstream: "docs/workstreams/20260818-example/",
    }),
    "resume",
  );
});

test("current repository preflight is explicitly read-only", () => {
  const report = collectPreflight();
  assert.equal(report.read_only, true);
  assert.equal(report.schema_version, 1);
  assert.ok(
    ["READY", "MATERIALIZATION_REQUIRED", "BLOCKED"].includes(report.status),
  );
});
