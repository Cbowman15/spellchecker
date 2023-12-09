try:    
    from bs4 import BeautifulSoup
except ImportError as e:
    print("Error importing BeautifulSoup: {}".format(e))
try:
    import fitz
except ImportError as e:
    print("Error importing fitz: {}".format(e))
try:
    from docx import Document
except ImportError as e:
    print("Error importing Document: {}".format(e))
try:
    import tkinter as tk
except ImportError as e:
    print("Error importing tkinter: {}".format(e))
try:
    from tkinter import filedialog
except ImportError as e:
    print("Error importing filedialog: {}".format(e))
try:
    import re
except ImportError as e:
    print("Error importing re: {}".format(e))
try:
    import time
except ImportError as e:
    print("Error importing time: {}".format(e))
try:
    import Levenshtein
except ImportError as e:
    print("Error importing Levenshtein: {}".format(e))
try:
    import threading
except ImportError as e:
    print("Error importing threading: {}".format(e))
try:
    import os
except ImportError as e:
    print("Error importing os: {}".format(e))
try:
    from fuzzywuzzy import process
except ImportError as e:
    print("Error importing process: {}".format(e))
try:
    from googletrans import Translator, LANGUAGES
except ImportError as e:
    print("Error importing Translator: {}".format(e))
try:
    import argparse
except ImportError as e:
    print("Error importing argparse: {}".format(e))

#Spellchecker class, basic spellchecking functionality
class Spellchecker():
    """
    Initializes a Spellchecker object, which checks text against a file of known,
    or correctly-spelled, words.
    
    Attributes:
    -reference_file (ReferenceFile): the text to be checked for spelling-errors
    -known_words (set): a set of strings, a reference for correctly-spelled words
    -ignored_words_file_path (str): file path to a custom list of words to be ignored (when spellchecking)
    -personal_dict_file (str): file path to a personal dictionary, contained words will be ignored (when spellchecking)
    -ignored_words (set): a set of words to be ignored when spellchecking
    -unknown_words (list): a list of words identified as misspelled
    
    Arguments:
    -reference_file (str): text input/ path to the text to be checked
    -known_words_file_path (str): path to file with correctly-spelled words
    -personal_dict_file_path (str): path to file for personal dictionary
    -ignored_words_file_path (str): path to file for words to ignore
    
    -Takes in all words from argument file paths
    -Takes in ignored_words from a 'load_files' method
    
    Required:
    -File paths must be assigned viable/real/accessible text files
    -known_words_file_path and personal_dict_file_path are text files, containing
     one word per line
     """
    def __init__(self, reference_file, known_words_file_path, personal_dict_file_path, ignored_words_file_path):
        self.reference_file = reference_file
        self.known_words = self.get_known_words(known_words_file_path, personal_dict_file_path)
        self.ignored_words_file_path = ignored_words_file_path
        self.personal_dict_file = personal_dict_file_path
        self.ignored_words = load_files(ignored_words_file_path)
        self.unknown_words = []
        
    def spell_check(self):
        """
        Parses the reference text and checks each individual word against known words and
        the personal dictionary. It then identifies the unknown words and produces suggestions
        for them.
        
        -Each word, after the use of a regex match, is checked against known words
        -Words that are at the start of a sentence, regardless of punctuation are
         identified as known. Words that are captialized are identified as known.
        -Exceptions are accounted for
        
        Returns:
        None
        
        Required:
        -The reference file should be initialized with text to be parsed
        -known_words should be populated with correctly-spelled words
        """
        try:
            words_to_check = self.reference_file.parse()
        except Exception as e:
            print("Error parsing reference file: {}".format(e))
        for index, word in enumerate(words_to_check):
            try:
                if re.match(r"^[a-zA-Z'-]+$", word):
                    known = (word.lower() in self.known_words) or (word in self.known_words)
                    if_start_sent = self.start_sentence(index, words_to_check)
                    if not known and not (if_start_sent and word.istitle()):
                        suggestions = Suggester.get_suggestions(word.lower(), self.known_words)
                        self.unknown_words.append((word, suggestions))
            except Exception as e:
                print("Error in spellcheck, word-{}: {}".format(word,e))
                

    def start_sentence(self, word_index, words_to_check):
        """
        Checks to see if a word is at the start of a sentence.

        Arguments:
        -word_index (int): index of the current word in the list of words to check
        -words_to_check (list): list of words, parsed from reference text

        Returns:
        -bool: True, if word follows punctuation. Otherwise, False

        -Exceptions are accounted for

        Required:
        -word_index is a non-negative integer, within bounds of words_to_check
        -words_to_check is a list of strings, with each string a word from reference text
        """
        if word_index == 0:
            return True
        try:
            prev_word = words_to_check[word_index-1]
            return prev_word[-1] in ".!?;"
        except Exception as e:
            print("Error in start_sentence: {}".format(e))

    def get_known_words(self, known_words_file_path, personal_dict_file_path):
        """
        Reads known words from known words file and personal dictionary file, combining
        them and returning them as a set.
        
        Arguments:
        -known_words_file_path (str): path to file of correctly-spelled words
        -personal_dict_file_path (str): path to file of personal dictionary
        
        Returns:
        -set: set of known words, taken from known words file and personal dictionary file
        
        -Exceptions accounted for
        
        Required:
        -Both arguments are strings for a viable/accessible file path
        -Files of known_words_file_path and personal_dict_file_path must be accessible
         and have one word per line
         """
        known_words = set()
        try:
            if os.path.isfile(known_words_file_path):
                with open(known_words_file_path, 'rt',encoding='utf-8') as known_file:
                    known_words.update(known_file.read().split())
            if os.path.isfile(personal_dict_file_path):
                with open(personal_dict_file_path, 'rt') as personal_dict_file:
                    known_words.update(personal_dict_file.read().split())
        except Exception as e:
            print("Error in get_known_words: {}".format(e))
        return known_words

