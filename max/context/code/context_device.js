autowatch = 1;
inlets = 1;
outlets = 2;

var STATUS = {
  sidecar_down: "Context sidecar is not running on localhost. Start it, then retry.",
  empty_prompt: "Type what to do next, then run.",
  apply_success: "Wrote clips into the arrangement. Undo in Live to revert.",
  apply_failure: "Could not write every clip. Undo in Live if the arrangement looks partial.",
  empty_source: "Play or select material on this track, or drop a loop."
};

var state = {
  health: null,
  prompt: "",
  mode: "track_follow",
  scope: "this_track",
  focus: "host_clip",
  reverence: 0.5,
  abstraction: 0.5,
  amount: 0.4,
  wet: 0.0,
  tempo_key_lock: 1,
  variation: 0,
  locks: [],
  target_section: null,
  drop_in_path: "",
  reference_path: "",
  preview: null,
  fixture_audio: "",
  sidecar_port: 8765
};

function sidecarHealthy() {
  return state.health && state.health.ok === true;
}

function canRun() {
  return sidecarHealthy() && String(state.prompt || "").replace(/\s+/g, "").length > 0;
}

function canApply() {
  return sidecarHealthy() && state.preview;
}

function canAudition() {
  return !!state.preview;
}

function statusLine() {
  if (!sidecarHealthy()) {
    return STATUS.sidecar_down;
  }
  if (!String(state.prompt || "").replace(/^\s+|\s+$/g, "")) {
    return STATUS.empty_prompt;
  }
  if (!state.preview) {
    return "Type what to do next, then run.";
  }
  return "Preview ready. Audition stays in-device. Apply writes.";
}

function setprompt(text) {
  state.prompt = String(text || "");
  bang();
}

function setmode(name) {
  state.mode = String(name || "track_follow");
}

function setscope(name) {
  state.scope = String(name || "this_track");
}

function setfocus(name) {
  state.focus = String(name || "host_clip");
}

function setdropin(path) {
  state.drop_in_path = String(path || "");
}

function setreference(path) {
  state.reference_path = String(path || "");
}

function setknob(name, value) {
  state[name] = Number(value);
}

function sethealth(jsonText) {
  try {
    state.health = JSON.parse(jsonText);
  } catch (error) {
    state.health = null;
  }
  bang();
}

function setpreview(jsonText) {
  try {
    state.preview = JSON.parse(jsonText);
  } catch (error) {
    state.preview = null;
  }
  bang();
}

function setfixture(path) {
  state.fixture_audio = String(path || "");
}

function audition() {
  if (!canAudition()) {
    outlet(1, statusLine());
    return;
  }
  outlet(1, "Audition (wet). No clips written.");
}

function bang() {
  outlet(1, statusLine());
  outlet(0, JSON.stringify({
    can_run: canRun(),
    can_apply: canApply(),
    can_audition: canAudition(),
    reference_knobs: String(state.reference_path || "").length > 0,
    status: statusLine(),
    audition_writes: false
  }));
}
