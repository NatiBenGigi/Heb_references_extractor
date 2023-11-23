# Project: Hebrew Reference extractor
#
# Created by: Nati Ben-Gigi
# Date: 11/2023
#
# License: MIT
# Copyright: Nati Ben-Gigi 2023
#
# File: find_ref_helper.py
# Description: 
#This file holds helper function for the project.
#including text processing. name normalization (canonization) and more

import sys
import os
from bidi.algorithm import get_display

DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

from shared_classes import *


# we need to skip notes files, (in case uf using the responsa project corpus)
def isNotesFile(content):
    _, title = clean_text2(content)
    i = title.find("הערות")
    
    if i == -1: #couldn't find the word הערה so we assume its not a notes file
        return False
    else:
        return True

# extract the text's title from the beginning text
def extractTitle(Text):   
    if Text in ["", None]:
        return ""
    
    title = ""
    for c in Text:
        c_unicode = ord(c)
        if c_unicode == 10 or c ==".": # 10 is the character ' \n ' (new line)
            break
        else:
            title += c
    
    return title

# Clean the original text from digits and non Hebrew characters
def clean_text2(originalText, encode_value = "utf8" ,remove_header = False):
    if originalText in ["", None]:
        return "", ""
    
    keep_first_break_line = True
    title = extractTitle(originalText)
    clean_content = ""
    idx = 0
    originalTextLen = len(originalText)
    prev_c_unicode = 0
    for c in originalText:

        c_unicode = ord(c)
        if 48 <= c_unicode <= 57: # skip number
            pass
        elif 65 <= c_unicode <= 90: # skip Uppercase Latin alphabet
            pass
        elif 97 <= c_unicode <= 122: # skip Lowercase Latin alphabet
            pass
        elif c_unicode == 47: # skip "/"
            pass
        elif c_unicode == 43: # skip "+"
            pass
        elif c_unicode == 42: # skip "*"
            pass
        elif c_unicode == 824: # skip "/"
            pass
        elif c_unicode == 92: # skip \"
            pass
        elif c_unicode == 6: # skip ACK"
            pass
        elif c_unicode == 7: # skip BEL"
            pass                
        elif c_unicode == 12: # skip FF"
            pass
        elif c_unicode == 225: # skip á"
            pass
        elif c_unicode == 64: # skip @"
            pass
        elif c_unicode == 160: # the character "No-Break Space" \x{A0}
            pass
        elif c_unicode == 177: # the character ' ± '
            clean_content += r'״'  #convert to ' " '
        elif c_unicode == 8801: # the character ' ≡ '
            clean_content += "´" #chr(180)  convert to ' ´ '
        # when dealing with original responsa stuff that should be the pranthsis direction (e.g. need to inverse it)
        #'''
        #elif c_unicode == 41: # the character ' ) '
        #    clean_content +=   " { " # " } "#
        #elif c_unicode == 40: # the character ' ( '
        #    clean_content +=   " } " #" { "#
        #'''
        # when dealing with responsas coming from the web need to keep the direction of the original paranthsis
        elif c_unicode == 41: # the character ' ) '
            if encode_value == "cp1255":
                clean_content +=   " { " # " } "#
            else:
                clean_content +=   " } " # " } "#
        elif c_unicode == 40: # the character ' ( '
            if encode_value == "cp1255":
                clean_content +=   " } " # " } "#
            else:
                clean_content +=   " { " #" { "#

        elif c_unicode == 123: # the character ' { '
            clean_content +=   " { " 
        elif c_unicode == 125: # the character ' } '
            clean_content +=   " } " 
        elif c_unicode == 91: # the character ' [ '
            clean_content +=   " ] " 
        elif c_unicode == 93: # the character ' ] '
            clean_content +=   " [ " 
        elif c_unicode == 58: # the character ' : '
            clean_content +=   " : " 
        elif c_unicode == 59: # the character ' ; '
            clean_content +=   " ; " 
        elif c_unicode == 46: # the character ' . '
            clean_content +=   " . " 
        elif c_unicode == 44: # the character ' , '
            clean_content +=   " , "
        elif c_unicode == 63: # the character ' ? '
            clean_content +=   " ? " 
        elif c_unicode == 33: # the character ' ! '
            clean_content +=   " ! "  
        elif c_unicode == 34: # the character ' " ' (new line)
            clean_content +=   '״' 
        elif c_unicode == 39: # the character ' ' ' (new line)
            clean_content +=   '´'
        elif c_unicode == 61: # the character =
            # first lets check if we found the = at the end of the word or in its begining
            if prev_c_unicode in [32, 0]: # 32 is the space symbol wich means we are starting a word (the 0 means we are at the very begining of the text)
                clean_content += c
                clean_content += " "
            else:
                clean_content += " "
                clean_content += c
        elif c_unicode == 10: # the character ' \n ' (new line)
            if keep_first_break_line: # we must keep the first \n in order to find the title of the responsa, but
                clean_content += c
                keep_first_break_line = False
            elif idx != originalTextLen: #if we are at the end of the originalText we don't need to replace the \n but just to remove it
                clean_content +=   " " 
        else:
            #this code is for removing the responsa footnotes index letters from the text
            if c_unicode >= 1488 and c_unicode <= 1514: # we have an hebrew latter
                #check current location vs. text length
                if idx < 2 or ( originalTextLen - idx < 2 ): # too close to the start/end just just add the letters
                    clean_content += c
                else:
                    #we check that arround the index letter there are some chars. 
                    # befor we have ack (=6) and "1"
                    #after we check we have BEL (=7) 
                    # additionally since index letter can be composed from 2 letters we check the index accordingly 
                    if(((originalText[idx-1] == "1" and ord(originalText[idx-2]) == 6) or \
                    (originalText[idx-2] == "1" and ord(originalText[idx-3]) == 6)) and \
                    (ord(originalText[idx+1]) == 7 or ord(originalText[idx+2]) == 7 )):
                        pass
                    else: # we can really add the letter to our final text string (clean content)
                        clean_content += c
            else: #not an hebrew later but still need to be added
                clean_content += c

        idx += 1
        prev_c_unicode = ord(c) # we keep the curent c for the next loop

    if remove_header:
        clean_content = remove_text_header(clean_content)

    # lets remove all redudant spaces
    clean_content = ' '.join(clean_content.split())
    return clean_content, title

