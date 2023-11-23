# Project: Hebrew Reference extractor
#
# Created by: Nati Ben-Gigi
# Date: 11/2023
#
# License: MIT
# Copyright: Nati Ben-Gigi 2023
#
# File: 
# Description: scan_functions_base.py
# the initial base loops for retrieving text files from the corpus and scan it

import os
from NLP_model_API import *
from inference_main_loops import *
from BERT.tag_single_text_by_BERT_CRF import *
from bidi.algorithm import get_display
from enum import Enum

class DirectoryStatus(Enum):
    NOT_EXIST = "Directory does not exist"
    EMPTY = "Directory is empty"
    ONLY_FILES = "Contains only files"
    ONLY_SUBDIRECTORIES = "Contains only subdirectories"
    BOTH = "Contains both files and subdirectories"

# check the type of content of a folder
def directory_contents_type(directory):
    if not os.path.exists(directory):
        return DirectoryStatus.NOT_EXIST

    if not os.listdir(directory):
        return DirectoryStatus.EMPTY

    has_files = False
    has_subdirs = False

    for entry in os.listdir(directory):
        full_path = os.path.join(directory, entry)
        if os.path.isdir(full_path):
            has_subdirs = True
        elif os.path.isfile(full_path):
            has_files = True

        if has_files and has_subdirs:
            return DirectoryStatus.BOTH

    if has_files:
        return DirectoryStatus.ONLY_FILES
    else:
        return DirectoryStatus.ONLY_SUBDIRECTORIES

# get the last sub folder oof a path
# Note: If the given path ends with a slash (e.g., "/path/to/your/directory/"), 
# then os.path.basename() will return an empty string
def get_last_subfolder(full_path):
    # Normalize the path to ensure it has consistent directory separators
    normalized_path = os.path.normpath(full_path)
    
    # Extract the last subfolder name
    last_subfolder = os.path.basename(normalized_path)
    
    return last_subfolder

coding1 = "cp862"
coding1 = "cp1255"

#retrieve the source name from thr file name by number of words
def extract_Title_from_file_name_by_SIMAN(file_Name_layer1):
    file_Name_layer1 = file_Name_layer1.strip(".txt")
    words = file_Name_layer1.split()
    final_name = ""
    for word in words:
        if word == "סימן":
            return final_name[:-1]
        else:
            final_name += word + " "

    #in case by some reason the word "סימן" doesn't exist
    return final_name[:-1]

#read a words-tags file and return a list of words and another list of tags   
def read_word_tags_from_file(file_path):
    FileHandler = open(file_path, "r", encoding="utf8") 
    Lines = FileHandler.readlines()

    words = []
    tags = []
    # Strips the newline words
    for line in Lines:
        line = line.replace('"', '״')
        line = line.replace("'", '´')
        try:
            elemntsList = line.split()
            if len(elemntsList) == 2:
                words.append(elemntsList[0])
                tags.append(elemntsList[1])

        except:
            continue
    return words, tags

# find a file in a given directory (and its sub directory)
def find(name, path):
    for root, dirs, files in os.walk(path):
        if name in files:
            return os.path.join(root, name)

# a generator class that return (yield) a file content per next(scan_corpus_obj) iteration
def scan_corpus(source_Data_path, encoding_value = "utf8"):
    for root, dirs, files in os.walk(source_Data_path):
        for fileName in files:
            try:
                # find the last folder in the entire path string
                dir = root[root.rfind("/"):]
                dir = dir[1:]  # removing the char "/" from the folder name

                if fileName in [".DS_Store", "._.DS_Store"]:
                    # skip some entries (which are not real files name) python adds to the files list
                    continue

                FullFilePath = os.path.join(root, fileName)
                
                f = open(FullFilePath, 'r', encoding=encoding_value)
                content = f.read()
                f.close()

                #Skipping responsa project notes file
                if isNotesFile(content):
                    continue

                # clean the text
                clean_content, content_title = clean_text2(content, encoding_value, True)

                yield clean_content, content_title, root, FullFilePath, fileName

            except Exception as ex:
                print("issue in function: scan_corpus")
                print ('type is:', ex.__class__.__name__)
                print ('type is:', ex)
                break

