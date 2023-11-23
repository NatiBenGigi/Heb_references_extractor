# Project: Hebrew Reference extractor
#
# Created by: Nati Ben-Gigi
# Date: 11/2023
#
# License: MIT
# Copyright: Nati Ben-Gigi 2023
#
# File: logical_tagging_functions.py
# Description: 
# the functions in this file are related to building of 
# the reference object which holds all the data about a reference

from find_ref_helper import *
from tags_lists import *
from Hebrew_Gematria_helper import *

from Ontology import  ontology 
import copy
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

# this function duplicates the ref object
# remove from every instance the word_set that are not relevant using the word_set idx
# e.g. from the final object remove the rest of the word_set for the new ref_obj the previous wrod_set
# and clean the new ref obj from the previous attributes like author name, book name, etc... 
def duplicate_ref_obj(refObj, word_set_idx):
    final_refObj = copy.deepcopy(refObj)
    
    # Zero the foundings in all the word_set that are not relevant for this ref_obj e.g. the word_sets that are after the idx
    for idx in range(word_set_idx, len(refObj.extended_words_tags_list)):
        final_refObj.extended_words_tags_list[idx][3] = []#"NA"
        final_refObj.extended_words_tags_list[idx][4] = []#"NA"
        final_refObj.extended_words_tags_list[idx][5] = []
        final_refObj.extended_words_tags_list[idx][6] = "NA"
    
    # zero the foundings in previous word sets till the word_set_idx that represent the split point between the new and the finalize ref_obj
    for idx in range(word_set_idx):
        refObj.extended_words_tags_list[idx][3] = []#"NA"
        refObj.extended_words_tags_list[idx][4] = []#"NA"
        refObj.extended_words_tags_list[idx][5] = []
        refObj.extended_words_tags_list[idx][6] = "NA"

    #the refObj will still be processed, so lets clean if from previous findings
    clean_refObj(refObj)
    return final_refObj, refObj


# this functions checks the following
# once we found a word_set that is a an entity (like BN, AN, etc), but our refObj already has such entity lets check if the current word_set
# is the same results (e.g. continuum) or a entity
def isContinum(Canonize_abbrv_list, word_set):
    if len(Canonize_abbrv_list) == 0: # if we don't have previous book then we don't really need to duplicate the refObj (which is the purpose of this entire checking)
        return True
    for canonize_abbrv in Canonize_abbrv_list:
        for word_set_Cnonize_abbrv in word_set[5]:
            if canonize_abbrv.canonizedStr == word_set_Cnonize_abbrv.canonizedStr:
                return True #indeed the new word set BN value is a continuum of the previous word
    
    return False

