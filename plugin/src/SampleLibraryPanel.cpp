#include "SampleLibraryPanel.h"
#include "AsciiUi.h"

namespace
{
  bool isAudioFile(const juce::File& file)
  {
    return file.hasFileExtension("wav;aiff;aif;flac;mp3;ogg");
  }
}

SampleLibraryPanel::SampleLibraryPanel()
{
  heading.setText("Sample Library", juce::dontSendNotification);
  heading.setColour(juce::Label::textColourId, juce::Colours::white);
  heading.setFont(juce::FontOptions(16.0f));
  addAndMakeVisible(heading);

  pathLabel.setColour(juce::Label::textColourId, juce::Colour(0xffc8c8c8));
  pathLabel.setFont(juce::FontOptions(12.0f));
  pathLabel.setMinimumHorizontalScale(0.5f);
  addAndMakeVisible(pathLabel);

  query.setTextToShowWhenEmpty("dark punchy analog snare...", juce::Colour(0xff666666));
  addAndMakeVisible(query);
  query.onReturnKey = [this] { if (onSearch) onSearch(); };

  choose.onClick = [this] { chooseFolder(); };
  search.onClick = [this] { if (onSearch) onSearch(); };
  all.onClick = [this] { browseLocal(); };
  use.onClick = [this] { useSelected(); };
  drag.onClick = [this] { dragSelected(); };
  reveal.onClick = [this] { revealSelected(); };
  done.onClick = [this] { if (onDone) onDone(); };
  addAndMakeVisible(choose);
  addAndMakeVisible(search);
  addAndMakeVisible(all);
  addAndMakeVisible(use);
  addAndMakeVisible(drag);
  addAndMakeVisible(reveal);
  addAndMakeVisible(done);

  table.setModel(this);
  table.setMultipleSelectionEnabled(false);
  table.getHeader().addColumn("Name", 1, 220);
  table.getHeader().addColumn("Folder", 2, 220);
  table.getHeader().addColumn("Match", 3, 70);
  table.setColour(juce::ListBox::backgroundColourId, juce::Colour(0xff0e0e0e));
  table.setColour(juce::ListBox::outlineColourId, juce::Colour(0xff2a2a2a));
  table.setRowHeight(22);
  table.getHeader().setStretchToFitActive(true);
  table.setOutlineThickness(1);
  if (auto* view = table.getViewport())
  {
    view->setScrollBarsShown(true, true);
    view->setScrollBarThickness(12);
  }
  table.onDragFiles = [this] { startRowDrag(); };
  addAndMakeVisible(table);

  hint.setColour(juce::Label::textColourId, juce::Colour(0xff8a8a8a));
  hint.setFont(juce::FontOptions(12.0f));
  hint.setText("Search lists every matching sample here. Click a row to preview. Drag a row, or Drag to Live.",
               juce::dontSendNotification);
  addAndMakeVisible(hint);

  const auto fallback = juce::File::getSpecialLocation(juce::File::userApplicationDataDirectory)
                            .getChildFile("Context")
                            .getChildFile("Samples");
  fallback.createDirectory();
  setRoot(fallback);
}

void SampleLibraryPanel::paint(juce::Graphics& g)
{
  g.fillAll(juce::Colour(0xff121212));
  g.setColour(juce::Colour(0xff7ec8ff));
  g.fillRect(0, 0, 4, getHeight());
}