#this function scans a corpus and save teh BERT CRF rabbinic tags to files
def tag_by_BERT_CRF_rabbinic_full_corpuse(source_files_path, target_files_path):
    result = directory_contents_type(source_files_path)
    
    if result.value in [DirectoryStatus.NOT_EXIST, DirectoryStatus.EMPTY]:
        raise  Exception("invalid or empty folder")
    elif result.value ==  DirectoryStatus.ONLY_SUBDIRECTORIES:
        input_books_folders = os.listdir(source_files_path)
    else:
        last_subfolder = get_last_subfolder(source_files_path)
        input_books_folders = [""]
    
    try:
        layer_1_output_folder = target_files_path + "/layer1"
        layer_2_output_folder = target_files_path + "/layer2"
        num_of_un_procssed_files = 0

        dual_layers_tagger = BERT_CRF_Rabbinic_layer1_2()

        for book_folder in input_books_folders:
            full_book_path = os.path.join(source_files_path, book_folder)

            files_iter = iter(scan_corpus(full_book_path))
            while True:
                try:
                    clean_content, content_title, root, FullFilePath, fileName = next(files_iter)
                    # invoke the layer 1 and layer 2 model on the responsa text, return a set of
                    layer_1_2_mergedResults  = dual_layers_tagger.tag_text_layer_1_2(clean_content)
                    if layer_1_2_mergedResults == 0:  # we had some issue with this responsa, lets log the problematic file and move to the next file
                        num_of_un_procssed_files += 1
                        continue

                    target_final_file_path_layer_1 = FullFilePath.replace(
                        source_files_path, layer_1_output_folder)
                    target_final_file_path_layer_2 = FullFilePath.replace(
                        source_files_path, layer_2_output_folder)

                    # build the path if not exist
                    final_folder_layer1 = target_final_file_path_layer_1.replace(
                        fileName, "")
                    final_folder_layer2 = target_final_file_path_layer_2.replace(
                        fileName, "")
                    if not os.path.exists(final_folder_layer1):
                        os.makedirs(final_folder_layer1)
                    if not os.path.exists(final_folder_layer2):
                        os.makedirs(final_folder_layer2)

                    # aggrgate the tagged results/content
                    final_tagged_content_layer_1 = ""
                    final_tagged_content_layer_2 = ""
                    for item in layer_1_2_mergedResults:
                        line_layer_1 = item[0] + " " + item[1] + "\n"
                        final_tagged_content_layer_1 += line_layer_1

                        line_layer_2 = item[0] + " " + item[2] + "\n"
                        final_tagged_content_layer_2 += line_layer_2

                    final_tagged_content_layer_1 += "\n"
                    final_tagged_content_layer_2 += "\n"

                    # save the final content to files
                    try:
                        target_final_file_handler_layer_1 = open(
                            target_final_file_path_layer_1, "w+", encoding="utf8")
                        target_final_file_handler_layer_1.write(
                            final_tagged_content_layer_1)
                        target_final_file_handler_layer_1.close()

                        target_final_file_handler_layer_2 = open(
                            target_final_file_path_layer_2, "w+" , encoding="utf8")
                        target_final_file_handler_layer_2.write(
                            final_tagged_content_layer_2)
                        target_final_file_handler_layer_2.close()
                    except Exception as e:
                        print(e)

                    print("complet file: " + FullFilePath)
                except Exception as e:
                    print(e)
                    print(
                        "No more files in the corpus OR issue in func process_mallet_format_files_and_save_word_tags_files")
                    break
    

    except Exception as ex:
        print("issue in function: scan_corpus")
        print ('type is:', ex.__class__.__name__)
        print ('type is:', ex)