#abstract class for subclass parsing
class ReferenceFile():
    """
    Abstract class for different file types, for text extraction.
    
    Attributes:
    -text (str): plain-text content of file
    
    Methods:
    -parse: abstract method, is intended to be overridden by subclasses
    """
    def __init__(self, text):
        """
        Initializes ReferenceFile object with provided text.
        
        Arguments:
        -text (str): plain-text content of file
        """
        self.text = text
    def parse(self):
        pass

#class for suggestions
class Suggester():
    """
    Checks whether given word is in known words, and if not, produces suggestions for
    similarly spelled words, based on Levenshtein distance.
    
    (Levenshtein distance is a measure of single-character edits to transform one word
     into another)
    
    Attributes:
    -known_words (set): a set of correctly-spelled words
    
    Methods:
    -get_suggestions(word, known_words): static method, returning list of suggestions
    -checker(word): checks if word is in known_words
    """
    @staticmethod
    def get_suggestions(word, known_words):
        """
        Provides suggestions for given word, from known words, based on Levenshtein
        distance.
        
        Arguments:
        -word (str): word to produce suggestions for
        -known_words (iterable): iterable containing known words
        
        Returns:
        -list: list of supposed top three suggestions
        """
        suggestions = sorted(known_words, key=lambda known_word:Levenshtein.distance(word, known_word))
        return suggestions[:3]
    
    def __init__(self, known_words=None):
        """
        Initializes Suggester with set of known words.
        
        Arguments:
        -known_words (iterable): optional iterable of known words; else, defaults
         to empty set
         """
        self.known_words = known_words or set()
    def checker(self, word):
        """
        Checks if word is in known words set.
        
        Arguments:
        -word (str): word to check against known words
        
        Returns:
        -bool: True if word in set of known words, else False
        """
        if word in self.known_words:
            return True
        else:
            return False

#subclass parsing
class TextFile(ReferenceFile):
    """
    A subclass of ReferenceFile, specifically for the handling of .txt files
    
    Arguments:
    text (str): contents of text file
    
    -Parse method is overridden, as regex was used
    """
    def __init__(self, text):
        """
        Initializes parent class with text.
        """
        super().__init__(text)
    def parse(self):
        """
        Parses file contents into list of words, splitting at whitespace.

        Returns:
        -list: list of strings, which are parsed words from file
        """
        return re.split(r'\s', self.text.strip())

#subclass parsing
class HTMLFile(ReferenceFile):
    def __init__(self, text):
        super().__init__(text)
    def parse(self):
        soup = BeautifulSoup(self.text, "lxml")
        html_content = soup.get_text()
        return html_content.split()

#subclass parsing
class PDFFile(ReferenceFile):
    def __init__(self, file_path):
        super().__init__(None)
        self.file_path = file_path
    def parse(self):
        with fitz.open(self.file_path) as document:
            content = ""
            for page in document:
                content += page.get_text()
        return content

#subclass parsing
class DocxFile(ReferenceFile):
    def __init__(self, text):
        super().__init__(text)
    def parse(self):
        return self.text.split()