void SampleLibraryPanel::resized()
{
  auto area = getLocalBounds().reduced(16);
  heading.setBounds(area.removeFromTop(22));
  area.removeFromTop(8);
  auto pathRow = area.removeFromTop(28);
  choose.setBounds(pathRow.removeFromRight(88));
  pathRow.removeFromRight(8);
  pathLabel.setBounds(pathRow);
  area.removeFromTop(8);
  auto searchRow = area.removeFromTop(28);
  search.setBounds(searchRow.removeFromRight(72));
  searchRow.removeFromRight(6);
  all.setBounds(searchRow.removeFromRight(56));
  searchRow.removeFromRight(8);
  query.setBounds(searchRow);
  area.removeFromTop(8);
  auto actions = area.removeFromBottom(28);
  done.setBounds(actions.removeFromRight(done.isVisible() ? 72 : 0));
  if (done.isVisible())
    actions.removeFromRight(8);
  reveal.setBounds(actions.removeFromRight(72));
  actions.removeFromRight(8);
  drag.setBounds(actions.removeFromRight(100));
  actions.removeFromRight(8);
  use.setBounds(actions.removeFromRight(130));
  area.removeFromBottom(8);
  hint.setBounds(area.removeFromBottom(32));
  area.removeFromBottom(6);
  table.setBounds(area);
}

void SampleLibraryPanel::setRoot(const juce::File& folder)
{
  libraryRoot = folder;
  pathLabel.setText(libraryRoot.getFullPathName(), juce::dontSendNotification);
}

void SampleLibraryPanel::collectAudio(juce::Array<SampleRow>& dest, int cap) const
{
  dest.clear();
  if (!libraryRoot.isDirectory())
    return;
  juce::Array<juce::File> found;
  libraryRoot.findChildFiles(found, juce::File::findFiles, true, "*");
  for (const auto& file : found)
  {
    if (!isAudioFile(file))
      continue;
    SampleRow row;
    row.file = file;
    row.name = file.getFileName();
    row.folder = file.getParentDirectory().getRelativePathFrom(libraryRoot);
    if (row.folder == ".")
      row.folder = {};
    dest.add(row);
    if (dest.size() >= cap)
      break;
  }
}

void SampleLibraryPanel::browseLocal()
{
  collectAudio(rows, 400);
  if (!libraryRoot.isDirectory())
    hint.setText("That folder is missing. Choose a sample library.", juce::dontSendNotification);
  else
    hint.setText("Showing " + juce::String(rows.size()) + " samples in " + libraryRoot.getFileName() + ". Search to rank them.",
                 juce::dontSendNotification);
  table.updateContent();
  table.repaint();
  if (rows.size() > 0)
    table.selectRow(0);
}

void SampleLibraryPanel::searchLocal(const juce::String& query)
{
  juce::Array<SampleRow> found;
  collectAudio(found, 400);
  juce::StringArray tokens;
  tokens.addTokens(query.toLowerCase(), " ", "");
  tokens.removeEmptyStrings();
  rows.clear();
  for (auto row : found)
  {
    const auto blob = (row.name + " " + row.folder).toLowerCase();
    row.score = 0.0;
    for (const auto& token : tokens)
      if (blob.contains(token))
        row.score += 1.0;
    rows.add(row);
  }
  struct ByScore
  {
    int compareElements(const SampleRow& a, const SampleRow& b) const
    {
      if (a.score > b.score)
        return -1;
      if (a.score < b.score)
        return 1;
      return a.name.compareIgnoreCase(b.name);
    }
  } sorter;
  rows.sort(sorter);
  hint.setText("Listed " + juce::String(rows.size()) + " samples"
                   + (tokens.size() > 0 ? " ranked for \"" + asciiUi(query) + "\"" : "")
                   + ". Click to preview. Drag into Live.",
               juce::dontSendNotification);
  table.updateContent();
  table.repaint();
  if (rows.size() > 0)
    table.selectRow(0);
}

void SampleLibraryPanel::showHits(const juce::Array<SampleRow>& hits, const juce::String& backend, int totalCount)
{
  rows = hits;
  searching = false;
  const auto shown = juce::String(rows.size());
  const auto total = totalCount > 0 ? juce::String(totalCount) : shown;
  hint.setText("Ranked " + shown + " of " + total + " - " + asciiUi(backend) + ". Double-click or Use as reference. Drag a row into Live.",
               juce::dontSendNotification);
  table.updateContent();
  table.repaint();
  if (rows.size() > 0)
    table.selectRow(0);
}

