#include "DropWriter.h"

#include <cmath>
#include <vector>

namespace
{
  constexpr int kPpq = 480;
  constexpr double kSampleRate = 44100.0;

  juce::String normalized(const juce::String& prompt)
  {
    return prompt.toLowerCase().retainCharacters("abcdefghijklmnopqrstuvwxyz0123456789 ");
  }

  bool hasWord(const juce::String& text, const juce::String& needle)
  {
    return text.contains(needle);
  }

  std::vector<int> scaleFor(const juce::String& key)
  {
    if (key == "C")
      return { 60, 62, 64, 65, 67, 69, 71, 72 };
    return { 57, 60, 62, 64, 67, 69, 72, 74 };
  }

  bool writeMidi(const juce::File& dest, const std::vector<PhraseNote>& notes, double tempoBpm, const juce::String& name)
  {
    juce::MidiMessageSequence sequence;
    sequence.addEvent(juce::MidiMessage::textMetaEvent(3, name), 0.0);
    sequence.addEvent(juce::MidiMessage::tempoMetaEvent(juce::roundToInt(60000000.0 / tempoBpm)), 0.0);
    sequence.addEvent(juce::MidiMessage::timeSignatureMetaEvent(4, 4), 0.0);
    for (const auto& note : notes)
    {
      sequence.addEvent(juce::MidiMessage::noteOn(1, note.pitch, (juce::uint8)juce::jlimit(1, 127, note.velocity)), note.startBeats * kPpq);
      sequence.addEvent(juce::MidiMessage::noteOff(1, note.pitch), (note.startBeats + note.lengthBeats) * kPpq);
    }
    sequence.updateMatchedPairs();
    sequence.sort();
    juce::MidiFile midi;
    midi.setTicksPerQuarterNote(kPpq);
    midi.addTrack(sequence);
    dest.deleteFile();
    juce::FileOutputStream stream(dest);
    return stream.openedOk() && midi.writeTo(stream, 1);
  }

  bool writeWav(const juce::File& dest, const juce::AudioBuffer<float>& buffer)
  {
    dest.deleteFile();
    auto stream = dest.createOutputStream();
    if (stream == nullptr)
      return false;
    juce::WavAudioFormat format;
    std::unique_ptr<juce::AudioFormatWriter> writer(
        format.createWriterFor(stream.release(), kSampleRate, static_cast<unsigned int>(buffer.getNumChannels()), 16, {}, 0));
    return writer != nullptr && writer->writeFromAudioSampleBuffer(buffer, 0, buffer.getNumSamples());
  }

  void renderNotes(juce::AudioBuffer<float>& buffer,
                   const std::vector<PhraseNote>& notes,
                   double tempo,
                   float reverence,
                   float abstraction)
  {
    double endBeats = 0.0;
    for (const auto& note : notes)
      endBeats = juce::jmax(endBeats, note.startBeats + note.lengthBeats);
    const int numSamples = juce::jmax(1, juce::roundToInt((endBeats + 0.25) * 60.0 / tempo * kSampleRate));
    buffer.setSize(2, numSamples);
    buffer.clear();
    const float detune = (1.0f - reverence) * 0.035f + abstraction * 0.02f;
    const float sawMix = (1.0f - reverence) * 0.75f;
    const float octaveMix = abstraction * 0.55f;
    for (const auto& note : notes)
    {
      const int start = juce::roundToInt(note.startBeats * 60.0 / tempo * kSampleRate);
      const int length = juce::jmax(1, juce::roundToInt(note.lengthBeats * 60.0 / tempo * kSampleRate));
      const double freq = 440.0 * std::pow(2.0, (note.pitch - 69) / 12.0);
      const float vel = note.velocity / 127.0f;
      double phase = 0.0;
      for (int i = 0; i < length && start + i < numSamples; ++i)
      {
        const double t = static_cast<double>(i) / kSampleRate;
        float osc = 0.0f;
        float env = static_cast<float>(juce::jmin(1.0, i / (0.01 * kSampleRate)) * std::exp(-t * (note.pitch < 40 ? 16.0 : 3.2 + reverence * 2.5)));
        if (note.pitch < 40)
        {
          const double sweep = freq * std::exp(-t * 8.0);
          phase += 2.0 * juce::MathConstants<double>::pi * sweep / kSampleRate;
          osc = static_cast<float>(std::sin(phase));
        }
        else if (note.pitch == 42 || note.pitch == 44 || note.pitch == 46)
        {
          osc = static_cast<float>(((i * 1103515245 + 12345) % 32768) / 16384.0f - 1.0f);
          env = static_cast<float>(std::exp(-t * 40.0));
        }
        else
        {
          const float sine = static_cast<float>(std::sin(2.0 * juce::MathConstants<double>::pi * freq * t));
          const float saw = static_cast<float>(2.0 * std::fmod(freq * t, 1.0) - 1.0);
          osc = sine * (1.0f - sawMix) + saw * sawMix;
          osc += octaveMix * static_cast<float>(std::sin(4.0 * juce::MathConstants<double>::pi * freq * t));
        }
        const float sample = 0.5f * vel * env * osc;
        buffer.addSample(0, start + i, sample);
        buffer.addSample(1, start + i, sample * (1.0f - detune * 8.0f) + 0.15f * abstraction * sample);
      }
    }
    const auto peak = buffer.getMagnitude(0, buffer.getNumSamples());
    if (peak > 0.001f)
      buffer.applyGain(0.89f / peak);
  }

