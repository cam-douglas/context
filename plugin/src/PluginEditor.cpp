#include "PluginEditor.h"
#include "AsciiUi.h"
#include "DropWriter.h"
#include "SidecarSupervisor.h"

#include <thread>

namespace
{
  bool isAudioFile(const juce::File& file)
  {
    return file.hasFileExtension("wav;aiff;aif;flac;mp3;ogg");
  }
}

WaveformStrip::WaveformStrip(ContextAudioProcessor& processorToUse) : audioProcessor(processorToUse) {}

void WaveformStrip::paint(juce::Graphics& g)
{
  g.fillAll(juce::Colour(0xff101010));
  g.setColour(juce::Colour(0xff2a2a2a));
  g.drawRect(getLocalBounds(), 1);
  if (!audioProcessor.hasAudition())
  {
    g.setColour(juce::Colours::white.withAlpha(0.45f));
    g.setFont(juce::FontOptions(13.0f));
    g.drawFittedText("No clip yet. Audition or Apply, then drag this waveform into the DAW.",
                     getLocalBounds().reduced(10), juce::Justification::centred, 2);
    return;
  }
  std::vector<float> peaks;
  audioProcessor.copyWaveformPeaks(peaks, juce::jmax(8, getWidth()));
  const auto bounds = getLocalBounds().toFloat().reduced(2.0f);
  const float mid = bounds.getCentreY();
  const float scale = bounds.getHeight() * 0.46f;
  juce::Path path;
  path.startNewSubPath(bounds.getX(), mid);
  for (size_t i = 0; i < peaks.size(); ++i)
  {
    const float x = bounds.getX() + (static_cast<float>(i) / static_cast<float>(peaks.size())) * bounds.getWidth();
    path.lineTo(x, mid - peaks[i] * scale);
  }
  for (int i = static_cast<int>(peaks.size()) - 1; i >= 0; --i)
  {
    const float x = bounds.getX() + (static_cast<float>(i) / static_cast<float>(peaks.size())) * bounds.getWidth();
    path.lineTo(x, mid + peaks[static_cast<size_t>(i)] * scale);
  }
  path.closeSubPath();
  g.setColour(juce::Colour(0xff7ec8ff));
  g.fillPath(path);
}

void WaveformStrip::mouseDown(const juce::MouseEvent&)
{
  dragging = false;
  draggedOut = false;
}

void WaveformStrip::mouseDrag(const juce::MouseEvent& e)
{
  if (!audioProcessor.lastWavFile.existsAsFile())
    return;
  if (e.getDistanceFromDragStart() < 8)
    return;
  dragging = true;
  const auto screen = e.getScreenPosition();
  const bool overRef = isOverReference && isOverReference(screen);
  if (onReferenceHover)
    onReferenceHover(overRef);
  if (overRef || draggedOut)
    return;
  auto* editor = findParentComponentOfClass<ContextAudioProcessorEditor>();
  if (editor != nullptr && editor->getScreenBounds().contains(screen))
    return;
  draggedOut = true;
  if (onReferenceHover)
    onReferenceHover(false);
  if (onDragToDaw)
    onDragToDaw();
}

void WaveformStrip::mouseUp(const juce::MouseEvent& e)
{
  const bool overRef = isOverReference && isOverReference(e.getScreenPosition());
  if (onReferenceHover)
    onReferenceHover(false);
  if (dragging && !draggedOut && overRef && onDropOnReference)
    onDropOnReference();
  dragging = false;
  draggedOut = false;
}

PromptGatePanel::PromptGatePanel()
{
  heading.setText("Prompt Gate", juce::dontSendNotification);
  heading.setColour(juce::Label::textColourId, juce::Colours::white);
  heading.setFont(juce::FontOptions(16.0f));
  addAndMakeVisible(heading);

  ranks.setText(
      "1  SYSTEM     hard gate - wins every conflict\n"
      "1  RULES      hard - appended to SYSTEM, same force\n"
      "2  NEGATIVE   hard reject - never produce these\n"
      "3  REQUEST    suggestion only - the line on the face cannot override 1-2",
      juce::dontSendNotification);
  ranks.setColour(juce::Label::textColourId, juce::Colour(0xffc8c8c8));
  ranks.setFont(juce::FontOptions(12.0f));
  ranks.setJustificationType(juce::Justification::topLeft);
  addAndMakeVisible(ranks);

  auto setupRank = [this](juce::Label& label, const juce::String& text, juce::Colour colour) {
    label.setText(text, juce::dontSendNotification);
    label.setColour(juce::Label::textColourId, colour);
    label.setFont(juce::FontOptions(12.0f));
    addAndMakeVisible(label);
  };
  setupRank(systemLabel, "SYSTEM  -  rank 1  -  hard", juce::Colour(0xffe08a3c));
  setupRank(rulesLabel, "RULES  -  rank 1  -  hard  -  extra instructions appended to SYSTEM", juce::Colour(0xffe08a3c));
  setupRank(negativeLabel, "NEGATIVE  -  rank 2  -  hard reject", juce::Colour(0xffd35a5a));

  requestNote.setText("REQUEST stays on the face as a suggestion. It influences generation but cannot override SYSTEM, RULES, or NEGATIVE.",
                      juce::dontSendNotification);
  requestNote.setColour(juce::Label::textColourId, juce::Colour(0xff8a8a8a));
  requestNote.setFont(juce::FontOptions(12.0f));
  requestNote.setMinimumHorizontalScale(0.7f);
  addAndMakeVisible(requestNote);

  styleEditor(systemEditor, juce::Colour(0xffe08a3c));
  styleEditor(rulesEditor, juce::Colour(0xffe08a3c));
  styleEditor(negativeEditor, juce::Colour(0xffd35a5a));

  auto notify = [this] { if (onChange) onChange(); };
  systemEditor.onTextChange = notify;
  rulesEditor.onTextChange = notify;
  negativeEditor.onTextChange = notify;

  reset.onClick = [this] { if (onReset) onReset(); };
  done.onClick = [this] { if (onDone) onDone(); };
  addAndMakeVisible(reset);
  addAndMakeVisible(done);
}