#'the' GUI
class SpellcheckerApp:
    """
    'The' GUI
    
    Attributes:
    window (tk.Tk): main application window
    
    Arguments:
    window (tk.Tk): Tkinter window
    spellchecker (Spellchecker): initialized Spellchecker object"""
    def __init__(self, window, spellchecker):
        self.window = window
        self.window.title("Spellchecker EECE2140")
        self.frm = tk.Frame(self.window)
        self.frm.pack()
        self.text = tk.Text(self.frm, wrap="word", width=80, height=30)
        self.text.pack(expand=True, fill='both', padx=30, pady=15)
        try:
            with open("example.txt", 'rt') as example_text_file:
                text_content = example_text_file.read()
        except IOError:
            raise FileExistsError("example.txt file not found")

        self.sug_listbox = tk.Listbox(self.frm, width=40,height=3, takefocus=False)
        self.sug_listbox.pack(side=tk.BOTTOM)
        self.sug_listbox.bind("<Button-1>", self.focus_text)
        self.sug_listbox.bind("<Button-2>", self.focus_text)   
        self.sug_listbox.bind("<Button-3>", self.focus_text)   
        self.text.insert(tk.END, text_content)
        self.lang_entry = tk.Entry(self.frm)
        self.initial = True
        self.current_unknown_index = 0
        self.highlight_indexes = []
        self.previous_highlight = None
        self.btn_next_unknown = tk.Button(self.frm, text="NEXT", command=self.next_unknown)
        self.btn_next_unknown.pack(side=tk.RIGHT, padx=3, pady=3, anchor=tk.SE)
        self.btn_prev_unknown = tk.Button(self.frm, text="PREVIOUS", command=self.previous_unknown)
        self.btn_prev_unknown.pack(side=tk.RIGHT, padx=3, pady=3, anchor=tk.SW)
        self.btn_next_unknown.pack()
        self.btn_prev_unknown.pack()
        self.btn_undo = tk.Button(self.frm, text="UNDO", command=self.undo)
        self.btn_undo.pack(side=tk.LEFT, padx=3, pady=3, anchor=tk.SW)
        self.btn_redo = tk.Button(self.frm, text="REDO", command=self.redo)
        self.btn_redo.pack(side=tk.LEFT, padx=3, pady=3, anchor=tk.SE)
        self.btn_translate = tk.Button(self.frm, text="TRANSLATE", command=self.translate)
        self.btn_close_trans = tk.Button(self.frm, text="CLOSE TRANSLATE", command=self.close_trans)
        self.btn_undo.pack()
        self.btn_redo.pack()
        self.undo_hist = []
        self.redo_hist = []
        self.btn_next_unknown["takefocus"] = False
        self.btn_prev_unknown["takefocus"] = False
        self.btn_undo["takefocus"] = False
        self.btn_redo["takefocus"] = False
        self.btn_translate["takefocus"] = False
        self.btn_close_trans["takefocus"] = False
        self.sug_listbox["takefocus"] = False
        self.text.config(undo=False)
        self.spellchecker = spellchecker
        self.unknown_words = spellchecker.unknown_words
        self.text.tag_config("highlight", background="yellow")
        self.text.tag_config("selected", background="CadetBlue1")
        self.text.tag_bind("highlight", "<Button-3>", self.show_menu)
        self.text.bind("<KeyPress>", self.keypress_action)
        self.text.bind("<KeyRelease>", self.keyrelease_action)
        self.arrow_key_mode = False
        self.arrow_last_time = time.time()
        self.arrow_time_reset = 5
        self.arrow_key_count = 0
        self.arrow_key_req = 3
        self.text.bind("<Left>", self.arrow_key_move)
        self.text.bind("<Right>", self.arrow_key_move)
        self.text.bind("<Up>", self.on_arrow_mode)
        self.text.bind("<Down>", self.off_arrow_mode)
        self.text.bind("<Shift-Left>", self.overload_shift)
        self.text.bind("<Shift-Right>", self.overload_shift)
        self.text.bind("<Shift-Up>", self.overload_shift)
        self.text.bind("<Shift-Down>", self.overload_shift)
        self.text.bind("<KeyPress>", self.keypress_action)
        self.text.bind("<KeyRelease>", self.keyrelease_action)
        self.text.bind("<Control-z>", self.new_undo)
        self.text.bind("<Control-y>", self.new_redo)
        self.text.bind("<Control-t>", self.open_trans)
        self.text.bind("<Control-q>", self.refresh)
        self.window.bind("<Control-o>", self.open_file_two)
        self.window.bind("<Control-s>", self.save_file)
        self.window.bind("<Control-S>", self.save_as)
        self.top_menu = tk.Menu(window)
        self.file_menu = tk.Menu(self.top_menu, tearoff=0)
        self.top_menu.add_cascade(label = "File", menu= self.file_menu)
        self.file_menu.add_command(label = "Open", accelerator="Ctrl+O", command=self.open_file_two)
        self.file_menu.add_command(label="Save", accelerator="Ctrl+s", command=self.save_file)
        self.file_menu.add_command(label="Save As", accelerator="Ctrl+S", command=self.save_as)
        self.tool_menu = tk.Menu(self.top_menu, tearoff=0)
        self.top_menu.add_cascade(label="Tools", menu=self.tool_menu)
        self.tool_menu.add_command(label="Translate", accelerator="Ctrl+t", command=self.open_trans)
        self.tool_menu.add_command(label="Spellcheck", accelerator="Ctrl+q", command=self.refresh)
        window.config(menu=self.top_menu)
        self.btn_ignore = tk.Button(self.frm, text="IGNORE", command=self.ignore_unknown)
        self.btn_ignore.pack(side=tk.RIGHT, padx=3, pady=3, anchor=tk.SE)
        self.btn_ignore.pack()
        self.btn_dict = tk.Button(self.frm, text="+DICTIONARY", command=self.add_dict, width=12)
        self.btn_dict.pack(side=tk.LEFT, padx=3, pady=3, anchor=tk.SW)
        self.dict_off()
        self.last_select = None
        self.text.bind("<FocusOut>", self.focus_out)
        self.text.bind("<FocusIn>", self.focus_in)
        self.curr_word_pos = None
        self.timer_delay = None
        self.time_delay = 500
        self.menu=tk.Menu(self.text, tearoff=0)
        self.working_file = None
        self.translator = Translator()

#file opening, on separate thread from rest
    def refresh(self, event=None):
        curr_index = self.text.index(tk.INSERT)
        start_index = self.text.index("sel.first")
        end_index = self.text.index("sel.last")
        selected = self.text.get(start_index, end_index)
        self.spellchecker.reference_file.text = selected
        self.spellchecker.spell_check()
        self.highlight_unknown()
        self.add_listbox()
        self.add_dict
        self.text.see(curr_index)

    def open_file_one(self, file_to_open):
        try:
            self.working_file = file_to_open
            if file_to_open.lower().endswith('.txt'):
                with open(file_to_open, 'rt') as file:
                    text_content = file.read()
                self.spellchecker.reference_file = TextFile(text_content)
            elif file_to_open.lower().endswith('.html') or file_to_open.lower().endswith('.htm'):
                with open(file_to_open, 'rt') as file:
                    text_content = file.read()
                self.spellchecker.reference_file= HTMLFile(text_content)
            elif file_to_open.lower().endswith('.pdf'):
                self.spellchecker.reference_file = PDFFile(file_to_open)
                text_content = self.spellchecker.reference_file.parse()
            elif file_to_open.lower().endswith('.docx'):
                document = Document(file_to_open)
                text_content = '\n'.join(paragraph.text for paragraph in document.paragraphs if paragraph.text)
                self.spellchecker.reference_file = DocxFile(text_content)
            else:
                print("File not supported")
                return
        except Exception as e:
            print("Unable to open {}: {}".format(file_to_open,e))
        self.update_window(text_content)
        self.title(os.path.basename(file_to_open))
        #self.refresh()--if wanted auto, ruins efficiency, though
    
    def update_window(self, text_content):
        if text_content:
            self.window.after(0, self.text.delete, "1.0", tk.END)
            self.window.after(0, self.text.insert, tk.END, text_content)
            self.spellchecker.reference_file.text = text_content

    def open_file_two(self, event=None):
        file_to_open = filedialog.askopenfilename()
        if file_to_open:
            threading.Thread(target=self.open_file_one, args=(file_to_open,), daemon=True).start()
        return "break"
    
    def title(self, title):
        self.window.title("{}".format(title))