#this function removes the header of the responsa by finding the \n in the text and all the text BEFOR the \n 
def remove_text_header(originalText):
    clean_text = ""
    header_removed = False
    char_index = 0
    for c in originalText:
        char_index += 1
        c_unicode = ord(c)
        if c_unicode == 10 and not header_removed: #checking the \n value
            clean_text = "" # we found the \n, and we still didn't remove the heaer, from now on we need the entier text
            header_removed = True #we don't need to enter this IF condition again
        else:
            clean_text += c
        
        # IF we progressed so much and we still didn't found the \n 
        # we probably got a text without the header lets just return the entier text 
        if char_index >= 50 and header_removed == False: 
            return originalText


    return clean_text

def convertRowData2MalletFormat(RowData):
    reponsaMalletFormat = ""
    singleWord = ""
    for c in RowData:
        c_unicode = ord((c))
        #print(c)
        #print(c_unicode)
        if c_unicode == 32 or c_unicode ==  10: #space or EOL e.g. "\n"
            if singleWord: #we just finished a word
                singleWord += c #add the space after the word, this is mallet requirment
                reponsaMalletFormat += ("%s\n" % singleWord)  
                singleWord = "" # cleaning the token variable for the next loop
                continue # lets move to the next char (which starts the next wrod)
            else: # there is a sequence of spaces, lets skip it
                continue

        if (c == "{" or 
            c == "}" or 
            c == "]" or 
            c == "[" or 
            c == ":" or
            c == ";" or
            c == "," or  
            c == "."):
            if singleWord: #we just finished a word, lets first save it
                singleWord += " " #add the space after the word, this is mallet 
                reponsaMalletFormat += ("%s\n" % singleWord)

            #now lets treat the prantesis    
            singleWord = c
            singleWord += " "
            reponsaMalletFormat += ("%s\n" % singleWord)
            singleWord = "" # cleaning the token variable for the next loop
            continue # lets move to the next char (which starts the next wrod)
           
        singleWord += c #add the character to the current word and move to the next character

    return reponsaMalletFormat

#remove all the noise arround the amnual tagged data
def clean_tagged_data_file_v2(file_path):
    word_tags_list = []
    with open(file_path) as f:
        for index, line in enumerate(f):
            word_tag = line.split()
            if len(word_tag) == 1 or len(word_tag) == 0: #we are in an empty line between 2 paragraph
                word_tags_list.append("\n") 
            elif len(word_tag) == 2:
                word = word_tag[0].strip()
                word = word.replace(chr(1081), '')
                word = word.replace(chr(8234), '')
                word = word.replace(chr(8206), '')
                word = word.replace("\n", '')

                tag = word_tag[1].strip()
                tag = tag.replace(chr(1081), '')
                tag = tag.replace(chr(8234), '')
                tag = tag.replace(chr(8206), '')
                tag = tag.replace("\n", '')

                final_line = word + " " + tag +"\n"
                word_tags_list.append(final_line)

    word_tags_list.append("\n") 
    return word_tags_list

#convert the text string to a list of tokens + clean escapse charcter
def text2token_list2(originalText):
    token_list = []
    clean_content = ""
    #print("===stating===")
    word_index = 0 #word index can be 0 or 1
    for c in originalText:
        
        c_unicode = ord((c))
        #print(c)
        #print(c_unicode)
        if c_unicode == 32: #space
            if word_index == 1: #we are in the second word and we have some spaces we have to clean befor we find the "\n" char
                continue
            if clean_content: #we are on the first word of the line, the string is not empty
                token_list.append(clean_content)
                clean_content = "" # cleaning the token variable for the next loop
                word_index = 1 # change flag to notify we are moving to the second word on the line
            continue
        if c_unicode ==  10: #"\n" # we reached the end of line  
            clean_content += c #we have to save the word coming befor the "\n" (+ the "\n")
            token_list.append(clean_content)
            word_index = 0 # change flag to notify we are moving to the first word in the coming new line
            clean_content = "" # cleaning the token variable for the next loop
            continue

        if c_unicode == 8236: # skip "Pop Directional Formatting"
            continue
        if c_unicode == 8234: # skip "Left-To-Right Embedding"
            continue
        
        clean_content += c #add the character to the current word and move to the next character
    return token_list  

