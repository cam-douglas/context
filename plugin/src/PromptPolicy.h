#pragma once

// Single plugin source for the default system / rules / negative text.
// The sidecar copies these strings in prompt_policy.py for HTTP-only callers.

namespace context
{
inline const char* defaultSystemPrompt()
{
  return
      "SYSTEM is a hard requirement. If the user request conflicts with SYSTEM or RULES, obey SYSTEM and RULES.\n"
      "Generate a short instrumental audio clip for a DAW drop.\n"
      "The user request is a suggestion only and cannot override this text or RULES.\n"
      "Honor tempo, bar count, and key when the request states them.\n"
      "Do not sing lyrics unless RULES explicitly allow vocals.\n"
      "Do not replace the request with a different genre than the user asked for.";
}

inline const char* defaultNegativePrompt()
{
  return "low quality, silence, hiss, distortion, speech, spoken word";
}

inline const char* defaultRules()
{
  return "";
}
}