#other options for handling file
    def save_file(self, event=None):
        try:
            if self.working_file:
                with open(self.working_file, 'wt') as save_file:
                    saving_text = self.text.get("1.0", tk.END)
                    save_file.write(saving_text.rstrip())
                self.title(os.path.basename(self.working_file))
            else:
                self.save_as(event)
        except Exception as e:
            print("Error in save_file: {}".format(e))

    def save_as(self, event=None):
        try:
            save_file = filedialog.asksaveasfilename(filetypes=[("All Files", "*.*")])
            if save_file:
                with open(save_file, 'wt') as save_as_file:
                    saving_text = self.text.get("1.0", tk.END)
                    save_as_file.write(saving_text.rstrip())
                    self.working_file = save_file
                    self.title(os.path.basename(save_file))
        except Exception as e:
            print("Error in save_as: {}".format(e))

#arrow keys mode functionality
    def on_arrow_mode(self, event):
        try:    
            if not self.arrow_key_mode and (event.state & 0x1):
                self.arrow_key_count += 1
                if self.arrow_key_count >= self.arrow_key_req:
                    self.arrow_key_mode = True
                    self.arrow_key_count = 0
                    self.btn_next_anchor = tk.SE
                    self.btn_prev_anchor = tk.SW
                    self.hide_btns()
                    self.dict_on()
        except Exception as e:
            print("Error in on_arrow_mode: {}".format(e))
    
    def off_arrow_mode(self, event):
        try:
            if self.arrow_key_mode and (event.state & 0x1):
                self.arrow_key_count += 1
                if self.arrow_key_count >= self.arrow_key_req:
                    self.arrow_key_mode=False
                    self.arrow_key_count = 0
                    self.btn_next_anchor = tk.RIGHT
                    self.btn_prev_anchor = tk.RIGHT
                    self.btn_undo_anchor = tk.LEFT
                    self.btn_redo_anchor = tk.LEFT
                    self.show_btns()
                    self.dict_off()
        except Exception as e:
            print("Error in off_arrow_mode: {}".format(e))
    
    def arrow_key_move(self, event):
        try:
            if self.arrow_key_mode:
                if event.keysym == "Left":
                    self.previous_unknown()
                elif event.keysym == "Right":
                    self.next_unknown()
        except Exception as e:
            print("Error in arrow_key_move: {}".format(e))
    
    def hide_btns(self):
        try:
            self.btn_next_unknown.pack_forget()
            self.btn_prev_unknown.pack_forget()
            self.btn_undo.pack_forget()
            self.btn_redo.pack_forget()
        except Exception as e:
            print("Error in hide_btns: {}".format(e))
    
    def show_btns(self):
        try:
            self.btn_next_unknown.pack(side=self.btn_next_anchor, padx=3, pady=3, anchor=tk.SE)
            self.btn_prev_unknown.pack(side=self.btn_prev_anchor, padx=3, pady=3, anchor=tk.SW)
            self.btn_undo.pack(side=self.btn_undo_anchor, padx=3, pady=3, anchor=tk.SW)
            self.btn_redo.pack(side=self.btn_redo_anchor, padx=3, pady=3, anchor=tk.SE)
        except Exception as e:
            print("Error in show_btns: {}".format(e))

#focusing for GUI, friendlier experience
    def focus_text(self, event):
        self.text.focus_set()
    
    def set_insertion(self, pos, event=None):
        if self.arrow_key_mode:
            pos = pos+"+1c"
        self.text.mark_set(tk.INSERT, pos)
        self.text.see(pos)

    def focus_out(self, event=None):
        if self.text.tag_ranges('sel'):
            self.last_select = (self.text.index("sel.first"), self.text.index("sel.last"))

    def focus_in(self, event=None):
        if self.last_select:
            self.text.tag_add("sel", self.last_select[0], self.last_select[1])
            self.text.mark_set("insert", self.last_select[0])
            self.text.see("insert")
            self.last_select = None

    def processing_event(self):
        curr_index = self.text.index(tk.INSERT)
        curr_word = self.get_curr_word(curr_index)
        if curr_word:
            suggestions = Suggester.get_suggestions(curr_word, self.spellchecker.known_words)
        if self.timer_delay:
            self.window.after_cancel(self.timer_delay)
            self.timer_delay = None

    def overload_shift(self, event):
        if event.keysym == "Up" and (event.state & 0x1):
            self.on_arrow_mode(event)
            return "break"
        elif event.keysym == "Down" and (event.state & 0x1):
            self.off_arrow_mode(event)
            return "break"
        else:
            return "break"
        
    def keypress_action(self, event):
        if event.char.isalpha():
            if self.timer_delay:
                self.window.after_cancel(self.timer_delay)
            self.timer_delay = self.window.after(self.time_delay, self.processing_event)
        if event.char in '.!?,;)("][':
            self.save_undo()
        
    def keyrelease_action(self, event):
        if self.timer_delay:
            self.window.after_cancel(self.timer_delay)
        self.timer_delay = self.window.after(self.time_delay, self.processing_event)