#this function reomes froma string all the unicode character representing the hebrew Nikud
def remove_nikud(text):
    clean_text = ""
    for c in text:
        if ord(c) > 1487 or ord(c) < 1424: #the hebrew nikud is between 1424 to 1478
            clean_text += c
    
    return clean_text

# given a book, find who wrote this book
def resolve_author_of_book(book, Authors_Biography):
    try:
        for author, author_bio in Authors_Biography.items():
            if book in author_bio.books:
                return author

        print(get_display("Warning: Could not find who wrote the book: " + book))
    except Exception as ex:
        print("exception in function: resolve_book_author")
        print(ex)

    return ""

# Canonization process for Talmud stuff
def canonize_talmud_building_block(building_block_str, Building_block_type, ontology):
    try:
        
        if len(building_block_str) <= 2: # its a too short string no such masechet/chapter
            return None, None, None

        #check if the name we found is somthing like בבא (with no masechet name) which we should skip
        if building_block_str.strip() in ontology.books_2_skip:
            return None, None, None

        results = []
        final_type = None
        quality = None
        if Building_block_type == Building_block_type_Enum.AB:
            results, quality = resolve_canonizedStr_from_row_text2(building_block_str, ontology.Archi_books, Building_block_type_Enum.AB)
            final_type = Building_block_type_Enum.AB

        if Building_block_type == Building_block_type_Enum.TM:
            results, quality  = resolve_canonizedStr_from_row_text2(building_block_str, ontology.TM_Masechtot, Building_block_type_Enum.TM)
            final_type = Building_block_type_Enum.TM
            
            if len(results) == 0:
                results, quality  = resolve_canonizedStr_from_row_text2(building_block_str, ontology.TR_chapters, Building_block_type_Enum.TR)
                final_type = Building_block_type_Enum.TR

        if Building_block_type == Building_block_type_Enum.TR:
            results, quality  = resolve_canonizedStr_from_row_text2(building_block_str, ontology.TR_chapters, Building_block_type_Enum.TR)
            final_type = Building_block_type_Enum.TR
            if len(results) == 0:
                results, quality  = resolve_canonizedStr_from_row_text2(building_block_str, ontology.TM_Masechtot, Building_block_type_Enum.TM)
                final_type = Building_block_type_Enum.TM
        
        results = find_str_overlap2(results)

    except Exception as ex:
        print("Issue in function: canonize_talmud_building_block")
        print(ex)

    if len(results) > 0:
        return results, final_type, quality
    else:
        return None, None, None

# this function canonize general ref words
def canonize_general_ref_words(text, ontology):
    try: 
        results, _ = resolve_canonizedStr_from_row_text2(text, ontology.General_Ref_Words, Building_block_type_Enum.R)
    
        results = find_str_overlap2(results)

    except Exception as ex:
        print("Issue in function: canonize_general_ref_words")
        print(ex)

    if len(results) > 0:
        return results
    else:
        return None
    
# this function canonize the Rambam Hilchot Hayad Hahazaka
def canonize_Hilchot_Yad_Hahazaka(text, ontology):
    try: 
        results, _ = resolve_canonizedStr_from_row_text2(text, ontology.Hayad_Hahazaka_abbr, Building_block_type_Enum.RR)
    
        results = find_str_overlap2(results)

    except Exception as ex:
        print("Issue in function: canonize_Hilchot_Yad_Hahazaka")
        print(ex)

    if len(results) > 0:
        return results
    else:
        return None

