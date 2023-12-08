
import bs4 #may not have downloaded correctly? (yellow underline)
from bs4 import BeautifulSoup
import fitz
from docx import Document
import tkinter as tk
from tkinter import filedialog
import re
import time
import Levenshtein
import threading
import os
class Spellchecker():
    def __init__(self, reference_file, known_words_file, personal_dict):
        self.reference_file = reference_file
        self.known_words = self.get_known_words(known_words_file, personal_dict)
        self.ignored_words = set()
        self.unknown_word_count = 0 #remember to print at the end
        self.unknown_words = []
        
    def spell_check(self):
        words_to_check = self.reference_file.parse() #check this phrase
        for index, word in enumerate(words_to_check):
            known = (word.lower() in self.known_words) or (word in self.known_words)
            if_start_sent = self.start_sentence(index, words_to_check)
            if not known and not (if_start_sent and word.istitle()):
                suggestions = Suggester.get_suggestions(word.lower(), self.known_words)
                self.unknown_word_count += 1
                self.unknown_words.append((word, suggestions))

    def start_sentence(self, word_index, words_to_check):
        if word_index == 0:
            return True
        prev_word = words_to_check[word_index-1]
        return prev_word[-1] in ".!?;"

    def get_known_words(self, known_words_file, personal_dict):
        known_words = set()
        with open(known_words_file, "rt") as known_file:
            known_words.update(known_file.read().split())
        with open(personal_dict, "rt") as personal_dict_file:
            known_words.update(personal_dict_file.read().split())
        return known_words

class ReferenceFile():
    def __init__(self, text):
        self.text = text
    def parse(self):
        pass #research implies is good to use, may be redundant (check later)

class Suggester():
    @staticmethod
    def get_suggestions(word, known_words): #work on this NEXT!
        suggestions = sorted(known_words, key=lambda known_word:Levenshtein.distance(word, known_word))
        return suggestions[:3]
    
    def __init__(self, known_words=None):
        self.known_words = known_words or set()
    def checker(self, word):
        if word in self.known_words:
            return True
        else:
            return False

class TextFile(ReferenceFile):
    def __init__(self, text):
        super().__init__(text)
    def parse(self):
        return re.split(r'\s', self.text.strip())

class HTMLFile(ReferenceFile): #depending on how I want command line, may
    def __init__(self, text):  #have to use a 'with open'
        super().__init__(text)
    def parse(self):
        soup = BeautifulSoup(self.text, "lxml") #may have done wrong, importing
        html_content = soup.get_text()
        return html_content.split()

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

class DocxFile(ReferenceFile):
    def __init__(self, text):
        super().__init__(text)
    def parse(self):
        return self.text.split()

