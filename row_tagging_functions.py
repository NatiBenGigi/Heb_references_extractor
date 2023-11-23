# Project: Hebrew Reference extractor
#
# Created by: Nati Ben-Gigi
# Date: 11/2023
#
# License: MIT
# Copyright: Nati Ben-Gigi 2023
#
# File: 
# Description: row_tagging_functions.py
# This file include the functionality that given a tagged word 
# the word in normalized according by mapping tables corresponding to the tag 

from logical_tagging_functions import *
from Ontology import  ontology 


# resolve the type of the building blockס
def resolve_building_block_type2(words_set, Model_layer):
    if Model_power.Layer_2_model == Model_layer:
        # start by layer 2
        if words_set[2] in TM_tags:
            return Building_block_type_Enum.TM
        elif words_set[2] in TR_tags:
            return Building_block_type_Enum.TR
        elif words_set[2] in AB_tags:
            return Building_block_type_Enum.AB
        elif words_set[2] in RR_tags:
            return Building_block_type_Enum.RR  # Rambam tags
        elif words_set[2] in R_tags:
            return Building_block_type_Enum.R
        elif words_set[2] in RT_tags:
            return Building_block_type_Enum.RT
        elif words_set[2] in TSR_tags:
            return Building_block_type_Enum.TSR
        elif words_set[2] == "O":
            return Building_block_type_Enum.No_Tag
    
    elif Model_power.Layer_1_model == Model_layer:
        # resolve layer 1
        if words_set[1] in Author_tags:
            return Building_block_type_Enum.AN
        if words_set[1] in Books_tag:
            return Building_block_type_Enum.BN
        elif words_set[1] in GA_tags:
            return Building_block_type_Enum.AB
        elif words_set[1] in R_tags:
            return Building_block_type_Enum.R
        elif words_set[1] == "O":
            return Building_block_type_Enum.No_Tag

    return None

# this function does the last step of finalizing the building block
# canonize it according to its type
def resolve_BB(building_block, model_layer):
    results = None
    try:
        #building the string for searching
        for wors_set in building_block.word_set_list:
            building_block.str += wors_set[0] + " "
        
        #remove the blank space
        building_block.str = building_block.str.strip()

        # talmud building block stuff
        if building_block.tag_type in [Building_block_type_Enum.AB , Building_block_type_Enum.TM , Building_block_type_Enum.TR]:
            results, final_type, _ = canonize_talmud_building_block(
                building_block.str, building_block.tag_type, ontology)
            if results != None:
                building_block.res_list = results
                building_block.final_type = final_type
                bind_building_block_2_word_set(building_block, model_layer)
                return building_block
            else:
                return None

        # author and book building block
        if building_block.tag_type in [Building_block_type_Enum.AN, Building_block_type_Enum.BN]:
            results, final_type, _ = canonize_book_and_author_building_block(
                    building_block.str, building_block.tag_type, ontology)  
            
            if results != None:
                building_block.res_list = results
                building_block.final_type = final_type
                bind_building_block_2_word_set(building_block, model_layer)
                return building_block
            else:
                return None

        # Rambam stuff
        if building_block.tag_type == Building_block_type_Enum.RR:
            # Check no too much "RR" or "RT" which are a model error
            if is_valid_BB(building_block.word_set_list) == True:
                results = create_Cnonize_abbrv(Building_block_type_Enum.RR, building_block.str, ontology)

                if results != None:
                    building_block.res_list.append(results)
                # lets check if we have the RR tag, which mean we have reference to the Yad Hahazaka
                for word_set in building_block.word_set_list: #checking may be we also have a reference to the book and not just the name
                    if word_set[2] == "RR":
                        building_block.res_list.append(Cnonize_abbrv(building_block.str ,"היד החזקה", Ref_quality.High, Building_block_type_Enum.RR))
                        break
            
            if len(building_block.res_list) > 0:
                building_block.final_type = Building_block_type_Enum.RR
                bind_building_block_2_word_set(building_block, model_layer)
                return building_block
            else:
                return None

        # 4 TURIM stuff
        if building_block.tag_type == Building_block_type_Enum.TSR:
            #TODO do we need this condition? if len(building_block.words_tags_list) < 6: #some time the model tags 
            # a long list of words to RR (and its not related at all to RR) so its a model miss-tagging
            results = create_Cnonize_abbrv(Building_block_type_Enum.TSR, building_block.str, ontology)
            if results != None:
                building_block.res_list.append(results)       
                building_block.final_type = Building_block_type_Enum.TSR
                bind_building_block_2_word_set(building_block, model_layer)
                return building_block  
            else:
                return None

        # working on Reference Top (RT) tagging or R then lets check everything
        if building_block.tag_type in [Building_block_type_Enum.RT, Building_block_type_Enum.R]:
            # Check no too much "RR" or "RT" as if it happens its a model error
            if is_valid_BB(building_block.word_set_list) == True:
                results, final_type, _ = canonize_general_building_block(
                        building_block.str, building_block.tag_type, ontology)  
            
        if results != None:
            building_block.res_list = results
            building_block.final_type = building_block.tag_type
            bind_building_block_2_word_set(building_block, model_layer)
            return building_block
        
        
        #we didn't succeed the canonization, but since its "R", we log it as reference details
        elif building_block.tag_type in [Building_block_type_Enum.R]:
            # we just create a canonized result, with the original text values
            building_block.res_list = [Cnonize_abbrv(building_block.str ,building_block.str, Ref_quality.Low, Building_block_type_Enum.R)]
            building_block.final_type = building_block.tag_type
            bind_building_block_2_word_set(building_block, model_layer)
            return building_block
        
        else:
            return None
        
    except Exception as ex:
        print("issue in func: resolve_BB")
        print(ex)
    return None