# pick the values from the word_set merge results and populate the attributes of the ref object (archi book, base book, etc... )
def populate_refObjs(refObj):
    final_refObj_list = []
    merge_idx = 5
    internal_ref = False
    previous_word_set = None
    word_set_idx = -1
    try:
        for word_set in refObj.extended_words_tags_list:
            word_set_idx += 1
            
            if len(word_set[merge_idx]) == 0: #no values at this word_set, so just continue
                continue
            
            if (previous_word_set != None) and (word_set[merge_idx] == previous_word_set[merge_idx]): #the same object as in the previous cycle, so it was already handled, so continue
                #keep the word_set for the next cycle
                previous_word_set = word_set
                continue
            else:
                previous_word_set = word_set

            # check if may be we have an internal break point
            # if so, lets log the current as a ref
            if word_set[2] in BM_internal_tags:
                final_refObj = copy.deepcopy(refObj)
                final_refObj_list.append(final_refObj)
                internal_ref = True
            
            #Archi Book
            if word_set[merge_idx][0].type == Building_block_type_Enum.AB:
                # if we already have such results, then its probably a new ref, 
                # lets log the previous one. however if its an internal ref then we need to override the previous value
                # for example if its an internal ref and only the TM changes then we override the existing TM with a new TM
                if isContinum(refObj.archi_book, word_set) == False and internal_ref == False:
                    final_refObj, refObj = duplicate_ref_obj(refObj, word_set_idx)
                    final_refObj_list.append(final_refObj)
                # lets check compatibility between the archi book and the other ingredients:
                elif (len(refObj.book_name) > 0):
                    if refObj.book_name[0].canonizedStr == "הגמרא" or refObj.book_name[0].canonizedStr == "המשנה":
                        pass
                    else: 
                        #so we have a book, lets check if its a commentary on the archi book and should be stored at the same ref or not
                        if not is_commentary(word_set[merge_idx] , refObj.book_name[0].canonizedStr, ontology):
                            final_refObj, refObj = duplicate_ref_obj(refObj, word_set_idx)
                            final_refObj_list.append(final_refObj)

                elif (len(refObj.author_name) > 0):
                    try:
                        is_commantary = False
                        for author in refObj.author_name:
                            for book in ontology.Authors_Biography[author.canonizedStr].books:
                                try:
                                    book_details = ontology.Books_details[book]
                                    if book_details.commentary_of == word_set[merge_idx][0].canonizedStr:
                                        is_commantary = True
                                except Exception as ex:
                                    pass  
                        
                        # The book of the author(s) is not a commentary, hence we must split the reference
                        if is_commantary == False:
                            final_refObj, refObj = duplicate_ref_obj(refObj, word_set_idx)
                            final_refObj_list.append(final_refObj)

                    except Exception as ex:
                        print("issue in func: populate_refObjs")
                        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
                        print("could not find Author: ", author_obj.canonizedStr[::-1])
                        print(ex)
                    
                
                # what ever we split the ref or not lets log the new word
                refObj.archi_book = word_set[merge_idx]
            
            # Talmud Masechet
            elif word_set[merge_idx][0].type == Building_block_type_Enum.TM:
                #if we already have such results, then its probably a new ref, lets log the previous one
                if (isContinum(refObj.base_book, word_set) == False and internal_ref == False):
                    final_refObj, refObj = duplicate_ref_obj(refObj, word_set_idx)
                    final_refObj_list.append(final_refObj)

                # we also have a book, lets see if the book is a commentary on the Talmud
                elif (len(refObj.book_name) > 0):
                # if the book is the talmud then we are good and we can continue
                    if refObj.book_name[0].canonizedStr == "הגמרא" or refObj.book_name[0].canonizedStr == "המשנה":
                        pass
                    # lets see if the current book is a commentary on the Talmud and not on the Mishnah
                    # otherwise split the ref
                    elif (not is_commentary(refObj.book_name, "הגמרא", ontology)) and (not is_commentary(refObj.book_name, "המשנה", ontology)):
                        final_refObj, refObj = duplicate_ref_obj(refObj, word_set_idx)
                        final_refObj_list.append(final_refObj)

                
                # lets see if the TM corresponds to the TR, if no, then its probably a new ref
                if len(refObj.base_book_details) > 0:
                    try:
                        # lets retrieve al the chapters and see if one of the corresponds to our TR-base book details
                        chapter_found = False
                        masechet_chapters = ontology.Masechet_2_chapter[word_set[merge_idx][0].canonizedStr]
                        for chapter in refObj.base_book_details:
                            if chapter.canonizedStr in masechet_chapters:
                                # we found that the masechet correspond to some chapter
                                chapter_found = True
                                refObj.base_book_details = [chapter]
                                refObj.base_book = word_set[merge_idx]
                                break
                        # if we didn't find a match between the TM and the TR, then probably its a new ref
                        if chapter_found == False:
                            final_refObj, refObj = duplicate_ref_obj(refObj, word_set_idx)
                            final_refObj_list.append(final_refObj)

                            refObj.base_book = word_set[merge_idx]


                    except Exception as ex:
                        print("issue in func: populate_refObjs")
                        print("we have an issue in: ontology.Masechet_2_chapter[masechet]")
                        print(ex)    
                        
                else: #we don't have a base book details (TR) so lets just assign the base book (TM)
                    refObj.base_book = word_set[merge_idx]
                
            
            #Talmud refrence (chapter)
            elif word_set[merge_idx][0].type == Building_block_type_Enum.TR:
                #if we already have such results, then its probably a new ref, lets log the previous one
                if (isContinum(refObj.base_book_details, word_set) == False and internal_ref == False):
                    final_refObj, refObj = duplicate_ref_obj(refObj, word_set_idx)
                    final_refObj_list.append(final_refObj)
                
                # we also have a book, lets see if the book is a commentary on the Talmud
                elif (len(refObj.book_name) > 0):
                    # if the book is the talmud then we are good and we can continue
                    if refObj.book_name[0].canonizedStr == "הגמרא" or refObj.book_name[0].canonizedStr == "המשנה":
                        pass
                    # lets see if the current book is a commentary on the Talmud or the Mishnah
                    # otherwise split the ref
                    elif (not is_commentary(refObj.book_name, "הגמרא", ontology)) and (not is_commentary(refObj.book_name, "המשנה", ontology)):
                        final_refObj, refObj = duplicate_ref_obj(refObj, word_set_idx)
                        final_refObj_list.append(final_refObj)
                        

                # lets see if the TM matches to the TR, if no, then its probably a new ref
                if len(refObj.base_book) > 0:
                    chapter_found = False
                    masechet = refObj.base_book[0].canonizedStr
                    try:
                        # lets retrieve al the chapters and see if one of the corresponds to our TR-base book details
                        masechet_chapters = ontology.Masechet_2_chapter[masechet]
                        for can_chapter in word_set[merge_idx]:
                            if can_chapter.canonizedStr in masechet_chapters:
                                # we found that the masechet corresponds to some chapter
                                chapter_found = True
                                refObj.base_book_details = [can_chapter]
                                break

                        # if we didn't find a match between the TM and the TR, then probably its a new ref
                        if chapter_found == False:
                            final_refObj, refObj = duplicate_ref_obj(refObj, word_set_idx)
                            final_refObj_list.append(final_refObj)
                            
                            refObj.base_book_details = word_set[merge_idx]
                    
                    except Exception as ex:
                        print("issue in func: populate_refObjs")
                        print("we have an issue in: ontology.Masechet_2_chapter[masechet]")
                        print(ex)
                        
                else: #we don't have a base book (TM) so lets just assign the base book details (TR)
                    refObj.base_book_details = word_set[merge_idx]
            
            # Book name
            # BUG BUG BUG - this will be resolved once the Mishnah will be considered as Archi Book
            elif word_set[merge_idx][0].type == Building_block_type_Enum.BN:
                #if we already have such results, then its probably a new ref, lets log the previous one
                if (isContinum(refObj.book_name, word_set) == False and internal_ref == False) or \
                    (not check_book_vs_author_compatibility(word_set[merge_idx] , refObj.author_name, ontology)):
                    final_refObj, refObj = duplicate_ref_obj(refObj, word_set_idx)
                    final_refObj_list.append(final_refObj)

                # if we hve a base book lets check if the book is a commentary on the talmud
                elif (len(refObj.base_book) > 0) or (len(refObj.base_book_details) > 0):
                    
                    # lets see if the current book is a commentary on the Talmud
                    # otherwise split the ref
                    if not is_commentary(word_set[merge_idx], "הגמרא", ontology):
                        final_refObj, refObj = duplicate_ref_obj(refObj, word_set_idx)
                        final_refObj_list.append(final_refObj)

                elif (len(refObj.archi_book) > 0):
                    try:
                        if word_set[merge_idx][0].canonizedStr == "הגמרא" or word_set[merge_idx][0].canonizedStr == "המשנה":
                            pass
                        else: 
                            #so we have a book, lets check if its a commentary on the archi book and should be kept at the same ref or not
                            if not is_commentary(word_set[merge_idx] , refObj.archi_book[0].canonizedStr, ontology):
                                final_refObj, refObj = duplicate_ref_obj(refObj, word_set_idx)
                                final_refObj_list.append(final_refObj)
                    except Exception as ex:
                        pass   
                # any how now log the new word
                refObj.book_name = word_set[merge_idx]
            
            # Author name
            elif word_set[merge_idx][0].type == Building_block_type_Enum.AN:
                #if we already have such results, then its probably a new ref, lets log the previous one
                # we are checking the following:
                # 1. the current An is not a continuum of teh previous
                # 2. if we already found a book, check the AN indeed wrote  
                if (isContinum(refObj.author_name, word_set) == False and internal_ref == False) or \
                     (not check_book_vs_author_compatibility(refObj.book_name , word_set[merge_idx], ontology)):
                    final_refObj, refObj = duplicate_ref_obj(refObj, word_set_idx)
                    final_refObj_list.append(final_refObj)

                # if we hve a base book lets check if the another has book that is a commentary on the talmud
                elif (len(refObj.base_book) > 0) or (len(refObj.base_book_details) > 0):
                    
                    # if we already have a book the compatibility vs. the Talmud was already done and we can continue
                    # otherwise:
                    if(len(refObj.book_name) == 0):
                        # lets see if the author wrote book that is a commentary on the Talmud
                        # otherwise split the ref
                        for author_obj in word_set[merge_idx]:
                            try: 
                                Author_bio = ontology.Authors_Biography[author_obj.canonizedStr]
                                for book in Author_bio.books:
                                    if not is_commentary(refObj.book_name, book, ontology):
                                        final_refObj, refObj = duplicate_ref_obj(refObj, word_set_idx)
                                        final_refObj_list.append(final_refObj)

                                        break
                            except Exception as ex:
                                print("issue in func: populate_refObjs")
                                print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
                                print("could not find Author: ", author_obj.canonizedStr[::-1])
                                print(ex)
                # Lets check if we already have an author name that may not be compatible with the archi book we already found
                elif (len(refObj.archi_book) > 0):
                    try:
                        is_commantary = False
                        for author in word_set[merge_idx]:
                            for book in ontology.Authors_Biography[author.canonizedStr].books:
                                try:
                                    book_details = ontology.Books_details[book]
                                    if book_details.commentary_of == word_set[merge_idx][0].canonizedStr:
                                        is_commantary = True
                                except Exception as ex:
                                    pass    
                        # The book of the author(s) is not a commantary, hence we must split the reference
                        if is_commantary == False:
                            final_refObj, refObj = duplicate_ref_obj(refObj, word_set_idx)
                            final_refObj_list.append(final_refObj)

                    except Exception as ex:
                        print("issue in func: populate_refObjs")
                        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
                        print("could not find Author: ", author_obj.canonizedStr[::-1])
                        print(ex)

                refObj.author_name = word_set[merge_idx]
            
            #Rambam stuff
            elif word_set[merge_idx][0].type == Building_block_type_Enum.RR:
                #if we already have such results, then its probably a new ref, lets log the previous one
                duplicat_flag = False
                if (len(refObj.book_name) > 0 and internal_ref == False):
                    if (refObj.book_name[0].canonizedStr not in ["היד החזקה", ""]):
                        duplicat_flag = True
                
                elif (len(refObj.author_name) > 0 and internal_ref == False):
                    
                    #print(refObj.author_name[0].canonizedStr)
                    RamBam_Flag_found = False
                    for author_name in refObj.author_name:
                        if author_name.canonizedStr in ["ר´ משה בן מיימון", "", 'ר״ם לא ידוע']:
                            # since the context of our search is RR and we found a author name that can eb RamBam, 
                            # then we can be (probably) sure its Rambam and we will create a new canonization obj
                            # with RamBam inside 
                            refObj.author_name = [Cnonize_abbrv(author_name.abbreviation ,"ר´ משה בן מיימון", Ref_quality.High, Building_block_type_Enum.AN)]
                            RamBam_Flag_found = True
                            break
                    # if in the author name we didn't find any name corresponds to Rambam,
                    # so its probaby another author, hence lets break (duplicate) the reference, 
                    if RamBam_Flag_found == False:
                        duplicat_flag = True

                elif (len(refObj.base_book) > 0):
                    duplicat_flag = True
                elif (len(refObj.base_book_details) > 0):
                    duplicat_flag = True

                # if we conclude that the previous content is not related to the RamBAM
                # lets duplicate the previous stuff 
                if duplicat_flag == True:
                    final_refObj, refObj = duplicate_ref_obj(refObj, word_set_idx)
                    final_refObj_list.append(final_refObj)
                
                #assign current word set to the new ref object
                refObj.book_name = word_set[merge_idx]
            
            #when its "R" we just append it to the previous details
            elif word_set[merge_idx][0].type == Building_block_type_Enum.R:
                if len(refObj.refrence_deatils) == 0:
                    refObj.refrence_deatils = [word_set[merge_idx]]
                elif word_set[merge_idx] not in refObj.refrence_deatils:
                    refObj.refrence_deatils.append(word_set[merge_idx])

            else:
                print("which ENUM type did i forgot?")

        # we are out of the loop lets see if we need to log the last refObj
        if not is_ref_obj_empty_v2(refObj):
            final_refObj_list.append(refObj)
    
    except Exception as E:
        print("issue in function: populate_refObjs")
        print(E)
        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
    return final_refObj_list