class SpellcheckerApp:
    def __init__(self, window, spellchecker):
        self.window = window
        self.window.title("Spellchecker EECE2140")
        self.frm = tk.Frame(self.window)
        self.frm.pack()
        self.text = tk.Text(self.frm, wrap="word", width=80, height=30)
        self.text.pack(expand=True, fill='both', padx=30, pady=15)

        with open("example.txt", 'rt') as example_text_file:
            text_content = example_text_file.read()
            
        text_content = ' ' + text_content
        self.text.insert(tk.END, text_content)
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
        self.btn_undo.pack()
        self.btn_redo.pack()
        self.undo_hist = []
        self.redo_hist = []
        self.text.config(undo=False)
        self.spellchecker = spellchecker
        self.unknown_words = spellchecker.unknown_words
        self.text.tag_config("highlight", background="yellow")
        self.text.tag_config("selected", background="blue")
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
        self.window.bind("<Control-o>", self.open_file_two)
        self.window.bind("<Control-s>", self.save_file)
        self.window.bind("<Control-S>", self.save_as)
        self.top_menu = tk.Menu(window)
        self.file_menu = tk.Menu(self.top_menu, tearoff=0)
        self.file_menu.add_command(label = "Open", accelerator="Ctrl+O", command=self.open_file_two)
        window.config(menu=self.top_menu)
        self.top_menu.add_cascade(label = "File", menu= self.file_menu)
        self.file_menu.add_command(label="Save", accelerator="Ctrl+s", command=self.save_file)
        self.file_menu.add_command(label="Save As", accelerator="Ctrl+S", command=self.save_as)
        self.btn_ignore = tk.Button(self.frm, text="IGNORE", command=self.ignore_unknown)
        self.btn_ignore.pack(side=tk.RIGHT, padx=3, pady=3, anchor=tk.SW)
        self.btn_ignore.pack()
        self.curr_word_pos = None
        self.timer_delay = None
        self.time_delay = 500
        self.menu=tk.Menu(self.text, tearoff=0)
        self.working_file = None
        spellchecker.spell_check()
        self.highlight_unknown()

    def open_file_one(self, file_to_open):
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
        self.update_window(text_content)
        self.title(os.path.basename(file_to_open))
    
    def update_window(self, text_content):
        if text_content:
            self.window.after(0, self.text.delete, "1.0", tk.END)
            self.window.after(0, self.text.insert, tk.END, text_content)
            self.spellchecker.reference_file.text = text_content
            self.window.after(0, self.spellchecker.spell_check)
            self.window.after(0, self.highlight_unknown)

    def open_file_two(self, event=None):
        file_to_open = filedialog.askopenfilename()
        if file_to_open:
            threading.Thread(target=self.open_file_one, args=(file_to_open,), daemon=True).start()
        return "break"
    
    def title(self, title):
        self.window.title("{}".format(title))

    def save_file(self, event=None):
        if self.working_file:
            with open(self.working_file, 'wt') as save_file:
                saving_text = self.text.get("1.0", tk.END)
                save_file.write(saving_text.rstrip())
            self.title(os.path.basename(self.working_file))
        else:
            self.save_as(event)

    def save_as(self, event=None):
        save_file = filedialog.asksaveasfilename(filetypes=[("All Files", "*.*")])
        if save_file:
            with open(save_file, 'wt') as save_as_file:
                saving_text = self.text.get("1.0", tk.END)
                save_as_file.write(saving_text.rstrip())
                self.working_file = save_file
                self.title(os.path.basename(save_file))
    def on_arrow_mode(self, event):
        if not self.arrow_key_mode and (event.state & 0x1):
            self.arrow_key_count += 1
            if self.arrow_key_count >= self.arrow_key_req:
                self.arrow_key_mode = True
                self.arrow_key_count = 0
                self.btn_next_anchor = tk.SE
                self.btn_prev_anchor = tk.SW
                self.hide_btns()
    
    def off_arrow_mode(self, event):
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
    
    def hide_btns(self):
        self.btn_next_unknown.pack_forget()
        self.btn_prev_unknown.pack_forget()
        self.btn_undo.pack_forget()
        self.btn_redo.pack_forget()
    
    def show_btns(self):
        self.btn_next_unknown.pack(side=self.btn_next_anchor, padx=3, pady=3, anchor=tk.SE)
        self.btn_prev_unknown.pack(side=self.btn_prev_anchor, padx=3, pady=3, anchor=tk.SW)
        self.btn_undo.pack(side=self.btn_undo_anchor, padx=3, pady=3, anchor=tk.SW)
        self.btn_redo.pack(side=self.btn_redo_anchor, padx=3, pady=3, anchor=tk.SE)


    def arrow_key_move(self, event):
        if self.arrow_key_mode:
            if event.keysym == "Left":
                self.previous_unknown()
            elif event.keysym == "Right":
                self.next_unknown()
            else:
                pass

    def overload_shift(self, event):
        if event.keysym == "Up" and (event.state & 0x1):
            self.on_arrow_mode(event)
            return "break"
        elif event.keysym == "Down" and (event.state & 0x1):
            self.off_arrow_mode(event)
            return "break"
        else:
            return "break"
        
    def undo(self):
        self.new_undo()
    
    def redo(self):
        self.new_redo()
        

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
    
    def processing_event(self):
        curr_index = self.text.index(tk.INSERT)
        curr_word = self.get_curr_word(curr_index)
        if curr_word:
            suggestions = Suggester.get_suggestions(curr_word, self.spellchecker.known_words)
        if self.timer_delay:
            self.window.after_cancel(self.timer_delay)
            self.timer_delay = None

    def save_undo(self):
        text = self.text.get("1.0", tk.END)
        cursor_pos = self.text.index(tk.INSERT)
        self.undo_hist.append((text, cursor_pos))
    
    def new_undo(self, event=None):
        if self.undo_hist:
            current = (self.text.get("1.0", tk.END), self.text.index(tk.INSERT))
            self.redo_hist.append(current)
            prev = self.undo_hist.pop()
            self.text.delete("1.0", tk.END)
            self.text.insert("1.0", prev[0])
            self.text.mark_set(tk.INSERT, prev[1])
        return "break"
    
    def new_redo(self, event=None):
        if self.redo_hist:
            current = (self.text.get("1.0", tk.END), self.text.index(tk.INSERT))
            self.undo_hist.append(current)
            new = self.redo_hist.pop()
            self.text.delete("1.0", tk.END)
            self.text.insert("1.0", new[0])
            self.text.mark_set(tk.INSERT, new[1])
        return "break"
    
    def get_curr_word(self, curr_index):
        start_word = self.text.search(r'\m', curr_index,backwards=True,regexp = True)
        end_word = self.text.search(r'\M', curr_index, regexp=True)
        if start_word and end_word:
            return self.text.get(start_word, end_word)
        return None

    def show_menu(self, event):
        curr_index = self.text.index(tk.CURRENT)
        word = self.text.get(curr_index + " wordstart", curr_index + " wordend")
        r_move_insert = self.text.index("@%d, %d"%(event.x, event.y))
        self.text.mark_set(tk.INSERT, r_move_insert)
        if "highlight" in self.text.tag_names(curr_index) and word and word in self.unknown_words:
            self.curr_word_pos = curr_index
            self.text.tag_remove("selected", "1.0", tk.END)
            self.text.tag_add("selected", curr_index + " wordstart", curr_index + " wordend")
            self.text.tag_config("selected", background="blue")
            menu = tk.Menu(self.text, tearoff=1)
            menu.add_command(label="Ignore", command=self.ignore_unknown)
            menu.add_command(label="Get Suggestion", command=self.accept_suggestion)
            menu.add_command(label="+Personal Dict", command=self.personal_dict)
            menu.post(event.x_root, event.y_root)

    def next_unknown(self):
        if self.highlight_indexes:
            self.text.tag_config("highlight", background="yellow")
            self.initial = False
        else:
            self.text.tag_config("selected", background="blue")
        if self.highlight_indexes:
            self.text.tag_remove("selected", "1.0", tk.END)
            self.current_unknown_index = (self.current_unknown_index+1) % (len(self.highlight_indexes))
            (start_index, end_index) = self.highlight_indexes[self.current_unknown_index]
            self.set_insertion(start_index)
            for index, (start, end) in enumerate(self.highlight_indexes):
                if index != self.current_unknown_index:
                    self.text.tag_add("highlight", start, end)
            self.text.tag_add("selected", start_index, end_index)
            self.text.tag_config("selected", background="blue")
            self.text.tag_config("highlight", background="yellow")
            
    def previous_unknown(self):
        if self.highlight_indexes:
            self.text.tag_remove("selected", "1.0", tk.END)
            self.current_unknown_index = (self.current_unknown_index-1)%(len(self.highlight_indexes))
            (start_index, end_index) = self.highlight_indexes[self.current_unknown_index]
            self.set_insertion(start_index)
            self.text.tag_remove("highlight", "1.0", tk.END)
            for index, (start, end) in enumerate(self.highlight_indexes):
                if index != self.current_unknown_index:
                    self.text.tag_add("highlight", start, end)
            self.text.tag_add("selected", start_index, end_index)
            self.text.tag_config("selected", background="blue")
            self.text.tag_config("highlight", background="yellow")
        
    
    def set_insertion(self, pos):
        if not self.arrow_key_mode:
            self.text.mark_set(tk.INSERT, pos)
            self.text.see(tk.INSERT)

    def highlight_unknown(self):
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


    def hlight_word(self, word, line_start, now_known_indexes):
        match = re.search(r'\b{}\b'.format(re.escape(word)), self.text.get(line_start, line_start+"lineend"))
        if match:
            start_pos = "{}+{}c".format(line_start, match.start())
            end_pos = "{}+{}c".format(line_start, match.end())
            self.text.tag_add("highlight", start_pos, end_pos)
            now_known_indexes.append((start_pos, end_pos))
            if (word.lower() not in self.unknown_words) and (word not in self.unknown_words):
                self.unknown_words.append(word.lower())
            
    def ignore_unknown(self):
        if not self.highlight_indexes:
            return
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
            with open("ign_words.txt", 'at') as ignored_file:
                ignored_file.write(word + '\n')
            self.highlight_unknown()
    
    def ignore_all(self, event=None):
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
        with open("ign_words.txt", 'at') as ignored_file:
            ignored_file.write(curr_word+'\n')

    def get_next_unknown_start(self, from_index):
        next_index = self.text.search(r'\b[a-zA-Z]+\b', from_index, tk.END, regexp=True)
        while next_index:
            if self.text.get(next_index + " wordstart", next_index + " wordend") in self.unknown_words:
                return next_index
            next_index = self.text.index(next_index + " wordend")
            next_index = self.text.search(r'\b[a-zA-Z]+\b', next_index + " +1c", tk.END, regexp=True)
        return None
    
    def accept_suggestion(self):
        if self.curr_word_pos:
            word = self.text.get(self.curr_word_pos+" wordstart", self.curr_word_pos+" wordend")
            if word:
                suggestions = Suggester.get_suggestions(word, self.spellchecker.known_words)
                self.suggestion_menu(word, suggestions)
    
    def suggestion_menu(self, unknown_word, suggestions):
        self.menu.delete(0, tk.END)
        if suggestions:
            for suggestion in suggestions:
                self.menu.add_command(label=suggestion, command=lambda s=suggestion: self.replace_unknown(unknown_word, s))
            x = self.text.winfo_pointerx()
            y = self.text.winfo_pointery()
            self.menu.tk_popup(x,y) #will need to check on this--not sure about it
        

    def get_a_suggestion(self, unknown_word, suggestion):
        return lambda: self.replace_unknown(unknown_word, suggestion)

    def replace_unknown(self, unknown_word, suggestion):
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
    
    def update_known(self, prev, new):
        if prev in self.unknown_words:
            self.unknown_words.remove(prev)
        self.spellchecker.ignored_words.discard(prev)
        self.spellchecker.known_words.add(new)
        self.highlight_unknown()

    def personal_dict(self):
        if self.curr_word_pos:
            new_word = self.text.get(self.curr_word_pos+" wordstart",self.curr_word_pos+" wordend")
            if new_word:
                new_word = new_word.strip()
                if new_word and (new_word not in self.spellchecker.known_words):
                    self.spellchecker.known_words.add(new_word)
                    self.text.tag_remove("highlight", self.curr_word_pos+" wordstart", self.curr_word_pos+" wordend")
                    self.text.tag_remove("selected", self.curr_word_pos+" wordstart", self.curr_word_pos+" wordend")
                    with open(personal_dict, 'rt') as personal_dict_file:
                        if new_word not in personal_dict:
                            with open(personal_dict, 'at') as personal_dict_file:
                                personal_dict_file.write(new_word+'\n')
                    self.highlight_unknown()

if __name__ == "__main__":
    with open("example.txt", 'rt') as example_text_file:
        text_content = example_text_file.read()

    reference_file = TextFile(text_content)
    known_words_file = "words.txt"
    ign_words_file = "ign_words.txt"
    personal_dict = "pers_dict.txt"
    window = tk.Tk()
    spellchecker = Spellchecker(reference_file,known_words_file, personal_dict)
    app = SpellcheckerApp(window, spellchecker)
    window.mainloop()
#rest of globals