void PromptGatePanel::styleEditor(juce::TextEditor& editor, juce::Colour outline)
{
  editor.setMultiLine(true, true);
  editor.setReturnKeyStartsNewLine(true);
  editor.setColour(juce::TextEditor::backgroundColourId, juce::Colour(0xff0e0e0e));
  editor.setColour(juce::TextEditor::textColourId, juce::Colours::white);
  editor.setColour(juce::TextEditor::outlineColourId, outline);
  editor.setColour(juce::TextEditor::focusedOutlineColourId, outline.brighter(0.2f));
  addAndMakeVisible(editor);
}

void PromptGatePanel::paint(juce::Graphics& g)
{
  g.fillAll(juce::Colour(0xff121212));
  g.setColour(juce::Colour(0xffe08a3c));
  g.fillRect(0, 0, 4, getHeight());
}

void PromptGatePanel::resized()
{
  auto area = getLocalBounds().reduced(16);
  heading.setBounds(area.removeFromTop(22));
  area.removeFromTop(6);
  ranks.setBounds(area.removeFromTop(64));
  area.removeFromTop(8);
  systemLabel.setBounds(area.removeFromTop(16));
  systemEditor.setBounds(area.removeFromTop(88));
  area.removeFromTop(8);
  rulesLabel.setBounds(area.removeFromTop(16));
  rulesEditor.setBounds(area.removeFromTop(72));
  area.removeFromTop(8);
  negativeLabel.setBounds(area.removeFromTop(16));
  negativeEditor.setBounds(area.removeFromTop(56));
  area.removeFromTop(8);
  requestNote.setBounds(area.removeFromTop(36));
  area.removeFromTop(8);
  auto actions = area.removeFromTop(28);
  reset.setBounds(actions.removeFromLeft(120));
  actions.removeFromLeft(8);
  done.setBounds(actions.removeFromLeft(80));
}

void PromptGatePanel::setTexts(const juce::String& systemText, const juce::String& rulesText, const juce::String& negativeText)
{
  systemEditor.setText(systemText, false);
  rulesEditor.setText(rulesText, false);
  negativeEditor.setText(negativeText, false);
}

void PromptGatePanel::focusField(int which)
{
  juce::TextEditor* editor = &systemEditor;
  if (which == 2)
    editor = &rulesEditor;
  else if (which == 3)
    editor = &negativeEditor;
  editor->grabKeyboardFocus();
}

ContextAudioProcessorEditor::ContextAudioProcessorEditor(ContextAudioProcessor& p)
    : AudioProcessorEditor(&p), audioProcessor(p), waveform(p)
{
  setSize(640, 520);
  setResizable(true, true);
  setResizeLimits(480, 420, 1400, 1400);
  addAndMakeVisible(scroller);
  scroller.setViewedComponent(&page, false);
  scroller.setScrollBarsShown(true, false);
  scroller.setScrollBarThickness(12);

  auto setupLabel = [this](juce::Label& label, float size, juce::Justification just) {
    label.setColour(juce::Label::textColourId, juce::Colours::white);
    label.setFont(juce::FontOptions(size));
    label.setJustificationType(just);
    page.addAndMakeVisible(label);
  };

  setupLabel(referenceLabel, 12.0f, juce::Justification::centredLeft);
  setupLabel(title, 18.0f, juce::Justification::centredLeft);
  setupLabel(health, 13.0f, juce::Justification::centredLeft);
  setupLabel(revLabel, 12.0f, juce::Justification::centred);
  setupLabel(absLabel, 12.0f, juce::Justification::centred);
  setupLabel(dropHint, 12.0f, juce::Justification::centredLeft);
  setupLabel(status, 13.0f, juce::Justification::centredLeft);
  setupLabel(promptRank, 11.0f, juce::Justification::centredLeft);
  promptRank.setColour(juce::Label::textColourId, juce::Colour(0xff8a8a8a));
  status.setMinimumHorizontalScale(0.7f);

  title.onUp = [this](const juce::MouseEvent& e) { titleClicked(e); };
  title.setMouseCursor(juce::MouseCursor::PointingHandCursor);

  referenceField.setMultiLine(false);
  referenceField.setReadOnly(false);
  referenceField.setTextToShowWhenEmpty("Drop a reference clip or Choose a file", juce::Colour(0xff666666));
  referenceField.onReturnKey = [this] {
    const juce::File typed(referenceField.getText().trim());
    if (typed.existsAsFile() && isAudioFile(typed))
      setReferenceFile(typed);
  };
  page.addAndMakeVisible(referenceField);
  referenceChoose.onClick = [this] { chooseReferenceFile(); };
  page.addAndMakeVisible(referenceChoose);
  refreshReferenceField();

  prompt.setMultiLine(false);
  prompt.setReturnKeyStartsNewLine(false);
  prompt.setText(audioProcessor.prompt, false);
  prompt.onTextChange = [this] { audioProcessor.prompt = prompt.getText(); };
  page.addAndMakeVisible(prompt);

  preview.setMultiLine(true);
  preview.setReadOnly(true);
  preview.setText("preview");
  page.addAndMakeVisible(preview);

  auto setupSlider = [this](juce::Slider& slider) {
    slider.setSliderStyle(juce::Slider::RotaryHorizontalVerticalDrag);
    slider.setTextBoxStyle(juce::Slider::TextBoxBelow, false, 56, 16);
    slider.setNumDecimalPlacesToDisplay(2);
    page.addAndMakeVisible(slider);
  };
  setupSlider(reverence);
  setupSlider(abstraction);

  revAttach = std::make_unique<juce::AudioProcessorValueTreeState::SliderAttachment>(audioProcessor.parameters, "reverence", reverence);
  absAttach = std::make_unique<juce::AudioProcessorValueTreeState::SliderAttachment>(audioProcessor.parameters, "abstraction", abstraction);

  waveform.onDragToDaw = [this] { dragGeneratedFiles(); };
  waveform.onDropOnReference = [this] { useOutputAsReference(); };
  waveform.isOverReference = [this](juce::Point<int> screen) { return referenceScreenBounds().contains(screen); };
  waveform.onReferenceHover = [this](bool over) { setReferenceDropHover(over); };
  page.addAndMakeVisible(waveform);

  run.onClick = [this] { runClicked(); };
  audition.onClick = [this] { auditionClicked(); };
  apply.onClick = [this] { applyClicked(); };
  library.onClick = [this] { toggleSampleLibrary(); };
  library.setColour(juce::TextButton::buttonColourId, juce::Colour(0xff2d4a66));
  prompts.onClick = [this] { showPromptsMenu(); };
  prompts.setColour(juce::TextButton::buttonColourId, juce::Colour(0xff5a3a18));
  prompts.setColour(juce::TextButton::textColourOffId, juce::Colour(0xffffc27a));
  page.addAndMakeVisible(run);
  page.addAndMakeVisible(audition);
  page.addAndMakeVisible(apply);
  page.addAndMakeVisible(library);
  page.addAndMakeVisible(prompts);

  promptGate.setTexts(audioProcessor.systemPrompt, audioProcessor.rules, audioProcessor.negativePrompt);
  promptGate.onChange = [this] { persistGateTexts(); };
  promptGate.onReset = [this] {
    audioProcessor.systemPrompt = context::defaultSystemPrompt();
    audioProcessor.rules = context::defaultRules();
    audioProcessor.negativePrompt = context::defaultNegativePrompt();
    promptGate.setTexts(audioProcessor.systemPrompt, audioProcessor.rules, audioProcessor.negativePrompt);
  };
  promptGate.onDone = [this] { closePromptGate(); };
  promptGate.setVisible(false);
  addChildComponent(promptGate);

  if (audioProcessor.sampleLibrary.isDirectory())
    sampleLibrary.setRoot(audioProcessor.sampleLibrary);
  sampleLibrary.onFolder = [this](const juce::File& folder) { audioProcessor.sampleLibrary = folder; };
  sampleLibrary.onSearch = [this] { searchSampleLibrary(); };
  sampleLibrary.onUse = [this](const juce::File& file) { useLibraryFile(file); };
  sampleLibrary.onPreview = [this](const juce::File& file) { previewLibraryFile(file); };
  sampleLibrary.onDrag = [this](const juce::File& file) { dragLibraryFile(file); };
  sampleLibrary.onDone = [this] { setLibraryOpen(false); };
  sampleLibrary.setDismissible(true);
  sampleLibrary.setVisible(false);
  page.addChildComponent(sampleLibrary);

  setWantsKeyboardFocus(true);
  startTimerHz(4);
  SidecarSupervisor::instance().requestStart();
  refreshHealth();
  if (std::getenv("CONTEXT_SMOKE_APPLY") != nullptr)
    applyClicked();
}

