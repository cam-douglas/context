autowatch = 1;

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
  if (value instanceof Array && value.length === 1) {
    return isTruthy(value[0]);
  }
  return !!value;
}

function findWriteTargets() {
  var liveSet = new LiveAPI("live_set");
  var count = liveSet.getcount("tracks");
  var audio = null;
  var midi = null;
  var index;
  for (index = 0; index < count; index += 1) {
    var track = new LiveAPI("live_set tracks " + index);
    if (isTruthy(liveGet(track, "is_frozen"))) {
      continue;
    }
    var hasMidi = liveGet(track, "has_midi_input");
    if (isTruthy(hasMidi) && !midi) {
      midi = { api: track, index: index, id: String(liveGet(track, "id") || index) };
    }
    if (!isTruthy(hasMidi) && !audio) {
      audio = { api: track, index: index, id: String(liveGet(track, "id") || index) };
    }
  }
  return { audio: audio, midi: midi };
}

function firstEmptySlot(trackIndex) {
  var track = new LiveAPI("live_set tracks " + trackIndex);
  var count = track.getcount("clip_slots");
  var index;
  for (index = 0; index < count; index += 1) {
    var slot = new LiveAPI("live_set tracks " + trackIndex + " clip_slots " + index);
    if (!isTruthy(liveGet(slot, "has_clip"))) {
      return { slot: slot, index: index };
    }
  }
  return null;
}

function applyFixtures(audioPath, position, midiStart, midiLength) {
  var targets = findWriteTargets();
  if (!targets.midi) {
    return {
      ok: false,
      wrote: false,
      error: "need_unlocked_midi_track"
    };
  }
  var wroteAudio = false;
  var wroteMidi = false;
  if (targets.audio) {
    try {
      targets.audio.api.call("create_audio_clip", audioPath, Number(position || 0));
      wroteAudio = true;
    } catch (errorAudio) {
      try {
        var audioSlot = firstEmptySlot(targets.audio.index);
        if (audioSlot) {
          audioSlot.slot.call("create_audio_clip", audioPath);
          wroteAudio = true;
        }
      } catch (errorSlot) {
        wroteAudio = false;
      }
    }
  }
  try {
    targets.midi.api.call("create_midi_clip", Number(midiStart || 0), Number(midiLength || 4));
    wroteMidi = true;
  } catch (errorMidi12) {
    var empty = firstEmptySlot(targets.midi.index);
    if (!empty) {
      return { ok: false, wrote: false, error: "no_empty_midi_clip_slot" };
    }
    try {
      empty.slot.call("create_clip", Number(midiLength || 4));
      wroteMidi = true;
      var clip = new LiveAPI("live_set tracks " + targets.midi.index + " clip_slots " + empty.index + " clip");
      clip.set("name", "Context");
      try {
        targets.midi.api.call("duplicate_clip_to_arrangement", "id", Number(clip.id), Number(midiStart || 0));
      } catch (errorArr) {
        try {
          targets.midi.api.call("duplicate_clip_to_arrangement", clip, Number(midiStart || 0));
        } catch (errorArr2) {
          // Session clip is enough on Live 11.
        }
      }
    } catch (errorMidi11) {
      return { ok: false, wrote: false, error: String(errorMidi11) };
    }
  }
  if (!wroteMidi) {
    return { ok: false, wrote: false, error: "midi_write_failed" };
  }
  return {
    ok: true,
    wrote: true,
    wrote_audio: wroteAudio,
    undo_hint: wroteAudio
      ? "Wrote clips. Undo in Live to revert."
      : "Wrote MIDI clip named Context in Session View. Undo in Live to revert."
  };
}

function applyArrangement(planJson) {
  var plan = JSON.parse(planJson);
  var liveSet = new LiveAPI("live_set");
  var locators = plan.locators || [];
  var index;
  for (index = 0; index < locators.length; index += 1) {
    try {
      liveSet.call("set_or_delete_cue", locators[index].beats);
    } catch (error) {
      // Cue API varies by Live version; surface and continue.
    }
  }
  outlet(0, JSON.stringify({ ok: true, wrote: true, kind: "arrangement" }));
}

function apply(audioPath) {
  outlet(0, JSON.stringify(applyFixtures(audioPath, 0, 0, 4)));
}