  void addNote(std::vector<PhraseNote>& notes, int pitch, double start, double length, int velocity = 100)
  {
    notes.push_back({ pitch, start, length, velocity });
  }
}

PromptPlan DropWriter::parsePrompt(const juce::String& prompt)
{
  PromptPlan plan;
  plan.prompt = prompt.trim();
  const auto text = normalized(plan.prompt);
  plan.seed = std::abs(plan.prompt.hashCode());

  if (auto bpm = text.fromFirstOccurrenceOf("bpm", false, false); text.contains("bpm"))
  {
    const auto before = text.upToFirstOccurrenceOf("bpm", false, false).trim();
    const auto number = before.fromLastOccurrenceOf(" ", false, false);
    const auto value = (number.isEmpty() ? before : number).getDoubleValue();
    if (value >= 40.0 && value <= 220.0)
      plan.tempoBpm = value;
  }
  if (text.contains("bar"))
  {
    const auto before = text.upToFirstOccurrenceOf("bar", false, false).trim();
    const auto token = before.fromLastOccurrenceOf(" ", false, false);
    const int bars = (token.isEmpty() ? before : token).getIntValue();
    if (bars >= 1 && bars <= 16)
      plan.bars = bars;
  }
  if (text.contains("c major") || text.contains("cmaj") || text.contains("in c"))
    plan.key = "C";
  else if (text.contains("a minor") || text.contains("in am") || text.contains("minor"))
    plan.key = "Am";
  else if (text.contains("major"))
    plan.key = "C";

  struct Rule
  {
    PromptStyle style;
    const char* name;
    const char* a;
    const char* b;
  };
  const Rule rules[] = {
    { PromptStyle::house, "house", "house", "four on the floor" },
    { PromptStyle::techno, "techno", "techno", "acid" },
    { PromptStyle::ambient, "ambient", "ambient", "pad" },
    { PromptStyle::ambient, "ambient", "drone", "texture" },
    { PromptStyle::lofi, "lofi", "lofi", "lo fi" },
    { PromptStyle::trap, "trap", "trap", "808" },
    { PromptStyle::dnb, "dnb", "dnb", "drum and bass" },
    { PromptStyle::jazz, "jazz", "jazz", "seventh" },
    { PromptStyle::funk, "funk", "funk", "groove" },
    { PromptStyle::pop, "pop", "pop", "chorus" },
    { PromptStyle::arp, "arp", "arp", "arpeggio" },
    { PromptStyle::melody, "melody", "melody", "piano" },
    { PromptStyle::melody, "melody", "lead", "riff" },
    { PromptStyle::bass, "bass", "bassline", "bass" },
    { PromptStyle::drums, "drums", "drums", "percussion" },
  };
  for (const auto& rule : rules)
  {
    if (hasWord(text, rule.a) || hasWord(text, rule.b))
    {
      plan.style = rule.style;
      plan.styleName = rule.name;
      break;
    }
  }

  if (plan.tempoBpm == 120.0)
  {
    if (plan.style == PromptStyle::house)
      plan.tempoBpm = 124.0;
    else if (plan.style == PromptStyle::techno)
      plan.tempoBpm = 130.0;
    else if (plan.style == PromptStyle::trap)
      plan.tempoBpm = 140.0;
    else if (plan.style == PromptStyle::dnb)
      plan.tempoBpm = 174.0;
    else if (plan.style == PromptStyle::ambient)
      plan.tempoBpm = 80.0;
    else if (plan.style == PromptStyle::lofi)
      plan.tempoBpm = 86.0;
  }

  auto slug = (plan.styleName + "-" + text).replaceCharacters(" ", "-").retainCharacters("abcdefghijklmnopqrstuvwxyz0123456789-");
  while (slug.contains("--"))
    slug = slug.replace("--", "-");
  slug = slug.substring(0, 48).trimCharactersAtStart("-").trimCharactersAtEnd("-");
  plan.slug = slug.isNotEmpty() ? slug : plan.styleName;
  return plan;
}