ContextAudioProcessorEditor::~ContextAudioProcessorEditor()
{
  audioProcessor.setAuditionPlaying(false);
  discardAuditionFiles();
}

void ContextAudioProcessorEditor::paint(juce::Graphics& g)
{
  g.fillAll(juce::Colour(0xff161616));
  if (fileDragOver)
  {
    g.setColour(juce::Colour(0xff7ec8ff).withAlpha(0.18f));
    g.fillRect(getLocalBounds());
    g.setColour(juce::Colour(0xff7ec8ff));
    g.drawRect(getLocalBounds().reduced(4), 2);
  }
  if (referenceDropHover && !referenceRowBounds.isEmpty())
  {
    g.setColour(juce::Colour(0xff7ec8ff));
    g.drawRect(getLocalArea(&page, referenceRowBounds).expanded(2), 2);
  }
}

void ContextAudioProcessorEditor::resized()
{
  scroller.setBounds(getLocalBounds());
  const int pageW = juce::jmax(520, getWidth());
  const int pageH = libraryOpen ? juce::jmax(760, getHeight()) : juce::jmax(520, getHeight());
  page.setSize(pageW, pageH);
  layoutPage();
}

void ContextAudioProcessorEditor::layoutPage()
{
  auto area = page.getLocalBounds().reduced(12);
  auto refRow = area.removeFromTop(26);
  referenceRowBounds = refRow;
  referenceLabel.setBounds(refRow.removeFromLeft(72));
  refRow.removeFromLeft(8);
  referenceChoose.setBounds(refRow.removeFromRight(88));
  refRow.removeFromRight(8);
  referenceField.setBounds(refRow);
  area.removeFromTop(8);
  auto header = area.removeFromTop(22);
  title.setBounds(header.removeFromLeft(100));
  header.removeFromLeft(8);
  prompts.setBounds(header.removeFromLeft(80));
  header.removeFromLeft(8);
  library.setBounds(header.removeFromLeft(80));
  header.removeFromLeft(8);
  health.setBounds(header);
  area.removeFromTop(8);
  auto promptRow = area.removeFromTop(26);
  run.setBounds(promptRow.removeFromRight(72));
  promptRow.removeFromRight(8);
  prompt.setBounds(promptRow);
  area.removeFromTop(4);
  promptRank.setBounds(area.removeFromTop(14));
  area.removeFromTop(6);
  if (promptGate.isVisible())
    promptGate.setBounds(getLocalBounds().withTrimmedTop(36));
  auto knobs = area.removeFromTop(56);
  const int knobWidth = knobs.getWidth() / 2;
  reverence.setBounds(knobs.removeFromLeft(knobWidth).reduced(36, 0));
  abstraction.setBounds(knobs.reduced(36, 0));
  auto knobLabels = area.removeFromTop(14);
  revLabel.setBounds(knobLabels.removeFromLeft(knobWidth));
  absLabel.setBounds(knobLabels);
  area.removeFromTop(4);
  waveform.setBounds(area.removeFromTop(52));
  area.removeFromTop(4);
  dropHint.setBounds(area.removeFromTop(16));
  area.removeFromTop(4);
  preview.setBounds(area.removeFromTop(36));
  area.removeFromTop(8);
  auto actions = area.removeFromTop(28);
  audition.setBounds(actions.removeFromLeft(100));
  actions.removeFromLeft(8);
  apply.setBounds(actions.removeFromLeft(100));
  area.removeFromTop(6);
  status.setBounds(area.removeFromTop(40));
  status.setMinimumHorizontalScale(0.85f);
  area.removeFromTop(8);
  if (libraryOpen)
  {
    sampleLibrary.setVisible(true);
    sampleLibrary.setBounds(area);
  }
  else
  {
    sampleLibrary.setVisible(false);
    sampleLibrary.setBounds({});
  }
  audition.toFront(false);
  apply.toFront(false);
}