#checking if we really didn't found anything
def is_ref_obj_empty_v2(refObject):
    if len(refObject.archi_book) != 0:
        return False
    if len(refObject.base_book) != 0:
        return False
    if len(refObject.base_book_details) != 0:
        return False
    if len(refObject.author_name) != 0:
        return False
    if len(refObject.book_name) != 0:
        return False
    if len(refObject.refrence_deatils) != 0:
        return False

    #if we are here it mean we didn't found anything -> the rejObj is empty
    return True 

# convert the lists of values to strings.
# in case we multiple value try to eliminate it by all kind of technics
def finalize_refObjs(ref_obj_list):
    try:
        finalized_ref_obj_list = []
        for RefObj in ref_obj_list:
            
            # archi books
            if len(RefObj.archi_book) > 1: # first try to remove duplicate entries
                RefObj.archi_book = remove_duplications(RefObj.archi_book)
            
            if len(RefObj.archi_book) > 1:
                print("len(RefObj.archi_book) >  1 !!!")
                RefObj.archi_book = format_multiple_res_str(RefObj.archi_book)
            elif len(RefObj.archi_book) == 1:
                RefObj.archi_book = RefObj.archi_book[0].canonizedStr
            elif len(RefObj.archi_book) == 0:
                RefObj.archi_book = ""
            
            # TR -> base book details, aka, talmud chapter
            if len(RefObj.base_book_details) == 1:
                RefObj.base_book_details = RefObj.base_book_details[0].canonizedStr
            elif len(RefObj.base_book_details) > 1:
                if len(RefObj.base_book) == 1:
                    _, candidate_son = resolve_son_from_father(RefObj.base_book[0].canonizedStr , RefObj.base_book_details, ontology.Masechet_2_chapter)
                    if candidate_son != None:
                        RefObj.base_book_details = candidate_son
                    else:
                        print ("candidate_son == None! how could it be?!?" )    
                else:
                    RefObj.base_book_details = format_multiple_res_str(RefObj.base_book_details)
                    RefObj.ref_quality = Ref_quality.Medium
            elif len(RefObj.base_book_details) == 0:
                RefObj.base_book_details = ""

            # TM -> Base book, aka masechet
            if len(RefObj.base_book) > 1: # first try to remove duplicate entries
                RefObj.base_book = remove_duplications(RefObj.base_book)
            if len(RefObj.base_book) > 1:
                print("len(RefObj.base_book) >  1 !!!")
            elif len(RefObj.base_book) == 1:
                RefObj.base_book = RefObj.base_book[0].canonizedStr
            elif len(RefObj.base_book) == 0:
                # if we have the chapter str value, lets find the corresponds masechet
                if type (RefObj.base_book_details) == str:
                    base_book_list = resolve_father_from_childrens(RefObj.base_book_details, ontology.Masechet_2_chapter)
                    # only if we have a single results e take it
                    if len(base_book_list) == 1:
                        RefObj.base_book = base_book_list[0]
                    else:
                        RefObj.base_book = ""   
                else:
                    RefObj.base_book = ""
           
            final_book = ""
            # BN ->book name
            if len(RefObj.book_name) == 1:
                final_book = RefObj.book_name[0].canonizedStr
            elif len(RefObj.book_name) > 1:
                #we have multiple books name, lets see if we can reduce the number by using the author name
                if len(RefObj.author_name) == 1:
                    _, book = resolve_books_by_author(RefObj.author_name[0].canonizedStr , RefObj.book_name, ontology.Authors_Biography)
                    if book != None: # we reduce the number of book :)
                        final_book = book
            elif len(RefObj.book_name) == 0:
                RefObj.book_name = ""

            # author name
            if len(RefObj.author_name) == 1:
                RefObj.author_name = RefObj.author_name[0].canonizedStr
                if DEBUG:  
                    author = RefObj.author_name
                    print(author[::-1])
            elif len(RefObj.author_name) > 1:
                author = None
                #we have multiple author name, lets see if we can reduce the number by using the book name
                if len(RefObj.book_name) == 1:
                    author = resolve_authors_by_books(RefObj.book_name[0].canonizedStr , RefObj.author_name, ontology.Authors_Biography)
                    if author != None: # we reduce the number of book :)
                        RefObj.author_name = author
                
                # we still have multiple author_name, as the book didn't help to resolve
                if author == None:   
                    RefObj.author_name = format_multiple_res_str(RefObj.author_name)
                    RefObj.ref_quality = Ref_quality.Medium
            elif len(RefObj.author_name) == 0:
                RefObj.author_name = ""

            # check if the mentioned author is the one that actually wrote the text
            if RefObj.author_name != "":
                #we are checking may be the name we found in the name of the text author (usually its a signature)
                if RefObj.text_author == RefObj.author_name:
                    RefObj.ref_quality = Ref_quality.self_mentioned
                
                # lets try to retrieve it via teh text source
                # first checking we really have a source of the text
                elif RefObj.text_source == "": 
                    pass 
                else:
                    # Some time the text source was identify as a name and not as a book
                    if RefObj.text_source in ontology.Authors_Biography:
                        if RefObj.text_source == RefObj.author_name: 
                            RefObj.ref_quality = Ref_quality.self_mentioned
                    else:
                        text_author = resolve_author_of_book(RefObj.text_source, ontology.Authors_Biography)
                        if text_author == RefObj.author_name:
                            RefObj.ref_quality = Ref_quality.self_mentioned
                        
                # Now lets check dates compatibility
                # E.g. the reference author is younger than the text author
                author_date_no_match = check_author_date(RefObj, ontology)
                if author_date_no_match:
                    RefObj.ref_quality = Ref_quality.anachronistic_ref

            # finish the book name assignment
            if final_book != "":
                RefObj.book_name = final_book
            else:
                RefObj.book_name = format_multiple_res_str(RefObj.book_name)

            # now lets check if the refrence was not written by the original ref author but by a later editor of the ref
            if RefObj.book_name != None:
                book_date_no_match = check_book_date(RefObj, ontology)
                if book_date_no_match:
                    RefObj.ref_quality = Ref_quality.anachronistic_ref  

            # setting the english name of the book
            if RefObj.book_name != "":
                try:
                    RefObj.book_name_ENGLISH = ontology.Books_details[RefObj.book_name].ENGLISH_name
                except Exception:
                    pass

            # setting the english name of the author
            if RefObj.author_name != "":
                try:
                    RefObj.author_name_ENGLISH = ontology.Authors_Biography[RefObj.author_name].ENGLISH_name
                except Exception:
                    pass

            # handle refrence details
            RefObj.refrence_deatils = construct_ref_details_v2(RefObj) #construct_ref_details(RefObj)

            # if we only have an archi book lets populate the author name
            if RefObj.archi_book != "" and RefObj.book_name == "" and RefObj.author_name == "":
                if RefObj.archi_book == "ארבע טורים":
                    RefObj.author_name == "ר´ יעקב בן אשר"
                if RefObj.archi_book == "הלכות רב אלפס":
                    RefObj.author_name == "ר´ יצחק אלפסי"

            finalized_ref_obj_list.append(RefObj)
    
    except Exception as ex:
        print(ex)
        print("Issue in function: finalize_refObjs")
        print('Error on line {}'.format(sys.exc_info()
                [-1].tb_lineno), type(ex).__name__, ex)

    # we finished the loop, lets return teh list of result
    return finalized_ref_obj_list