# this function contains multiple steps:
# 1. retrieve the text and infer it by using BERT CRF rabbinic
# 2. process the above text-tags and output a list references
def retrive_Refrences_from_corpuse(corpuse_folder, save_tagged_corpuse = False, encoding_value = 'utf8'):

    result = directory_contents_type(corpuse_folder)
    
    if result.value in [DirectoryStatus.NOT_EXIST, DirectoryStatus.EMPTY]:
        raise  Exception("invalid or empty folder")
    elif result.value ==  DirectoryStatus.ONLY_SUBDIRECTORIES:
        input_books_folders = os.listdir(corpuse_folder)
    else:
        last_subfolder = get_last_subfolder(corpuse_folder)
        input_books_folders = [""]
    
    num_of_un_procssed_files = 0

    dual_layers_tagger = BERT_CRF_Rabbinic_layer1_2()

    for book_folder in input_books_folders:
        full_book_path = os.path.join(corpuse_folder, book_folder)
        
        if full_book_path.find(".DS_Store") != -1: continue
        
        files_iter = iter(scan_corpus(full_book_path, encoding_value))
        while True:
            try:
                clean_content, content_title, root, FullFilePath, fileName = next(files_iter)
                # invoke the layer 1 and layer 2 model on the responsa text, return a set of
                layer_1_2_mergedResults  = dual_layers_tagger.tag_text_layer_1_2(clean_content)
                if layer_1_2_mergedResults == 0:  # we had some issue with this responsa, lets log the problematic file and move to the next file
                    num_of_un_procssed_files += 1
                    continue
                
                if (save_tagged_corpuse == True):
                    save_tagged_file_results(layer_1_2_mergedResults, FullFilePath, corpuse_folder, fileName)

                text_source = resolve_text_source(FullFilePath)

                #print("==== resource ====")
                #print(text_source)

                # entry point for the processing of the tags and contracting refrences
                found_refrenses_list = process_layer_1_2_results_v2(
                layer_1_2_mergedResults, text_source, FullFilePath)
                
                yield found_refrenses_list

            except Exception as ex:
                if type(ex).__name__ == "StopIteration":
                    print("No more files in the corpus")
                    break
                else:
                    print(ex)
                    print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(ex).__name__, ex)
                    print("issue in func: retrive_tagged_results_from_saved_tagged_corpus")
                    raise ex

# split the full path of a file to the list of folder that compose this path 
def split_path(path):
    folders = []
    file_name = ""

    # If path is a file, remove the file name
    if os.path.isfile(path):
        file_name = os.path.basename(path)
        file_name, _ = clean_text2(file_name)
        path = os.path.dirname(path)

    while True:
        path, folder = os.path.split(path)

        if folder != "":
            folders.append(folder)
        else:
            if path != "":
                folders.append(path)

            break

    return folders, file_name

# this function checks if we have a single result, and we can convert author name to a book name
def check_canonization_results(results, file_path, folder, building_block_type):
    # we found something!
    text_source = ""
    if results != None: 
        if len(results) != 0:
            if len(results) != 1:
                print("function: resolve_text_source() we found multiple results!!!")
                print("full folder: ", file_path)
                print("sub folder: ", folder)
                return ""
            else:
                text_source = results[0].canonizedStr
            
        if building_block_type == Building_block_type_Enum.AN:
            # lets find from which book the text was taken
            try:
                if len(ontology.Authors_Biography[text_source].books) == 1:
                    book = ontology.Authors_Biography[text_source].books[0]
                    if len(book) != 0: # checking to book is not junt an empty string
                        text_source = book
            except Exception as ex:
                if DEBUG:
                    print("Warning: function: check_canonization_results, could not find the following author in the biblyoraphy file", text_source)

        
        return text_source
    else: 
        return "" 

