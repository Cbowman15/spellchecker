
import unittest
import tkinter as tk
from spellchecker import Spellchecker, SpellcheckerApp, Suggester, ReferenceFile
from spellchecker import TextFile, PDFFile, HTMLFile, DocxFile

reference_file = "C:\\Users\\cb6f1\\OneDrive\\Desktop\\Project\\spellchecker\\example.txt"
known_words_file_path = "C:\\Users\\cb6f1\\OneDrive\\Desktop\\Project\\spellchecker\\words.txt"
personal_dict_file_path = "C:\\Users\\cb6f1\\OneDrive\\Desktop\\Project\\spellchecker\\pers_dict.txt"
ignored_words_file_path = "C:\\Users\\cb6f1\\OneDrive\\Desktop\\Project\\spellchecker\\ign_words.txt"

class TestSpellchecker(unittest.TestCase):
    def fxn():
        return
    
class TestSpellcheckerApp(unittest.TestCase):
    def test_refresh(self):
        window = tk.Tk()
        reference_file = type("ReferenceFile", (), {"text": ""})()
        known_words_file_path = "known_words.txt"
        personal_dict_file_path = "personal_dict.txt"
        ignored_words_file_path = "ignored_words.txt"
        spellchecker = Spellchecker(reference_file, known_words_file_path, personal_dict_file_path, ignored_words_file_path)
        spellcheckerapp = SpellcheckerApp(window, spellchecker)

        spellcheckerapp.text.insert(tk.END, "The first test")
        spellcheckerapp.text.tag_add("sel", "1.0", "1.4")
        spellcheckerapp.refresh()
        assert spellcheckerapp.spellchecker.reference_file.text == "waht"
        tag = spellcheckerapp.text.tag_names("1.0")
        assert "highlight" in tag
        suggestions = spellcheckerapp.sug_listbox.get(0, tk.END)
        assert not suggestions
        curr_index = spellcheckerapp.text.index(tk.INSERT)
        assert curr_index == "1.0"

    def test_arrow_mode_activation(self):
        from tkinter import Event
        window = tk.Tk()
        class MockSpellchecker:
            unknown_words = []
        spellchecker = MockSpellchecker()
        spellcheckerapp = SpellcheckerApp(window, spellchecker)
        event = Event()
        event.state = 0x1
        spellcheckerapp.on_arrow_mode(event)
        spellcheckerapp.on_arrow_mode(event)
        spellcheckerapp.on_arrow_mode(event)
        assert spellcheckerapp.arrow_key_mode == True