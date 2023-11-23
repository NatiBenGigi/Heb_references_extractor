# Project: Hebrew Reference extractor
#
# Created by: Nati Ben-Gigi
# Date: 11/2023
#
# License: MIT
# Copyright: Nati Ben-Gigi 2023
#
# File: main.py
# Description: 
# The main of the project. contain the GUI to interact with the reference extractions engine.

import os
import sys

platform = sys.platform

class Logger(object):
    def __init__(self, filename="Default.log"):
        self.terminal = sys.stdout
        if platform == "darwin":
            encoding = 'utf-8'
        elif platform == "win32":
            encoding = 'cp1252'
        self.log = open(filename, "a", encoding=encoding)

    # This function handle the saving the messages to the files
    def reverse_hebrew_text(self, text):
        reversed_text = ''
        hebrew_text = ''
        for char in text:
            if '\u0590' <= char <= '\u05FF' or '\uFB1D' <= char <= '\uFB4F':
                hebrew_text = char + hebrew_text
            else:
                reversed_text += hebrew_text + char
                hebrew_text = ''
        reversed_text += hebrew_text
        return reversed_text
    
    def write(self, message):
        self.terminal.write(message)
        self.log.write(self.reverse_hebrew_text(message))

    def flush(self):
        # this flush method is needed for python 3 compatibility.
        # this handles the flush command by doing nothing.
        pass

sys.stdout = Logger("Heb_Reference_extractor_LOG.txt")

# GUI files
import tkinter as tk
from tkinter import *
from tkinter import filedialog
from tkinter import ttk
from tkinter import scrolledtext
from tkinter.filedialog import askopenfilename
import time
from functools import partial
from tkinter import messagebox


# My files
from scan_corpus import *

text_decodes = ["utf8", "cp1255","cp862"]