# some time we have tones of "RR" or "RT" which are a model error 
# this functions checks it
def is_valid_BB(sub_mergedResults):
    RR_counter = 0
    RT_counter = 0
    for word_set in sub_mergedResults:
        if word_set[2] == "RT":
            RT_counter += 1
        elif word_set[2] == "RR":
            RR_counter += 1
    # lets check the counter size, if they are large this is probably a model error
    if RT_counter >= 7 or RR_counter >=7:
        return False
    else:
        return True

#binding the result to the exact words its covering
def bind_building_block_2_word_set(building_block, model_layer):
    try:
        # special treatment for the RR (Rambam) reference parts, not the RamBam name
        # for every word set that has a RR tag we will bind the canonized_abbr that has the RR tag
        if building_block.final_type == Building_block_type_Enum.RR:
            for Cnonize_abbr in building_block.res_list:
                if Cnonize_abbr.type == Building_block_type_Enum.RR:
                    for word_set in building_block.word_set_list:
                        if word_set[2] == "RR":
                            word_set[4].append(Cnonize_abbr) # RR is a layer 2 tag so will will place the obj (Cnonize_abbr) in index 4 of the word set, which is the layer2 object place holder
            # we finished the RR BB, lets exit
            return

        if model_layer == Model_power.Layer_1_model:
            word_set_model_idx = 3 #the location in the word_set array of the layer 1 foundings
        else: # we are working with layer 2
            word_set_model_idx = 4
        for Cnonize_abbr in building_block.res_list:
            abbr_words = Cnonize_abbr.abbreviation.split()
            if len(abbr_words) == 1:
                for word_set in building_block.word_set_list:
                    idx = word_set[0].find(Cnonize_abbr.abbreviation)
                    if idx != -1: #we found the word in the BB that include our abbreviation.
                        word_set[word_set_model_idx].append(Cnonize_abbr) 
                        break # we finished to bind the current Cnonize_abbr, let move to the next one
            else:
                # we have an abbr built from multiple words
                # hence we need to find all the words that are part of this abbreviation
                window_size = len(abbr_words)
                for word_set_idx in range(len(building_block.word_set_list)):
                    word_set_win = []
                    #first build the candidate window
                    for word_i in range(window_size):
                        if word_set_idx + word_i == len(building_block.word_set_list): #we reached the end, the windows is overflowing the word set list
                            break
                        word_set_win.append(building_block.word_set_list[word_set_idx + word_i]) 

                    # now check if the abbreviation is in this window
                    win_text = ""
                    for word_set in word_set_win:
                        win_text += word_set[0] + " "
                    idx = win_text.find(Cnonize_abbr.abbreviation)
                    if idx != -1: #we found the abbreviation in the text, lets log to each word the Cnonize_abbr
                        for word_set in word_set_win:
                            word_set[word_set_model_idx].append(Cnonize_abbr)
                        break #we finished the current Cnonize_abbr, let's move to the next
                

    except Exception as ex:
        print("issue in func: bind_building_block_2_word_set")
        print(ex)

