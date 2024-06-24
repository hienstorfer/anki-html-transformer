import json
from aqt import mw
from aqt.qt import QAction, QMenu
from aqt.utils import showInfo
from bs4 import BeautifulSoup
from anki.hooks import addHook
from anki.notes import Note

# Load configuration
config = mw.addonManager.getConfig(__name__)

class HTMLCleaner:
    def __init__(self, html_data):
        self.soup = BeautifulSoup(html_data, 'html.parser')

    def replace_specific_tags(self, tag_attr_new_tag_tuples):
        """Replace specific tags with given attributes with new tags."""
        for old_tag, attributes, new_tag in tag_attr_new_tag_tuples:
            for tag in self.soup.find_all(old_tag, attributes):
                new_tag_element = self.soup.new_tag(new_tag)
                new_tag_element.string = tag.string
                tag.replace_with(new_tag_element)
        return self

    def remove_all_except(self, allowed_tags):
        """Remove all tags except those specified in allowed_tags."""
        for tag in self.soup.find_all(True):
            if tag.name not in allowed_tags:
                tag.unwrap()
        return self

    def get_clean_html(self):
        """Return the cleaned HTML."""
        return str(self.soup)

def process_html(note):
    fields_to_process = config.get("fields_to_process", [])
    tag_replacements = config.get("tags_replacements", [])
    allowed_tags = config.get("allowed_tags", [])

    cleaner = HTMLCleaner("")

    for field in fields_to_process:
        if field in note:
            cleaner.soup = BeautifulSoup(note[field], 'html.parser')
            cleaner.replace_specific_tags(tag_replacements)
            cleaner.remove_all_except(allowed_tags)
            note[field] = cleaner.get_clean_html()

    note.flush()

def on_html_transformer():
    selected_notes = mw.col.find_notes(mw.form.browser.selectedNotes())
    for note_id in selected_notes:
        note = mw.col.get_note(note_id)
        process_html(note)
    mw.reset()

def setup_menu(browser):
    menu = QMenu("HTML Transformer", browser.form.menuEdit)
    action = QAction("Transform HTML in selected notes", browser)
    action.triggered.connect(on_html_transformer)
    menu.addAction(action)
    browser.form.menuEdit.addMenu(menu)

addHook("browser.setupMenus", setup_menu)