# resolve the ingredients of a reference to the Yad Hahazaka
def resolve_Hilchot_Yad_Hahazaka_v2(Yad_Hahazaka_str, ref_details_dict):
    try:
        Yad_Hahazaka_str = Yad_Hahazaka_str.strip()
        res = canonize_Hilchot_Yad_Hahazaka(Yad_Hahazaka_str, ontology)
        if res != None:
            if len(res) == 1:
                final_Hilchot_str = res[0].canonizedStr.replace("הלכות", "")
                ref_details_dict["הלכות"] = final_Hilchot_str
                
            else: 
                if DEBUG:
                    print("warning: Hilchot_Yad_Hahazaka embiguity!!!! ")
                    res_list = [item.canonizedStr for item in res]
                    result = " vs. ".join(res_list)
                    print(get_display(result))
        else:
            if DEBUG:
                print("warning: Hilchot_Yad_Hahazaka could not be resolved: ", Yad_Hahazaka_str)
    
    except Exception as ex:
        print(ex)
        print("Issue in function: resolve_Hilchot_Yad_Hahazaka_v2")
        print('Error on line {}'.format(sys.exc_info()
                      [-1].tb_lineno), type(ex).__name__, ex)
        
    return ref_details_dict

# Construct the reference details part like chapter, page, section etc. 
def construct_ref_details_v2(RefObj):
    try: 
        layer_2_idx = 2
        layer_1_idx = 1
        final_tag_idx = 5
        NA_tag_idx = 6
        ref_details_dict = {}
        
        # if its only a AB or AN, then refrence low level deatils is not relevant as we need a BOOK to also have its details. lets exit
        if RefObj.base_book == "" and RefObj.book_name == "" and RefObj.base_book_details == "" and RefObj.archi_book == "":
            return ""    
        latest_general_word = ""
        Yad_Hahazaka_str = ""
        for word_set in RefObj.extended_words_tags_list:
            # first lets check if the word is not a part of the current process ref
            # in this case its not relevant to process it
            if word_set[NA_tag_idx] == "NA":
                continue
                 
            # Before processing new word, lets check if we finished a Yad Hahazaka text
            # lets start by checking its not a Rambam Related
            if word_set[layer_2_idx] != "RR":
                # Now lets check we already had such text, if yes lets process it
                if Yad_Hahazaka_str != "":
                    ref_details_dict = resolve_Hilchot_Yad_Hahazaka_v2(Yad_Hahazaka_str, ref_details_dict)
                    # Zero the Yad_Hahazaka text
                    Yad_Hahazaka_str = ""

            if word_set[layer_2_idx] in ["R", "RR", "RW", "RC"] or word_set[layer_1_idx] in ["R", "RW", "RC"]:
                # before we start lets check if may be this word was already used for another identification
                if len(word_set[final_tag_idx]) != 0:
                    if word_set[final_tag_idx][0].quality in [Ref_quality.High, Ref_quality.Medium] and \
                    word_set[layer_2_idx] not in ["RR"]:
                        # if there is already a tag on this value and its high Ref_quality
                        # so it means the word is already used and we want process it
                        # however if its RR (Rambam related) we would like to still process it
                        continue
                
                # Now we can start the identification
                current_word = word_set[0]
                
                res = canonize_general_ref_words(current_word, ontology)
                if res != None:
                    if len(res) == 1:
                        ref_details_dict[res[0].canonizedStr] = ""
                        latest_general_word = res[0].canonizedStr
                        continue
                    else: 
                        #DEBUG
                        print("wrning: General ref embiguity!!!! ")
                        full_lis_of_words = ""
                        for item in res:
                            full_lis_of_words += item + " " 
                        print(full_lis_of_words)

                # we will check if may be the current_word is a chapter only if there is no general word befor it
                # if there is a general word, the word פרק can't appear it
                if latest_general_word == "":
                    res = check_if_chapter(current_word)
                    if res != False:
                        if latest_general_word == "פרק": # the latest word was פרק now lets just add the value
                            ref_details_dict[latest_general_word] = res
                        else: #the latest word was not פרק so lets add both the word פרק and the value
                            ref_details_dict["פרק"] = res
                        
                        # lets zero the general word for the next loop
                        latest_general_word = ""
                        continue

                res = check_Hebrew_number_correctness(current_word)
                if res not in [False, None]:
                    # lets if we had in teh previouse loop a general wordm in this case lets add the value
                    if latest_general_word != "":
                        ref_details_dict[latest_general_word] = current_word
                    else: # we have a value without a general wordm lets just add the value
                        ref_details_dict[current_word] = current_word
                    
                    # lets zero the general word for the next loop
                    latest_general_word = ""
                    continue
                
                if word_set[layer_2_idx] in ["RR"]:
                    Yad_Hahazaka_str += current_word + " "
                    # lets zero the general word from the previouse loop (in case we had such) for the next loop
                    latest_general_word = ""
                    continue

                #since we are here it means we have a word that don't much any of the above conditions
                # so lets zero the general word and move to the next loop
                latest_general_word = ""
                continue
            
            else:
                #the current_word is not tagged as R, RW, RC, etc,,
                # so lets zero the general word and move to the next loop
                latest_general_word = ""
                continue

        # we finished the loop, lets check we don't have lefts over
        if Yad_Hahazaka_str != "":
            ref_details_dict = resolve_Hilchot_Yad_Hahazaka_v2(Yad_Hahazaka_str, ref_details_dict)
      
        # If we only have a base book, we can do cleanup on the ref values
        if RefObj.base_book != "" and RefObj.book_name == "" and RefObj.base_book_details == "" and RefObj.archi_book == "":
            ref_details_dict = check_base_book_ref(ref_details_dict, RefObj.base_book)
        # We finished the loop now construct the ref details string
        ref_details_str = ""
        for k, v in ref_details_dict.items():
            # skip the general words that did not have a coresponding value
            if v == "": continue
            # we hade Key and Value, e.g. a general words and a coresponding value lets add it 
            if v != k:  
                ref_details_str += k + " " + v + " "
            # if the general word equal its value it means we got a word w/out any general value, so we just add teh word
            else:
                ref_details_str += v + " "   

        ref_details_str = ref_details_str.strip()
        return ref_details_str

    except Exception as ex:
        print(ex)
        print("Issue in function: construct_ref_details_v2")
        print('Error on line {}'.format(sys.exc_info()
                      [-1].tb_lineno), type(ex).__name__, ex)
    
    return finalizeRefDetails(ref_details_str, RefObj)