std::vector<PhraseNote> DropWriter::phraseFor(const PromptPlan& plan)
{
  std::vector<PhraseNote> notes;
  const int beats = plan.bars * 4;
  const auto scale = scaleFor(plan.key);
  const int seed = plan.seed;

  if (plan.style == PromptStyle::house)
  {
    for (int beat = 0; beat < beats; ++beat)
    {
      addNote(notes, 36, beat, 0.2, 120);
      addNote(notes, 42, beat + 0.5, 0.15, 70);
      if (beat % 2 == 1)
        addNote(notes, 39, beat, 0.2, 110);
      if (beat % 4 == 0 || beat % 4 == 3)
        addNote(notes, 33, beat, 0.4, 100);
    }
    return notes;
  }
  if (plan.style == PromptStyle::techno)
  {
    for (int beat = 0; beat < beats; ++beat)
    {
      addNote(notes, 36, beat, 0.18, 120);
      addNote(notes, 42, beat + 0.25, 0.1, 80);
      addNote(notes, 42, beat + 0.75, 0.1, 60);
    }
    return notes;
  }
  if (plan.style == PromptStyle::ambient || plan.style == PromptStyle::lofi)
  {
    const int roots[] = { scale[0] - 12, scale[2] - 12, scale[4] - 12, scale[0] };
    for (int bar = 0; bar < plan.bars; ++bar)
    {
      const int root = roots[(bar + seed) % 4];
      addNote(notes, root, bar * 4, 4.0, 70);
      addNote(notes, root + 7, bar * 4, 4.0, 55);
      addNote(notes, root + 12, bar * 4 + 2, 2.0, 50);
    }
    if (plan.style == PromptStyle::lofi)
    {
      for (int beat = 0; beat < beats; beat += 2)
        addNote(notes, 42, beat + 0.5, 0.1, 40);
    }
    return notes;
  }
  if (plan.style == PromptStyle::trap)
  {
    for (int beat = 0; beat < beats; ++beat)
    {
      if (beat % 4 == 0)
        addNote(notes, 36, beat, 0.2, 120);
      addNote(notes, 42, beat + 0.5, 0.08, 60);
      if (beat % 4 == 2)
        addNote(notes, 38, beat, 0.15, 110);
      if (beat % 2 == 0)
        addNote(notes, 33, beat + 0.75, 0.2, 95);
    }
    return notes;
  }
  if (plan.style == PromptStyle::dnb)
  {
    for (int beat = 0; beat < beats; ++beat)
    {
      addNote(notes, 36, beat % 2 == 0 ? beat : beat + 0.25, 0.12, 120);
      addNote(notes, 42, beat + 0.5, 0.08, 75);
      if (beat % 2 == 1)
        addNote(notes, 40, beat, 0.12, 105);
    }
    return notes;
  }
  if (plan.style == PromptStyle::jazz || plan.style == PromptStyle::funk || plan.style == PromptStyle::pop)
  {
    const int voicings[4][4] = { { 0, 4, 7, 11 }, { 2, 5, 9, 12 }, { 0, 5, 7, 10 }, { 0, 4, 7, 9 } };
    for (int bar = 0; bar < plan.bars; ++bar)
    {
      for (int tone = 0; tone < 4; ++tone)
        addNote(notes, scale[0] - 12 + voicings[(bar + seed) % 4][tone], bar * 4, plan.style == PromptStyle::funk ? 1.0 : 3.5, 80);
      if (plan.style == PromptStyle::funk)
      {
        addNote(notes, 36, bar * 4, 0.15, 110);
        addNote(notes, 38, bar * 4 + 2, 0.15, 100);
      }
    }
    return notes;
  }
  if (plan.style == PromptStyle::bass)
  {
    const int pattern[] = { 0, 0, 3, 0, 5, 5, 3, 0 };
    for (int beat = 0; beat < beats; ++beat)
      addNote(notes, scale[0] - 24 + pattern[(beat + seed) % 8], beat, 0.45, 110);
    return notes;
  }
  if (plan.style == PromptStyle::drums)
  {
    for (int beat = 0; beat < beats; ++beat)
    {
      if (beat % 4 == 0 || beat % 4 == 2)
        addNote(notes, 36, beat, 0.15, 115);
      if (beat % 4 == 1 || beat % 4 == 3)
        addNote(notes, 38, beat, 0.15, 105);
      addNote(notes, 42, beat + 0.5, 0.1, 70);
    }
    return notes;
  }
  if (plan.style == PromptStyle::arp)
  {
    const int degrees[] = { 0, 2, 4, 7, 4, 2 };
    for (int i = 0; i < beats * 2; ++i)
      addNote(notes, scale[degrees[i % 6] % static_cast<int>(scale.size())], i * 0.5, 0.4, 90);
    return notes;
  }

  for (int i = 0; i < beats; ++i)
  {
    addNote(notes, scale[(seed + i * 3) % static_cast<int>(scale.size())], static_cast<double>(i), i % 4 == 0 ? 1.2 : 0.7, 95);
    if (i % 4 == 0)
      addNote(notes, scale[0] - 12, static_cast<double>(i), 2.0, 70);
  }
  return notes;
}

