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
        words_to_check = []
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
    """
    Subclass of ReferenceFile, specifically for handling and parsing HTML content.
    
    Parses HTML content, extracting text with Beautiful Soup
    """
    def __init__(self, text):
        """
        Initializes parent class with HTML content, to be parsed
        
        Arguments:
        -text (str): string containing HTML content
        """
        super().__init__(text)
    def parse(self):
        """
        Parses HTML content, extracting text, returning list of words.
        
        Uses BeautifulSoup for HTML parsing
        
        Returns:
        -list: list of strings, which are words from HTML content
        """
        soup = BeautifulSoup(self.text, "lxml")
        html_content = soup.get_text()
        return html_content.split()

#subclass parsing
class PDFFile(ReferenceFile):
    """
    Subclass of ReferenceFile, specifically for handling and parsing PDF content.
    
    Parses PDF content, extracting text with fitz
    """
    def __init__(self, file_path):
        """
        Initializes instance of PDFFile, with file path to PDF file.
        
        Arguments:
        -file_path (str): file path to PDF file
        """
        super().__init__(None)
        self.file_path = file_path
    def parse(self):
        """
        Opens PDF file, extracting text from each page, combining it into one string.
        
        Returns:
        str: combined text from PDF file
        """
        with fitz.open(self.file_path) as document:
            content = ""
            for page in document:
                content += page.get_text()
        return content

#subclass parsing
class DocxFile(ReferenceFile):
    """
    Subclass of ReferenceFile, specifically for handling and parsing content
    from .docx files.
    
    Initialized with content from .docx file, and then parses and extracts text
    from it.
    """
    def __init__(self, text):
        """
        Initializes instance of DocxFile, with file path to a .docx file.
        
        Arguments:
        -file_path (str): file path to .docx file
        """
        super().__init__(text)
    def parse(self):
        """
        Opens .docx file, extracting text from each paragraph into single list.
        
        Returns:
        -list: list of words from .docx file
        """
        return self.text.split()