#this function checks the validite of a base book (talmud) reference and clean it accordingly
def check_base_book_ref(ref_details_dict, base_book):
    # a base book ref should include the following:
    # Page number
    # Amud a or b
    new_ref_details_dict = {}
    Daf = ""
    Amud = ""
    for k, v in ref_details_dict.items():
        #simple assignments
        if k == "דף":
            Daf = v
        if k == "עמוד":
            Amud = v
        # skip the general words that did not have a coresponding value
        if v == "":
            pass
        if v == k:
            #lets check what can be the meaning of this value:
            # if its the base book then just lets keep it and continue
            if v == base_book:
                pass 
            # check if its the Amud
            elif v in ["א", "עא", 'ע"א', "ב", "עב", 'ע"ב']:
                Amud = v
            # check if its the page
            elif Daf == "":
                if v[-1] in [".", ":"]:
                    res = check_Hebrew_number_correctness(v[:-1])
                else:
                    res = check_Hebrew_number_correctness(v)
                if res not in [False, None]:
                    Daf = v
                else:
                    # if its none of them then just lets continue WITHOUT keeping it
                    continue
            # if its none of them then just lets continue WITHOUT keeping it
            else:
                # this is an importent IF as it means the value we have in not needed and we can remove it from the dict
                continue
        new_ref_details_dict[k] = v

    
    return new_ref_details_dict