bool ContextAudioProcessorEditor::keyPressed(const juce::KeyPress& key)
{
  if (key == juce::KeyPress::escapeKey && promptGate.isVisible())
  {
    closePromptGate();
    return true;
  }
  return false;
}

void ContextAudioProcessorEditor::titleClicked(const juce::MouseEvent& e)
{
  const auto now = juce::Time::getMillisecondCounter();
  if (now - lastTitleClickMs < 700)
    ++titleClicks;
  else
    titleClicks = 1;
  lastTitleClickMs = now;
  if (e.mods.isAltDown() || titleClicks >= 5)
  {
    titleClicks = 0;
    togglePromptGate();
  }
}

void ContextAudioProcessorEditor::showPromptsMenu()
{
  juce::PopupMenu menu;
  menu.addItem(1, "SYSTEM  -  hard gate");
  menu.addItem(2, "RULES  -  hard");
  menu.addItem(3, "NEGATIVE  -  hard reject");
  if (promptGate.isVisible())
    menu.addItem(4, "Close");
  menu.showMenuAsync(juce::PopupMenu::Options().withTargetComponent(&prompts), [this](int result) {
    if (result == 4)
      closePromptGate();
    else if (result >= 1)
      openPromptGate(result);
  });
}

void ContextAudioProcessorEditor::openPromptGate(int field)
{
  promptGate.setTexts(audioProcessor.systemPrompt, audioProcessor.rules, audioProcessor.negativePrompt);
  promptGate.setVisible(true);
  promptGate.toFront(true);
  resized();
  promptGate.focusField(field);
}

void ContextAudioProcessorEditor::togglePromptGate()
{
  if (promptGate.isVisible())
  {
    closePromptGate();
    return;
  }
  openPromptGate(1);
}

void ContextAudioProcessorEditor::closePromptGate()
{
  persistGateTexts();
  promptGate.setVisible(false);
  resized();
}

void ContextAudioProcessorEditor::persistGateTexts()
{
  audioProcessor.systemPrompt = promptGate.systemText();
  audioProcessor.rules = promptGate.rulesText();
  audioProcessor.negativePrompt = promptGate.negativeText();
}

void ContextAudioProcessorEditor::toggleSampleLibrary()
{
  setLibraryOpen(!libraryOpen);
}

void ContextAudioProcessorEditor::closeSampleLibrary()
{
  setLibraryOpen(false);
}

void ContextAudioProcessorEditor::setLibraryOpen(bool open)
{
  if (open && promptGate.isVisible())
    closePromptGate();
  libraryOpen = open;
  sampleLibrary.setVisible(open);
  if (open)
  {
    if (audioProcessor.sampleLibrary.isDirectory())
      sampleLibrary.setRoot(audioProcessor.sampleLibrary);
    sampleLibrary.browseLocal();
    sampleLibrary.focusQuery();
    setSize(getWidth(), juce::jmax(720, getHeight()));
  }
  else
  {
    setSize(getWidth(), 520);
  }
  resized();
  if (open)
    scroller.setViewPosition(0, juce::jmax(0, sampleLibrary.getY() - 8));
}

void ContextAudioProcessorEditor::refreshReferenceField()
{
  if (audioProcessor.referenceFile.existsAsFile())
    referenceField.setText(audioProcessor.referenceFile.getFullPathName(), false);
  else
    referenceField.clear();
}

void ContextAudioProcessorEditor::chooseReferenceFile()
{
  const auto start = audioProcessor.referenceFile.existsAsFile()
                         ? audioProcessor.referenceFile.getParentDirectory()
                         : juce::File::getSpecialLocation(juce::File::userHomeDirectory);
  referenceChooser = std::make_unique<juce::FileChooser>("Choose reference audio", start, "*.wav;*.aiff;*.aif;*.flac;*.mp3;*.ogg");
  constexpr auto flags = juce::FileBrowserComponent::openMode | juce::FileBrowserComponent::canSelectFiles;
  referenceChooser->launchAsync(flags, [this](const juce::FileChooser& picked) {
    const auto file = picked.getResult();
    if (file.existsAsFile())
      setReferenceFile(file);
  });
}

void ContextAudioProcessorEditor::setReferenceFile(const juce::File& source)
{
  if (!source.existsAsFile())
    return;
  auto dest = DropWriter::referenceFolder().getChildFile(source.getFileName());
  source.copyFileTo(dest);
  audioProcessor.referenceFile = dest.existsAsFile() ? dest : source;
  refreshReferenceField();
  dropHint.setText("Reference: " + audioProcessor.referenceFile.getFileName(), juce::dontSendNotification);
  status.setText("Using " + audioProcessor.referenceFile.getFileName() + " as the next generation reference.",
                 juce::dontSendNotification);
}

