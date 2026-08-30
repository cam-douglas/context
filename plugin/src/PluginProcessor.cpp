#include "PluginProcessor.h"
#include "PluginEditor.h"
#include "SidecarSupervisor.h"

#include <cmath>

ContextAudioProcessor::ContextAudioProcessor()
    : AudioProcessor(BusesProperties()
                         .withInput("Input", juce::AudioChannelSet::stereo(), true)
                         .withOutput("Output", juce::AudioChannelSet::stereo(), true)),
      parameters(*this, nullptr, "CONTEXT", createLayout())
{
  sampleLibrary = juce::File::getSpecialLocation(juce::File::userApplicationDataDirectory)
                      .getChildFile("Context")
                      .getChildFile("Samples");
  sampleLibrary.createDirectory();
  SidecarSupervisor::instance().retainProcessor();
}

ContextAudioProcessor::~ContextAudioProcessor()
{
  SidecarSupervisor::instance().releaseProcessor();
}

juce::AudioProcessorValueTreeState::ParameterLayout ContextAudioProcessor::createLayout()
{
  std::vector<std::unique_ptr<juce::RangedAudioParameter>> params;
  params.push_back(std::make_unique<juce::AudioParameterFloat>(juce::ParameterID{"reverence", 1}, "Reverence", 0.0f, 1.0f, 0.5f));
  params.push_back(std::make_unique<juce::AudioParameterFloat>(juce::ParameterID{"abstraction", 1}, "Abstraction", 0.0f, 1.0f, 0.5f));
  return {params.begin(), params.end()};
}

void ContextAudioProcessor::prepareToPlay(double sampleRate, int)
{
  const juce::ScopedLock lock(historyLock);
  currentSampleRate = sampleRate > 0.0 ? sampleRate : 44100.0;
  history.setSize(2, juce::jmax(1, juce::roundToInt(currentSampleRate * 8.0)));
  history.clear();
  historyWrite = 0;
  hasSignal.store(false);
}

void ContextAudioProcessor::releaseResources() {}

bool ContextAudioProcessor::copyCapturedAudio(juce::AudioBuffer<float>& dest, double& sampleRateOut) const
{
  const juce::ScopedLock lock(historyLock);
  sampleRateOut = currentSampleRate;
  if (!hasSignal.load() || history.getNumSamples() <= 0)
    return false;
  dest.setSize(history.getNumChannels(), history.getNumSamples());
  dest.clear();
  const int cap = history.getNumSamples();
  const int start = historyWrite;
  for (int ch = 0; ch < history.getNumChannels(); ++ch)
  {
    dest.copyFrom(ch, 0, history, ch, start, cap - start);
    if (start > 0)
      dest.copyFrom(ch, cap - start, history, ch, 0, start);
  }
  double sum = 0.0;
  int count = 0;
  for (int ch = 0; ch < dest.getNumChannels(); ++ch)
  {
    const auto* data = dest.getReadPointer(ch);
    for (int i = 0; i < dest.getNumSamples(); ++i)
    {
      sum += static_cast<double>(data[i]) * static_cast<double>(data[i]);
      ++count;
    }
  }
  const float rms = count > 0 ? static_cast<float>(std::sqrt(sum / static_cast<double>(count))) : 0.0f;
  return rms > 0.05f;
}

bool ContextAudioProcessor::isBusesLayoutSupported(const BusesLayout& layouts) const
{
  const auto mainIn = layouts.getMainInputChannelSet();
  const auto mainOut = layouts.getMainOutputChannelSet();
  return !mainIn.isDisabled() && mainIn == mainOut
         && (mainOut == juce::AudioChannelSet::mono() || mainOut == juce::AudioChannelSet::stereo());
}

bool ContextAudioProcessor::hasAudition() const
{
  const juce::ScopedLock lock(auditionLock);
  return auditionBuffer.getNumSamples() > 0;
}

bool ContextAudioProcessor::loadAuditionWav(const juce::File& file)
{
  juce::AudioFormatManager formats;
  formats.registerBasicFormats();
  std::unique_ptr<juce::AudioFormatReader> reader(formats.createReaderFor(file));
  if (reader == nullptr || reader->lengthInSamples <= 0)
    return false;

  const int maxSamples = juce::jmax(1, juce::roundToInt(reader->sampleRate * 12.0));
  const int numSamples = juce::jmin(static_cast<int>(reader->lengthInSamples), maxSamples);
  juce::AudioBuffer<float> loaded(juce::jmax(1, static_cast<int>(reader->numChannels)), numSamples);
  reader->read(&loaded, 0, loaded.getNumSamples(), 0, true, true);
  if (loaded.getMagnitude(0, loaded.getNumSamples()) < 1.0e-4f)
    return false;
  const juce::ScopedLock lock(auditionLock);
  auditionBuffer = std::move(loaded);
  auditionSampleRate = reader->sampleRate > 0.0 ? reader->sampleRate : 44100.0;
  auditionFrame = 0.0;
  lastWavFile = file;
  return true;
}