# This function gets a row name and finds its canonized representation
def canonize_book_and_author_building_block(building_block_str, Building_block_type, ontology, check_Masechtot = True):
    try:
        #check if the name we found is somthing like הרב, הגאון (with no other name) which we should skip
        if building_block_str.strip() in ontology.Authors_2_skip:
            return None, None, None

        #check if the name we found is somthing like בבא (with no masechet name) which we should skip
        if building_block_str.strip() in ontology.books_2_skip:
            return None, None, None

        # usually we don't count str with 2 letters, however 
        # Samson ben Abraham of Sens has a 2 letter acronym  
        if building_block_str == "רש":
            pass
        elif len(building_block_str) <= 2: # its a too short string no such book/author
            return None, None, None
        
        #lets search for book and author
        results = []
        final_type = None
        quality = None 
        if Building_block_type in [Building_block_type_Enum.BN]:
            results , quality = resolve_canonizedStr_from_row_text2(building_block_str, ontology.Books, Building_block_type_Enum.BN)
            final_type = Building_block_type_Enum.BN
            if len(results) == 0:
                results , quality = resolve_canonizedStr_from_row_text2(building_block_str, ontology.Authors, Building_block_type_Enum.AN)
                if len(results) != 0 and quality == Ref_quality.Medium:
                    temp_results = [item for item in results if item.canonizedStr not in ontology.low_confidance_authors]
                    results = temp_results
                    final_type = Building_block_type_Enum.AN

        if Building_block_type in [Building_block_type_Enum.AN]:
            results , quality = resolve_canonizedStr_from_row_text2(building_block_str, ontology.Authors, Building_block_type_Enum.AN)
            if len(results) != 0 and quality == Ref_quality.Medium:
                temp_results = [item for item in results if item.canonizedStr not in ontology.low_confidance_authors]
                results = temp_results
                final_type = Building_block_type_Enum.AN

            if len(results) == 0:
                results , _ = resolve_canonizedStr_from_row_text2(building_block_str, ontology.Books, Building_block_type_Enum.BN)
                final_type = Building_block_type_Enum.BN
        
        # some time a mesechet (TM) is alos tagged as book name
        if check_Masechtot:
            if len(results) == 0: 
                results, quality  = resolve_canonizedStr_from_row_text2(building_block_str, ontology.TM_Masechtot, Building_block_type_Enum.TM)
                final_type = Building_block_type_Enum.TM

        results = find_str_overlap2(results)

    except Exception as ex:
        print("issue in func: canonize_book_and_author_building_block")
        print(ex)
        print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(ex).__name__, ex)
    
    if len(results) > 0:
        return results, final_type, quality
    else:
        return None, None, None

# checks if a book is a commentary of another book
def is_commentary(books_objs_list, commented_book, ontology):
    if books_objs_list == None or len(books_objs_list)==0:
        return False
    if commented_book in ("", None):
        return False
    
    #retrive the books
    books_list = []
    for book_obj in books_objs_list:
        books_list.append(book_obj.canonizedStr)

    #check if the book really comments the commented_book
    for book in books_list:
        try:
            book_details = ontology.Books_details[book]
            if book_details.commentary_of == commented_book:
                return True #its indeed a commentary
        except Exception as E:
            print("issue in function: is_commentary")
            print("Could not find the book: ", book[::-1])
            print(E)
            continue
    #its not a commentary
    return False
    
# used for refObj checking compatibility between refrence ingredients
# check that the book was indeed writen by that author
def check_book_vs_author_compatibility(books, authors, ontology):
    try:
        if len(authors) == 0 or len(books) == 0: 
            return True  
        # first transform the objects to simple strings
        books_list = []
        authors_list = []
        for book in books:
            books_list.append(book.canonizedStr)

        for author in authors:
            authors_list.append(author.canonizedStr)

        #lets search for compatibility between the author and the book
        for author in authors_list:
            try:
                Author_bio = ontology.Authors_Biography[author]
            except Exception as ex:
                print("issue in func: check_book_vs_author_compatibility")
                print("could not find Author: ", author[::-1])
                print(ex)
                continue #continue to next author in the list 

            for book in books_list:
                if book in Author_bio.books:
                    if DEBUG:
                        print("Author: ", author[::-1], " book: ", book[::-1])
                    return True #we found lets exit!
    except Exception as E:
        print("issue in function: check_book_vs_author_compatibility")
        print(E)
        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
    #we didn't found any compatibility
    return False

