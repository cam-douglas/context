#pragma once

#include <JuceHeader.h>

struct SampleRow
{
  juce::File file;
  juce::String name;
  juce::String folder;
  double score = 0.0;
};

class SampleLibraryPanel : public juce::Component,
                           public juce::TableListBoxModel
{
public:
  SampleLibraryPanel();

  void paint(juce::Graphics&) override;
  void resized() override;

  void setRoot(const juce::File& folder);
  juce::File root() const { return libraryRoot; }
  void browseLocal();
  void searchLocal(const juce::String& query);
  void showHits(const juce::Array<SampleRow>& hits, const juce::String& backend, int totalCount);
  void setBusy(bool busy);
  void setDismissible(bool showDone);
  void focusQuery();
  juce::String queryText() const { return query.getText(); }
  juce::File selectedFile() const;

  std::function<void(const juce::File&)> onFolder;
  std::function<void()> onSearch;
  std::function<void(const juce::File&)> onUse;
  std::function<void(const juce::File&)> onPreview;
  std::function<void(const juce::File&)> onDrag;
  std::function<void()> onDone;

  int getNumRows() override;
  void paintRowBackground(juce::Graphics&, int rowNumber, int width, int height, bool rowIsSelected) override;
  void paintCell(juce::Graphics&, int rowNumber, int columnId, int width, int height, bool rowIsSelected) override;
  void cellDoubleClicked(int rowNumber, int columnId, const juce::MouseEvent&) override;
  void cellClicked(int rowNumber, int columnId, const juce::MouseEvent&) override;
  void selectedRowsChanged(int lastRowSelected) override;

private:
  void collectAudio(juce::Array<SampleRow>& dest, int cap) const;
  void chooseFolder();
  void revealSelected();
  void useSelected();
  void dragSelected();
  void startRowDrag();

  juce::Label heading;
  juce::Label pathLabel;
  juce::TextButton choose{"Choose..."};
  juce::TextEditor query;
  juce::TextButton search{"Search"};
  juce::TextButton all{"All"};
  class DragTable : public juce::TableListBox
  {
  public:
    std::function<void()> onDragFiles;
    void mouseDrag(const juce::MouseEvent& e) override
    {
      juce::TableListBox::mouseDrag(e);
      if (!dragging && e.getDistanceFromDragStart() > 8 && onDragFiles)
      {
        dragging = true;
        onDragFiles();
      }
    }
    void mouseUp(const juce::MouseEvent& e) override
    {
      dragging = false;
      juce::TableListBox::mouseUp(e);
    }
    bool dragging = false;
  };

  DragTable table;
  juce::TextButton use{"Use as reference"};
  juce::TextButton drag{"Drag to Live"};
  juce::TextButton reveal{"Reveal"};
  juce::TextButton done{"Done"};
  juce::Label hint;
  juce::File libraryRoot;
  juce::Array<SampleRow> rows;
  std::unique_ptr<juce::FileChooser> chooser;
  bool searching = false;

  JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR(SampleLibraryPanel)
};
