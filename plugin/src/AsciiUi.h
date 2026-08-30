#pragma once

#include <JuceHeader.h>

// Owner rule: plugin UI is ASCII only. Map common punctuation; drop the rest.
inline juce::String asciiUi(const juce::String& text)
{
  juce::String out;
  out.preallocateBytes(static_cast<size_t>(text.getNumBytesAsUTF8()) + 8);
  for (int i = 0; i < text.length(); ++i)
  {
    const auto c = text[i];
    if ((c >= 32 && c <= 126) || c == 9 || c == 10 || c == 13)
      out += static_cast<juce::juce_wchar>(c);
    else if (c == 0x2014 || c == 0x2013 || c == 0x00B7 || c == 0x2022)
      out += '-';
    else if (c == 0x2026)
      out += "...";
    else if (c == 0x201C || c == 0x201D || c == 0x2018 || c == 0x2019)
      out += '"';
  }
  return out;
}
