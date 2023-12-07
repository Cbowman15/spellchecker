
import bs4 #may not have downloaded correctly? (yellow underline)
from bs4 import BeautifulSoup
import PyPDF2
from PyPDF2 import PdfReader
import tkinter as tk
from tkinter import simpledialog
import re
import time
import Levenshtein
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
        for word in words_to_check:
            if word not in self.known_words and word not in self.ignored_words:
                suggestions = Suggester.get_suggestions(word, self.known_words)
                self.unknown_word_count += 1
                self.unknown_words.append((word, suggestions))
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
    def __init__(self, text):
        super().__init__(text)
    def parse(self):
        pdf_reader = PyPDF2.PdfReader(self.text)
        pdf_content = ""
        for num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[num]
            pdf_content += page.extract_text()
        return pdf_content.split()

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
        
        self.btn_ignore = tk.Button(self.frm, text="IGNORE", command=self.ignore_unknown)
        self.btn_ignore.pack(side=tk.RIGHT, padx=3, pady=3, anchor=tk.SW)
        self.btn_ignore.pack()
        self.curr_word_pos = None
        self.timer_delay = None
        self.time_delay = 500
        self.menu=tk.Menu(self.text, tearoff=0)
        spellchecker.spell_check()
        self.highlight_unknown()

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
                self.show_btns()
    
    def hide_btns(self):
        self.btn_next_unknown.pack_forget()
        self.btn_prev_unknown.pack_forget()
    
    def show_btns(self):
        self.btn_next_unknown.pack(side=self.btn_next_anchor, padx=3, pady=3, anchor=tk.SE)
        self.btn_prev_unknown.pack(side=self.btn_prev_anchor, padx=3, pady=3, anchor=tk.SW)

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
        

    def keypress_action(self, event):
        if event.char.isalpha():
            if self.timer_delay:
                self.window.after_cancel(self.timer_delay)
            self.timer_delay = self.window.after(self.time_delay, self.processing_event)
        
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
    
    def update_hlight(self):
        self.text.tag_remove("highlight", "1.0", tk.END)
        for (start_word, end_word) in self.highlight_indexes:
            self.text.tag_add("highlight", start_word, end_word)
    
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
            menu.add_command(label="Delete", command=self.delete_unknown)
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
        prev_whitespace = self.text.search(r'\s', pos, backwards=True, regexp=True)
        if self.arrow_key_mode:
            if self.text.compare(tk.INSERT, '>', pos):
                self.text.mark_set(tk.INSERT, "{}+1c".format(pos))
            else:
                self.text.mark_set(tk.INSERT, "{}-1c".format(pos))
        else:
            self.text.mark_set(tk.INSERT, pos)

    def highlight_unknown(self):
        curr_time = time.time()
        if self.arrow_key_mode and (curr_time-self.arrow_last_time>self.arrow_time_reset):
            self.arrow_key_mode = False
        if not self.arrow_key_mode:
            curr_index = self.text.index(tk.INSERT)
            curr_line_num = int(curr_index.split('.')[0])
            self.text.tag_remove("highlight", "1.0", tk.END)
            now_known_indexes = []
            for line_num in range(1, int(self.text.index(tk.END).split('.')[0])+1):
                line_start= "{}.0".format(line_num)
                line_end= "{}.end".format(line_num)
                line_text = self.text.get(line_start, line_end)
                for match in re.finditer(r'\b[a-zA-Z]+\b', line_text):
                    word=match.group()
                    if word not in self.spellchecker.known_words and word not in self.spellchecker.ignored_words:
                        start_pos = "{}+{}c".format(line_start, match.start())
                        end_pos = "{}+{}c".format(line_start, match.end())
                        self.text.tag_add("highlight", start_pos, end_pos)
                        now_known_indexes.append((start_pos, end_pos))
                        if word not in self.unknown_words:
                            self.unknown_words.append(word)
            self.highlight_indexes = now_known_indexes
            self.current_unknown_index = (len(self.highlight_indexes)-1)
            for index, (start_index, end_index) in enumerate(self.highlight_indexes):
                if index!=self.current_unknown_index:
                    self.text.tag_add("highlight", start_index, end_index)
                    self.text.tag_config("highlight", background="yellow")
            curr_highlight_area  = len(self.text.get(curr_index+" wordstart", curr_index+" wordend"))
            curr_index = "{}.{}".format(curr_line_num, curr_highlight_area)
            self.text.tag_add("highlight", curr_index+" wordstart", curr_index+" wordend")
            self.set_insertion(curr_index)
            
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
            if word in [unknown_word[0] for unknown_word in self.spellchecker.unknown_words]:
                suggestions = Suggester.get_suggestions(word, self.spellchecker.known_words)
                if suggestions:
                    self.suggestion_menu(word, suggestions)
    
    def suggestion_menu(self, unknown_word, suggestions):
        menu = tk.Menu(self.text, tearoff=0)
        for suggestion in suggestions:
            menu.add_command(label=suggestion, command=lambda s=suggestion, uw=unknown_word: self.replace_unknown(uw, s))
        menu.post(self.text.winfo_pointerx(), self.text.winfo_pointery()) #will need to check on this--not sure about it
        

    def get_a_suggestion(self, unknown_word, suggestion):
        return lambda: self.replace_unknown(unknown_word, suggestion)

    def replace_unknown(self, unknown_word, suggestion):
        start_index = self.text.search(unknown_word, "1.0", tk.END)
        if start_index:
            end_index = self.text.index("{}+{}c".format(start_index, len(unknown_word)))
            self.text.delete(start_index, end_index)
            self.text.insert(start_index, suggestion)
            self.spellchecker.known_words.add(suggestion)
            if unknown_word in self.spellchecker.unknown_words:
                self.spellchecker.unknown_words.remove(unknown_word)
            self.text.tag_remove("highlight", start_index, "{}+{}c".format(start_index, len(suggestion)))
            self.highlight_unknown()
        
    def delete_unknown(self):
        if self.highlight_indexes and (self.current_unknown_index<len(self.highlight_indexes)):
            (start_index, end_index) = self.highlight_indexes[self.current_unknown_index]
            del_word = self.text.get(start_index, end_index)
            if del_word in self.unknown_words:
                self.text.delete(start_index, end_index)
                if del_word in self.spellchecker.ignored_words:
                    self.unknown_words.remove(del_word)
                self.text.insert(start_index, "<REPLACE>")
                self.spellchecker.unknown_word_count -= 1
                self.highlight_indexes.pop(self.current_unknown_index)
                self.update_hlight()
                self.next_unknown()

    def personal_dict(self):
        if self.curr_word_pos:
            new_word = self.text.get(self.curr_word_pos+" wordstart",self.curr_word_pos+" wordend")
            if new_word:
                new_word = new_word.strip()
                if new_word and (new_word not in self.spellchecker.known_words):
                    self.spellchecker.known_words.add(new_word)
                    self.text.tag_remove("highlight", self.curr_word_pos+" wordstart", self.curr_word_pos+" wordend")
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