# this function gets a path and retrieve the book (not Masechtet) mentioned in that path 
def resolve_text_source(file_path):
    try:
        if file_path == "": 
            return ""

        folders_list, file_name = split_path(file_path)
        #lets add the file name to the last idx of the folders list so teh file name will be checked only as last option
        folders_list.append(file_name)

        if len(folders_list) == 0:
            return ""
        
        clean_folder_list = []
        for item in folders_list:
            item, _ = clean_text2(item)
            item = ' '.join(item.split())
            clean_folder_list.append(item)


        folders_list = clean_folder_list 
        for folder in folders_list:
            #folder, _ = clean_text2(folder)
            #folder = ' '.join(folder.split())

            # there are 2 books with the name אורחות חיים but in our corpuse we have the book of "ר׳ אהרן בן משולם מלוניל" hence we will return this name
            if "אורחות חיים" in folders_list:
                return 'ר´ אהרן בן משולם מלוניל'
            # same for the book המנהיג
            if "המנהיג" in folders_list:
                return "ר´ אברהם בן נתן הירחי"
            # same for the book המנהיג
            if "העיטור" in folders_list:
                return "ר´ יצחק בן אבא מארי"
            if "החינוך" in folders_list:
                return "ספר החינוך"
            if "דרשות רי אבן שועיב" in folders_list:
                return "ר´ יהושע אבן שועיב"
            if "הגימטריאות" in folders_list:
                return "ר´ יהודה בן שמואל החסיד"
            if 'מנורת המאור { אלנקאוה }'  in folders_list:
                return "ר´ ישראל בן יוסף אלנקאוה"
            if ("תשובות מיימוניות" in folders_list) or ("הגהות מיימוניות" in folders_list):
                return "ר´ מאיר בן ברוך מרוטנבורג"
            if "הלכות מלכים רמבם-מלכים" in folders_list:
                return "ר´ משה בן מיימון"
            if "משנה תורה לרמבם { עם ראבד }" in folders_list:
                return "ר´ משה בן מיימון"
            if "בית הבחירה למאירי" in folders_list:
                return "ר´ מנחם בן שלמה המאירי"
            if "האגודה" in folders_list:
                return "ר´ אלכסנדר זוסלין הכהן"
            if "מגדל דוד ספר מצוה" in folders_list:
                return "ר´ דוד בן שמואל הכוכבי"
            if "מחזור ויטרי" in folders_list:
                return "ר´ שלמה יצחקי"
            if "תוספות הראש" in folders_list:
                return 'ר´ אשר בן יחיאל { הרא״ש }'
            if "ראש" in folders_list:
                return 'ר´ אשר בן יחיאל { הרא״ש }'
            if "ראש { פירוש לשס }" in folders_list:
                return 'ר´ אשר בן יחיאל { הרא״ש }'
            if "תוספות מהרם מרוטנבורג" in folders_list:
                return "ר´ מאיר בן ברוך מרוטנבורג"
            if "תוספות רבינו פרץ" in folders_list:
                return "ר´ פרץ בן אליהו מקורביל"
            if "תוספות ריד" in folders_list:
                return "ר´ ישעיה בן מאלי דטרני"
            if "השגות הראבד על הריף" in folders_list:
                return "ר´ אברהם בן דוד מפושקירה"
            if "דרשה לפסח לרוקח" in folders_list:
                return "ר´ אליעזר מגרמייזא"
            if "ראש השנה { לפי דפי הריף }" in folders_list:
                return "ר´ יהונתן הכהן מלוניל"
            if "אבן העזר טור-אבן-העזר" in folders_list:
                return "ר´ יעקב בן אשר"
            if "לקט יושר" in folders_list:
                return "ר´ יוסף בן משה"
            if "מגדל עוז" in folders_list:
                return "ר´ שם טוב בן אברהם אבן גאון"
            if "רש" in folders_list:
                return "ר´ שמשון בן אברהם משנץ"
            if "רן" in folders_list:
                return "ר´ ניסים גירונדי"
            
            if 'יסוד התשובהמחשבה-יסוד-התשובה = מחשבה-יסוד-התשובה' in folders_list:
                return "ר´ יונה גירונדי"
            if 'אגרת הרמבןמחשבה-אגרת-הרמבן = מחשבה-אגרת-הרמבן' in folders_list:
                return "ר´ משה בן נחמן גירונדי"
            if 'אגרת תימןמחשבה-אגרת-תימן = מחשבה-אגרת-תימן' in folders_list:
                return "ר´ משה בן מיימון"
            if 'אגרת תחית המתיםמחשבה-אגרת-תחית-המתים = מחשבה-אגרת-תחית-המתים' in folders_list:
                return "ר´ משה בן מיימון"
            if 'אגרת השמדמחשבה-אגרת-השמד = מחשבה-אגרת-השמד' in folders_list:
                return "ר´ משה בן מיימון"
            if 'היראהמחשבה-היראה = מחשבה-היראה' in folders_list:
                return "ר´ יונה גירונדי"
            

            if 'דרשה לראש השנה לרמבaן@@@מנהגים-דרשה-לראש-השנה=000010מנהגים-דרשה-לראש-השנה' in folders_list:
                return "ר´ משה בן נחמן גירונדי"
            if "הגדה של פסח לריטבaא@@@מנהגים-הגדה-של-פסח-לריטבא=000010מנהגים-הגדה-של-פסח-לריטבא" in folders_list:
                return "ר´ יום טוב בן אברהם אלאשבילי"
            if "הגדה של פסח לרשבaץ@@@מנהגים-הגדה-של-פסח-לרשבץ=000010מנהגים-הגדה-של-פסח-לרשבץ" in folders_list:
                return "ר´ שמעון בן צמח דוראן"
            if "הלכות לולב לראבaד@@@מנהגים-הלכות-לולב-לראבד=000010מנהגים-הלכות-לולב-לראבד" in folders_list:
                return "ר´ אברהם בן דוד מפושקירה"
            
            if "המחכים@@@מנהגים-המחכים=000010מנהגים-המחכים" in folders_list:
                return "ר´ נתן בן יהודה"
            if "מנהגי הרב זלמן יענט@@@מנהגים-מנהגים-זלמן-יענט=000010מנהגים-מנהגים-זלמן-יענט" in folders_list:
                return "ר´ יצחק אייזיק טירנא"
            if "משפט החרם@@@מנהגים-משפט-החרם=000010מנהגים-משפט-החרם" in folders_list:
                return "ר´ משה בן נחמן גירונדי"
            if "נימוקי ר' מנחם מרזבורק@@@מנהגים-נימוקי-מנחם=000010מנהגים-נימוקי-מנחם" in folders_list:
                return "ר´ מנחם בן פינחס ממירזבורג"
            


            if "ספרי" in folder: continue


            
            # Book name
            text_source_BN = ""
            results, _, _ = canonize_book_and_author_building_block(
                        folder, Building_block_type_Enum.BN, ontology, False)  
            # check if we found somthing, if yes, lets log it  
            if results != None and len(results) != 0:
                text_source_BN = check_canonization_results(results, file_path, folder, Building_block_type_Enum.BN)
                #return text_source
            
            #Archi BOOK
            text_source_AB = ""
            results, _, _ = canonize_book_and_author_building_block(
                        folder, Building_block_type_Enum.AB, ontology, False)  
            # check if we found somthing, if yes, lets log it  
            if results != None and len(results) != 0:
                text_source_AB = check_canonization_results(results, file_path, folder, Building_block_type_Enum.AB)
            
            # Author name
            text_source_AN = ""
            results, _, _ = canonize_book_and_author_building_block(
                        folder, Building_block_type_Enum.AN, ontology, False)
            # check if we found somthing, if yes, lets log it  
            if results != None and len(results) != 0:
                text_source_AN = check_canonization_results(results, file_path, folder, Building_block_type_Enum.AN)

            longest_str =  max(text_source_BN, text_source_AB, text_source_AN, key=len)
            if len(longest_str) != 0:
                return longest_str
            
            '''
            elif results != None and len(results) != 0:
                text_source = check_canonization_results(results, file_path, folder, Building_block_type_Enum.AB)
                return text_source
            # we didn't find anything, lets search for author name
            else:
                results, _, _ = canonize_book_and_author_building_block(
                        folder, Building_block_type_Enum.AN, ontology, False)

                # check if we found somthing, if yes, lets log it  
                if results != None and len(results) != 0:
                    text_source = check_canonization_results(results, file_path, folder, Building_block_type_Enum.AN)
                    return text_source
            '''


        if DEBUG:
            # Could not resolve any resource from the file path 
            print("Warning: function: resolve_text_source() Could not resolve any book/author from the file path")
            print("full folder: ", file_path)
        return ""
    
    except Exception as ex:
        print(ex)
        print("Issue in function: resolve_text_source")
        print('Error on line {}'.format(sys.exc_info()
                [-1].tb_lineno), type(ex).__name__, ex)
        return ""