#'the' GUI
class SpellcheckerApp:
    """
    'The' GUI. The SpellcheckerApp class integrates the functions of a spellchecker
     and text editor, while also providing the ability for translation. It is an
     interactive application, in which a user can open files, edit them, and check
     for misspellings.
    
    Attributes:
    -window (tk.Tk): main application window
    -frm (tk.Frame): main frame widget for other widgets
    -text (tk.Text): main text widget for the display and edit of textual file content
    -sug_listbox (tk.Listbox): listbox widget for displaying suggestions for
     misspelled words (non-interactive)
    -lang_entry (tk.Entry): entry widget to input language for translation feature
    -btn_next_unknown (tk.Button): button to move to next unknown word in text
    -btn_prev_unknown (tk.Button): button to move to previous unknown word in text
    -btn_undo (tk.Button): button for undo text feature
    -btn_redo (tk.Button): button for redo text feature
    -btn_translate (tk.Button): button, triggers translation of currently highlighted text
    -btn_close_trans (tk.Button): button, closes translation feature
    -btn_ignore (tk.Button): button to ignore spelling suggestion for current word
    -btn_dict (tk.Button): button to add current word to personal dictionary
    -top_menu (tk.Menu): top menu of application, which provides file and tools options
    -file_menu (tk.Menu): a menu in top menu for file options (open, save, save as)
    -tool_menu (tk.Menu): a menu in top menu for tool options (translate, spellcheck)
    -spellchecker (Spellchecker): initialized Spellchecker object, referenced for
     spellchecking capabilities
    -unknown_words (list): list of words identified as unknown by spellchecker
    -undo_hist (list): list of history of actions by user in modification of text;
     used for undo feature
    -redo_hist (list): list of history of actions by user in modification of text;
     used for redo feature
    -initial (bool): a flag, initially set tot True, tracking initial state of application
    -current_unknown_index (int): index to track current word, in unknown words
     list, being modified
    -highlight_indexes (tuple list): list with start and end index positions of
     the highlighted words in the text
    -previous_highlight (str or None): the previous highlighted word
    -arrow_key_mode (bool): a flag that checks whether arrow mode is activated, initially
     set to False
    -arrow_last_time (float): the time at which the arrow key was last pressed, used for
     activation purposes
    -arrow_time_reset (int): time duration required to pass without activation of arrow mode
     in order for press count to reset
    -arrow_key_count (int): counts arrow key presses, allowing for activation of arrow mode
    -arrow_key_req (int): number of arrow key presses required to activate arrow mode
    -last_select (str/None): last selected word
    -curr_word_pos (tuple/None): current position of word being modified
    -timer_delay (int/None): stored time for delayed actions
    -time_delay (int): time for delay, before given action triggered
    -menu (tk.Menu): pop-up menu, providing modification options for word under cursor
    -working_file (str): path of currently opened text file
    -translator (Translator): object of Translator class; used for translation feature

    Arguments:
    -window (tk.Tk): Tkinter window
    -spellchecker (Spellchecker): initialized Spellchecker object

    Methods: (too many!)
    -handles interactions between attributes
    """
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
        """
        Refreshes the spellchecking, highlighting, and suggestion display
        for the application. Optionally, can make application real-time spellchecker,
        however, it excessively slows program down. It is applicable, currently, 
        to only system-highlighted text.

        Arguments:
        -event (Event, optional): a given event that triggers the function.
         Defaulted to None.

        Required:
        -A correct Tkinter text widget to be initialized as self.text

        Returns:
        -Nothing

        -If no text is selected, currently, nothing happens        
        """
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
        """
        Opens a given file, updates reference file type for parsing and extraction.
        
        Required:
        -file_to_open must be a string, with a supported file type
        
        Arguments:
        -fill_to_open: a string of file path to be opened and read
        
        Returns:
        -Nothing
        
        -If file ends with .txt, read as plain text
        -If file ends with .html or .htm, read as HTML
        -If file ends with .pdf, read as PDF
        -If file ends with .docx, read as .docx file (read, lines joined)
        -If file ends with something else, error message printed
        """
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
        """
        Updates window text area. It clears existing text, inserting the new
        file content, and updates the spellchecker's reference file text.
        
        Arguments:
        -text_content (str): text content to be inserted into window text widget
        
        Required:
        -text_content must be a string, which is the content of a given file

        Returns:
        -Nothing
        """
        if text_content:
            self.window.after(0, self.text.delete, "1.0", tk.END)
            self.window.after(0, self.text.insert, tk.END, text_content)
            self.spellchecker.reference_file.text = text_content

    def open_file_two(self, event=None):
        """
        Opens the file dialog for the user to select a file. Opens the file
        on a separate thread, for efficiency.
        
        Arguments:
        -event (Event, optional): event that triggers the method. Defaulted
         to None.
         
        Required:
        -filedialog module must be imported successfully
        -threading module must be imported successfully
         
        Returns:
        -str: returns string "break" to stop event from triggering other methods

        -Shows user file dialog, without exiting the program
        """
        file_to_open = filedialog.askopenfilename()
        if file_to_open:
            threading.Thread(target=self.open_file_one, args=(file_to_open,), daemon=True).start()
        return "break"
    
    def title(self, title):
        """
        Sets the title of the window with a string.
        
        Arguments:
        -title (str): new title for window
        
        Returns:
        -Nothing
        """
        self.window.title("{}".format(title))