# Canonization process for tags like RT, R
def canonize_general_building_block(building_block_str, Building_block_type, ontology):
    try:
        #check if the name we found is somthing like הרב, הגאון (with no other name) which we should skip
        if building_block_str.strip() in ontology.Authors_2_skip:
            return None, None, None

        #check if the name we found is somthing like בבא (with no masechet name) which we should skip
        if building_block_str.strip() in ontology.books_2_skip:
            return None, None, None

        if len(building_block_str) <= 2: # its a too short string no such book/author
            return None, None, None
        
        #lets search for book and author
        quality = None 
        
        try:
            books_results , quality = resolve_canonizedStr_from_row_text2(building_block_str, ontology.Books, Building_block_type_Enum.BN)
            if quality == Ref_quality.High: #we fully covered teh text string, lets log and exist
                return books_results, Building_block_type_Enum.BN, quality
            
            author_results , quality = resolve_canonizedStr_from_row_text2(building_block_str, ontology.Authors, Building_block_type_Enum.AN)
            if quality == Ref_quality.High: #we fully covered teh text string, lets log and exist
                return author_results, Building_block_type_Enum.AN, quality

            TM_results , quality = resolve_canonizedStr_from_row_text2(building_block_str, ontology.TM_Masechtot, Building_block_type_Enum.TM)
            if quality == Ref_quality.High: #we fully covered teh text string, lets log and exist
                return TM_results, Building_block_type_Enum.TM, quality

            TR_results , quality = resolve_canonizedStr_from_row_text2(building_block_str, ontology.TR_chapters, Building_block_type_Enum.TR)
            if quality == Ref_quality.High: #we fully covered teh text string, lets log and exist
                return TR_results, Building_block_type_Enum.TR, quality

            AB_results , quality = resolve_canonizedStr_from_row_text2(building_block_str, ontology.Archi_books, Building_block_type_Enum.AB)
            if quality == Ref_quality.High: #we fully covered teh text string, lets log and exist
                return TR_results, Building_block_type_Enum.AB, quality
        except Exception as ex:
            print("issue in func: canonize_general_building_block")
            print(ex)

        #if we don't have a high quality results, lets collect all the results we have
        #TODO fine tune the results agregation according to the exact words, that matchs the rsults e.g.
        # and not just be selecting the first acording to priority
        final_results = []
        if len(AB_results) > 0:
            final_results.extend(AB_results)
        elif len(author_results) > 0:
            final_results.extend(author_results)
        elif len(books_results) > 0:
            final_results.extend(books_results)
        
    
        #elif len(TM_results) > 0:
        #    final_results.extend(TM_results)
        #elif len(TR_results) > 0:
        #    final_results.extend(TR_results)
        
        
        #may be we have duplicate items
        final_results = remove_duplications(final_results)
        if final_results == None:
            print("DEBUG: final res == none")
            pass
        final_results = find_str_overlap2(final_results)
        if final_results == None:
            print("DEBUG: final res == none")
            pass

        # remove low confidance author since we are dealing with Medium quality
        temp_results = [item for item in final_results if item.canonizedStr not in ontology.low_confidance_authors]
        final_results = temp_results

        if len(final_results) == 1:
            return final_results, final_results[0].type, Ref_quality.Medium
        elif len(final_results) > 1:
            return final_results, Building_block_type, Ref_quality.Medium
        else:
            return None, None, None
    
    
    except Exception as ex:
        print("issue in func: canonize_general_building_block")
        print(ex)
    
    return None, None, None

#remove duplicate items of Cnonize_abbrv
def remove_duplications(Cnonize_abbrv_list):
    try:
        #if we have only one element or less lets return
        if len(Cnonize_abbrv_list) < 2:
            return Cnonize_abbrv_list

        final_results = []
        for item in Cnonize_abbrv_list:
            item_already_saved = False
            for stored_item in final_results:
                if item == stored_item: #we found tourselves, lets continue
                    continue
                if stored_item.canonizedStr == item.canonizedStr: #we found a duplication
                    item_already_saved = True
                    break
            #Lets just add the item
            if item_already_saved == False:
                final_results.append(item)
            #if we already have the item, lets check may be the none stored item has high quality 
            if item_already_saved == True:
                if stored_item.quality != Ref_quality.High: 
                    if item.quality == Ref_quality.High:
                        final_results.remove(stored_item)
                        final_results.append(item)
    except Exception as ex:
        print("issue in func: remove_duplications")
        print(ex)
        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
    return final_results

# we check that the string is really the author/book we assumed and create the canonize-abbreviation object
def create_Cnonize_abbrv(Building_block_type, text, ontology):
    # Note: we return high quality becuase of 2 factors:
    # 1. the model identify it
    # 2. the abbreviation was found in the text
    longest_abbr = None
    try:
        #Rambam stuff
        if Building_block_type == Building_block_type_Enum.RR:
            longest_abbr = find_longest_abbr(ontology.Authors['ר´ משה בן מיימון'], text)
            if longest_abbr != None:
                return Cnonize_abbrv(longest_abbr ,"ר´ משה בן מיימון", Ref_quality.High, Building_block_type_Enum.AN)
        # Tur and Shulhan Aruch stuff
        if Building_block_type == Building_block_type_Enum.TSR:
            longest_abbr = find_longest_abbr(ontology.Authors["ר´ יעקב בן אשר"], text)
            if longest_abbr != None:
                return Cnonize_abbrv(longest_abbr ,"ר´ יעקב בן אשר", Ref_quality.High, Building_block_type_Enum.AN)
            
            longest_abbr = find_longest_abbr(ontology.Archi_books["ארבע טורים"], text)
            if longest_abbr != None:
                return Cnonize_abbrv(longest_abbr ,"ארבע טורים", Ref_quality.High, Building_block_type_Enum.BN)

            longest_abbr = find_longest_abbr(ontology.Books["חושן משפט"], text)
            if longest_abbr != None:
                return Cnonize_abbrv(longest_abbr ,"חושן משפט", Ref_quality.High, Building_block_type_Enum.BN)

            longest_abbr = find_longest_abbr(ontology.Books["ספר אבן העזר"], text)
            if longest_abbr != None:
                return Cnonize_abbrv(longest_abbr ,"ספר אבן העזר", Ref_quality.High, Building_block_type_Enum.BN)

            longest_abbr = find_longest_abbr(ontology.Books["יורה דעה"], text)
            if longest_abbr != None:
                return Cnonize_abbrv(longest_abbr ,"יורה דעה", Ref_quality.High, Building_block_type_Enum.BN)

            longest_abbr = find_longest_abbr(ontology.Books["אורח חיים"], text)
            if longest_abbr != None:
                return Cnonize_abbrv(longest_abbr ,"אורח חיים", Ref_quality.High, Building_block_type_Enum.BN)

            '''
            longest_abbr = find_longest_abbr(ontology.Authors["ר´ יוסף קארו"], text)
            if longest_abbr != None:
                return Cnonize_abbrv(longest_abbr ,"ר´ יוסף קארו", Ref_quality.High, Building_block_type_Enum.AN)
                
            longest_abbr = find_longest_abbr(ontology.Books["שולחן ערוך"], text)
            if longest_abbr != None:
                return Cnonize_abbrv(longest_abbr ,"שולחן ערוך", Ref_quality.High, Building_block_type_Enum.AN)   
            ''' 

    except Exception as ex:
        print(ex)
        print("Issue in function: create_Cnonize_abbrv")
        print('Error on line {}'.format(sys.exc_info()
                [-1].tb_lineno), type(ex).__name__, ex)

    # if we are here then the text wan't recognized
    return None