void ContextAudioProcessorEditor::searchSampleLibrary()
{
  const auto folder = sampleLibrary.root();
  const auto typed = sampleLibrary.queryText().trim();
  if (!folder.isDirectory())
  {
    status.setText("Choose a sample library folder first.", juce::dontSendNotification);
    return;
  }
  audioProcessor.sampleLibrary = folder;
  if (typed.isEmpty())
  {
    sampleLibrary.browseLocal();
    status.setText("Showing every audio file in " + folder.getFileName() + ".", juce::dontSendNotification);
    return;
  }
  sampleLibrary.searchLocal(typed);
  status.setText("Listed local matches in " + asciiUi(folder.getFileName()) + ". Ranking...", juce::dontSendNotification);
  juce::Component::SafePointer<ContextAudioProcessorEditor> safe(this);
  std::thread([safe, typed, dest = folder.getFullPathName()] {
    SidecarClient client;
    juce::String body;
    juce::String error;
    if (client.healthOk())
    {
      juce::DynamicObject::Ptr payload = new juce::DynamicObject();
      payload->setProperty("query", typed);
      payload->setProperty("folder", dest);
      payload->setProperty("limit", 80);
      payload->setProperty("quick", true);
      body = client.post("/search", juce::JSON::toString(juce::var(payload.get())));
      error = client.lastError();
    }
    else
    {
      error = "sidecar down";
    }
    juce::MessageManager::callAsync([safe, body, error] {
      if (safe != nullptr)
        safe->finishLibrarySearch(body, error);
    });
  }).detach();
}

void ContextAudioProcessorEditor::finishLibrarySearch(const juce::String& body, const juce::String& error)
{
  sampleLibrary.setBusy(false);
  if (error.isNotEmpty())
  {
    status.setText("Showing local search results. " + error, juce::dontSendNotification);
    return;
  }
  const auto parsed = juce::JSON::parse(body);
  auto* obj = parsed.getDynamicObject();
  if (obj == nullptr)
    return;
  juce::Array<SampleRow> hits;
  if (auto files = obj->getProperty("hits"); files.isArray())
  {
    for (const auto& item : *files.getArray())
    {
      auto* hit = item.getDynamicObject();
      if (hit == nullptr)
        continue;
      SampleRow row;
      row.file = juce::File(hit->getProperty("file_path").toString());
      row.name = hit->getProperty("name").toString();
      if (row.name.isEmpty())
        row.name = row.file.getFileName();
      row.folder = hit->getProperty("folder").toString();
      row.score = static_cast<double>(hit->getProperty("score"));
      if (row.file.existsAsFile())
        hits.add(row);
    }
  }
  if (hits.isEmpty())
    return;
  const auto backend = obj->getProperty("backend").toString();
  const int count = static_cast<int>(obj->getProperty("count"));
  sampleLibrary.showHits(hits, backend.isNotEmpty() ? backend : "search", count);
  status.setText("Library search - " + juce::String(hits.size()) + " listed - " + (backend.isNotEmpty() ? backend : "local"),
                 juce::dontSendNotification);
}

void ContextAudioProcessorEditor::previewLibraryFile(const juce::File& source)
{
  if (!source.existsAsFile())
    return;
  if (!audioProcessor.loadAuditionWav(source))
  {
    status.setText("Could not preview " + source.getFileName() + ".", juce::dontSendNotification);
    return;
  }
  audioProcessor.setAuditionPlaying(true);
  audition.setButtonText("Stop");
  dropHint.setText("Preview: " + source.getFileName() + ". Drag the row into Live.", juce::dontSendNotification);
  status.setText("Previewing " + source.getFileName() + ". Drag the row or use Drag to Live.",
                 juce::dontSendNotification);
  waveform.repaint();
}

void ContextAudioProcessorEditor::dragLibraryFile(const juce::File& source)
{
  if (!source.existsAsFile())
    return;
  performExternalDragDropOfFiles({source.getFullPathName()}, false);
}

void ContextAudioProcessorEditor::useLibraryFile(const juce::File& source)
{
  setReferenceFile(source);
}

void ContextAudioProcessorEditor::timerCallback()
{
  waveform.repaint();
  if (composeBusy)
  {
    refreshProgress();
    return;
  }
  if (++healthPulse < 8)
    return;
  healthPulse = 0;
  refreshHealth();
}

void ContextAudioProcessorEditor::refreshProgress()
{
  const auto body = sidecar.get("/progress");
  const auto parsed = juce::JSON::parse(body);
  auto* obj = parsed.getDynamicObject();
  if (obj == nullptr)
    return;

  const int step = static_cast<int>(obj->getProperty("step"));
  const int steps = static_cast<int>(obj->getProperty("steps"));
  const auto etaVar = obj->getProperty("eta_sec");
  const bool hasEta = etaVar.isDouble() || etaVar.isInt() || etaVar.isInt64();
  const double eta = hasEta ? static_cast<double>(etaVar) : -1.0;
  const auto phase = obj->getProperty("phase").toString();
  const auto generator = obj->getProperty("id").toString();
  juce::String line = "Generating";
  if (generator.isNotEmpty())
    line += " with " + asciiUi(generator);
  if (steps > 0)
    line += " - " + juce::String(step) + " of " + juce::String(steps);
  if (phase == "loading")
    line += ". Loading model...";
  else if (!hasEta || eta < 0.0 || step < 2)
    line += ". Estimating time...";
  else if (eta < 2.0)
    line += ". Almost done.";
  else if (eta < 90.0)
    line += ". About " + juce::String(juce::roundToInt(eta)) + " seconds left.";
  else
    line += ". About " + juce::String(juce::jmax(1, juce::roundToInt(eta / 60.0))) + " minutes left.";
  status.setText(asciiUi(line), juce::dontSendNotification);

  const bool previewReady = static_cast<bool>(obj->getProperty("preview_ready"));
  const int generation = static_cast<int>(obj->getProperty("preview_generation"));
  const auto previewPath = obj->getProperty("preview_wav").toString();
  if (!previewReady || previewPath.isEmpty() || generation == lastPreviewGeneration)
    return;
  const juce::File previewFile(previewPath);
  if (!previewFile.existsAsFile())
    return;
  lastPreviewGeneration = generation;
  if (!audioProcessor.loadAuditionWav(previewFile))
    return;
  waveform.repaint();
  if (composePlayAfter)
  {
    audioProcessor.setAuditionPlaying(true);
    audition.setButtonText("Stop");
  }
}