#other options for handling file
    def save_file(self, event=None):
        """
        Saves current text, in self.working_file, to system. Updates title
        of the window after successfully saving.

        Arguments:
        -event (Event, optional): event that triggers the save feature.
         Defaulted to None.
        
        Returns:
        -None
        
        -If not already saved into system, it calls self.save_as.
        -If already saved into system, it overwrites the former state of text.
        """
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
        """
        Prompts user to select file path for saving current state of text in
        window. Makes use of file dialog, with file format not defaulted.
        After successful save, window name is updated.
        
        Arguments:
        -event (Event, optional): event that triggers save-as feature.
         Defaulted to None.
         
        Returns:
        -None
        """
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
        """
        Uses keyboard event to toggle on arrow mode. Checks whether mode is
        currently active, before moving forward. If off, will work. Dependent on
        number of times arrow key (up) is pressed. Upon reaching threshold (x3),
        arrow mode is activated. Afterward, the count is reset. Disables/forgets
        NEXT, PREVIOUS, UNDO, and REDO buttons. Activates +DICTIONARY button.
        
        Arguments:
        -event (Event): event containing information about key presses
        
        Returns:
        -None
        """
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
        """
        Uses keyboard event to toggle off arrow mode. Checks whether mode is
        currently active, before moving forward. If on, will work. Dependent on
        number of times arrow key (down) is pressed. Upon reaching threshold (x3),
        arrow mode is deactivated. Afterward, the count is reset. Activates
        NEXT, PREVIOUS, UNDO, and REDO buttons. Deactivates/forgets +DICTIONARY button.
        
        Arguments:
        -event (Event): event containing information about key presses
        
        Returns:
        -None
        """
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
        """
        Handles arrow key movement (left/right), when arrow mode is activated.
        When the left arrow is pressed, self.previous_unknown() is triggered.
        When the right arrow is pressed, self.next_unknown() is triggered. It
        allows for the navigation between unknown words, highlighting the current
        word a different color from the rest.
        
        Arguments:
        -event (Event): event which includes key press event information
        
        Returns:
        -None
        """
        try:
            if self.arrow_key_mode:
                if event.keysym == "Left":
                    self.previous_unknown()
                elif event.keysym == "Right":
                    self.next_unknown()
        except Exception as e:
            print("Error in arrow_key_move: {}".format(e))
    
    def hide_btns(self):
        """
        Hides the NEXT, PREVIOUS, UNDO, and REDO buttons when triggered.
        Is initially disabled, but is enabled when arrow mode is activated.
        
        Arguments:
        -None
        
        Returns:
        -None
        """
        try:
            self.btn_next_unknown.pack_forget()
            self.btn_prev_unknown.pack_forget()
            self.btn_undo.pack_forget()
            self.btn_redo.pack_forget()
        except Exception as e:
            print("Error in hide_btns: {}".format(e))
    
    def show_btns(self):
        """
        Displays the NEXT, PREVIOUS, UNDO, and REDO buttons when activated.
        Initially enabled upon start. Disabled upon the activation of arrow mode.
        
        Arguments:
        -None
        
        Returns:
        -None
        """
        try:
            self.btn_next_unknown.pack(side=self.btn_next_anchor, padx=3, pady=3, anchor=tk.SE)
            self.btn_prev_unknown.pack(side=self.btn_prev_anchor, padx=3, pady=3, anchor=tk.SW)
            self.btn_undo.pack(side=self.btn_undo_anchor, padx=3, pady=3, anchor=tk.SW)
            self.btn_redo.pack(side=self.btn_redo_anchor, padx=3, pady=3, anchor=tk.SE)
        except Exception as e:
            print("Error in show_btns: {}".format(e))

