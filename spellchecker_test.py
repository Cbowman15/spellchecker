
import unittest
import tkinter as tk
from spellchecker import Spellchecker, SpellcheckerApp, Suggester, ReferenceFile
from spellchecker import TextFile, PDFFile, HTMLFile, DocxFile

reference_file = "C:\\Users\\cb6f1\\OneDrive\\Desktop\\Project\\spellchecker\\example.txt"
known_words_file_path = "C:\\Users\\cb6f1\\OneDrive\\Desktop\\Project\\spellchecker\\words.txt"
personal_dict_file_path = "C:\\Users\\cb6f1\\OneDrive\\Desktop\\Project\\spellchecker\\pers_dict.txt"
ignored_words_file_path = "C:\\Users\\cb6f1\\OneDrive\\Desktop\\Project\\spellchecker\\ign_words.txt"

class TestSpellchecker(unittest.TestCase):
    def test__init__(self):
        reference_file = TextFile("I'm done and out for break.")
        known_words_file_path = "known_words.txt"
        personal_dict_file_path = "pers_dict.txt"
        ignored_words_file_path = "ign_words.txt"
        spellchecker = Spellchecker(reference_file, known_words_file_path, personal_dict_file_path, ignored_words_file_path)
        assert spellchecker.known_words == set()
        assert spellchecker.unknown_words == []
        
    def test_spell_check_unknown(self):
        class MockReferenceFile:
            def parse(self):
                return ["Holly", "Jlly", "christmas."]
        reference_file = MockReferenceFile()
        known_words_file_path = "known_words.txt"
        personal_dict_file_path = "pers_dict.txt"
        ignored_words_file_path = "ign_words.txt"
        spellchecker = Spellchecker(reference_file, known_words_file_path,personal_dict_file_path,ignored_words_file_path)
        spellchecker.spell_check()
        self.assertEqual(spellchecker.unknown_words, [("Jlly", [])])
    
    def test_spell_check_known(self):
        class MockReferenceFile:
            def parse(self):
                return ["Holly", "Jolly", "christmas."]
        reference_file = MockReferenceFile()
        known_words_file_path = "known_words.txt"
        personal_dict_file_path = "pers_dict.txt"
        ignored_words_file_path = "ign_words.txt"
        spellchecker = Spellchecker(reference_file, known_words_file_path, personal_dict_file_path,ignored_words_file_path)
        spellchecker.known_words = {"Holly", "Jolly", "christmas."}
        spellchecker.spell_check()
        self.assertNotIn(spellchecker.unknown_words, [("Holly", []), ("Jolly", []), ("christmas.", [])])

    def test_start_sentence(self):
        words_to_check = ["Have", "a", "holly", ",", "jolly,", "Christmas", "."]
        spellchecker = Spellchecker(reference_file, known_words_file_path,personal_dict_file_path,ignored_words_file_path)
        check = spellchecker.start_sentence(-1, words_to_check)
        self.assertFalse(check)

    def test_get_known_words(self):
        known_words_file_path = "known_words.txt"
        personal_dict_file_path = "pers_dict.txt"
        ignored_words_file_path = "ign_words.txt"
        spellchecker = Spellchecker(None, known_words_file_path,personal_dict_file_path,ignored_words_file_path)
        known_words = spellchecker.get_known_words(known_words_file_path,personal_dict_file_path)
        self.assertIsInstance(known_words, set)
    
class TestReferenceFile(unittest.TestCase):
    def test_text_parse(self):
        text = "It's the best time of the year."
        reference_file = TextFile(text)
        words = reference_file.parse()
        self.assertEqual(words, ["It's", "the", "best", "time", "of", "the", "year."])
    
    def test_html_parse(self):
        text = "<html><body><p>Say hello to friends you know</p></body></html>"
        reference_file = HTMLFile(text)
        words = reference_file.parse()
        self.assertEqual(words, ["Say", "hello", "to", "friends", "you", "know"])

    def test_docx_parse(self):
        text = "and everyone you meet."
        docx_file = DocxFile(text)
        words = ["and", "everyone", "you", "meet."]
        self.assertEqual(docx_file.parse(), words)

class TestSuggester(unittest.TestCase):
    def test_get_suggestions(self):
        known_words = {"tech", "ten", "the"}
        unknown = "teh"
        pos_sug = sorted(["the", "tech", "ten"])
        suggester = Suggester(known_words)
        suggestions = suggester.get_suggestions(unknown, known_words)
        self.assertEqual(suggestions, pos_sug)

class TestSpellcheckerApp(unittest.TestCase):
    def test_refresh(self):
        window = tk.Tk()
        reference_file = type("ReferenceFile", (), {"text": ""})()
        known_words_file_path = "known_words.txt"
        personal_dict_file_path = "pers_dict.txt"
        ignored_words_file_path = "ign_words.txt"
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