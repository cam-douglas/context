autowatch = 1;
inlets = 1;
outlets = 2;

var FIXTURE = "/Users/camdouglas/context/fixtures/silence.wav";
var promptText = "add a bridge";
var lastPreview = null;

function liveGet(api, property) {
  try {
    var value = api.get(property);
    if (value instanceof Array && value.length === 1) {
      return value[0];
    }
    return value;
  } catch (error) {
    return null;
  }
}

function isTruthy(value) {
  if (value === null || value === undefined || value === false) {
    return false;
  }
  if (value === 0 || value === "0") {
    return false;
  }
  if (value instanceof Array) {
    if (value.length === 0) {
      return false;
    }
    if (value.length === 1) {
      return isTruthy(value[0]);
    }
  }
  return true;
}

function postln(text) {
  post("Context: " + text + "\n");
}

function status(text) {
  outlet(1, text);
  postln(text);
}

function loadbang() {
  postln("harness loaded. Apply writes a Session MIDI clip named Context.");
  snapshot();
}

function bang() {
  snapshot();
}

function msg_int(value) {
  if (isTruthy(value)) {
    apply();
  }
}

function setprompt(text) {
  promptText = String(text || "");
}

function anything() {
  if (messagename === "text") {
    promptText = String(arguments[0] || "");
    return;
  }
  postln("ignored message: " + messagename);
}

function run() {
  if (!String(promptText || "").replace(/^\s+|\s+$/g, "")) {
    status("Type what to do next, then run.");
    return;
  }
  lastPreview = { prompt: promptText, ok: true };
  status("Preview ready. Audition stays in-device. Apply writes.");
  outlet(0, "preview", JSON.stringify(lastPreview));
}

function audition() {
  status("Audition (wet). No clips written.");
}

function findWriteTargets() {
  var liveSet = new LiveAPI("live_set");
  var count = 0;
  try {
    count = liveSet.getcount("tracks");
  } catch (error) {
    return { audio: null, midi: null, count: 0, attached: false };
  }
  var audio = null;
  var midi = null;
  var index;
  for (index = 0; index < count; index += 1) {
    var track = new LiveAPI("live_set tracks " + index);
    if (isTruthy(liveGet(track, "is_frozen"))) {
      continue;
    }
    if (isTruthy(liveGet(track, "has_midi_input"))) {
      if (!midi) {
        midi = { api: track, index: index };
      }
    } else if (!audio) {
      audio = { api: track, index: index };
    }
  }
  return { audio: audio, midi: midi, count: count, attached: true };
}

function firstEmptySlot(trackIndex) {
  var track = new LiveAPI("live_set tracks " + trackIndex);
  var count = 0;
  try {
    count = track.getcount("clip_slots");
  } catch (error) {
    count = 8;
  }
  var index;
  for (index = 0; index < count; index += 1) {
    var slot = new LiveAPI("live_set tracks " + trackIndex + " clip_slots " + index);
    if (!isTruthy(liveGet(slot, "has_clip"))) {
      return { slot: slot, index: index };
    }
  }
  return null;
}

function nameClip(trackIndex, slotIndex, name) {
  try {
    var clip = new LiveAPI("live_set tracks " + trackIndex + " clip_slots " + slotIndex + " clip");
    clip.set("name", name);
    return clip;
  } catch (error) {
    postln("could not name clip: " + error);
    return null;
  }
}

function duplicateToArrangement(trackApi, clipApi, beats) {
  try {
    trackApi.call("duplicate_clip_to_arrangement", "id", Number(clipApi.id), Number(beats));
    return true;
  } catch (errorId) {
    try {
      trackApi.call("duplicate_clip_to_arrangement", clipApi, Number(beats));
      return true;
    } catch (errorObj) {
      postln("arrangement duplicate skipped: " + errorObj);
      return false;
    }
  }
}

function showSessionView() {
  try {
    var view = new LiveAPI("live_set view");
    view.call("show_view", "Session");
    view.call("focus_view", "Session");
  } catch (error) {
    postln("could not focus Session View: " + error);
  }
}

function tryLive12Audio(audioTarget, audioPath) {
  if (!audioTarget) {
    return false;
  }
  try {
    audioTarget.api.call("create_audio_clip", audioPath, 0);
    return true;
  } catch (errorArr) {
    try {
      var empty = firstEmptySlot(audioTarget.index);
      if (!empty) {
        return false;
      }
      empty.slot.call("create_audio_clip", audioPath);
      return true;
    } catch (errorSlot) {
      postln("audio clip API unavailable (expected on Live 11): " + errorSlot);
      return false;
    }
  }
}

function tryLive12Midi(midiTarget) {
  try {
    midiTarget.api.call("create_midi_clip", 0, 4);
    return true;
  } catch (error) {
    postln("Live 12 arrangement MIDI API unavailable, using Session create_clip.");
    return false;
  }
}

function apply(audioPath) {
  var path = String(audioPath || FIXTURE);
  status("Apply clicked.");
  var targets;
  try {
    targets = findWriteTargets();
  } catch (error) {
    status("LiveAPI not attached. Click Edit on the device ON the Live track, then type the js object in THAT window.");
    return;
  }
  if (!targets.attached) {
    status("LiveAPI not attached. Click Edit on the device ON the Live track, then type the js object in THAT window.");
    return;
  }
  if (!targets.midi) {
    status("Add an unlocked MIDI track (Create → Insert MIDI Track), then click Apply again.");
    return;
  }

  var wroteAudio = tryLive12Audio(targets.audio, path);
  var wroteMidi = tryLive12Midi(targets.midi);
  var arranged = false;

  if (!wroteMidi) {
    var empty = firstEmptySlot(targets.midi.index);
    if (!empty) {
      status("Every MIDI Session slot is full. Delete one clip slot, then Apply.");
      return;
    }
    try {
      empty.slot.call("create_clip", 4);
      wroteMidi = true;
      var clip = nameClip(targets.midi.index, empty.index, "Context");
      if (clip) {
        arranged = duplicateToArrangement(targets.midi.api, clip, 0);
      }
    } catch (error) {
      status("Could not create a MIDI clip: " + error);
      return;
    }
  }

  showSessionView();

  if (wroteMidi && wroteAudio) {
    status("Wrote clips. Look at Session View. Undo with Cmd+Z.");
    return;
  }
  if (wroteMidi && arranged) {
    status("Wrote MIDI clip named Context in Session and Arrangement. Undo with Cmd+Z.");
    return;
  }
  if (wroteMidi) {
    status("Wrote MIDI clip named Context. Press Tab for Session View. Undo with Cmd+Z.");
    return;
  }
  status("Apply ran but wrote nothing. View → Max Window and send the last Context: line.");
}

function snapshot() {
  try {
    var targets = findWriteTargets();
    if (!targets.attached) {
      status("Harness loaded, but this window is not the Live device. Click Edit on the track device.");
      return;
    }
    var liveSet = new LiveAPI("live_set");
    var tempo = liveGet(liveSet, "tempo");
    postln("tempo " + tempo + " tracks " + targets.count);
    status(
      "Ready. " +
        targets.count +
        " tracks. Click Apply, then look at Session View on the MIDI track."
    );
  } catch (error) {
    status("Harness loaded, but LiveAPI is not attached. Put js in the Edit window of the TRACK device.");
  }
}