#bottom menu buttons, click-menu options
    def undo(self):
        try:
            self.new_undo()
        except Exception as e:
            print("Error during undo process: {}".format(e))
    
    def redo(self):
        try:
            self.new_redo()
        except Exception as e:
            print("Error during redo process: {}".format(e))

    def save_undo(self):
        try:
            text = self.text.get("1.0", tk.END)
            cursor_pos = self.text.index(tk.INSERT)
            self.undo_hist.append((text, cursor_pos))
        except Exception as e:
            print("Error in save_undo: {}".format(e))
    
    def new_undo(self, event=None):
        try:
            if self.undo_hist:
                current = (self.text.get("1.0", tk.END), self.text.index(tk.INSERT))
                self.redo_hist.append(current)
                prev = self.undo_hist.pop()
                self.text.delete("1.0", tk.END)
                self.text.insert("1.0", prev[0])
                self.text.mark_set(tk.INSERT, prev[1])
        except Exception as e:
            print("Error in new_undo: {}".format(e))
        return "break"
    
    def new_redo(self, event=None):
        try:
            if self.redo_hist:
                current = (self.text.get("1.0", tk.END), self.text.index(tk.INSERT))
                self.undo_hist.append(current)
                new = self.redo_hist.pop()
                self.text.delete("1.0", tk.END)
                self.text.insert("1.0", new[0])
                self.text.mark_set(tk.INSERT, new[1])
        except Exception as e:
            print("Error in new_redo: {}".format(e))
        return "break"

    def dict_off(self):
        try:
            self.btn_dict.pack_forget()
            self.sug_listbox.pack_forget()
        except Exception as e:
            print("Error in dict_off: {}".format(e))
    
    def dict_on(self):
        try:
            self.btn_dict.pack(side=tk.LEFT, padx=3, pady=3, anchor=tk.SW)
            self.sug_listbox.pack(side=tk.BOTTOM, padx=3,pady=3)
        except Exception as e:
            print("Error in dict_on: {}".format(e))
    
    def add_dict(self):
        try:
            curr_view = self.text.yview()
            curr_index = self.text.index(tk.INSERT)
            curr_word = self.get_cur_unknown()
            if curr_word:
                curr_lower_word = curr_word.lower()
                self.spellchecker.known_words.add(curr_lower_word)
                unknowns = []
                for word, suggestions in self.unknown_words:
                    if word.lower() != curr_lower_word:
                        unknowns.append((word, suggestions))
                self.unknown_words = unknowns
                try:
                    with open(self.spellchecker.personal_dict_file_path, 'at') as dict_file:
                        dict_file.write(curr_word+'\n')
                except IOError as e:
                    print("Error writing to dict_file: {}".format(e))
                self.highlight_unknown()
            self.text.yview_moveto(curr_view[0])
            self.text.mark_set(tk.INSERT, curr_index)
            self.text.see(curr_index)
        except Exception as e:
            print("Error in add_dict: {}".format(e))

    def ignore_unknown(self):
        if not self.highlight_indexes:
            return
        try:
            curr_view = self.text.yview()
            curr_index = self.text.index(tk.INSERT)
            curr_word_start = curr_index + " wordstart"
            curr_word_end = curr_index + " wordend"
            word = self.text.get(curr_word_start, curr_word_end)
            if word in self.unknown_words:
                self.unknown_words.remove(word)
                self.spellchecker.ignored_words.add(word)
                self.text.tag_remove("highlight", curr_word_start, curr_word_end)
                self.text.tag_remove("selected", curr_word_start, curr_word_end)
                self.highlight_unknown()
                try:
                    with open(self.spellchecker.ignored_words_file_path, 'at') as ignored_file:
                        ignored_file.write(word + '\n')
                except IOError as e:
                    print("Error writing to ignored_file: {}".format(e))
                self.highlight_unknown()
                self.text.yview_moveto(curr_view[0])
        except Exception as e:
            print("Error in ignore_unknown: {}".format(e))
    
    def ignore_all(self, event=None):
        try:
            curr_word = self.get_curr_word(self.text.index(tk.INSERT))
            if not curr_word:
                return
            self.spellchecker.ignored_words.add(curr_word)
            updated_words = []
            for word in self.unknown_words:
                if word[0] != curr_word:
                    updated_words.append(word)
            self.unknown_words = updated_words
            self.text.tag_remove("highlight", "1.0", tk.END)
            self.text.tag_remove("selected", "1.0", tk.END)
            updated_hlight = []
            for (start_index, end_index) in self.highlight_indexes:
                if self.text.get(start_index, end_index) != curr_word:
                    updated_hlight.append((start_index, end_index))
            self.highlight_indexes = updated_hlight
            self.highlight_unknown()
            try:
                with open("ign_words.txt", 'at') as ignored_file:
                    ignored_file.write(curr_word+'\n')
            except IOError as e:
                print("Error writing {} to ignored_file".format(curr_word))
        except Exception as e:
            print("Error in ignore_all: {}".format(e))

    def get_a_suggestion(self, unknown_word, suggestion):
        return lambda: self.replace_unknown(unknown_word, suggestion)

    def accept_suggestion(self):
        if self.curr_word_pos:
            try:
                word = self.text.get(self.curr_word_pos+" wordstart", self.curr_word_pos+" wordend")
                if word:
                    suggestions = Suggester.get_suggestions(word, self.spellchecker.known_words) if word else []
                    self.suggestion_menu(word, suggestions)
            except Exception as e:
                print("Error in accept_suggestion: {}".format(e))

    def replace_unknown(self, unknown_word, suggestion):
        try:
            curr_view = self.text.yview()
            curr_index = self.text.index(tk.INSERT)
            start_index = self.text.search(unknown_word, "1.0", tk.END)
            while start_index:
                end_index = self.text.index("{}+{}c".format(start_index, len(unknown_word)))
                curr_word = self.text.get(start_index, end_index)
                if curr_word == unknown_word and self.text.tag_ranges("selected"):
                    start_word = self.text.index("selected.first")
                    end_word = self.text.index("selected.last")
                    if start_index == start_word and end_index == end_word:
                        self.text.delete(start_index, end_index)
                        self.text.insert(start_index, suggestion)
                        self.update_known(unknown_word, suggestion)
                        self.curr_word_pos = None
                        break
                start_index = self.text.search(unknown_word, end_index, tk.END)
            self.text.yview_moveto(curr_view[0])
            self.text.mark_set(tk.INSERT, curr_index)
            self.text.see(curr_index)
        except Exception as e:
            print("Error in replace_unknown: {}".format(e))

    def update_known(self, prev, new):
        try:
            if prev in self.unknown_words:
                self.unknown_words.remove(prev)
            self.spellchecker.ignored_words.discard(prev)
            self.spellchecker.known_words.add(new)
            self.highlight_unknown()
        except AttributeError as e:
            print("Error in update_known")
            print("Error while updating known words: {}".format(e))

    def suggestion_menu(self, unknown_word, suggestions):
        try:
            self.menu.delete(0, tk.END)
            if suggestions:
                for suggestion in suggestions:
                    self.menu.add_command(label=suggestion, command=lambda s=suggestion: self.replace_unknown(unknown_word, s))
            else:
                self.menu.add_command(label="undetermined", command=tk.NONE)
            x = self.text.winfo_pointerx()
            y = self.text.winfo_pointery()
            self.menu.tk_popup(x,y)
        except Exception as e:
            print("Error in suggestion_menu: {}".format(e))

    def chosen_listbox(self, event):
        try:
            curr_view = self.text.yview()
            curr_index = self.text.index(tk.INSERT)
            if not self.sug_listbox.curselection():
                return
            lb_index = self.sug_listbox.curselection()[0]
            suggestion = self.sug_listbox.get(lb_index)
            (start_index, end_index) = self.highlight_indexes[self.current_unknown_index]
            self.text.delete(start_index, end_index)
            self.text.insert(start_index, suggestion)
            self.update_known(self.text.get(start_index, "{}+{}c".format(
                start_index, len(suggestion)
            )), suggestion)
            self.text.yview_moveto(curr_view[0])
            self.text.mark_set(tk.INSERT, curr_index)
            self.text.see(curr_index)
            self.next_unknown()
            self.add_listbox()
        except Exception as e:
            print("Error in chosen_listbox: {}".format(e))

    def add_listbox(self):
        try:
            self.sug_listbox.delete(0, tk.END)
            if self.current_unknown_index<(len(self.unknown_words)):
                unknown = self.unknown_words[self.current_unknown_index]
                if isinstance(unknown, tuple) and len(unknown) == 2:
                    (curr_word, suggestions) = unknown
                    for suggestion in suggestions:
                        self.sug_listbox.insert(tk.END, suggestion)
        except Exception as e:
            print("Error in add_listbox: {}".format(e))

    def show_menu(self, event):
        try:
            curr_index = self.text.index(tk.CURRENT)
            word = self.text.get(curr_index + " wordstart", curr_index + " wordend")
            r_move_insert = self.text.index("@%d, %d"%(event.x, event.y))
            self.text.mark_set(tk.INSERT, r_move_insert)
            if "highlight" in self.text.tag_names(curr_index) and word and word in self.unknown_words:
                self.curr_word_pos = curr_index
                self.text.tag_remove("selected", "1.0", tk.END)
                self.text.tag_add("selected", curr_index + " wordstart", curr_index + " wordend")
                self.text.tag_config("selected", background="CadetBlue1")
                menu = tk.Menu(self.text, tearoff=1)
                menu.add_command(label="Ignore", command=self.ignore_unknown)
                menu.add_command(label="Get Suggestion", command=self.accept_suggestion)
                menu.add_command(label="+Personal Dict", command=self.personal_dict)
                menu.post(event.x_root, event.y_root)
        except Exception as e:
            print("Error in show_menu: {}".format(e))

    def autofix_lang(self, typed_lang):
        try:
            lang = process.extractOne(typed_lang, LANGUAGES.values())
            if lang:
                lang_name = lang[0]
            else:
                None
            for lang_key, name in LANGUAGES.items():
                if name == lang_name:
                    return lang_key
            return 'en'
        except Exception as e:
            print("Error in autofix_lang: {}".format(e))

    def translate(self, event=None):
        try:
            self.lang_entry.pack(side=tk.TOP, fill=tk.X,padx=3,pady=3)
            self.btn_close_trans.pack(side=tk.BOTTOM, fill=tk.X,pady=3)
            self.translate_mode = True
            if not self.text.tag_ranges("sel"):
                return "break"
            selected = self.text.get("sel.first", "sel.last")
            typed_lang = self.lang_entry.get().lower()
            if not typed_lang:
                return "break"
            lang_key = self.autofix_lang(typed_lang)
            if lang_key:
                trans_text = self.translator.translate(selected, dest=lang_key).text
                if trans_text:    
                    self.text.delete("sel.first", "sel.last")
                    self.text.insert("insert", trans_text)
            self.text.focus_set()
            return "break"
        except Exception as e:
            print("Error during translation")
            print("Error in translate: {}".format(e))
    
    def open_trans(self, event=None):
        try:
            self.lang_entry.pack(side=tk.TOP, fill=tk.X, padx=3,pady=3)
            self.btn_translate.pack(side=tk.TOP, padx=3,pady=3)
            self.btn_close_trans.pack(side=tk.BOTTOM, pady=3)
            self.lang_entry.focus_set()
        except Exception as e:
            print("Error in open_trans: {}".format(e))

    def close_trans(self):
        try:
            self.lang_entry.pack_forget()
            self.btn_close_trans.pack_forget()
            self.btn_translate.pack_forget()
            self.translate_mode=False
        except Exception as e:
            print("Error in close_trans: {}".format(e))