# Clean the final refrence details
def finalizeRefDetails(ref_details_str, RefObj):
    if ref_details_str == "":
        return

    # clean the string:
    ref_details_str = ref_details_str.strip()

    ref_details_str = ref_details_str.replace("/", "")
    
    #clean . and :
    if ref_details_str != "":
        if ref_details_str[-1] in [",", "´"]: 
            ref_details_str = ref_details_str[:-1]
        
        ref_details_str = ref_details_str.strip()
        if ref_details_str[-1] in [".", ":"]:
            #if its not a talmud Masechet we can simply remove the "." or the ":"
            if RefObj.base_book == "": 
                ref_details_str = ref_details_str[:-1]
            else:
                try:
                    talmud_AMUD = ref_details_str[-4:-1]
                    if talmud_AMUD in ['ע״א', 'ע״ב']:
                        ref_details_str = ref_details_str[:-1]
                
                except Exception as ex:
                    # if we are here it means we got of index 
                    # hence not relevant to what we are checking, lets just continue
                    pass
    
    ref_details_str = ref_details_str.strip()

    # convert the talmud sub-page 'ע״א'and 'ע״ב' to "." or to ":"
    if RefObj.base_book != "":
        idx = ref_details_str.find('ע״א')
        if idx != -1:
            ref_details_str = ref_details_str.replace('ע״א', ".")
            ref_details_str = ref_details_str[0 : (idx-1) : ] + ref_details_str[idx : :]

        idx = ref_details_str.find('ע״ב')
        if idx != -1:
            ref_details_str = ref_details_str.replace('ע״ב', ":")
            ref_details_str = ref_details_str[0 : (idx-1) : ] + ref_details_str[idx : :]

        ref_details_str = ref_details_str.strip()

    return ref_details_str

