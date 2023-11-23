# Project: Hebrew Reference extractor
#
# Created by: Nati Ben-Gigi
# Date: 11/2023
#
# License: MIT
# Copyright: Nati Ben-Gigi 2023
#
# File: formatting_functions.py
# Description: 
# This file holds formatting related function for the project.

import sys
from tags_lists import *
import unicodedata
from tabulate import tabulate
#from bidi.algorithm import get_display 

LTR = '\u202A'  # Left-to-Right embedding
RTL = '\u202B'  # Right-to-Left embedding
PDF = '\u202C'  # Pop Directional Formatting

# check if the results are empty
def is_results_empty(reference):
    if (reference.archi_book == "") and \
        (reference.base_book == "") and \
        (reference.base_book_details == "") and \
        (reference.book_name == "") and \
        (reference.author_name == "") and \
        (reference.refrence_deatils == ""):
        return True
    else:
        return False

# check if a given string is composed from Hebrew letters
def is_hebrew(word):
    for char in word:
        if 'HEBREW' in unicodedata.name(char):
            return True
    return False

# creating a string that holds the entire original reference words, but with << >> marks for start - end 
def build_ref_with_delimiter(refObject):
    refrence_str_with_delimiter = ""
    try:
        # creating a string that holds the entire original reference words, but with << >> marks for start - end 
        # first we loop over the list and search when the words have tags and we put before a << mark
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
            if words_tags_set[0]in ["<<", ">>"]:
                refrence_str_with_delimiter += " " + words_tags_set[0]
            else:
                refrence_str_with_delimiter += " " + RTL + words_tags_set[0] + PDF

        refrence_str_with_delimiter.strip()
    
    except Exception as ex:
        print("issue in func: build_ref_with_delimiter")
        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(ex)

    return refrence_str_with_delimiter

# This function take separates every word and tags in teh reference with | to display the word and it tagging
def build_ref_and_tags_str(refObject):
    rows = []
    clean_words_str = ""
    clean_words_list = []
    layer_1_tags_list = []
    layer_2_tags_list = []
    try:

        for words_tags_set in refObject.extended_words_tags_list:
            clean_words_list.append(words_tags_set[0])
            layer_1_tags_list.append(words_tags_set[1])
            layer_2_tags_list.append(words_tags_set[2])
            
            clean_words_str += " " + words_tags_set[0]
        
        clean_words_str.strip()

        # Find the maximum width for each column
        column_widths = [max(len(a), len(b), len(c)) for a, b, c in zip(clean_words_list, layer_1_tags_list, layer_2_tags_list)]

        rows = []
        for l in (clean_words_list, layer_1_tags_list, layer_2_tags_list):
            row = []
            for word, width in zip(l, column_widths):
                if is_hebrew(word):
                    padding = ' ' * (width - len(word))
                    row.append(padding + word)
                else:
                    row.append(word.ljust(width))
            rows.append(row)

        rows[1] = reversed(rows[1])
        rows[2] = reversed(rows[2])
        words_tags_table_str = '\n'.join('|'.join(row) for row in rows)

    except Exception as ex:
        print("issue in func: build_ref_and_tags_str")
        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(ex)

    return words_tags_table_str, clean_words_str

# prepare the ref object result for logging/printing
def format_results(refObject):
    refrence_str_delimited = ""
    try:
        words_tags_table_str, clean_words_str = build_ref_and_tags_str(refObject)
        '''
        if len(words_tags_rows) > 0:
            ref_words_delimited = words_tags_rows[0]
            layer_1_tags_delimited = words_tags_rows[1]  
            layer_2_tags_delimited = words_tags_rows[2]
        '''
        # this function search for the exact reference words in teh entire ref str and put around it < and >
        refrence_str_delimited = build_ref_with_delimiter(refObject)
    
    except Exception as ex:
        print("issue in func: format_results")
        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(ex)

    #return  ref_words_delimited, layer_1_tags_delimited, layer_2_tags_delimited, clean_words_str, refrence_str_delimited
    return words_tags_table_str, clean_words_str, refrence_str_delimited