# remove item that thier abbreviation is a sub string of another item
def find_str_overlap2(cnonize_abbrv_list):
    try:
        # we need more than 1 item in order to compare between items...
        if len(cnonize_abbrv_list) < 2:
            return cnonize_abbrv_list
        
        # lets see if all the results are totaly based on the exact same word.
        # in that case we embiguty of the results, and there is nothing we can do at this level
        prev_item_abbre_str = ""
        same_abbr_str_flag = True
        for item in cnonize_abbrv_list:
            if prev_item_abbre_str == "": #we are still at the first word, lets just assign it and continue
                prev_item_abbre_str = item.abbreviation
                continue
            else:
                # the abbr are diffrent, mark it and lets continue the function flow
                if prev_item_abbre_str != item.abbreviation: 
                    same_abbr_str_flag = False
                    break
        
        # all the abbreviations are exactly the same, lets just return 
        if same_abbr_str_flag == True:
            return cnonize_abbrv_list

        # lets search for overlaps
        sub_cnonize_abbrv_list = []

        #find all the items that are sub of another item
        for item in cnonize_abbrv_list:
            for sub_item in cnonize_abbrv_list:
                if sub_item == item: # we found ourselve lets continue
                    continue
                idx = item.abbreviation.find(sub_item.abbreviation)
                if (idx != -1) and len(sub_item.abbreviation) < len(item.abbreviation):
                    sub_cnonize_abbrv_list.append(sub_item)

        #now remove the sub item from our original list (by creating a new one)
        final_cnonize_abbrv_list = []
        for item in cnonize_abbrv_list:
            if item not in sub_cnonize_abbrv_list:
                final_cnonize_abbrv_list.append(item)
        
    except Exception as ex:
        print("issue in func: find_str_overlap2")
        print(ex) 

    return final_cnonize_abbrv_list

