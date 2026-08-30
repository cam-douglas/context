#pragma once

#include "PromptPolicy.h"

#include <JuceHeader.h>
#include <atomic>
#include <vector>

class ContextAudioProcessor : public juce::AudioProcessor
{
public:
  ContextAudioProcessor();
  ~ContextAudioProcessor() override;

  void prepareToPlay(double sampleRate, int samplesPerBlock) override;
  void releaseResources() override;
  bool isBusesLayoutSupported(const BusesLayout& layouts) const override;
  void processBlock(juce::AudioBuffer<float>&, juce::MidiBuffer&) override;

  juce::AudioProcessorEditor* createEditor() override;
  bool hasEditor() const override { return true; }

  const juce::String getName() const override { return "Context 14"; }
  bool acceptsMidi() const override { return false; }
  bool producesMidi() const override { return false; }
  bool isMidiEffect() const override { return false; }
  double getTailLengthSeconds() const override { return 0.0; }

  int getNumPrograms() override { return 1; }
  int getCurrentProgram() override { return 0; }
  void setCurrentProgram(int) override {}
  const juce::String getProgramName(int) override { return {}; }
  void changeProgramName(int, const juce::String&) override {}

  void getStateInformation(juce::MemoryBlock& destData) override;
  void setStateInformation(const void* data, int sizeInBytes) override;

  juce::AudioProcessorValueTreeState parameters;
  juce::String prompt{"type what to make"};
  juce::String systemPrompt{context::defaultSystemPrompt()};
  juce::String rules{context::defaultRules()};
  juce::String negativePrompt{context::defaultNegativePrompt()};
  juce::String lastComposedPrompt;
  juce::File lastWavFile;
  juce::File lastMidFile;
  juce::File referenceFile;
  juce::File sampleLibrary;
  bool copyCapturedAudio(juce::AudioBuffer<float>& dest, double& sampleRateOut) const;
  bool loadAuditionWav(const juce::File& file);
  void setAuditionPlaying(bool shouldPlay);
  bool isAuditionPlaying() const { return auditionPlaying.load(); }
  bool hasAudition() const;
  void copyWaveformPeaks(std::vector<float>& dest, int bins) const;

private:
  static juce::AudioProcessorValueTreeState::ParameterLayout createLayout();
  mutable juce::CriticalSection historyLock;
  juce::AudioBuffer<float> history;
  int historyWrite = 0;
  double currentSampleRate = 44100.0;
  std::atomic<bool> hasSignal{false};
  mutable juce::CriticalSection auditionLock;
  juce::AudioBuffer<float> auditionBuffer;
  double auditionSampleRate = 44100.0;
  double auditionFrame = 0.0;
  std::atomic<bool> auditionPlaying{false};
  JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR(ContextAudioProcessor)
};