void ContextAudioProcessor::copyWaveformPeaks(std::vector<float>& dest, int bins) const
{
  const juce::ScopedLock lock(auditionLock);
  dest.assign(static_cast<size_t>(juce::jmax(1, bins)), 0.0f);
  const int samples = auditionBuffer.getNumSamples();
  if (samples <= 0)
    return;
  const int channels = juce::jmax(1, auditionBuffer.getNumChannels());
  const int width = juce::jmax(1, bins);
  for (int bin = 0; bin < width; ++bin)
  {
    const int start = (bin * samples) / width;
    const int end = juce::jmax(start + 1, ((bin + 1) * samples) / width);
    float peak = 0.0f;
    for (int ch = 0; ch < channels; ++ch)
    {
      const auto* data = auditionBuffer.getReadPointer(ch);
      for (int i = start; i < end && i < samples; ++i)
        peak = juce::jmax(peak, std::abs(data[i]));
    }
    dest[static_cast<size_t>(bin)] = peak;
  }
}

void ContextAudioProcessor::setAuditionPlaying(bool shouldPlay)
{
  if (shouldPlay)
  {
    const juce::ScopedLock lock(auditionLock);
    auditionFrame = 0.0;
  }
  auditionPlaying.store(shouldPlay);
}

void ContextAudioProcessor::processBlock(juce::AudioBuffer<float>& buffer, juce::MidiBuffer& midi)
{
  juce::ignoreUnused(midi);
  juce::ScopedNoDenormals noDenormals;
  for (int channel = getTotalNumInputChannels(); channel < getTotalNumOutputChannels(); ++channel)
    buffer.clear(channel, 0, buffer.getNumSamples());

  {
    const juce::ScopedLock lock(historyLock);
    if (history.getNumSamples() > 0)
    {
      const int channels = juce::jmin(buffer.getNumChannels(), history.getNumChannels());
      const int cap = history.getNumSamples();
      for (int i = 0; i < buffer.getNumSamples(); ++i)
      {
        float peak = 0.0f;
        for (int ch = 0; ch < channels; ++ch)
        {
          const float sample = buffer.getSample(ch, i);
          history.setSample(ch, historyWrite, sample);
          peak = juce::jmax(peak, std::abs(sample));
        }
        if (peak > 0.01f)
          hasSignal.store(true);
        historyWrite = (historyWrite + 1) % cap;
      }
    }
  }

  if (!auditionPlaying.load())
    return;

  const juce::ScopedLock lock(auditionLock);
  if (auditionBuffer.getNumSamples() <= 0)
    return;

  const double ratio = (auditionSampleRate > 0.0 && currentSampleRate > 0.0)
                           ? auditionSampleRate / currentSampleRate
                           : 1.0;
  const int n = auditionBuffer.getNumSamples();
  for (int i = 0; i < buffer.getNumSamples(); ++i)
  {
    const int idx = static_cast<int>(auditionFrame) % n;
    for (int ch = 0; ch < buffer.getNumChannels(); ++ch)
    {
      const int srcCh = juce::jmin(ch, auditionBuffer.getNumChannels() - 1);
      buffer.setSample(ch, i, auditionBuffer.getSample(srcCh, idx));
    }
    auditionFrame += ratio;
    if (auditionFrame >= static_cast<double>(n))
      auditionFrame -= static_cast<double>(n);
  }
}

juce::AudioProcessorEditor* ContextAudioProcessor::createEditor()
{
  return new ContextAudioProcessorEditor(*this);
}

void ContextAudioProcessor::getStateInformation(juce::MemoryBlock& destData)
{
  auto state = parameters.copyState();
  state.setProperty("prompt", prompt, nullptr);
  state.setProperty("systemPrompt", systemPrompt, nullptr);
  state.setProperty("rules", rules, nullptr);
  state.setProperty("negativePrompt", negativePrompt, nullptr);
  if (sampleLibrary.isDirectory())
    state.setProperty("sampleLibrary", sampleLibrary.getFullPathName(), nullptr);
  if (auto xml = state.createXml())
    copyXmlToBinary(*xml, destData);
}

void ContextAudioProcessor::setStateInformation(const void* data, int sizeInBytes)
{
  if (auto xml = getXmlFromBinary(data, sizeInBytes))
  {
    parameters.replaceState(juce::ValueTree::fromXml(*xml));
    prompt = xml->getStringAttribute("prompt", prompt);
    systemPrompt = xml->getStringAttribute("systemPrompt", juce::String(context::defaultSystemPrompt()));
    rules = xml->getStringAttribute("rules", juce::String(context::defaultRules()));
    negativePrompt = xml->getStringAttribute("negativePrompt", juce::String(context::defaultNegativePrompt()));
    const auto library = xml->getStringAttribute("sampleLibrary");
    if (library.isNotEmpty())
      sampleLibrary = juce::File(library);
  }
}

juce::AudioProcessor* JUCE_CALLTYPE createPluginFilter()
{
  return new ContextAudioProcessor();
}