#this function tries to extract an item (TR or AB or TM) name from row text and returns its canonization
def resolve_canonizedStr_from_row_text2(text, abbreviationDict, Building_block_type):
    high_quality_reults = [] # high quality results means that the ENTIER provided text matchs a name/abbr from our DB
    results = []
    if text == "": return results, Ref_quality.Low
    text = text.strip()
    text_words = text.split()

    try:
        # first let's see if the text is equal to the canonized name, if yes we finished 
        for canonizedStr, abbr_list in abbreviationDict.items():
            canonizedStr = canonizedStr.strip()
            # if we have the exact str as the canonized one just return it
            if text == canonizedStr:
                high_quality_reults.append(Cnonize_abbrv(text ,canonizedStr, Ref_quality.High, Building_block_type))

        #Canonized strings are unique if we found lets exist
        if len(high_quality_reults) > 0: return high_quality_reults, Ref_quality.High

        #we didn't found a fully matched cnonized name to the given text, lest do a search string
        for canonizedStr, abbr_list in abbreviationDict.items():
            canonizedStr = canonizedStr.strip()

            # control flow flag
            abbreviation_found = False
            
            #lets start by searching exact match, e.g. the text string exactly matches an abreviation
            
            for abbreviation in abbr_list:
                #abbreviation = abbreviation.strip()
                if abbreviation == "":
                    continue
                if abbreviation == text:
                    high_quality_reults.append(Cnonize_abbrv(text ,canonizedStr, Ref_quality.High, Building_block_type)) #abbr' are not unique so lets move to the next name, e.g. we may have a 2 names with this exact abbreviation
                    abbreviation_found =  True
                    break
            '''
            
            if text in abbr_list:
                high_quality_reults.append(Cnonize_abbrv(text ,canonizedStr, Ref_quality.High, Building_block_type)) #abbr' are not unique so lets move to the next name, e.g. we may have a 2 names with this exact abbreviation
                abbreviation_found =  True
            '''

            if abbreviation_found: continue # if we found an abbreviation, it means we already logged it canonized string, lets move to the next name

            # if we are here we didn't find an exact match lets search for a sub string
            for abbreviation in abbr_list:
                abbreviation = abbreviation.strip()
                if abbreviation == "":
                    continue
                
                # if the abreviation is built from multiple words then lets just do a simple text search
                if len(abbreviation.split()) > 1:
                    idx = text.find(abbreviation) # we choose to find the abbreviation we know about in the text
                    if (idx != -1):
                        longest_abbr = find_longest_abbr(abbr_list, text)
                        if longest_abbr == None:
                            longest_abbr = abbreviation
                        results.append(Cnonize_abbrv(longest_abbr ,canonizedStr, Ref_quality.Medium, Building_block_type))
                        break
                # if the abreviation is build from a single word lets try to match the abbreviation to a word
                else:
                    result_found = False
                    for text_w in text_words:
                        idx = text_w.find(abbreviation)
                        if (idx != -1):  # checking maybe morfological lettes were added to the abbreviation, otherwise, if the abbreviation is too much inside the word then its probably not the abbreviation,  but part of another word
                            if (idx < 2):
                                if idx != 0: # we have some prefix letter, lets check its a legal Hebrew prefix latter
                                    if text_w[0] not in ["ב", "ל", "כ", "ו", "ה", "ש", "מ"]:
                                        continue
                                if (len(text_w) - len(abbreviation) < 2): #if the text word is much longer then abbreviation is probably not correct
                                    # first lets check if we can find teh full text inside one of the abbreviations
                                    longest_abbr_full_text = find_longest_abbr(abbr_list, text)
                                    # now lets check if the splited text (any word from the original text)
                                    longest_abbr_split_text = find_longest_abbr(abbr_list, text_w) #we found an abbr but may be there is another one, longer, that still match the text_w
                                    
                                    if len(longest_abbr_full_text) > len (longest_abbr_split_text):
                                        longest_abbr = longest_abbr_full_text
                                    else:
                                        longest_abbr = longest_abbr_split_text

                                    # TODO longest_abbr may be None - need to handle it

                                    # lets check if abbreviation is at the end of the word (Its a must) otherwise its a wrong match
                                    # for example the book שמות may be found in the word שמותר but this is a wrong match as we know
                                    # that a book/author name can't have additional letters after its original name
                                    if text_w.endswith(longest_abbr):
                                        results.append(Cnonize_abbrv(longest_abbr ,canonizedStr, Ref_quality.Medium, Building_block_type))
                                        result_found = True
                                    
                        
                    # if we found a matching abbreviation, we can exist this entry's abbreviation
                    if result_found == True: 
                        break


        #if we have high quality reustls lets return it, otherwise return the medium quality results 
        if len(high_quality_reults) > 0: return high_quality_reults, Ref_quality.High
        
        #if we have multiple results lets check no res is a sub set of another res
        reduced_results = []
        #super_word_found = False
        for w in results:
            super_word_found = False
            for other_word in results:
                if other_word.abbreviation == w.abbreviation: continue # we just found oursleves move to next word
                idx = other_word.abbreviation.find(w.abbreviation)
                if idx != -1: #we found a word that include W, hence we want to exclude W from the final list of super_words
                    super_word_found = True
                    break
                
            if super_word_found != True: # the current w is not included in any other_word so lets keep it 
                reduced_results.append(w)

        # in case we have multiple results and one of them is from "unknowen Rabbi", lets remove it 
        final_results = []
        if len(reduced_results) > 1:
            for item in reduced_results:
                idx = item.canonizedStr.find("לא ידוע")
                if idx != -1:    
                    continue
                else:
                    final_results.append(item)
        
        # if we deleted everything. then lets keep the original
        if len(final_results) == 0:
            final_results = reduced_results

        # if we have so much results this is probably a too short/wormg string
        if len(final_results) >= 4: return [], Ref_quality.Low # we found too much results lets just return nothing

    except Exception as ex:
        print(ex)
        print("Issue in function: resolve_canonizedStr_from_row_text2")
        print('Error on line {}'.format(sys.exc_info()
                [-1].tb_lineno), type(ex).__name__, ex)
    
    return final_results, Ref_quality.Medium

# from a list of abbreviations find the longest that is still contained in the given text
def find_longest_abbr(abbr_list, text):
    try:    
        if text == "": 
            return ""
        if len(abbr_list) == 0: 
            return None
        if len(abbr_list) == 1: 
            return abbr_list[0]
        
        longet_abbr = ""
        for abbr in abbr_list:
            if len(abbr) > len(longet_abbr): #we found a longer abbr, lets check it also sub string of the given text 
                idx = text.find(abbr)
                if idx != -1: # its really a substring and its longer, then the current we have, so lets change
                    longet_abbr = abbr
        
        if longet_abbr == "":
            return None
        else: 
            return longet_abbr

    except Exception as ex:
        if DEBUG:
            print("issue in func: find_longest_abbr")
            print(ex)