#word handling for highlighting, etc.
    def get_curr_word(self, curr_index):
        try:
            start_word = self.text.search(r'\m', curr_index,backwards=True,regexp = True)
            end_word = self.text.search(r'\M', curr_index, regexp=True)
            if start_word and end_word:
                return self.text.get(start_word, end_word)
            return None
        except Exception as e:
            print("Error in get_curr_word: {}".format(e))

    def get_cur_unknown(self):
        try:
            if not self.unknown_words or (self.current_unknown_index>=len(self.unknown_words)):
                return None
            return self.unknown_words[self.current_unknown_index][0]
        except Exception as e:
            print("Error in get_cur_unknown: {}".format(e))

    def next_unknown(self):
        try:
            if self.highlight_indexes:
                self.text.tag_config("highlight", background="yellow")
                self.initial = False
            else:
                self.text.tag_config("selected", background="CadetBlue1")
            if self.highlight_indexes:
                self.text.tag_remove("selected", "1.0", tk.END)
                self.current_unknown_index = (self.current_unknown_index+1) % (len(self.highlight_indexes))
                self.add_listbox()
                (start_index, end_index) = self.highlight_indexes[self.current_unknown_index]
                self.text.see(start_index)
                self.set_insertion(start_index)
                for index, (start, end) in enumerate(self.highlight_indexes):
                    if index != self.current_unknown_index:
                        self.text.tag_add("highlight", start, end)
                self.text.tag_add("selected", start_index, end_index)
                self.text.tag_config("selected", background="CadetBlue1")
                self.text.tag_config("highlight", background="yellow")
        except Exception as e:
            print("Error in next_unknown: {}".format(e))
            
    def previous_unknown(self):
        try:
            if self.highlight_indexes:
                self.text.tag_remove("selected", "1.0", tk.END)
                self.current_unknown_index = (self.current_unknown_index-1)%(len(self.highlight_indexes))
                (start_index, end_index) = self.highlight_indexes[self.current_unknown_index]
                self.text.see(start_index)
                self.set_insertion(start_index)
                self.text.tag_remove("highlight", "1.0", tk.END)
                for index, (start, end) in enumerate(self.highlight_indexes):
                    if index != self.current_unknown_index:
                        self.text.tag_add("highlight", start, end)
                self.text.tag_add("selected", start_index, end_index)
                self.text.tag_config("selected", background="CadetBlue1")
                self.text.tag_config("highlight", background="yellow")
            self.add_listbox()
        except Exception as e:
            print("Error in previous_unknown: {}".format(e))

    def hlight_word(self, word, line_start, now_known_indexes):
        try:
            match = re.search(r'\b{}\b'.format(re.escape(word)), self.text.get(line_start, line_start+"lineend"))
            if match:
                start_pos = "{}+{}c".format(line_start, match.start())
                end_pos = "{}+{}c".format(line_start, match.end())
                self.text.tag_add("highlight", start_pos, end_pos)
                now_known_indexes.append((start_pos, end_pos))
                if (word.lower() not in self.unknown_words) and (word not in self.unknown_words):
                    self.unknown_words.append(word.lower())
        except Exception as e:
            print("Error in hlight_word: {}".format(e))

    def highlight_unknown(self):
        try:
            curr_time = time.time()
            if self.arrow_key_mode and (curr_time-self.arrow_last_time>self.arrow_time_reset):
                self.arrow_key_mode = False
            if not self.arrow_key_mode:
                curr_index = self.text.index(tk.INSERT)
                curr_line_num = int(curr_index.split('.')[0])
                self.text.tag_remove("highlight", "1.0", tk.END)
                now_known_indexes = []
                punctuation_mark = True
                for line_num in range(1, int(self.text.index(tk.END).split('.')[0])+1):
                    line_start= "{}.0".format(line_num)
                    line_end= "{}.end".format(line_num)
                    line_text = self.text.get(line_start, line_end)
                    for match in re.finditer(r'\b[a-zA-Z]+\b', line_text):
                        word=match.group()
                        lower_word = word.lower()
                        exclusions = word.istitle() and lower_word in self.spellchecker.known_words
                        capital_known_word = (word.isupper() or (
                            word.istitle() and not punctuation_mark)) and lower_word in self.spellchecker.known_words
                        start_pos = "{}+{}c".format(line_start, match.start())
                        end_pos = "{}+{}c".format(line_start, match.end())
                        if not exclusions and not capital_known_word:
                            if (lower_word not in self.spellchecker.known_words) and (
                                lower_word not in self.spellchecker.ignored_words):
                                self.text.tag_add("highlight", start_pos, end_pos)
                                now_known_indexes.append((start_pos, end_pos))
                                if lower_word not in self.unknown_words:
                                    self.unknown_words.append(lower_word)
                        punctuation_mark = re.match(r".*[.!?;]$", line_text[:match.end()])
                    self.highlight_indexes = now_known_indexes
                    self.current_unknown_index = len(self.highlight_indexes)-1
                    self.text.tag_config("highlight", background="yellow")
                    self.set_insertion("1.0")
                    self.text.tag_bind("highlight", "<Button-1>", self.show_menu)
        except Exception as e:
            print("Error in highlight_unknown: {}".format(e))

    def get_next_unknown_start(self, from_index):
        try:
            next_index = self.text.search(r'\b[a-zA-Z]+\b', from_index, tk.END, regexp=True)
            while next_index:
                if self.text.get(next_index + " wordstart", next_index + " wordend") in self.unknown_words:
                    return next_index
                next_index = self.text.index(next_index + " wordend")
                next_index = self.text.search(r'\b[a-zA-Z]+\b', next_index + " +1c", tk.END, regexp=True)
            return None
        except Exception as e:
            print("Error in get_next_unknown_start: {}".format(e))