# this function saves all the tagged resulst to files  
def save_tagged_file_results(layer_1_2_mergedResults, FullFilePath, corpuse_folder, fileName):

    dn = os.path.dirname(os.path.realpath(__file__))

    layer_1_output_folder = dn + "/tagged_corpus/layer1"
    layer_2_output_folder = dn + "/tagged_corpus/layer2"
    target_final_file_path_layer_1 = FullFilePath.replace(
        corpuse_folder, layer_1_output_folder)
    target_final_file_path_layer_2 = FullFilePath.replace(
        corpuse_folder, layer_2_output_folder)

    # build the path if not exist
    final_folder_layer1 = target_final_file_path_layer_1.replace(
        fileName, "")
    final_folder_layer2 = target_final_file_path_layer_2.replace(
        fileName, "")
    if not os.path.exists(final_folder_layer1):
        os.makedirs(final_folder_layer1)
    if not os.path.exists(final_folder_layer2):
        os.makedirs(final_folder_layer2)

    # aggrgate the tagged results/content
    final_tagged_content_layer_1 = ""
    final_tagged_content_layer_2 = ""
    for item in layer_1_2_mergedResults:
        line_layer_1 = item[0] + " " + item[1] + "\n"
        final_tagged_content_layer_1 += line_layer_1

        line_layer_2 = item[0] + " " + item[2] + "\n"
        final_tagged_content_layer_2 += line_layer_2

    final_tagged_content_layer_1 += "\n"
    final_tagged_content_layer_2 += "\n"

    # save the final content to files
    try:
        target_final_file_handler_layer_1 = open(
            target_final_file_path_layer_1, "w+", encoding="utf8")
        target_final_file_handler_layer_1.write(
            final_tagged_content_layer_1)
        target_final_file_handler_layer_1.close()

        target_final_file_handler_layer_2 = open(
            target_final_file_path_layer_2, "w+" , encoding="utf8")
        target_final_file_handler_layer_2.write(
            final_tagged_content_layer_2)
        target_final_file_handler_layer_2.close()
    except Exception as ex:
        print(ex)
        print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(ex).__name__, ex)
        print("issue in func: save_tagged_file_results")
        raise ex

