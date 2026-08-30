#pragma once

#include <JuceHeader.h>

class SidecarClient
{
public:
  explicit SidecarClient(int port = 8765);

  bool healthOk() const;
  juce::String lastError() const;
  juce::String get(const juce::String& path) const;
  juce::String post(const juce::String& path, const juce::String& jsonBody) const;
  juce::String postLong(const juce::String& path, const juce::String& jsonBody) const;

private:
  int port;
  mutable juce::String error;
  juce::String request(const juce::String& method, const juce::String& path, const juce::String& body, int timeoutSec = 2) const;
};