#focusing for GUI, friendlier experience
    def focus_text(self, event):
        """
        Sets focus in the application to the text widget.
        
        Arguments:
        -event (Event): event that triggers method. 
        
        Returns:
        -None
        """
        self.text.focus_set()
    
    def set_insertion(self, pos, event=None):
        """
        Adjusts the position of the insertion point in the text if arrow
        mode is currently active. It moves the point one character forward.
        
        Arguments:
        -pos (str): new position index for insertion point in text
        -event (Event, optional): event that triggers this method. Defaulted
         to None.
        
        Returns:
        -None
        """
        if self.arrow_key_mode:
            pos = pos+"+1c"
        self.text.mark_set(tk.INSERT, pos)
        self.text.see(pos)

    def focus_out(self, event=None):
        """
        Remembers selection range of text, given that focus is lost from the text
        
        Arguments:
        -event (Event, optional): event that triggered focus-out action. Defaulted
         to None
        
        Returns:
        -None
        """
        if self.text.tag_ranges('sel'):
            self.last_select = (self.text.index("sel.first"), self.text.index("sel.last"))

    def focus_in(self, event=None):
        """
        Restores selection range of text, when focus is regained to text. Works
        in parallel with the focus_out function.
        
        Arguments:
        -event (Event, optional): event that triggered focus-in action. Defaulted
         to None.
        
        Returns:
        -None
        """
        if self.last_select:
            self.text.tag_add("sel", self.last_select[0], self.last_select[1])
            self.text.mark_set("insert", self.last_select[0])
            self.text.see("insert")
            self.last_select = None

    def processing_event(self):
        """
        Gets current word at the cursor for suggestions. Fixed some bug
        in other functions.
        
        Arguments:
        -None
        
        Returns:
        -None
        """
        curr_index = self.text.index(tk.INSERT)
        curr_word = self.get_curr_word(curr_index)
        if curr_word:
            suggestions = Suggester.get_suggestions(curr_word, self.spellchecker.known_words)
        if self.timer_delay:
            self.window.after_cancel(self.timer_delay)
            self.timer_delay = None

    def overload_shift(self, event):
        """
        Handles events that involve pressing the Shift key, disabling normal
        system shortcuts. Arrow mode is activated through the pressing of
        the 'up' arrow (x3), while holding the Shift key. Arrow mode is 
        deactivated through the pressing of the 'down' arrow (x3), while
        holding the Shift key.
        
        Arguments:
        -event (Event, optional): Tkinter event object gets information of
         key press event.
        
        Returns:
        -"break" (str): preventing the trigger of other functions with given
         keyboard event.
         """
        if event.keysym == "Up" and (event.state & 0x1):
            self.on_arrow_mode(event)
            return "break"
        elif event.keysym == "Down" and (event.state & 0x1):
            self.off_arrow_mode(event)
            return "break"
        else:
            return "break"
        
    def keypress_action(self, event):
        """
        Allows for a more custom undo feature, saving individual histories up
        until certain punctuation, in addition to discrete changes in the text.

        Arguments:
        -event (Event): Tkinter event object, captures keypress event

        Returns:
        -None
        """
        if event.char.isalpha():
            if self.timer_delay:
                self.window.after_cancel(self.timer_delay)
            self.timer_delay = self.window.after(self.time_delay, self.processing_event)
        if event.char in '.!?,;)("][':
            self.save_undo()
        
    def keyrelease_action(self, event):
        """
        When user stops typing, the current state of the text is saved. Works
        in parallel with the keypress_action function. Additionally, uses a timer
        to automatically save current text state into the undo feature.
        
        Arguments:
        -event (Event, optional): Tkinter event object that passes information into
         the binding system for key releases. Defaulted to None.
         
        Returns:
        -None
        """
        if self.timer_delay:
            self.window.after_cancel(self.timer_delay)
        self.timer_delay = self.window.after(self.time_delay, self.processing_event)

