#include "SidecarClient.h"

#include <arpa/inet.h>
#include <errno.h>
#include <netinet/in.h>
#include <sys/socket.h>
#include <unistd.h>

#include <cstring>

SidecarClient::SidecarClient(int portToUse) : port(portToUse) {}

juce::String SidecarClient::lastError() const
{
  return error;
}

bool SidecarClient::healthOk() const
{
  const auto body = get("/health");
  return body.contains("\"ok\": true") || body.contains("\"ok\":true");
}

juce::String SidecarClient::get(const juce::String& path) const
{
  return request("GET", path, {}, 2);
}

juce::String SidecarClient::post(const juce::String& path, const juce::String& jsonBody) const
{
  return request("POST", path, jsonBody, 8);
}

juce::String SidecarClient::postLong(const juce::String& path, const juce::String& jsonBody) const
{
  return request("POST", path, jsonBody, 600);
}

juce::String SidecarClient::request(const juce::String& method, const juce::String& path, const juce::String& body, int timeoutSec) const
{
  error.clear();
  const int fd = ::socket(AF_INET, SOCK_STREAM, 0);
  if (fd < 0)
  {
    error = "socket failed";
    return {};
  }

  timeval timeout{};
  timeout.tv_sec = timeoutSec;
  timeout.tv_usec = 0;
  setsockopt(fd, SOL_SOCKET, SO_RCVTIMEO, &timeout, sizeof(timeout));
  setsockopt(fd, SOL_SOCKET, SO_SNDTIMEO, &timeout, sizeof(timeout));

  sockaddr_in addr{};
  addr.sin_family = AF_INET;
  addr.sin_port = htons(static_cast<uint16_t>(port));
  if (inet_pton(AF_INET, "127.0.0.1", &addr.sin_addr) != 1)
  {
    error = "invalid bind target";
    ::close(fd);
    return {};
  }

  if (::connect(fd, reinterpret_cast<sockaddr*>(&addr), sizeof(addr)) < 0)
  {
    error = "sidecar is not running on 127.0.0.1:" + juce::String(port);
    ::close(fd);
    return {};
  }

  juce::String requestText = method + " " + path + " HTTP/1.1\r\nHost: 127.0.0.1\r\nConnection: close\r\n";
  if (body.isNotEmpty())
  {
    requestText += "Content-Type: application/json\r\n";
    requestText += "Content-Length: " + juce::String(body.getNumBytesAsUTF8()) + "\r\n";
  }
  requestText += "\r\n";
  if (body.isNotEmpty())
    requestText += body;

  const auto utf8 = requestText.toRawUTF8();
  const auto bytes = static_cast<ssize_t>(std::strlen(utf8));
  if (::send(fd, utf8, static_cast<size_t>(bytes), 0) != bytes)
  {
    error = "send failed";
    ::close(fd);
    return {};
  }

  juce::MemoryOutputStream buffer;
  char chunk[2048];
  while (true)
  {
    const auto n = ::recv(fd, chunk, sizeof(chunk), 0);
    if (n > 0)
    {
      buffer.write(chunk, static_cast<size_t>(n));
      continue;
    }
    if (n == 0)
      break;
    if (errno == EINTR)
      continue;
    if (errno == EAGAIN || errno == EWOULDBLOCK)
      error = "sidecar timed out after " + juce::String(timeoutSec) + "s";
    else
      error = "connection dropped during generation";
    break;
  }
  ::close(fd);

  const auto raw = buffer.toString();
  const auto headerEnd = raw.indexOf("\r\n\r\n");
  if (headerEnd < 0)
  {
    if (error.isEmpty())
      error = raw.isEmpty() ? "empty HTTP response" : "invalid HTTP response";
    return raw;
  }
  return raw.substring(headerEnd + 4);
}
