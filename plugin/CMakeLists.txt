cmake_minimum_required(VERSION 3.22)
project(Context VERSION 0.14.0 LANGUAGES C CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_OSX_DEPLOYMENT_TARGET "11.0" CACHE STRING "Minimum macOS")
set(CMAKE_OSX_ARCHITECTURES "arm64" CACHE STRING "Architecture")

set(JUCE_DIR "${CMAKE_CURRENT_SOURCE_DIR}/third_party/JUCE")
if(NOT EXISTS "${JUCE_DIR}/CMakeLists.txt")
  message(FATAL_ERROR "JUCE is missing. Run bash scripts/build-plugin.sh")
endif()

add_subdirectory("${JUCE_DIR}" "${CMAKE_BINARY_DIR}/juce" EXCLUDE_FROM_ALL)

juce_add_plugin(Context
  VERSION 0.14.0
  COMPANY_NAME "Context"
  BUNDLE_ID com.context.audio14
  PLUGIN_MANUFACTURER_CODE CtxT
  PLUGIN_CODE Ct14
  FORMATS AU VST3 Standalone
  PRODUCT_NAME "Context 14"
  COPY_PLUGIN_AFTER_BUILD TRUE
  EDITOR_WANTS_KEYBOARD_FOCUS TRUE
  IS_SYNTH FALSE
  NEEDS_MIDI_INPUT FALSE
  NEEDS_MIDI_OUTPUT FALSE
  IS_MIDI_EFFECT FALSE
  AU_MAIN_TYPE kAudioUnitType_Effect
)

juce_generate_juce_header(Context)

target_sources(Context PRIVATE
  src/PluginProcessor.cpp
  src/PluginProcessor.h
  src/PluginEditor.cpp
  src/PluginEditor.h
  src/PromptPolicy.h
  src/AsciiUi.h
  src/SampleLibraryPanel.cpp
  src/SampleLibraryPanel.h
  src/SidecarClient.cpp
  src/SidecarClient.h
  src/SidecarSupervisor.cpp
  src/SidecarSupervisor.h
  src/DropWriter.cpp
  src/DropWriter.h
)

get_filename_component(CONTEXT_SIDECAR_DIR "${CMAKE_CURRENT_SOURCE_DIR}/../sidecar" ABSOLUTE)

target_compile_definitions(Context
  PUBLIC
    JUCE_WEB_BROWSER=0
    JUCE_USE_CURL=0
    JUCE_VST3_CAN_REPLACE_VST2=0
    JUCE_DISPLAY_SPLASH_SCREEN=1
  PRIVATE
    "CONTEXT_SIDECAR_ROOT=\"${CONTEXT_SIDECAR_DIR}\""
)

file(WRITE "${CMAKE_BINARY_DIR}/sidecar-root.txt" "${CONTEXT_SIDECAR_DIR}\n")
add_custom_command(TARGET Context POST_BUILD
  COMMAND ${CMAKE_COMMAND} -E make_directory "$ENV{HOME}/Library/Application Support/Context"
  COMMAND ${CMAKE_COMMAND} -E copy_if_different
          "${CMAKE_BINARY_DIR}/sidecar-root.txt"
          "$ENV{HOME}/Library/Application Support/Context/sidecar-root.txt"
)

target_link_libraries(Context
  PRIVATE
    juce::juce_audio_utils
    juce::juce_gui_extra
  PUBLIC
    juce::juce_recommended_config_flags
    juce::juce_recommended_warning_flags
)