bool ContextAudioProcessorEditor::isInterestedInFileDrag(const juce::StringArray& files)
{
  for (const auto& path : files)
    if (isAudioFile(juce::File(path)))
      return true;
  return false;
}

void ContextAudioProcessorEditor::fileDragEnter(const juce::StringArray&, int, int)
{
  fileDragOver = true;
  repaint();
}

void ContextAudioProcessorEditor::fileDragExit(const juce::StringArray&)
{
  fileDragOver = false;
  repaint();
}

void ContextAudioProcessorEditor::filesDropped(const juce::StringArray& files, int, int)
{
  fileDragOver = false;
  repaint();
  for (const auto& path : files)
  {
    juce::File source(path);
    if (!isAudioFile(source))
      continue;
    setReferenceFile(source);
    return;
  }
}

void ContextAudioProcessorEditor::refreshHealth()
{
  if (composeBusy)
    return;
  const auto body = sidecar.get("/health");
  if (body.contains("\"ok\": true") || body.contains("\"ok\":true"))
  {
    juce::String generator = "pedalboard";
    const auto key = body.fromFirstOccurrenceOf("\"id\":", false, false);
    if (key.isNotEmpty())
    {
      const auto quoted = key.fromFirstOccurrenceOf("\"", false, false);
      generator = quoted.upToFirstOccurrenceOf("\"", false, false);
    }
    health.setText("sidecar ok - generator: " + asciiUi(generator), juce::dontSendNotification);
    return;
  }

  if (SidecarSupervisor::instance().isStarting())
  {
    health.setText("sidecar: starting on 127.0.0.1:8765", juce::dontSendNotification);
    return;
  }

  SidecarSupervisor::instance().requestStart();
  const auto detail = SidecarSupervisor::instance().lastStatus();
  health.setText("sidecar: " + asciiUi(detail.isNotEmpty() ? detail : "down") + " (Apply still writes local files)",
                 juce::dontSendNotification);
}

float ContextAudioProcessorEditor::knob(const juce::String& id) const
{
  if (auto* param = audioProcessor.parameters.getRawParameterValue(id))
    return param->load();
  return 0.0f;
}

juce::String ContextAudioProcessorEditor::intentJson() const
{
  const auto escaped = audioProcessor.prompt.replace("\\", "\\\\").replace("\"", "\\\"");
  return juce::String()
         + "{"
         + "\"schema_version\":1,"
         + "\"prompt\":\"" + escaped + "\","
         + "\"mode\":\"track_follow\","
         + "\"scope\":\"this_track\","
         + "\"host_track\":{\"id\":\"track-0\",\"name\":\"Host\",\"inferred_role\":\"other\"},"
         + "\"project\":{\"tempo_bpm\":120,\"musical_key\":\"Am\",\"playhead_beats\":0,"
         + "\"tracks\":[{\"id\":\"track-0\",\"name\":\"Host\",\"kind\":\"audio\",\"inferred_role\":\"other\","
         + "\"clips\":[{\"id\":\"clip-0\",\"kind\":\"audio\",\"start_beats\":0,\"length_beats\":16,"
         + "\"file_path\":\"/Users/camdouglas/context/fixtures/silence.wav\"}]}]},"
         + "\"knobs\":{"
         + "\"reverence\":" + juce::String(knob("reverence"), 3) + ","
         + "\"abstraction\":" + juce::String(knob("abstraction"), 3) + "},"
         + "\"focus\":{\"kind\":\"host_clip\"},"
         + "\"locks\":[],"
         + "\"tempo_key_lock\":true,"
         + "\"variation\":false"
         + "}";
}

void ContextAudioProcessorEditor::runClicked()
{
  audioProcessor.prompt = prompt.getText();
  const auto text = audioProcessor.prompt.trim();
  if (text.isEmpty())
  {
    status.setText("Type what to do next, then run.", juce::dontSendNotification);
    return;
  }

  juce::String previewText = "{\"prompt\":\"" + text.replace("\"", "\\\"") + "\",\"ok\":true}";
  if (sidecar.healthOk())
  {
    const auto response = sidecar.post("/intent", intentJson());
    if (response.isNotEmpty())
      previewText = response;
    else
      previewText = sidecar.lastError();
  }
  else
  {
    previewText += "\n(sidecar down; local preview only)";
  }
  preview.setText(asciiUi(previewText));
  hasPreview = true;
  status.setText("Preview ready. Audition is temporary. Apply keeps the clip.", juce::dontSendNotification);
}

void ContextAudioProcessorEditor::setBusy(bool busy)
{
  composeBusy = busy;
  run.setEnabled(!busy);
  apply.setEnabled(!busy);
  audition.setEnabled(true);
  if (audioProcessor.isAuditionPlaying())
    audition.setButtonText("Stop");
  else if (busy)
    audition.setButtonText("Busy");
  else
    audition.setButtonText("Audition");
}

void ContextAudioProcessorEditor::discardAuditionFiles()
{
  audioProcessor.setAuditionPlaying(false);
  for (auto& file : tempFiles)
    file.deleteFile();
  tempFiles.clear();
  juce::Array<juce::File> leftovers;
  DropWriter::auditionFolder().findChildFiles(leftovers, juce::File::findFiles, false);
  for (auto& file : leftovers)
    file.deleteFile();
}