void SampleLibraryPanel::setBusy(bool busy)
{
  searching = busy;
  hint.setText(busy ? "Searching the library..." : hint.getText(), juce::dontSendNotification);
}

void SampleLibraryPanel::setDismissible(bool showDone)
{
  done.setVisible(showDone);
  resized();
}

void SampleLibraryPanel::focusQuery()
{
  query.grabKeyboardFocus();
}

juce::File SampleLibraryPanel::selectedFile() const
{
  const int row = table.getSelectedRow();
  if (row < 0 || row >= rows.size())
    return {};
  return rows.getReference(row).file;
}

int SampleLibraryPanel::getNumRows()
{
  return rows.size();
}

void SampleLibraryPanel::paintRowBackground(juce::Graphics& g, int, int width, int height, bool rowIsSelected)
{
  g.fillAll(rowIsSelected ? juce::Colour(0xff243040) : juce::Colour(0xff0e0e0e));
  g.setColour(juce::Colour(0xff1c1c1c));
  g.drawLine(0.0f, (float) height - 1.0f, (float) width, (float) height - 1.0f);
}

void SampleLibraryPanel::paintCell(juce::Graphics& g, int rowNumber, int columnId, int width, int height, bool)
{
  if (rowNumber < 0 || rowNumber >= rows.size())
    return;
  const auto& row = rows.getReference(rowNumber);
  juce::String text;
  if (columnId == 1)
    text = asciiUi(row.name);
  else if (columnId == 2)
    text = asciiUi(row.folder);
  else
    text = row.score > 0.0 ? juce::String(row.score, 2) : "-";
  g.setColour(juce::Colours::white.withAlpha(0.92f));
  g.setFont(juce::FontOptions(12.0f));
  g.drawText(text, 6, 0, width - 10, height, juce::Justification::centredLeft, true);
}

void SampleLibraryPanel::cellDoubleClicked(int rowNumber, int, const juce::MouseEvent&)
{
  if (rowNumber >= 0 && rowNumber < rows.size() && onUse)
    onUse(rows.getReference(rowNumber).file);
}

void SampleLibraryPanel::cellClicked(int rowNumber, int, const juce::MouseEvent& e)
{
  if (e.mods.isLeftButtonDown() && e.getDistanceFromDragStart() == 0)
    table.selectRow(rowNumber);
}

void SampleLibraryPanel::selectedRowsChanged(int lastRowSelected)
{
  if (lastRowSelected < 0 || lastRowSelected >= rows.size())
    return;
  const auto file = rows.getReference(lastRowSelected).file;
  if (file.existsAsFile() && onPreview)
    onPreview(file);
}

void SampleLibraryPanel::chooseFolder()
{
  chooser = std::make_unique<juce::FileChooser>("Choose sample library", libraryRoot, "*", true);
  constexpr auto flags = juce::FileBrowserComponent::openMode | juce::FileBrowserComponent::canSelectDirectories;
  chooser->launchAsync(flags, [this](const juce::FileChooser& picked) {
    const auto folder = picked.getResult();
    if (!folder.isDirectory())
      return;
    setRoot(folder);
    if (onFolder)
      onFolder(folder);
    browseLocal();
  });
}

void SampleLibraryPanel::revealSelected()
{
  const auto file = selectedFile();
  if (file.existsAsFile())
    file.revealToUser();
}

void SampleLibraryPanel::useSelected()
{
  const auto file = selectedFile();
  if (file.existsAsFile() && onUse)
    onUse(file);
}

void SampleLibraryPanel::dragSelected()
{
  startRowDrag();
}

void SampleLibraryPanel::startRowDrag()
{
  const auto file = selectedFile();
  if (!file.existsAsFile())
    return;
  if (onDrag)
  {
    onDrag(file);
    return;
  }
  if (auto* container = juce::DragAndDropContainer::findParentDragContainerFor(this))
    container->performExternalDragDropOfFiles({file.getFullPathName()}, false, this);
}
