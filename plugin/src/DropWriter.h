#pragma once

#include <JuceHeader.h>

struct PhraseNote
{
  int pitch = 60;
  double startBeats = 0.0;
  double lengthBeats = 0.5;
  int velocity = 100;
};

enum class PromptStyle
{
  house,
  techno,
  ambient,
  lofi,
  trap,
  dnb,
  jazz,
  melody,
  bass,
  drums,
  arp,
  funk,
  pop,
  custom
};

struct PromptPlan
{
  juce::String prompt;
  PromptStyle style = PromptStyle::custom;
  juce::String styleName{"custom"};
  double tempoBpm = 120.0;
  int bars = 4;
  juce::String key{"Am"};
  juce::String slug{"context"};
  int seed = 0;
};

struct DropRequest
{
  juce::String prompt{"type what to make"};
  double tempoBpm = 120.0;
  const juce::AudioBuffer<float>* captured = nullptr;
  double capturedSampleRate = 44100.0;
  bool capturedHasSignal = false;
  float reverence = 0.5f;
  float abstraction = 0.5f;
};

struct DropResult
{
  bool ok = false;
  juce::String message;
  juce::File folder;
  juce::Array<juce::File> files;
};

class DropWriter
{
public:
  static juce::File dropFolder();
  static juce::File dumpsFolder();
  static juce::File pluginFolder();
  static juce::File auditionFolder();
  static juce::File referenceFolder();
  static juce::File fixtureDir();
  static PromptPlan parsePrompt(const juce::String& prompt);
  static std::vector<PhraseNote> phraseFor(const PromptPlan& plan);
  static DropResult writeDrops(const DropRequest& request);
};