#bottom menu buttons, click-menu options
    def undo(self):
        """
        Performs an undo action. Reverts the current state of text, back to
        a previous point in the history list.
        
        Arguments:
        -None
        
        Returns:
        -None
        """
        try:
            self.new_undo()
        except Exception as e:
            print("Error during undo process: {}".format(e))
    
    def redo(self):
        """
        Performs a redo action. Reverts the current state of text, back to
        a previous point in the history list (given that the undo function
        was run).
        
        Arguments:
        -None
        
        Returns:
        -None
        """
        try:
            self.new_redo()
        except Exception as e:
            print("Error during redo process: {}".format(e))

    def save_undo(self):
        """
        Saves the current state of text, with the cursor position, for use 
        in the undo function.
        
        Arguments:
        -None
        
        Returns:
        -None

        -Appends new states into the undo_hist function
        """
        try:
            text = self.text.get("1.0", tk.END)
            cursor_pos = self.text.index(tk.INSERT)
            self.undo_hist.append((text, cursor_pos))
        except Exception as e:
            print("Error in save_undo: {}".format(e))
    
    def new_undo(self, event=None):
        """
        Reverts the text widget to a previous state, as recorded in the undo
        history. Places cursor back at previous position as well. Updates both
        undo_hist and redo_hist.
        
        Arguments:
        -event (Event, optional): takes in event information. Defaulted to None.

        Returns:
        -"break" (str): prevents events from triggering functions outside of current
        """
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
        """
        Restores the text widget to most recent saved-state in the redo history.
        Can redo up until last discrete change. Additionally saves the position
        of cursor from redo history.
        
        Arguments:
        -event (Event, optional): event object passed by the Tkinter binding
         (redo function). Defaulted to None.

        Returns:
        -"break" (str): to stop the event from triggering functions outside of the
         current.
        """
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
        """
        Hides the +Dictionary button and listbox from the window layout.

        Arguments:
        -None

        Returns:
        -None
        """
        try:
            self.btn_dict.pack_forget()
            self.sug_listbox.pack_forget()
        except Exception as e:
            print("Error in dict_off: {}".format(e))
    
    def dict_on(self):
        """
        Shows the +Dictionary and listbox on the window layout.
        
        Arguments:
        -None
        
        Returns:
        -None
        """
        try:
            self.btn_dict.pack(side=tk.LEFT, padx=3, pady=3, anchor=tk.SW)
            self.sug_listbox.pack(side=tk.BOTTOM, padx=3,pady=3)
        except Exception as e:
            print("Error in dict_on: {}".format(e))
    
    def add_dict(self):
        """
        Adds the current unknown word, at the mouse cursor, to a collection
        of known words in the spellchecker. Updates the personal dictionary, and
        refreshes text highlights. The current y-view, as well as the insertion
        point is stored, allowing for no apparent program change.
        
        Arguments:
        -None
        
        Returns:
        -None
        
        -modifies spellchecker known words set
        -modifies unknown words list
        """
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
        """
        Adds the current unknown word, at the mouse cursor, to the ignored words
        set. Removes word from list of unknown words, and refreshes text highlights.
        Stores y-view and cursor position to make it seem as if there was no program
        change.
        
        Arguments:
        -None
        
        Returns:
        -None
        
        -removes word from unknown words list
        -adds word to spellchecker ignored words set
        -writes to ignored words file
        """
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
        """
        Ignores all instances, within the text, of the unknown word at the
        current cursor position. Updates ignored words file to include given word.
        Refreshes text highlights. Stores y-view and cursor position to make it
        seem as if there was no apparent program change.
        
        Arguments:
        -event (Event, optional): a triggering event. Defaulted to None.
        
        Returns:
        -None
        
        -adds current unknown word to spellchecker ignored words
        -removes ignored word from unknown words
        -writes ignored word to ign_words file
        """
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
        """
        Replaces current unknown word with a suggestion, calling on the
        replace_unknown function
        
        Arguments:
        -unknown_word (str): string of word to be replaced
        -suggestion (str): string of suggested replacement for unknown_word
        """
        return lambda: self.replace_unknown(unknown_word, suggestion)

    def accept_suggestion(self):
        """
        Displays suggestion menu with correction options for currently selected word,
        at the cursor position. Gets suggestions from the Suggester class, showing
        them with the suggestion_menu function, inside of the show_menu function.

        Arguments:
        -None

        Returns:
        -None
        """
        if self.curr_word_pos:
            try:
                word = self.text.get(self.curr_word_pos+" wordstart", self.curr_word_pos+" wordend")
                if word:
                    suggestions = Suggester.get_suggestions(word, self.spellchecker.known_words) if word else []
                    self.suggestion_menu(word, suggestions)
            except Exception as e:
                print("Error in accept_suggestion: {}".format(e))

    def replace_unknown(self, unknown_word, suggestion):
        """
        Replaces current instance of unknown word with a suggestion, if called.
        Stores y-view and cursor position to make it seem as if there was no
        apparent change in the program.
        
        Arguments:
        -unknown_word (str): a string in text, marked as unknown
        -suggestion (str): a string to replace the unknown_word
        
        Returns:
        -None
        """
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
        """
        Updates known words set to include current word, while also
        removing the word from the unknown words list. Refreshes highlights
        for unknown words, highlighting all current unknown words.

        Arguments:
        -prev (str): unknown word to be updated
        -new (str): previously unknown word, now excluded from further checks

        Returns:
        -None
        """
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
        """
        Displays a menu with three options for word suggestions, which are
        similarly spelled as the unknown word. Selecting such a word will replace
        the unknown word.
        
        Arguments:
        -unknown_word (str): word in text marked as misspelled
        -suggestions (str list): list of suggestions for replacement of unknown_word
        
        Returns:
        -None
        """
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
        """
        *Selection is currently disabled, but left for future use*. Handles the
        event in which the user chooses a suggestion from the listbox to replace
        a current, unknown word. Only available while in arrow mode. Updates with
        navigation, showing three suggestions for currently selected word. Stores
        y-view and cursor position so that it seems as if there is no apparent
        change in the program upon refreshing.
        
        Arguments:
        -event (Event, optional): Tkinter event that triggered function. Defaulted
         to None.
        
        Returns:
        -None
        """
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
        """
        Populates the listbox, which only appears in arrow mode, with three
        suggestions for the currently unknown word. The said suggestions are
        words that are similarly spelled as the unknown word. Suggestions change
        with navigation while in arrow mode.

        Arguments:
        -None

        Returns:
        -None

        -listbox display for unknown words are stored as tuples, with list of suggestions
         ex. (word, [suggestions])
        -handles event in which there are no unknown words, wiping clean the listbox
        """
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
        """
        Displays menu when user right clicks on an unknown word in text. The
        menu options include 'ignore', 'get suggestions', and '+personal dict'.

        Arguments:
        -event (Event, optional): event object, containing x- and y-coordinates
         of mouse click, allowing for a correct placement of menu. Defaulted to None.

        Returns:
        -None
        """
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
        """
        Finds best match (of language, using fuzzywuzzy library) for string typed
        into entry box, returning determined language code from LANGUAGES dictionary.
        If no viable match can be found, the function defaults to English, showing
        no change in the text.

        Arguments:
        -typed_lang (str): name of language typed by the user

        Returns:
        -str: string of language code that best matches typed_lang; defaulted to 'en'
        """
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
        """
        Translates the currently selected text (system-highlighted) in the text
        widget to the language entered into the entry widget. The library used
        for translated is googletrans. After translation is completed, the selected
        text will be replaced with the translated text.

        Arguments:
        -event (Event, optional): event object passed by the Tkinter event binding.
         Defaulted to None.

        Returns:
        -"break" (str): prevents any further binding on the event from being processed
        """
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
        """
        Sets up interface for translation. Shows TRANSLATE and CLOSE TRANSLATE
        buttons, shows entry bar for typing intended language.
        
        Arguments:
        -event (Event, optional): event object passed by Tkinter event handling.
         Defaulted to None.
         
        Returns:
        -None
        """
        try:
            self.lang_entry.pack(side=tk.TOP, fill=tk.X, padx=3,pady=3)
            self.btn_translate.pack(side=tk.TOP, padx=3,pady=3)
            self.btn_close_trans.pack(side=tk.BOTTOM, pady=3)
            self.lang_entry.focus_set()
        except Exception as e:
            print("Error in open_trans: {}".format(e))

    def close_trans(self):
        """
        Hides the TRANSLATE and CLOSE TRANSLATE buttons, as well as the 
        entry bar, when called.
        
        Arguments:
        -None
        
        Returns:
        -None
        """
        try:
            self.lang_entry.pack_forget()
            self.btn_close_trans.pack_forget()
            self.btn_translate.pack_forget()
            self.translate_mode=False
        except Exception as e:
            print("Error in close_trans: {}".format(e))

