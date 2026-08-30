#include "SidecarSupervisor.h"
#include "SidecarClient.h"

#include <arpa/inet.h>
#include <cstdlib>
#include <netinet/in.h>
#include <sys/socket.h>
#include <unistd.h>

namespace
{
  int sidecarPort()
  {
    if (const char* raw = std::getenv("CONTEXT_SIDECAR_PORT"))
    {
      const int port = juce::String(raw).getIntValue();
      if (port > 0 && port < 65536)
        return port;
    }
    return 8765;
  }

  bool portIsOpen()
  {
    const int fd = ::socket(AF_INET, SOCK_STREAM, 0);
    if (fd < 0)
      return false;
    timeval timeout{};
    timeout.tv_sec = 0;
    timeout.tv_usec = 200000;
    setsockopt(fd, SOL_SOCKET, SO_RCVTIMEO, &timeout, sizeof(timeout));
    setsockopt(fd, SOL_SOCKET, SO_SNDTIMEO, &timeout, sizeof(timeout));
    sockaddr_in addr{};
    addr.sin_family = AF_INET;
    addr.sin_port = htons(static_cast<uint16_t>(sidecarPort()));
    inet_pton(AF_INET, "127.0.0.1", &addr.sin_addr);
    const bool open = ::connect(fd, reinterpret_cast<sockaddr*>(&addr), sizeof(addr)) == 0;
    ::close(fd);
    return open;
  }

  bool sidecarHealthy()
  {
    return SidecarClient(sidecarPort()).healthOk();
  }

  juce::String agentDomain()
  {
    return "gui/" + juce::String(static_cast<int>(::getuid())) + "/com.context.sidecar";
  }
}

SidecarSupervisor& SidecarSupervisor::instance()
{
  static SidecarSupervisor supervisor;
  return supervisor;
}

void SidecarSupervisor::retainProcessor() {}

void SidecarSupervisor::releaseProcessor() {}

bool SidecarSupervisor::isStarting() const
{
  return starting.load();
}

juce::String SidecarSupervisor::lastStatus() const
{
  const juce::ScopedLock guard(lock);
  return status;
}

void SidecarSupervisor::requestStart()
{
  bool expected = false;
  if (!starting.compare_exchange_strong(expected, true))
    return;

  juce::Thread::launch([this] {
    ensureRunning();
    starting.store(false);
  });
}

void SidecarSupervisor::ensureRunning()
{
  if (portIsOpen())
  {
    const juce::ScopedLock guard(lock);
    status = sidecarHealthy() ? "already running" : "listening (busy)";
    return;
  }

  if (sidecarHealthy())
  {
    const juce::ScopedLock guard(lock);
    status = "already running";
    return;
  }

  {
    const juce::ScopedLock guard(lock);
    status = "starting";
  }

  if (!kickstartAgent())
  {
    const juce::ScopedLock guard(lock);
    status = "could not start sidecar agent";
    return;
  }

  if (waitUntilHealthy(5000))
  {
    const juce::ScopedLock guard(lock);
    status = "ok";
    return;
  }

  const juce::ScopedLock guard(lock);
  status = "agent started but health check failed";
}

bool SidecarSupervisor::kickstartAgent()
{
  const auto plist = juce::File::getSpecialLocation(juce::File::userHomeDirectory)
                         .getChildFile("Library/LaunchAgents/com.context.sidecar.plist");
  if (!plist.existsAsFile())
    return false;

  juce::ChildProcess bootstrap;
  juce::StringArray bootstrapArgs;
  bootstrapArgs.add("/bin/launchctl");
  bootstrapArgs.add("bootstrap");
  bootstrapArgs.add("gui/" + juce::String(static_cast<int>(::getuid())));
  bootstrapArgs.add(plist.getFullPathName());
  bootstrap.start(bootstrapArgs, 0);
  bootstrap.waitForProcessToFinish(2000);

  juce::ChildProcess kick;
  juce::StringArray kickArgs;
  kickArgs.add("/bin/launchctl");
  kickArgs.add("kickstart");
  kickArgs.add("-k");
  kickArgs.add(agentDomain());
  if (!kick.start(kickArgs, 0))
    return false;
  kick.waitForProcessToFinish(2000);
  return true;
}

bool SidecarSupervisor::waitUntilHealthy(int timeoutMs)
{
  const auto deadline = juce::Time::getMillisecondCounter() + static_cast<juce::uint32>(timeoutMs);
  while (juce::Time::getMillisecondCounter() < deadline)
  {
    if (sidecarHealthy())
      return true;
    juce::Thread::sleep(100);
  }
  return sidecarHealthy();
}