bool ContextAudioProcessorEditor::promoteAudition()
{
  juce::File source = audioProcessor.lastWavFile;
  if (!source.existsAsFile() || source.getSize() < 1000)
  {
    const auto previewWav = DropWriter::pluginFolder().getChildFile(".preview").getChildFile("live.wav");
    if (previewWav.existsAsFile() && previewWav.getSize() >= 1000)
      source = previewWav;
  }
  if (!source.existsAsFile() || source.getSize() < 1000)
  {
    for (auto& file : tempFiles)
    {
      if (file.hasFileExtension("wav") && file.existsAsFile() && file.getSize() >= 1000)
      {
        source = file;
        break;
      }
    }
  }
  if (!source.existsAsFile() || source.getSize() < 1000)
    return false;

  const auto dest = DropWriter::pluginFolder();
  dest.createDirectory();
  juce::String name = source.getFileName();
  if (name == "live.wav" || source.isAChildOf(dest.getChildFile(".preview")))
  {
    auto slug = audioProcessor.lastComposedPrompt.trim().toLowerCase();
    slug = slug.retainCharacters("abcdefghijklmnopqrstuvwxyz0123456789- ");
    slug = slug.replaceCharacters(" ", "-");
    while (slug.contains("--"))
      slug = slug.replace("--", "-");
    name = (slug.isNotEmpty() ? slug : juce::String("context-output")) + ".wav";
  }
  auto target = dest.getChildFile(name);
  if (source.getFullPathName() != target.getFullPathName())
  {
    if (target.existsAsFile())
      target.deleteFile();
    if (!source.copyFileTo(target) || !target.existsAsFile())
      return false;
  }
  audioProcessor.lastWavFile = target;
  for (auto& file : tempFiles)
  {
    if (!file.hasFileExtension("mid") || !file.existsAsFile())
      continue;
    auto midTarget = dest.getChildFile(file.getFileName());
    if (file.getFullPathName() != midTarget.getFullPathName())
      file.copyFileTo(midTarget);
    if (midTarget.existsAsFile())
      audioProcessor.lastMidFile = midTarget;
  }
  tempFiles.clear();
  auditionApplied = true;
  audioProcessor.loadAuditionWav(target);
  return true;
}

void ContextAudioProcessorEditor::dragGeneratedFiles()
{
  auto wav = audioProcessor.lastWavFile;
  if (!wav.existsAsFile())
    return;
  if (wav.isAChildOf(DropWriter::auditionFolder()) || wav.getFileName() == "live.wav")
  {
    auto name = wav.getFileName() == "live.wav" ? juce::String("context-output.wav") : wav.getFileName();
    auto stable = DropWriter::pluginFolder().getChildFile(name);
    wav.copyFileTo(stable);
    if (stable.existsAsFile())
      wav = stable;
  }
  juce::StringArray files;
  files.add(wav.getFullPathName());
  if (audioProcessor.lastMidFile.existsAsFile())
    files.add(audioProcessor.lastMidFile.getFullPathName());
  performExternalDragDropOfFiles(files, false);
}

juce::Rectangle<int> ContextAudioProcessorEditor::referenceScreenBounds() const
{
  return page.localAreaToGlobal(referenceRowBounds);
}

void ContextAudioProcessorEditor::setReferenceDropHover(bool over)
{
  if (referenceDropHover == over)
    return;
  referenceDropHover = over;
  repaint();
}

void ContextAudioProcessorEditor::useOutputAsReference()
{
  if (!audioProcessor.lastWavFile.existsAsFile())
  {
    status.setText("No output clip yet. Audition or Apply first.", juce::dontSendNotification);
    return;
  }
  setReferenceFile(audioProcessor.lastWavFile);
}

void ContextAudioProcessorEditor::auditionClicked()
{
  if (audioProcessor.isAuditionPlaying() || composePlayAfter)
  {
    composePlayAfter = false;
    audioProcessor.setAuditionPlaying(false);
    audition.setButtonText(composeBusy ? "Busy" : "Audition");
    status.setText(composeBusy ? "Preview stopped. Still generating."
                               : "Audition stopped. Apply keeps the clip in Context/Plugin.",
                   juce::dontSendNotification);
    waveform.repaint();
    return;
  }
  if (composeBusy)
  {
    status.setText("Already generating. Wait for the sidecar, then try again.", juce::dontSendNotification);
    return;
  }
  audioProcessor.prompt = prompt.getText();
  const auto typed = audioProcessor.prompt.trim();
  if (typed.isEmpty() || typed == "type what to make")
  {
    status.setText("Type what to make, then Audition.", juce::dontSendNotification);
    return;
  }
  startCompose(typed, false, true);
}

void ContextAudioProcessorEditor::applyClicked()
{
  if (composeBusy)
  {
    status.setText("Already generating. Wait for the sidecar, then try Apply again.", juce::dontSendNotification);
    return;
  }
  audioProcessor.prompt = prompt.getText();
  const auto typed = audioProcessor.prompt.trim();
  if (typed.isEmpty() || typed == "type what to make")
  {
    status.setText("Type what to make, then Apply.", juce::dontSendNotification);
    return;
  }
  if (typed == audioProcessor.lastComposedPrompt && promoteAudition())
  {
    status.setText("Kept " + audioProcessor.lastWavFile.getFileName() + " in Context/Plugin. Drag the waveform into Live.",
                   juce::dontSendNotification);
    preview.setText(audioProcessor.lastWavFile.getFullPathName());
    return;
  }
  startCompose(typed, true, audioProcessor.isAuditionPlaying());
}