# this fuc return a list of refrences extracted from tagged files
def retrive_tagged_results_from_saved_tagged_corpus(files_path):

    layer_1_source_Data_path = files_path + "/layer1"
    layer_2_source_Data_path = files_path + "/layer2"
    if not os.path.isdir(layer_1_source_Data_path) or not os.path.isdir(layer_2_source_Data_path):
        print("The corpus folder needs to be structured as: 'corpus_folder\layer1' and 'corpus_folder\layer2'. However, the given path lacks subfolders in this specified format for scanning a tagged corpus.")
        raise Exception("The corpus folder needs to be structured as: 'corpus_folder\layer1' and 'corpus_folder\layer2'. However, the given path lacks subfolders in this specified format for scanning a tagged corpus.")
    print("=====================stating collecting tagged results from tagged corpus=======================")
    files_iter = iter(scan_corpus(layer_1_source_Data_path))
    while True:
        try:
            # note the file name is the same for the 2 layers, the difrent is by the folder
            _ , content_title, _ , FilePath_layer1, file_Name_layer1_and_2 = next(files_iter)

            # We can extract the title by loking in the file strtaing words 
            content_title = extract_Title_from_file_name_by_SIMAN(file_Name_layer1_and_2)
            # lets finally read the data  for layer 1
            layer_1_words, layer_1_tags = read_word_tags_from_file(FilePath_layer1)
            _, layer_1_results, _ = construct_single_layer_results(layer_1_tags, layer_1_words, False)
            
            #find the coresponding layer 2 file
            FilePath_layer2 = FilePath_layer1.replace("layer1", "layer2")#find(file_Name_layer1_and_2, layer_2_source_Data_path)
            # lets read the data  for layer 2
            layer_2_words, layer_2_tags = read_word_tags_from_file(FilePath_layer2)
            _, layer_2_results, _ = construct_single_layer_results(layer_2_tags, layer_2_words, False)

            # get_disply() support mix of english and Hebrew
            print(get_display("scanning: " + file_Name_layer1_and_2))

            #merge the results of layer 1 and 2 to a single list
            layer_1_2_mergedResults = merge_layer_1_and_layer_2_results(layer_1_results, layer_2_results)

            text_source = resolve_text_source(FilePath_layer1)
            #print("==== resource ====")
            #print(text_source)
            # entry point for the processing of the tags and contracting refrences
            found_refrenses_list = process_layer_1_2_results_v2(
            layer_1_2_mergedResults, text_source, FilePath_layer1)
            
            yield found_refrenses_list
            
        except Exception as ex:
            if type(ex).__name__ == "StopIteration":
                print("No more files in the corpus")
                break
            else:
                print(ex)
                print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(ex).__name__, ex)
                print("issue in func: retrive_tagged_results_from_saved_tagged_corpus")
                raise ex