# Given a book and a list of author, find the author who wrote that book
def resolve_authors_by_books(book, candiddate_authors_list, mapping_dict):
    authors_list = []
    for item in candiddate_authors_list:
        authors_list.append(item.canonizedStr)

    for author in authors_list:
        try:
            authors_books = mapping_dict[author].books # lets get all the books of the current author
        except Exception as ex:
            print("exception in function: resolve_author_books")
            print("authors_books = mapping_dict[author].books")
            print("couldnot find author: ", author[::-1])
            print(ex)
        if book in authors_books:
            return author
    
    # If we are here,it means no results
    return None

# concatinate multiple results to a string
def format_multiple_res_str(res_list):
    #first remove duplicate results
    canonizedStr_list = []
    for i in range(len(res_list)):
        canonizedStr_list.append(res_list[i].canonizedStr)
    unique_strings = []
    for item in canonizedStr_list:
        if item not in unique_strings:
            unique_strings.append(item)
    
    # build the final str
    str = ""
    for i in range(len(unique_strings)):
        str += unique_strings[i]
        if i < len(unique_strings) - 1:
            str += " \\ "
 
    return str

#given a list of sons and a father, find the correct son from the father
def resolve_son_from_father(father, childrens_list_abb_cann, mapping_dict):
    # Build the chapters list
    sons_list = []
    for item in childrens_list_abb_cann:
        sons_list.append(item.canonizedStr)
    
    # now lets search for the correct chapter in the masechf's list of chapter
    try:
        fathers_sons_list = mapping_dict[father]
        for candidate_son in sons_list:
            if candidate_son in fathers_sons_list:
                return father, candidate_son
        
    except: 
        pass
    
    return None, None
        
