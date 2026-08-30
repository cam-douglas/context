#pragma once

#include "PluginProcessor.h"
#include "SampleLibraryPanel.h"
#include "SidecarClient.h"

class WaveformStrip : public juce::Component
{
public:
  explicit WaveformStrip(ContextAudioProcessor& processorToUse);
  void paint(juce::Graphics&) override;
  void mouseDown(const juce::MouseEvent&) override;
  void mouseDrag(const juce::MouseEvent&) override;
  void mouseUp(const juce::MouseEvent&) override;
  std::function<void()> onDragToDaw;
  std::function<void()> onDropOnReference;
  std::function<bool(juce::Point<int>)> isOverReference;
  std::function<void(bool)> onReferenceHover;

private:
  ContextAudioProcessor& audioProcessor;
  bool dragging = false;
  bool draggedOut = false;
  JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR(WaveformStrip)
};

class ClickableLabel : public juce::Label
{
public:
  using juce::Label::Label;
  std::function<void(const juce::MouseEvent&)> onUp;
  void mouseUp(const juce::MouseEvent& e) override
  {
    juce::Label::mouseUp(e);
    if (onUp)
      onUp(e);
  }
};

class PromptGatePanel : public juce::Component
{
public:
  PromptGatePanel();
  void paint(juce::Graphics&) override;
  void resized() override;
  void setTexts(const juce::String& systemText, const juce::String& rulesText, const juce::String& negativeText);
  void focusField(int which);
  juce::String systemText() const { return systemEditor.getText(); }
  juce::String rulesText() const { return rulesEditor.getText(); }
  juce::String negativeText() const { return negativeEditor.getText(); }
  std::function<void()> onChange;
  std::function<void()> onReset;
  std::function<void()> onDone;

private:
  void styleEditor(juce::TextEditor& editor, juce::Colour outline);
  juce::Label heading;
  juce::Label ranks;
  juce::Label systemLabel;
  juce::Label rulesLabel;
  juce::Label negativeLabel;
  juce::Label requestNote;
  juce::TextEditor systemEditor;
  juce::TextEditor rulesEditor;
  juce::TextEditor negativeEditor;
  juce::TextButton reset{"Reset defaults"};
  juce::TextButton done{"Done"};
  JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR(PromptGatePanel)
};

class ContextAudioProcessorEditor : public juce::AudioProcessorEditor,
                                    public juce::DragAndDropContainer,
                                    public juce::FileDragAndDropTarget,
                                    private juce::Timer
{
public:
  explicit ContextAudioProcessorEditor(ContextAudioProcessor&);
  ~ContextAudioProcessorEditor() override;

  void paint(juce::Graphics&) override;
  void resized() override;
  bool keyPressed(const juce::KeyPress& key) override;
  bool isInterestedInFileDrag(const juce::StringArray& files) override;
  void fileDragEnter(const juce::StringArray&, int, int) override;
  void fileDragExit(const juce::StringArray&) override;
  void filesDropped(const juce::StringArray& files, int, int) override;
  juce::Rectangle<int> referenceScreenBounds() const;
  void setReferenceDropHover(bool over);
  void useOutputAsReference();

private:
  void timerCallback() override;
  void refreshHealth();
  void runClicked();
  void auditionClicked();
  void applyClicked();
  void titleClicked(const juce::MouseEvent& e);
  void showPromptsMenu();
  void openPromptGate(int field);
  void togglePromptGate();
  void closePromptGate();
  void persistGateTexts();
  void toggleSampleLibrary();
  void closeSampleLibrary();
  void setLibraryOpen(bool open);
  void refreshReferenceField();
  void chooseReferenceFile();
  void setReferenceFile(const juce::File& source);
  void searchSampleLibrary();
  void finishLibrarySearch(const juce::String& body, const juce::String& error);
  void useLibraryFile(const juce::File& file);
  void previewLibraryFile(const juce::File& file);
  void dragLibraryFile(const juce::File& file);
  void startCompose(const juce::String& typed, bool permanent, bool playAfter);
  void finishCompose(const juce::String& typed, const juce::String& body, const juce::String& error, bool permanent, bool playAfter);
  void refreshProgress();
  void setBusy(bool busy);
  void discardAuditionFiles();
  bool promoteAudition();
  void dragGeneratedFiles();
  juce::String intentJson() const;
  float knob(const juce::String& id) const;

  void layoutPage();

  ContextAudioProcessor& audioProcessor;
  SidecarClient sidecar;
  juce::Viewport scroller;
  juce::Component page;

  juce::Label referenceLabel{"", "Reference"};
  juce::TextEditor referenceField;
  juce::TextButton referenceChoose{"Choose..."};
  ClickableLabel title{"", "Context 14"};
  juce::Label health{"", "sidecar health: checking"};
  juce::TextEditor prompt;
  juce::Label promptRank{"", "request  -  suggestion - cannot override system, rules, or negatives"};
  juce::TextButton prompts{"Prompts"};
  juce::TextButton run{"Run"};
  juce::Slider reverence;
  juce::Slider abstraction;
  juce::Label revLabel{"", "Reverence"};
  juce::Label absLabel{"", "Abstraction"};
  WaveformStrip waveform;
  juce::Label dropHint{"", "Drag the waveform into Live, or onto Reference to reuse it."};
  juce::TextEditor preview;
  juce::TextButton audition{"Audition"};
  juce::TextButton apply{"Apply"};
  juce::TextButton library{"Library"};
  juce::Label status{"", "Type what to make. Audition is temporary. Apply keeps files in Context/Plugin."};
  PromptGatePanel promptGate;
  SampleLibraryPanel sampleLibrary;

  std::unique_ptr<juce::AudioProcessorValueTreeState::SliderAttachment> revAttach;
  std::unique_ptr<juce::AudioProcessorValueTreeState::SliderAttachment> absAttach;

  std::unique_ptr<juce::FileChooser> referenceChooser;
  juce::Array<juce::File> tempFiles;
  bool libraryOpen = false;
  bool hasPreview = false;
  bool composeBusy = false;
  bool composePlayAfter = false;
  bool auditionApplied = false;
  int lastPreviewGeneration = -1;
  juce::Rectangle<int> referenceRowBounds;
  bool fileDragOver = false;
  bool referenceDropHover = false;
  int titleClicks = 0;
  int healthPulse = 0;
  juce::uint32 lastTitleClickMs = 0;

  JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR(ContextAudioProcessorEditor)
};