# this function resolve the father by the son, for example masechet by chapter name
# basically the text here should be canonized
def resolve_father_from_childrens(text_list, mapping_dict):
     
    if type(text_list) == str:
        text_list = [text_list]
    results = []
    if len(text_list) == 0: return results 
    for text in text_list:
        if text == "": continue
        text = text.strip()
        #first we search the exact full string 
        for father_item, childrens in mapping_dict.items():
            for child in childrens: 
                try:
                    child = child.strip()
                except:
                    continue
                if text == child: #we found the exact text in the childrens list
                    if father_item != "":
                        results.append(father_item)
  
    return results

# check the book date is less then the data the responsa was written
def check_book_date(refObject, ontology):
    try: 
        # first check if the book is later than 1500 CE which is out of the corpus we are curreently scanning
        # which means its for sure an anachronistic_ref
        ref_book_author_bio = retrive_author_bio_from_book(refObject.book_name, ontology)
        if ref_book_author_bio == None: 
            return False # we can't check lets just exist
        if ref_book_author_bio.DATE_OF_BIRTH > 1500:
            return True
        
        #if we don't have a responsa source lets return
        if refObject.text_source == "" and refObject.text_author == "": return False
        
        # fuirst check if we have the text author
        text_author_bio = None
        if refObject.text_author != "":
            try:
                text_author_bio = ontology.Authors_Biography[refObject.text_author]
            except:
            #couldnot find author name in the bio
                if DEBUG:
                    print("un-recognized author: ", refObject.text_author)
                # if we are here we have some issue in our DB, lets return
                return False
        
        #no text author lets serch via the text source 
        else:
            text_author_bio = retrive_author_bio_from_book(refObject.text_source, ontology)
            if text_author_bio == None: 
                return False

        # the author of the ref died before the book author in the ref was born, 
        # it doesn't make sense! so lets remove the book mentioned in the ref
        if text_author_bio.DATE_DIED <= ref_book_author_bio.DATE_OF_BIRTH + 40:
            return True
        else:
            return False

    except:
        if DEBUG:
            print("Function: 'check_book_date' could not resolve: ", refObject.book_name)
        pass
    
    return False

# check if the mentioned author lived before the author of the responsa
# if no, we probably have an error 
def check_author_date(refObject, ontology):

    ref_author_bio = None
    text_author_bio = None
    #if we don't have a responsa source lets return
    if refObject.text_source == "" and refObject.text_author == "": return False
    
    # fuirst check if we have the text author
    try: 
        if refObject.text_author != "":
            try:
                text_author_bio = ontology.Authors_Biography[refObject.text_author]
            except:
            #couldnot find author name in the bio
                if DEBUG:
                    print("un-recognized author: ", refObject.author_name)
                # if we are here we have some issue in our DB, lets return
                return False
        #no text author lets serch via the text source 
        else:
            text_author_bio = retrive_author_bio_from_book(refObject.text_source, ontology)
            if text_author_bio == None: 
                return False
        
        try:
            ref_author_bio = ontology.Authors_Biography[refObject.author_name]
        except:
            #couldnot find author name in the bio
            if DEBUG:
                print("un-recognized author: ", refObject.author_name)
            return False

        # the author of the ref died before the name in the ref born, it doesn't make sense! 
        # so lets remove the author mentioned in the ref
        #if ref_author_bio.DATE_OF_BIRTH == None:
        #    return False
        
        if text_author_bio.DATE_DIED <= ref_author_bio.DATE_OF_BIRTH + 20:
            return True
        else:
            return False
    except:
        if DEBUG:
            print ("iisue in function: check_author_date" )
    
    return False

# given a ref lets return the bio of its author
def retrive_author_bio_from_book(text_source_name, ontology):
    if text_source_name == "":
        return None
    # the text source name is not canonized, lets find the exact source/book name
    book_found = True
    final_book = ""
    candidate_books = []
    for book_name, book_abbrevs in ontology.Books.items():
        if book_name == "": continue

        for single_book_abbrev in book_abbrevs:
            if single_book_abbrev == "": continue
            
            idx = text_source_name.find(single_book_abbrev)  
            if (idx != -1): 
                candidate_books.append(book_name)
                break # we found a book lets move to next optional book  

    
    #lets retrive the longets book name
    if len(candidate_books) == 1: # just one book in the list, lets just take it
        final_book = candidate_books[0]
    elif len(candidate_books) > 1: # Too much book lets take the longer
        for book in candidate_books:
            if len(book) > len(final_book):
                final_book = book
    else: # we didn't found any book
        book_found = False

    if (book_found): 
        #we found the book, lets find the author of this book
        for _ , Author_bio in ontology.Authors_Biography.items():
            if final_book in Author_bio.books:
                return Author_bio
        # if we are here we could not resolve the author BIO lets
        final_book = final_book[::-1]
        if DEBUG:
            print("could not resolve who wrote the book: {0} e.g. this book has no author in the system DB. function: retrive_author_bio_from_book ".format(final_book))

    else:    
        text_source_name = text_source_name[::-1]
        if DEBUG:
            print("the string: {0} don't conatin any book. function: retrive_author_bio_from_book ".format(text_source_name))

    
    return None