#personal dictionary file
    def personal_dict(self):
        try:
            curr_view = self.text.yview()
            curr_index = self.text.index(tk.INSERT)
            if self.curr_word_pos:
                new_word = self.text.get(self.curr_word_pos+" wordstart",self.curr_word_pos+" wordend")
                if new_word:
                    new_word = new_word.strip()
                    if new_word and (new_word not in self.spellchecker.known_words):
                        self.spellchecker.known_words.add(new_word)
                        self.text.tag_remove("highlight", self.curr_word_pos+" wordstart", self.curr_word_pos+" wordend")
                        self.text.tag_remove("selected", self.curr_word_pos+" wordstart", self.curr_word_pos+" wordend")
                        try:
                            with open(self.spellchecker.personal_dict_file, 'rt') as personal_dict_file:
                                if new_word not in personal_dict_file:
                                    with open(personal_dict_file_path, 'at') as personal_dict_file:
                                        personal_dict_file.write(new_word+'\n')
                        except IOError as e:
                            print("Error reading personal_dict: {}".format(e))
                        self.highlight_unknown()
                        self.text.yview_moveto(curr_view[0])
                        self.text.mark_set(tk.INSERT, curr_index)
                        self.text.see(curr_index)
        except Exception as e:
            print("Error in personal_dict: {}".format(e))

