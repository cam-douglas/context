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

function inferRole(name) {
  var lowered = String(name || "").toLowerCase();
  if (!lowered) {
    return "other";
  }
  if (/(drum|drums|kit|kick|perc|beat)/.test(lowered)) {
    return "drums";
  }
  if (/(bass|808|sub)/.test(lowered)) {
    return "bass";
  }
  if (/(vocal|vox|voice)/.test(lowered)) {
    return "vocal";
  }
  if (/(lead|melody)/.test(lowered)) {
    return "lead";
  }
  if (/(harm|pad|chord|keys|piano|guitar)/.test(lowered)) {
    return "harmony";
  }
  if (/(fx|riser|sweep|impact|transition)/.test(lowered)) {
    return "fx";
  }
  if (/(ambient|atm|texture|drone)/.test(lowered)) {
    return "ambient";
  }
  return "other";
}

function clipKindForTrack(track) {
  var hasMidi = liveGet(track, "has_midi_input");
  return hasMidi ? "midi" : "audio";
}

function collectClips(trackPath, kind) {
  var clips = [];
  var clipSlots = new LiveAPI(trackPath + " clip_slots");
  var count = 0;
  try {
    count = clipSlots.getcount("clip_slots");
  } catch (error) {
    count = 0;
  }
  var index;
  for (index = 0; index < count; index += 1) {
    var slot = new LiveAPI(trackPath + " clip_slots " + index);
    var hasClip = liveGet(slot, "has_clip");
    if (!hasClip) {
      continue;
    }
    var clip = new LiveAPI(trackPath + " clip_slots " + index + " clip");
    var item = {
      id: String(liveGet(clip, "id") || index),
      kind: kind,
      start_beats: Number(liveGet(clip, "start_time") || 0),
      length_beats: Number(liveGet(clip, "length") || 4)
    };
    if (kind === "audio") {
      item.file_path = String(liveGet(clip, "file_path") || "live://clip");
    } else {
      item.notes = [];
    }
    clips.push(item);
  }
  return clips;
}

function buildProjectSnapshot() {
  var liveSet = new LiveAPI("live_set");
  var thisDevice = new LiveAPI("this_device");
  var hostTrack = new LiveAPI(thisDevice.get("canonical_parent"));
  var trackCount = 0;
  try {
    trackCount = liveSet.getcount("tracks");
  } catch (error) {
    trackCount = 0;
  }
  var tracks = [];
  var index;
  for (index = 0; index < trackCount; index += 1) {
    var path = "live_set tracks " + index;
    var track = new LiveAPI(path);
    var name = String(liveGet(track, "name") || "Track " + index);
    var kind = clipKindForTrack(track);
    tracks.push({
      id: String(liveGet(track, "id") || index),
      name: name,
      kind: kind,
      inferred_role: inferRole(name),
      clips: collectClips(path, kind),
      frozen: Boolean(liveGet(track, "is_frozen")),
      locked: false
    });
  }
  var hostId = String(liveGet(hostTrack, "id") || (tracks[0] && tracks[0].id) || "0");
  var hostName = String(liveGet(hostTrack, "name") || (tracks[0] && tracks[0].name) || "Host");
  return {
    project: {
      tempo_bpm: Number(liveGet(liveSet, "tempo") || 120),
      musical_key: String(liveGet(liveSet, "scale_name") || ""),
      playhead_beats: Number(liveGet(new LiveAPI("live_set"), "current_song_time") || 0),
      tracks: tracks
    },
    host_track: {
      id: hostId,
      name: hostName,
      inferred_role: inferRole(hostName)
    }
  };
}

function snapshot() {
  outlet(0, JSON.stringify(buildProjectSnapshot()));
}