juce::File DropWriter::pluginFolder()
{
  auto folder = juce::File::getSpecialLocation(juce::File::userApplicationDataDirectory)
                    .getChildFile("Context")
                    .getChildFile("Plugin");
  folder.createDirectory();
  return folder;
}

juce::File DropWriter::auditionFolder()
{
  auto folder = pluginFolder().getChildFile(".audition");
  folder.createDirectory();
  return folder;
}

juce::File DropWriter::referenceFolder()
{
  auto folder = pluginFolder().getChildFile("Reference");
  folder.createDirectory();
  return folder;
}

juce::File DropWriter::dumpsFolder()
{
  return pluginFolder();
}

juce::File DropWriter::dropFolder()
{
  return pluginFolder();
}

juce::File DropWriter::fixtureDir()
{
  return {};
}

DropResult DropWriter::writeDrops(const DropRequest& request)
{
  DropResult result;
  result.folder = dropFolder();
  if (!result.folder.isDirectory())
  {
    result.message = "Could not create ~/Library/Application Support/Context/Plugin.";
    return result;
  }

  const auto plan = parsePrompt(request.prompt);
  if (plan.prompt.isEmpty())
  {
    result.message = "Type what to make, then Apply.";
    return result;
  }

  auto notes = phraseFor(plan);
  std::vector<PhraseNote> extras;
  for (size_t i = 0; i < notes.size(); ++i)
  {
    if (request.reverence >= 0.7f)
      notes[i].startBeats = std::round(notes[i].startBeats * 4.0) / 4.0;
    else if (request.reverence <= 0.3f)
    {
      notes[i].pitch += (i % 2 == 0 ? -5 : 4);
      notes[i].startBeats = juce::jmax(0.0, notes[i].startBeats + (i % 2 == 0 ? 0.14 : -0.08));
    }
    if (request.abstraction >= 0.7f)
    {
      if (i % 3 == 0)
        notes[i].pitch += 7;
      auto ghost = notes[i];
      ghost.pitch += 12;
      ghost.startBeats += 0.25;
      ghost.velocity = juce::jmax(36, ghost.velocity - 28);
      extras.push_back(ghost);
    }
  }
  notes.insert(notes.end(), extras.begin(), extras.end());

  const auto midiDest = result.folder.getChildFile(plan.slug + ".mid");
  const auto wavDest = result.folder.getChildFile(plan.slug + ".wav");
  if (!writeMidi(midiDest, notes, plan.tempoBpm, plan.styleName) || ![&] {
        juce::AudioBuffer<float> audio;
        renderNotes(audio, notes, plan.tempoBpm, request.reverence, request.abstraction);
        return writeWav(wavDest, audio);
      }())
  {
    result.message = "Could not write the loop files.";
    return result;
  }
  result.files.add(wavDest);
  result.files.add(midiDest);
  if (plan.style != PromptStyle::house)
  {
    for (const auto* name : { "HOUSE-LOOP.wav", "HOUSE-LOOP.mid", "house-loop.wav", "house-loop.mid" })
      result.folder.getChildFile(name).deleteFile();
  }

  result.ok = true;
  result.message = "Wrote " + wavDest.getFileName() + " to Context/Plugin (" + plan.styleName + ", "
                   + juce::String(plan.tempoBpm, 0) + " BPM).";
  return result;
}