class Viewer_main_form(tk.Tk):

    def __init__(self):
        super().__init__()

        self.filePath = tk.StringVar()
        # holds the original  text
        self.text_window = None
        # holds the tagging results of layer1
        self.taggedDataWindowLayer1 = None
        # holds the tagging results of layer2
        self.taggedDataWindowLayer2 = None
        # holds the summary of the extracted references
        self.final_results_window = None
        # This is the BERT CRF rabbinic warping 
        self.dual_layers_tagger = BERT_CRF_Rabbinic_layer1_2()

        # bring GUI components
        self.title("Hebrew References Extractor")
        self.set_main_frames()
        self.set_buttons()
        self.set_text_windows()
        self.set_entries()

    # this function is handling the scroll bar of the tagged data windows
    def viewall(self, *args):
        eval('self.taggedDataWindowLayer1.yview(*args)')
        eval('self.taggedDataWindowLayer2.yview(*args)')

    # this windows holds the original text
    def set_text_windows(self):
        # Using a scrolled Text control
        scrol_w = 120
        scrol_h = 10
        self.text_window = scrolledtext.ScrolledText(self.bottom_frame, width=scrol_w, height=scrol_h, wrap=tk.WORD, font=("Courier New",18))
        self.text_window.grid(row=0, column=0, columnspan=2)

        scrol_w = 60
        scrol_h = 10

        self.taggedDataWindowLayer1 = Text(self.bottom_frame, width=scrol_w, height=scrol_h, wrap=tk.WORD, font=("Courier New", 18))
        self.taggedDataWindowLayer1.grid(row=1, column=0)

        self.taggedDataWindowLayer2 = Text(self.bottom_frame, width=scrol_w, height=scrol_h, wrap=tk.WORD, font=("Courier New", 18))
        self.taggedDataWindowLayer2.grid(row=1, column=1)

        self.rolly = ttk.Scrollbar(self.bottom_frame, orient=VERTICAL, command=self.viewall)
        self.taggedDataWindowLayer1['yscrollcommand'] = self.rolly.set
        self.taggedDataWindowLayer2['yscrollcommand'] = self.rolly.set

        self.rolly.grid(row=1, column=3, sticky=(N, W, E, S))

        scrol_w = 120
        scrol_h = 15
        self.final_results_window = scrolledtext.ScrolledText(self.bottom_frame, width=scrol_w, height=scrol_h, wrap=tk.WORD, font=("Courier New",18))
        self.final_results_window.grid(row=2, column=0, columnspan=2)

    # set the frames that will hold the widgets
    def set_main_frames(self):

        self.top_frame = ttk.LabelFrame(self)
        self.top_frame.grid(column=0, row=0, sticky=tk.NSEW)

        self.middle_frame = ttk.LabelFrame(self)
        self.middle_frame.grid(column=0, row=1, sticky=tk.W)

        self.bottom_frame = ttk.LabelFrame(self)
        self.bottom_frame.grid(column=0, row=2, sticky=tk.W)

    # Sets up all the application buttons
    def set_buttons(self):

        button_load_data_to_Form = tk.Button(self.top_frame, text="Load a single txt file", command=self.load_file)
        button_load_data_to_Form.pack(side=tk.LEFT, padx=10, pady=10)

        button_extract_ref_from_text = tk.Button(self.top_frame, text="Extract references", command=self.extract_references)
        button_extract_ref_from_text.pack(side=tk.LEFT, padx=10, pady=10)

        button_scan_corpus_and_save_taggs = tk.Button(self.top_frame, text="Scan corpus and save tags", command=partial(self.scan_corpus, False, True)) #argumetns: scan_a_tagged_corpus ,save_tagged_files
        button_scan_corpus_and_save_taggs.pack(side=tk.LEFT, padx=10, pady=10)

        button_scan_corpus = tk.Button(self.top_frame, text="Scan corpus", command=partial(self.scan_corpus, False, False))  #argumetns: scan_a_tagged_corpus ,save_tagged_files
        button_scan_corpus.pack(side=tk.LEFT, padx=10, pady=10)

        button_scan_tagged_corpus = tk.Button(self.top_frame, text="Scan tagged corpus", command=partial(self.scan_corpus, True, False))  #argumetns: scan_a_tagged_corpus ,save_tagged_files
        button_scan_tagged_corpus.pack(side=tk.LEFT, padx=10, pady=10)

        button_clear_gui = tk.Button(self.top_frame, text="Clear GUI", command=self.clear_gui)
        button_clear_gui.pack(side=tk.RIGHT, padx=10, pady=10)


        self.selected_decode = tk.StringVar()
        self.encodes_cb = ttk.Combobox(self.top_frame, textvariable=self.selected_decode)
        self.encodes_cb['values'] = text_decodes
        self.encodes_cb.current(0)
        self.encodes_cb['state'] = 'readonly'
        self.encodes_cb.pack(side=tk.RIGHT, padx=10, pady=10)

    # Sets up the entry field for the file path
    def set_entries(self):
        path = tk.Entry(self.middle_frame, width=150,textvariable=self.filePath)
        path.pack()

    # Load a file to be scanned for references
    def load_file(self):
        path_file = askopenfilename()
        # if no path was provided (for example the user clicked Cancel, then just return)
        if path_file == "": return
        self.filePath.set(path_file)

        f = open(self.filePath.get(), 'r', encoding = self.encodes_cb.get())
        content = f.read()
        self.clean_content, _ = clean_text2(content, self.encodes_cb.get())
        f.close()

        self.update_responsa_text_window(self.clean_content)

    # Updates the text window with text and tags
    def update_responsa_text_window(self, text):
        self.text_window.delete(1.0, tk.END)

        if text != None:  # we have a row text
            self.text_window.insert(tk.INSERT, text, "right")
            self.text_window.tag_configure("right", justify="right")

    # Clears the GUI for new text processing
    def clear_gui(self):
        self.text_window.delete(1.0, tk.END)
        self.final_results_window.delete(1.0, tk.END)
        self.taggedDataWindowLayer1.delete(1.0, tk.END)
        self.taggedDataWindowLayer2.delete(1.0, tk.END)
        self.filePath.set('')

    # Retrieves and cleans the text from the log window
    def get_responsa_text(self):
        original_text = self.text_window.get("1.0", tk.END)
        # need to clean the text again in case it was past in to the text windows directly 
        responsa_text, _ = clean_text2(original_text, False)

        return responsa_text
    
    # display the words + layer 1 tags + layer 2 tags
    def print_words_tags(self, refObject):
        try:
            words_str = ""
            words_list = []
            clean_words_list = []
            layer_1_tags_str = ""
            layer_1_tags_list = []
            layer_2_tags_str = ""
            layer_2_tags_list = []
            idx = 0
            for words_tags_set in refObject.extended_words_tags_list:
                len_word = len(words_tags_set[0])
                len_layer_1_tag = len(words_tags_set[1])
                len_layer_2_tag = len(words_tags_set[2])

                cell_size = max(len_word, len_layer_1_tag, len_layer_2_tag)
                cell_size += 3

                word_str = words_tags_set[0]
                if idx == 0:
                    word_str = word_str.center(cell_size - 1)
                else:
                    word_str = word_str.center(cell_size)

                clean_words_list.append(word_str)
                if idx != 0:   
                    word_str = "|" + word_str

                words_list.append(word_str)

                layer_1_str = words_tags_set[1]
                layer_1_str = layer_1_str.center(cell_size)
                layer_1_str = "|" + layer_1_str
                layer_1_tags_list.append(layer_1_str)

                layer_2_str = words_tags_set[2]
                layer_2_str = layer_2_str.center(cell_size)
                layer_2_str = "|" + layer_2_str
                layer_2_tags_list.append(layer_2_str)

                idx += 1

            words_str = ""
            # for word in reversed(words_list):
            for word in words_list:
                words_str += word

            layer_1_tags_str = "| "
            for word in reversed(layer_1_tags_list):
                layer_1_tags_str += word

            layer_2_tags_str = "| "
            for word in reversed(layer_2_tags_list):
                layer_2_tags_str += word

            clean_words_str = ""
            for word in clean_words_list:
                clean_words_str += word

            # creating a string that holds the entire original reference words, but with < > marking the start - end of the ref
            # first we loop over the list and search when the words have tags and we put before a < mark
            # and then we loop by inverse and we do the same
            idx = 0
            for words_tags_set in refObject.extended_words_tags_list:
                if words_tags_set[5] == [] or words_tags_set[5][0].type in weak_tags: 
                    idx += 1
                    continue
                else:
                    if idx > 0:
                        if refObject.extended_words_tags_list[idx-1][0] == "(":
                            idx -= 1 #lets make sure we capture the brackets
                    refObject.extended_words_tags_list.insert(idx, ">>")
                    break
            

            idx = len(refObject.extended_words_tags_list) 
            #now in reveres
            for words_tags_set in refObject.extended_words_tags_list[::-1]:
                if words_tags_set[5] == [] or words_tags_set[5][0].type in weak_tags: 
                    idx -= 1
                    continue
                else:
                    if idx < len(refObject.extended_words_tags_list) -1: # if we don't check we may fail with index out of rang 
                        if refObject.extended_words_tags_list[idx][0] == ")":
                            idx += 1 # we miss the "(" so move the idx to include it"
                    refObject.extended_words_tags_list.insert(idx, "<<")
                    break
            
            refrence_str_with_delimiter = ""
            for words_tags_set in refObject.extended_words_tags_list:
                refrence_str_with_delimiter += " " + words_tags_set[0]
        except Exception as ex:
            print("issue in func: print_words_tags")
            print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
            print(ex)
        #DEBUG 
        print(refrence_str_with_delimiter[::-1])
        return words_str, layer_1_tags_str, layer_2_tags_str, clean_words_str, refrence_str_with_delimiter
    
    # display final layer 1 and 2 results
    def display_final_words_tags(self, final_results_string_layer1, final_results_string_layer2):
        # display the final results layer 1
        self.text_window.tag_configure("right", justify="right")
        self.taggedDataWindowLayer1.delete(1.0, tk.END)
        self.taggedDataWindowLayer1.insert(
            tk.INSERT, final_results_string_layer1, "right")

        # display the final results layer 2
        self.text_window.tag_configure("right", justify="right")
        self.taggedDataWindowLayer2.delete(1.0, tk.END)
        self.taggedDataWindowLayer2.insert(
            tk.INSERT, final_results_string_layer2, "right")

    # Prints a summary of references found in a single text
    def print_single_responsa_summary(self, found_refrenses_list):
        begin_header = "============High quality (Normalized) references Summary BEGIN  ==========="
        self.final_results_window.insert(tk.INSERT, "\n", "right")
        self.final_results_window.insert(tk.INSERT, begin_header, "right")
        self.final_results_window.insert(tk.INSERT, "\n", "right")

        num_of_results = 0
        # display the list of all the results
        for refObject in found_refrenses_list:
            # skip empty references
            if is_results_empty(refObject) == True:
                continue
                
            ref_header = "-------------------------" + \
                str(num_of_results + 1) + \
                "------------------------------------------------------"

            self.final_results_window.insert(tk.INSERT, "\n", "right")
            self.final_results_window.insert(
                tk.INSERT, ref_header, "right")
            self.final_results_window.insert(tk.INSERT, "\n", "right")

            if type(refObject.archi_book) == str:
                text = "archi_book: " + refObject.archi_book + "\n"
                self.final_results_window.insert(tk.INSERT, text, "right")

            if type(refObject.base_book) == str:
                text = "base_book: " + refObject.base_book + "\n"
                self.final_results_window.insert(tk.INSERT, text, "right")

            if type(refObject.base_book_details) == str:
                text = "base_book_details: " + refObject.base_book_details + "\n"
                self.final_results_window.insert(tk.INSERT, text, "right")

            if type(refObject.book_name) == str:
                text = "book_name: " + refObject.book_name + "\n"
                self.final_results_window.insert(tk.INSERT, text, "right")

            if type(refObject.author_name) == str:
                text = "author_name: " + refObject.author_name + "\n"
                self.final_results_window.insert(tk.INSERT, text, "right")

            if type(refObject.refrence_deatils) == str:
                text = "refrence_deatils: " + refObject.refrence_deatils + "\n"
                self.final_results_window.insert(tk.INSERT, text, "right")

            text = "ref_quality: " + str(refObject.ref_quality) + "\n"
            self.final_results_window.insert(tk.INSERT, text, "right") 

            _, _, ref_with_delimiters = format_results(refObject)
            text = "ref_with_delimiters: " +  ref_with_delimiters + "\n"
            self.final_results_window.insert(tk.INSERT, text, "right") 

            num_of_results += 1

        self.final_results_window.insert(
            tk.INSERT, "============ End of list. Total number of results: " + str(num_of_results) + "===========", "right")
        self.final_results_window.insert(tk.INSERT, "\n", "right")

    # extract reference from the text located in the text window
    def extract_references(self):
        # calling the two BERT CRF models (layer1 and layer 2) and receive back the tags for every word 
        layer_1_2_mergedResults = self.dual_layers_tagger.tag_text_layer_1_2(self.get_responsa_text())
        layer_1_word_tag = ""
        layer_2_word_tag = ""   

        for item in layer_1_2_mergedResults:
            layer_1_word_tag += item[0] + " " + item[1] + "\n"
            layer_2_word_tag += item[0] + " " + item[2] + "\n"
  
        self.display_final_words_tags(layer_1_word_tag, layer_2_word_tag)

        # entry point for the processing of the tags and contracting the references list
        found_refrenses_list = process_layer_1_2_results_v2(layer_1_2_mergedResults, "", self.filePath.get())
        self.print_single_responsa_summary(found_refrenses_list)

    # This func scans an entire corpus 
    def scan_corpus(self, scan_a_tagged_corpus ,save_tagged_files): 
        
        self.corpus_folder = filedialog.askdirectory()
        # if no path was provided (for example the user clicked Cancel, then just return)
        if self.corpus_folder == "": return
        
        start = time.time()
        corpus_dir_name = os.path.basename(self.corpus_folder)
        final_xls_name = corpus_dir_name + ".xlsx"
        dn = os.path.dirname(os.path.realpath(__file__))
        XLS_results = os.path.join(dn,final_xls_name)

        final_result, res_file_path = extract_references_from_corpus(self.corpus_folder, XLS_results, scan_a_tagged_corpus, save_tagged_files, encoding_value = self.encodes_cb.get()) # RowData = self.isRowData.get())
        end = time.time()
        print(' Took %.3f seconds' % (end - start))

        if final_result == False:
            if platform == "darwin":
                # Mac OS bug, don't display the title in TkInter message box
                messagebox.showerror("","Scan failed. See console log for details.")
            else:
                messagebox.showerror("Scan failed", "See console log for details.")
        else:
            str_msg = "Results file saved to: " + res_file_path
            if platform == "darwin":
                # Mac OS bug, don't display the title in TkInter message box
                str_msg = "Scan completed successfully " + str_msg
                messagebox.showinfo("", str_msg)
            else:
                messagebox.showinfo("Scan completed successfully", str_msg)


if __name__ == "__main__":                                        
    main_form = Viewer_main_form()
    main_form.mainloop()