#word handling for highlighting, etc.
    def get_curr_word(self, curr_index):
        """
        Gets current word, located at the specified index in the text widget.
        (Strictly only that word, as specified by the regex word pattern).
        
        Arguments:
        -curr_index (str): a string for the current index in the text
        
        Returns:
        -Word at current index, as a string, else None
        """
        try:
            start_word = self.text.search(r'\m', curr_index,backwards=True,regexp = True)
            end_word = self.text.search(r'\M', curr_index, regexp=True)
            if start_word and end_word:
                return self.text.get(start_word, end_word)
            return None
        except Exception as e:
            print("Error in get_curr_word: {}".format(e))

    def get_cur_unknown(self):
        """
        Gets current unknown word from collection of unknown words, based on index.

        Arguments:
        -None

        Returns:
        -current unknown word (str), else None
        """
        try:
            if not self.unknown_words or (self.current_unknown_index>=len(self.unknown_words)):
                return None
            return self.unknown_words[self.current_unknown_index][0]
        except Exception as e:
            print("Error in get_cur_unknown: {}".format(e))

    def next_unknown(self):
        """
        Moves to the next unknown word in the text, either through navigation
        by the NEXT button, or the right arrow key (if in arrow mode). Upon
        moving, it changes the currently selected word a different color from
        the rest of the unknown words.

        Arguments:
        -None

        Returns:
        -None

        -Completely dependent on self.highlight_indexes and self.current_unknown_index
         for features to work in text widget.
        -Responsible for updates in self.add_listbox and self.set_insertion
        """
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
        """
        Moves to the previous unknown word in the text, either through navigation
        with the PREVIOUS button, or the left arrow key (if in arrow mode). Upon
        moving, it changes the currently selected word a different color from
        the rest of the unknown words.
        
        Arguments:
        -None
        
        Returns:
        -None
        
        -Completely dependent on self.highlight_indexes and self.current_unknown_index
         for features to work in text widget.
        -Responsible for updates in self.add_listbox and self.set_insertion
        """
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
        """
        Highlights a given word in the text (by x.x position), recording its
        index. The word is added to the list of unknown words, if not already in it.
        
        Arguments:
        -word (str): word to be highlighted
        -line_start (str): text index representing start of the line
        -now_known_indexes (list): list, updated with start and end indexes
         of the word
        
        Returns:
        -None
        """
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
        """
        Checks the entire text, highlighting unknown words (words not in spellchecker's
        known words list, ignored words list). Ignores capitalization and punctuation
        when checking.
        
        Arguments:
        -None
        
        Returns:
        -None
        
        -Binds mouse clicks to highlighted words for menu pop-up
        """
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
        """
        Finds the starting index of the next unknown word, starting at a given index.
        
        Arguments:
        -from_index (str): text index from which search for next unknown word starts
        
        Returns:
        -str: index of start of next unknown word, else None
        """
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
        """
        Adds currently selected word, at the cursor position, to spellchecker's
        known words, as well as personal dictionary file. Afterward, refreshes
        view of text. Stores y-view and cursor position to make it seem as if
        there were no apparent changes in the program.

        Arguments:
        -None

        Returns:
        -None
        
        """
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