void ContextAudioProcessorEditor::startCompose(const juce::String& typed, bool permanent, bool playAfter)
{
  if (composeBusy)
    return;
  if (!permanent)
    discardAuditionFiles();
  audioProcessor.setAuditionPlaying(false);
  audition.setButtonText("Audition");
  composePlayAfter = playAfter || !permanent;
  lastPreviewGeneration = -1;
  setBusy(true);
  status.setText(permanent ? "Generating a permanent clip in Context/Plugin. Estimating time..."
                           : "Auditioning. Estimating time...",
                 juce::dontSendNotification);

  persistGateTexts();
  const auto dest = permanent ? DropWriter::pluginFolder() : DropWriter::auditionFolder();
  const float reverenceValue = knob("reverence");
  const float abstractionValue = knob("abstraction");
  const auto reference = audioProcessor.referenceFile.getFullPathName();
  const auto systemText = audioProcessor.systemPrompt;
  const auto rulesText = audioProcessor.rules;
  const auto negativeText = audioProcessor.negativePrompt;
  const auto libraryFolder = audioProcessor.sampleLibrary.getFullPathName();

  juce::Component::SafePointer<ContextAudioProcessorEditor> safe(this);
  std::thread([safe, typed, permanent, playAfter, dest, reverenceValue, abstractionValue, reference, systemText, rulesText,
               negativeText, libraryFolder] {
    SidecarClient client;
    juce::String body;
    juce::String error;
    if (client.healthOk())
    {
      juce::DynamicObject::Ptr payload = new juce::DynamicObject();
      payload->setProperty("prompt", typed);
      payload->setProperty("dest_dir", dest.getFullPathName());
      payload->setProperty("reference_path", reference);
      payload->setProperty("library_folder", libraryFolder);
      payload->setProperty("system_prompt", systemText);
      payload->setProperty("rules", rulesText);
      payload->setProperty("negative_prompt", negativeText);
      juce::DynamicObject::Ptr knobs = new juce::DynamicObject();
      knobs->setProperty("reverence", reverenceValue);
      knobs->setProperty("abstraction", abstractionValue);
      payload->setProperty("knobs", juce::var(knobs.get()));
      body = client.postLong("/compose", juce::JSON::toString(juce::var(payload.get())));
      error = client.lastError();
    }
    else
    {
      error = "sidecar down";
    }
    juce::MessageManager::callAsync([safe, typed, permanent, playAfter, body, error] {
      if (safe != nullptr)
        safe->finishCompose(typed, body, error, permanent, playAfter);
    });
  }).detach();
}

void ContextAudioProcessorEditor::finishCompose(const juce::String& typed,
                                               const juce::String& body,
                                               const juce::String& error,
                                               bool permanent,
                                               bool playAfter)
{
  juce::ignoreUnused(playAfter);
  const bool shouldPlay = composePlayAfter;
  composePlayAfter = false;
  setBusy(false);
  DropResult drop;
  juce::String generatorId;
  juce::String fallback;
  const auto parsed = juce::JSON::parse(body);
  if (auto* obj = parsed.getDynamicObject())
  {
    const auto wavPath = obj->getProperty("wav").toString();
    if (wavPath.isNotEmpty())
    {
      const auto wavFile = juce::File(wavPath);
      if (wavFile.existsAsFile())
        drop.files.add(wavFile);
    }
    const auto midiPath = obj->getProperty("midi").toString();
    if (midiPath.isNotEmpty())
    {
      const auto midiFile = juce::File(midiPath);
      if (midiFile.existsAsFile())
        drop.files.add(midiFile);
    }
    if (auto files = obj->getProperty("files"); files.isArray())
    {
      for (const auto& item : *files.getArray())
      {
        const auto file = juce::File(item.toString());
        if (file.existsAsFile())
          drop.files.addIfNotAlreadyThere(file);
      }
    }
    if (auto* gen = obj->getProperty("generator").getDynamicObject())
    {
      generatorId = gen->getProperty("id").toString();
      fallback = gen->getProperty("fallback").toString();
      if (!static_cast<bool>(gen->getProperty("ok")))
      {
        const auto reason = gen->getProperty("error").toString();
        drop.message = "Active tool " + generatorId + " did not write audio"
                       + (reason.isNotEmpty() ? (": " + reason) : ".");
      }
    }
    drop.folder = juce::File(obj->getProperty("folder").toString());
    bool hasWav = false;
    for (const auto& file : drop.files)
      hasWav = hasWav || file.hasFileExtension("wav");
    drop.ok = hasWav;
    if (auto okFlag = obj->getProperty("ok"); okFlag.isBool())
      drop.ok = static_cast<bool>(okFlag) && hasWav;
  }

  if (!drop.ok)
  {
    const auto reason = drop.message.isNotEmpty()
                          ? drop.message
                          : (error.isNotEmpty() ? error : "Generator did not write a clip. No stand-in was used.");
    status.setText(asciiUi(reason), juce::dontSendNotification);
    preview.setText(asciiUi(body.isNotEmpty() ? body : reason));
    if (shouldPlay && audioProcessor.hasAudition())
    {
      audioProcessor.setAuditionPlaying(true);
      audition.setButtonText("Stop");
    }
    waveform.repaint();
    return;
  }

  juce::File wav;
  tempFiles.clear();
  for (const auto& file : drop.files)
  {
    if (!permanent)
      tempFiles.add(file);
    if (file.hasFileExtension("wav"))
      wav = file;
    if (file.hasFileExtension("mid"))
      audioProcessor.lastMidFile = file;
  }
  auditionApplied = permanent;
  if (wav.existsAsFile())
  {
    audioProcessor.lastWavFile = wav;
    audioProcessor.lastComposedPrompt = typed;
    audioProcessor.loadAuditionWav(wav);
  }

  juce::String message = drop.message;
  if (message.isEmpty() && wav.existsAsFile())
  {
    message = (permanent ? "Kept " : "Auditioning ") + wav.getFileName();
    if (generatorId.isNotEmpty())
      message += " (" + generatorId + ")";
    if (fallback.isNotEmpty())
      message += " via " + fallback + " fallback";
    message += permanent ? ". Drag the waveform into Live." : ". Apply to keep it.";
  }
  status.setText(asciiUi(message), juce::dontSendNotification);
  preview.setText(asciiUi(body.isNotEmpty() ? body : message));
  hasPreview = true;
  waveform.repaint();

  if (shouldPlay && audioProcessor.hasAudition())
  {
    audioProcessor.setAuditionPlaying(true);
    audition.setButtonText("Stop");
  }
}