# Given an author and a list of books, find the book written by this author
def resolve_books_by_author(author, candidate_books_list, mapping_dict):
    # Build the chapters list
    books_list = []
    for item in candidate_books_list:
        books_list.append(item.canonizedStr)
    
    try:
        authors_books = mapping_dict[author].books # lets get all the books of the current author
    except Exception as ex:
        print("exception in function: resolve_author_books")
        print("authors_books = mapping_dict[author].books")
        print("couldnot find author: ", author[::-1])
        print(ex)
    
    # check if one of the books is nin the author books
    for book in books_list:
        if book in authors_books:
            return author, book
    # nothing was found
    return None, None

# clean to ref object from previouse values
def clean_refObj(refObj):
    refObj.archi_book = []
    refObj.book_name = []
    refObj.base_book = []
    refObj.base_book_details = []
    refObj.author_name = []
    refObj.publication = []


def populate_initial_meta_data(ref_Object):
    try:
        
        ref_Object.file_name = os.path.basename(ref_Object.file_path)
        ref_Object.clean_file_name, _ = clean_text2(ref_Object.file_name)

        text = ref_Object.text_source
        if text == "":
            return ref_Object

        # Details about the text we are mining reference fro
        # the text_source is an author name
        if text in ontology.Authors_Biography:
            ref_Object.text_author = text
            ref_Object.text_author_ENGLISH = ontology.Authors_Biography[text].ENGLISH_name
            authors_books = ontology.Authors_Biography[text].books
            if len(authors_books) == 1 and authors_books[0] != "":
                ref_Object.text_source = authors_books[0]
                ref_Object.text_source_ENGLISH = ontology.Books_details[ref_Object.text_source].ENGLISH_name
        #the source is a book
        else:
            ref_Object.text_source_ENGLISH = ontology.Books_details[text].ENGLISH_name
            ref_Object.text_source = text
            ref_Object.text_author = resolve_author_of_book(text, ontology.Authors_Biography)
            if ref_Object.text_author != "":
                ref_Object.text_author_ENGLISH = ontology.Authors_Biography[ref_Object.text_author].ENGLISH_name
    
    except Exception as ex:
            print(ex)
            print("issue in populate_initial_meta_data")
            print('Error on line {}'.format(sys.exc_info()
                    [-1].tb_lineno), type(ex).__name__, ex)
                
    return ref_Object
