#pragma once

#include <JuceHeader.h>

#include <atomic>

class SidecarSupervisor
{
public:
  static SidecarSupervisor& instance();

  void retainProcessor();
  void releaseProcessor();
  void requestStart();
  bool isStarting() const;
  juce::String lastStatus() const;

private:
  SidecarSupervisor() = default;

  void ensureRunning();
  bool kickstartAgent();
  bool waitUntilHealthy(int timeoutMs);

  mutable juce::CriticalSection lock;
  std::atomic<bool> starting{false};
  juce::String status{"idle"};
};