#application loop, command line
if __name__ == "__main__":
    
    default_folder = os.path.dirname(os.path.abspath(__file__))
    default_words_file = os.path.join(default_folder, "words.txt")
    default_ignored_file = os.path.join(default_folder, "ign_words.txt")
    default_personal_dict_file = os.path.join(default_folder, "pers_dict.txt")
    default_txt_example_file = os.path.join(default_folder, "example.txt")

    parser = argparse.ArgumentParser(description="Start the Application")
    parser.add_argument("--words", type=str, default=default_words_file, help="Path to known words file")
    parser.add_argument("--ignored", type=str, default=default_ignored_file, help="Path to ignored words file")
    parser.add_argument("--pd", type=str, default=default_personal_dict_file, help="Path to personal dictionary file")
    parser.add_argument("--ex", type=str, default=default_txt_example_file, help="Path to example text file")
    args = parser.parse_args()

    def load_files(file_path):
        try:
            if os.path.isfile(file_path):
                with open(file_path, 'rt') as file:
                    return set(file.read().splitlines())
            else:
                print("File: '{}' not found".format(file_path))
                return set()
        except IOError as e:
            print("Error reading the file-{}: {}".format(file_path,e))
            return set()
            

    known_words_file_path = args.words
    personal_dict_file_path = args.pd
    ign_words_file_path = args.ignored

    try:
        with open(args.ex, 'rt') as example_text_file:
            example_text = example_text_file.read()
    except IOError as e:
        print("Error reading example txt file: {}".format(e))
        example_text = ""

    reference_file = TextFile(example_text)
    window = tk.Tk()
    spellchecker = Spellchecker(reference_file,known_words_file_path,personal_dict_file_path, ign_words_file_path)
    spellchecker.ignored_words = load_files(ign_words_file_path)
    app = SpellcheckerApp(window, spellchecker)
    window.mainloop()

###phrase entry, personal-use###
#python "C:\Users\cb6f1\OneDrive\Desktop\Project\spellchecker\spellchecker.py"
# --words "C:\Users\cb6f1\OneDrive\Desktop\Project\spellchecker\words.txt"
# --pd "C:\Users\cb6f1\OneDrive\Desktop\Project\spellchecker\personal_dict.txt"
# --ignored "C:\Users\cb6f1\OneDrive\Desktop\Project\spellchecker\ign_words.txt"

