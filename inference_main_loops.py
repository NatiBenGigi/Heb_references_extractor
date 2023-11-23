# Project: Hebrew Reference extractor
#
# Created by: Nati Ben-Gigi
# Date: 11/2023
#
# License: MIT
# Copyright: Nati Ben-Gigi 2023
#
# File: inference_main_loops.py
# Description: 
# the main system that loops over the text + the tags and accordingly 
# break down the text and constructs the references list

from row_tagging_functions import *
from collections import deque

# This functions go over the long list of words and their tag and break it 
# to references. the function does it by searching for BM* (break mark) tags or
# by by a series of tye tag 0, which mean that those words are not a reference
# once a ref was found, the function invoke other function to identify the low level 
# ingredients of the reference
def process_layer_1_2_results_v2( mergedResults, text_source, file_path = ""):
    refrences_found = []
    sub_mergedResults = []
    end_ref_counter = 0
    in_ref = False
    previous_elements = deque(maxlen=7)
    
    #looping over the entire responsa words
    for i in range(len(mergedResults)):
       
        # TODO in case of RC, need to add the 3 previouse words (checking they were not used befor)
        # probably need to handle here the RC based refrence
        # 
        # we found a tagged word 
        # but we also check its not a point, hence a point serves as a stop tag
        if (((mergedResults[i][1] != "O") or (mergedResults[i][2] != "O")) and (mergedResults[i][0] != '.')):
            sub_mergedResults.append(mergedResults[i])
            in_ref = True
            end_ref_counter = 0 # Zeroing the "end of ref counter", as we found a tagged word
        else: #we found a non tagged word
            if in_ref == False: #we are not inside a ref, let's just continue
                previous_elements.append(mergedResults[i])
                continue

            else: # we are inside a ref, did we finished it?
                # we finished the ref words or becuase we reached a "." or we had 3 "O" in a row. 
                # its time to process it! 
                if (mergedResults[i][0] == ".") or end_ref_counter > 2:
                    #we are about to process the words we found
                    # first let's create a deep copy so we can do some manipulation
                    previous_elements_2_process = copy.deepcopy(previous_elements)
                    previous_elements_2_process = list(previous_elements_2_process)
                    #now lets Zero the values as we don't want this words to be really processed 
                    for word_set in previous_elements_2_process:
                        word_set[1] =  "O"
                        word_set[2] =  "O"
                    
                    if is_weak_tag_refrence(sub_mergedResults) == True:
                        RT_sub_mergedResults = copy.deepcopy(sub_mergedResults)
                        for word_set in RT_sub_mergedResults:
                            word_set[2] =  "RT"
                        # Now lets add the previous_elements_2_process to the sub_mergedResults
                        RT_sub_mergedResults = previous_elements_2_process + RT_sub_mergedResults
                        refObj_list = build_refrences(RT_sub_mergedResults, text_source, file_path)
                    else:    
                        #process the word list in sum_merge_Results and produce, corespondingly, ref_objects
                        sub_mergedResults = previous_elements_2_process + sub_mergedResults
                        refObj_list = build_refrences(sub_mergedResults, text_source, file_path)
                    # add the results to our list of the prevouse results
                    refrences_found.extend(refObj_list)
                    
                    # we finished the processing, lets zero evrything and continue the loop
                    sub_mergedResults = []
                    in_ref = False
                    end_ref_counter = 0 
                    
            
                else: 
                    #we didn't finish the current ref, lets just continue
                    sub_mergedResults.append(mergedResults[i])
                    end_ref_counter += 1
                    
    
    #we gote out of the loop but may be we still have ref to resolve
    if in_ref == True:
        if is_weak_tag_refrence(sub_mergedResults) == True:
            RT_sub_mergedResults = copy.deepcopy(sub_mergedResults)
            for word_set in RT_sub_mergedResults:
                word_set[2] =  "RT"
            refObj_list = build_refrences(RT_sub_mergedResults, text_source, file_path)
        else:    
            #process the word list in sum_merge_Results and produce, corespondingly, ref_objects
            refObj_list = build_refrences(sub_mergedResults, text_source, file_path)

        refrences_found.extend(refObj_list)
    
    return refrences_found

# some time the model only identify one or two tags like RC or SC 
# lets see if this ref is from this type
def is_weak_tag_refrence(sub_mergedResults):
    for word_set in sub_mergedResults:
        if word_set[1] in weak_tags and word_set[2] == "O":
            continue
        else:
            return False #real data tag was found
    
    #no real data tag was found, this is a weak ref
    return True

# break the ref words to their ingredient and build the ref objects
def build_refrences(sub_mergedResults, text_source = "", file_path = ""):
    try: 
        layer_1_iter = iter(process_by_layer_1(sub_mergedResults))
        layer_2_iter = iter(process_by_layer_2(sub_mergedResults))
        row_results = []
        refrences_found = []
        word_index = -1  # since we do the index augmentation at the beginning of the loop we must starts from -1 in order to be 0 and the first loop iteration
        # main loop over the text:
        refObj = RefObject(text_source, file_path)
          
        for word_set in sub_mergedResults:
            word_index += 1
            
            try:
                layer_1_state = next(layer_1_iter)
            except StopIteration:
                pass   
            
            try:
                layer_2_state = next(layer_2_iter)
            except StopIteration:
                pass  
            # If we have a mismatch of the words processing, aborting the process
            # Note this if is only for process health validation
            if (layer_1_state.current_word_set != word_set) or (layer_2_state.current_word_set != word_set):
                break

            # assigning the recursive value whatever its true of false    
            refObj.recursive_ref = layer_2_state.recursive_ref
            
            #we got indication from layer 2 we completed the ref (e.g. via a BM family tag)
            # alternately we got indication we running in to an internal ref
            if layer_2_state.ref_completed:
                row_results.append(refObj)
            
                #logging the ref obj we found till now, since we are still inside the loop lets continue
                refObj = RefObject(text_source, file_path)
            
            # add the word we are now processing
            refObj.extended_words_tags_list.append(word_set)

        # we finished the loop, but Maybe we still have some BB to resolve:
        try:
            layer_1_state = next(layer_1_iter)
        except StopIteration:
                pass
        try:
            layer_2_state = next(layer_2_iter)
        except StopIteration:
                pass
        row_results.append(refObj)
        for ref_Object in row_results:
            merge_layers_results(ref_Object)
            ref_Object = populate_initial_meta_data(ref_Object)
            ref_obj_list = populate_refObjs(ref_Object)
            current_final_res = finalize_refObjs(ref_obj_list)
            if len(current_final_res) > 0:
                refrences_found.extend(current_final_res)

    except Exception as ex:
        print("issue in func: build_refrences")
        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(ex)
    
    #we finished to process all the words in sub_mergedResults, lets return the ref objects we found
    return refrences_found

#assign to the word sets list the selected object at the merge_idx (= 5) location
def assign_final_merge_idx(refObj, word_set_idx, layer_res, layer_res_len, overlap_idx = 0):
    try:
        merge_idx = 5
        end_idx = word_set_idx + 1 - overlap_idx
        start_idx = word_set_idx - (layer_res_len - 1)
        for idx in range(start_idx, end_idx):
            refObj.extended_words_tags_list[idx][merge_idx] = layer_res
    except Exception as ex:
        print("issue in func: assign_final_merge_idx")
        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(ex)

#assign the results (all the Canonize_abbrv we found) to the ref object field: author, book, base book etc... 
def merge_layers_results(refObj):
    word_set_idx = -2 # since we always update the -1 idx and since we always increae the value of the idx at the begining of the loop hence we set it for -2
    layer_1_res_idx = 3
    layer_2_res_idx = 4
    merge_idx = 5
    layers_tag_value = Layers_tag_value()

    try:
        for word_set in refObj.extended_words_tags_list:
            word_set_idx += 1       

            if len(word_set[layer_1_res_idx]) == 0 and len(word_set[layer_2_res_idx]) == 0: #no results to log, so just continue
                #no new results, no previous results, lets just continue 
                if layers_tag_value.layer_1_res == None and layers_tag_value.layer_2_res == None: 
                    continue
                else:
                    if layers_tag_value.layer_1_res != None and layers_tag_value.layer_2_res == None:
                        assign_final_merge_idx(refObj, word_set_idx,layers_tag_value.layer_1_res, layers_tag_value.layer_1_res_len)
                    elif layers_tag_value.layer_1_res == None and layers_tag_value.layer_2_res != None:
                        assign_final_merge_idx(refObj, word_set_idx,layers_tag_value.layer_2_res, layers_tag_value.layer_2_res_len)       
                    else: # we have values in both lets check the type or log the longest 
                        
                        # type R is always less preferred if its not an R type then lets pick the tag by the longest one
                        if (layers_tag_value.layer_2_res_len > layers_tag_value.layer_1_res_len) or layers_tag_value.layer_1_res[0].type == Building_block_type_Enum.R:
                            assign_final_merge_idx(refObj, word_set_idx,layers_tag_value.layer_2_res, layers_tag_value.layer_2_res_len)  
                        else: #for now we are just taking the first one
                            assign_final_merge_idx(refObj, word_set_idx,layers_tag_value.layer_1_res, layers_tag_value.layer_1_res_len)
                        # TODO check deeper who is better: by quality or by number of results(?), or does they refer to the same canonized str? what else?
                        
                    # restart
                    layers_tag_value = Layers_tag_value()
                
            # we have a value only in layer 1
            # it imply multiple options:
            # 0. layer 1 tag was completed and now we have a new tag, need to log the previous one
            # 1. layer 1 tag has no previous tag
            # 2. layer 1 tag continue with the same tag from the previous word
            # given all the above, IN CASE WE NEED TO LOG (option 0), need to consider layer 2:
            # 1. No previous value in layer 2, only layer 1 need to be logged
            # 2. Layer 2 tag was also completed, need to decide if layer 1 or layer 2 should be logged
            elif len(word_set[layer_1_res_idx]) != 0 and len(word_set[layer_2_res_idx]) == 0:
                # Layer 1 is now empty, but maybe from the previous loops it hold values 
                if layers_tag_value.layer_2_res == None:
                    # Lets handle layer 1 tag results
                    if layers_tag_value.layer_1_res == None: #we are starting a new tag result 
                        layers_tag_value.layer_1_res = word_set[layer_1_res_idx]
                        layers_tag_value.layer_1_res_len = 1
                    else:
                        if layers_tag_value.layer_1_res == word_set[layer_1_res_idx]:  # we continue the previous tag result  
                            layers_tag_value.layer_1_res_len += 1 #so just increase it length
                        else:
                            # its a new tag type, lets log the previous, and then restart with this new tags
                            assign_final_merge_idx(refObj, word_set_idx,layers_tag_value.layer_1_res, layers_tag_value.layer_1_res_len)
                            # Now restart:
                            layers_tag_value = Layers_tag_value()
                            layers_tag_value.layer_1_res = word_set[layer_1_res_idx]
                            layers_tag_value.layer_1_res_len = 1  
                
                else: # Layer 1 was NOT empty, need to decide how to handle the previous word_set
                    # If the layer 2 tags type are new, then everything is new, so just assign the merge idx for te previous word_set
                    if layers_tag_value.layer_1_res != word_set[layer_1_res_idx]:
                        # type R is always less preferred if its not an R type then lets choose the tag by the longest one
                        if (layers_tag_value.layer_2_res_len > layers_tag_value.layer_1_res_len) or layers_tag_value.layer_1_res[0].type == Building_block_type_Enum.R:
                            assign_final_merge_idx(refObj, word_set_idx,layers_tag_value.layer_2_res, layers_tag_value.layer_2_res_len)
                        else: #for now we are just taking the first one
                            assign_final_merge_idx(refObj, word_set_idx,layers_tag_value.layer_1_res, layers_tag_value.layer_1_res_len)
                      
                        # any how since its a fresh start, lets restart 
                        layers_tag_value = Layers_tag_value()
                        layers_tag_value.layer_1_res = word_set[layer_1_res_idx]
                        layers_tag_value.layer_1_res_len = 1  

                    else: # we are continuum of layer 2, what to do with previous layer 1 values?
                        # we will do a kind of guess:
                        # we will assign layer 1 till the start of the current continuum layer 2
                        if layers_tag_value.layer_1_res_len < layers_tag_value.layer_2_res_len: #nothing to do, so lets just zero layer 1
                            over_lap_idx = layers_tag_value.layer_2_res_len - layers_tag_value.layer_1_res_len
                            assign_final_merge_idx(refObj, word_set_idx, layers_tag_value.layer_2_res, layers_tag_value.layer_2_res_len, over_lap_idx)      
                        # Now zero layer 1
                        layers_tag_value.layer_2_res_len = 0
                        layers_tag_value.layer_2_res = None
                        
                        # since we are continue we only have to increase the length
                        layers_tag_value.layer_1_res_len += 1   

            # exactly as above, but layer 2 has value while layer 1 has no value 
            elif len(word_set[layer_1_res_idx]) == 0 and len(word_set[layer_2_res_idx]) != 0:
                # Layer 1 is now empty, but maybe in the previous lops it hold values 
                if layers_tag_value.layer_1_res == None:
                    # Lets handle layer 1 tag results
                    if layers_tag_value.layer_2_res == None: #we are starting a new tag result 
                        layers_tag_value.layer_2_res = word_set[layer_2_res_idx]
                        layers_tag_value.layer_2_res_len = 1
                    else:
                        if layers_tag_value.layer_2_res == word_set[layer_2_res_idx]:  # we continue the previous tag result  
                            layers_tag_value.layer_2_res_len += 1 #so just increase it length
                        else:
                            # its a new tag type, lets log the previous, and then restart with this new tags
                            assign_final_merge_idx(refObj, word_set_idx,layers_tag_value.layer_2_res, layers_tag_value.layer_2_res_len)
                            # Now restart:
                            layers_tag_value = Layers_tag_value()
                            layers_tag_value.layer_2_res = word_set[layer_2_res_idx]
                            layers_tag_value.layer_2_res_len = 1  
                
                else: # Layer 1 was NOT empty, need to decide how to handle the previous word_set
                    # If the layer 2 tags type are new, then everything is new, so just assign the merge idx for te previous word_set
                    if layers_tag_value.layer_2_res != word_set[layer_2_res_idx]:
                        # type R is always less preferred if its not an R type then lets choose the tag by the longest one
                        if (layers_tag_value.layer_2_res_len > layers_tag_value.layer_1_res_len) or layers_tag_value.layer_1_res[0].type == Building_block_type_Enum.R:
                            assign_final_merge_idx(refObj, word_set_idx,layers_tag_value.layer_2_res, layers_tag_value.layer_2_res_len)
                        else: #for now we are just taking the first one
                            assign_final_merge_idx(refObj, word_set_idx,layers_tag_value.layer_1_res, layers_tag_value.layer_1_res_len)
                      
                        # any how since its a fresh start, lets restart 
                        layers_tag_value = Layers_tag_value()
                        layers_tag_value.layer_2_res = word_set[layer_2_res_idx]
                        layers_tag_value.layer_2_res_len = 1  

                    else: # we are continuum of layer 2, what to do with previous layer 1 values?
                        # we will do a kind of guess:
                        # we will assign layer 1 till the start of the current continuum layer 2
                        if layers_tag_value.layer_2_res_len < layers_tag_value.layer_1_res_len: #nothing to do, so lets just zero layer 1
                            over_lap_idx = layers_tag_value.layer_1_res_len - layers_tag_value.layer_2_res_len
                            assign_final_merge_idx(refObj, word_set_idx, layers_tag_value.layer_1_res, layers_tag_value.layer_1_res_len, over_lap_idx)      
                        # Now zero layer 1
                        layers_tag_value.layer_1_res_len = 0
                        layers_tag_value.layer_1_res = None
                        
                        # since we are continue we only have to increase the length
                        layers_tag_value.layer_2_res_len += 1   
                        

            # in case we have values in both of teh layers, need to check if both finished or only one 
            # if both just started, lets log and continue
            # if both finished, lets log the longer
            # if one is still running continue
            elif len(word_set[layer_1_res_idx]) != 0 and len(word_set[layer_2_res_idx]) != 0:
                # both layers just started we have no previous data, lets just log it
                if layers_tag_value.layer_1_res == None and layers_tag_value.layer_2_res == None:
                    layers_tag_value.layer_2_res = word_set[layer_2_res_idx]
                    layers_tag_value.layer_2_res_len = 1
                    layers_tag_value.layer_1_res = word_set[layer_1_res_idx]
                    layers_tag_value.layer_1_res_len = 1
                # we have history only in one layer
                # lets see if it continues the previous word, hence only log it
                # or its a new tag, hence log at merge index and log the new values
                elif layers_tag_value.layer_1_res != None and layers_tag_value.layer_2_res == None:
                    # it no a continuum, first log the previous
                    if layers_tag_value.layer_1_res != word_set[layer_1_res_idx]:
                        assign_final_merge_idx(refObj, word_set_idx,layers_tag_value.layer_1_res, layers_tag_value.layer_1_res_len)
                        #restarting for the new values
                        layers_tag_value.layer_2_res = word_set[layer_2_res_idx]
                        layers_tag_value.layer_2_res_len = 1
                        layers_tag_value.layer_1_res = word_set[layer_1_res_idx]
                        layers_tag_value.layer_1_res_len = 1
                    else: # its a continuum for layer 1
                        layers_tag_value.layer_2_res = word_set[layer_2_res_idx]
                        layers_tag_value.layer_2_res_len = 1
                        layers_tag_value.layer_1_res = word_set[layer_1_res_idx]
                        layers_tag_value.layer_1_res_len += 1
                # we have history in only the other layer
                elif layers_tag_value.layer_1_res == None and layers_tag_value.layer_2_res != None:
                    # its not a continuum, first log the previous
                    if layers_tag_value.layer_2_res != word_set[layer_2_res_idx]:
                        assign_final_merge_idx(refObj, word_set_idx,layers_tag_value.layer_2_res, layers_tag_value.layer_2_res_len)
                        #restarting for the new values
                        layers_tag_value.layer_2_res = word_set[layer_2_res_idx]
                        layers_tag_value.layer_2_res_len = 1
                        layers_tag_value.layer_1_res = word_set[layer_1_res_idx]
                        layers_tag_value.layer_1_res_len = 1 
                    else: # its a continuum for layer 2
                        layers_tag_value.layer_2_res = word_set[layer_2_res_idx]
                        layers_tag_value.layer_2_res_len += 1
                        layers_tag_value.layer_1_res = word_set[layer_1_res_idx]
                        layers_tag_value.layer_1_res_len = 1 
                # both have previous values
                elif layers_tag_value.layer_1_res != None and layers_tag_value.layer_2_res != None:
                    # both previous values are not a continuum of the current
                    #lets just log the longest
                    if layers_tag_value.layer_1_res != word_set[layer_1_res_idx] and layers_tag_value.layer_2_res != word_set[layer_2_res_idx]:
                        # type R is always less preferred if its not an R type then lets choose the tag by the longest one
                        if (layers_tag_value.layer_2_res_len > layers_tag_value.layer_1_res_len) or layers_tag_value.layer_1_res[0].type == Building_block_type_Enum.R:
                            assign_final_merge_idx(refObj, word_set_idx,layers_tag_value.layer_2_res, layers_tag_value.layer_2_res_len)
                        else: #for now we are just taking the first one
                            assign_final_merge_idx(refObj, word_set_idx,layers_tag_value.layer_1_res, layers_tag_value.layer_1_res_len)
                        # TODO check deeper who is better: by quality or by number of results(?), or does they refer to the same canonized str? what else?
                        
                        #restart
                        layers_tag_value.layer_2_res = word_set[layer_2_res_idx]
                        layers_tag_value.layer_2_res_len = 1
                        layers_tag_value.layer_1_res = word_set[layer_1_res_idx]
                        layers_tag_value.layer_1_res_len = 1
                    #both are continuum
                    elif layers_tag_value.layer_1_res == word_set[layer_1_res_idx] and layers_tag_value.layer_2_res == word_set[layer_2_res_idx]: 
                        layers_tag_value.layer_2_res_len += 1
                        layers_tag_value.layer_1_res_len += 1
                    #TODO we have a case were layer is continuum will layer 2 is not (and both have previous results) this code don't handle this case and need to add it
                    else:
                        # first lets give priority to none R types
                        if word_set[layer_1_res_idx][0].type == Building_block_type_Enum.R and word_set[layer_2_res_idx][0].type != Building_block_type_Enum.R: #if we 
                            assign_final_merge_idx(refObj, word_set_idx,layers_tag_value.layer_2_res, layers_tag_value.layer_2_res_len)
                            if layers_tag_value.layer_2_res == word_set[layer_2_res_idx]:
                                layers_tag_value.layer_2_res_len += 1
                            else:
                                layers_tag_value.layer_2_res = word_set[layer_2_res_idx]
                            layers_tag_value.layer_2_res_len = 1
                        # no "none R" priority:
                        if layers_tag_value.layer_1_res == word_set[layer_1_res_idx] and layers_tag_value.layer_2_res != word_set[layer_2_res_idx]: 
                            assign_final_merge_idx(refObj, word_set_idx,layers_tag_value.layer_1_res, layers_tag_value.layer_1_res_len)
                            layers_tag_value.layer_1_res_len += 1
                        elif layers_tag_value.layer_1_res != word_set[layer_1_res_idx] and layers_tag_value.layer_2_res == word_set[layer_2_res_idx]:
                            assign_final_merge_idx(refObj, word_set_idx,layers_tag_value.layer_2_res, layers_tag_value.layer_2_res_len)
                            layers_tag_value.layer_2_res_len += 1
            else:
                print("i want to see it!!!")

        #since we got out of the loop, but we sill may have to assign, lets increase the index
        word_set_idx += 1
        # we finished the loop, let's see if we have values in layers_tag_value we need to log 
        if layers_tag_value.layer_1_res == None and layers_tag_value.layer_2_res == None:
            # no left overs, lets go out
            pass 
        # both layers provided results, lets search for the longer
        elif layers_tag_value.layer_1_res != None and layers_tag_value.layer_2_res != None:
            if layers_tag_value.layer_2_res_len > layers_tag_value.layer_1_res_len:
                assign_final_merge_idx(refObj, word_set_idx,layers_tag_value.layer_2_res, layers_tag_value.layer_2_res_len)
            elif layers_tag_value.layer_2_res_len < layers_tag_value.layer_1_res_len:
                assign_final_merge_idx(refObj, word_set_idx,layers_tag_value.layer_1_res, layers_tag_value.layer_1_res_len)
            # both are equal size, lets see if one is higher quality
            # TODO check deeper who is better: by quality or by number of results(?), or does they refer to the same canonized str? what else?
            else: #for now we are just taking the first one
                if layers_tag_value.layer_1_res[0].type == Building_block_type_Enum.R and layers_tag_value.layer_2_res[0].type != Building_block_type_Enum.R:
                    assign_final_merge_idx(refObj, word_set_idx,layers_tag_value.layer_2_res, layers_tag_value.layer_2_res_len)
                else:
                    assign_final_merge_idx(refObj, word_set_idx,layers_tag_value.layer_1_res, layers_tag_value.layer_1_res_len)

        # only layer 1 provided values
        elif layers_tag_value.layer_1_res != None:
            assign_final_merge_idx(refObj, word_set_idx,layers_tag_value.layer_1_res, layers_tag_value.layer_1_res_len)
        # only layer 1 provided values
        elif layers_tag_value.layer_2_res != None:
            assign_final_merge_idx(refObj, word_set_idx,layers_tag_value.layer_2_res, layers_tag_value.layer_2_res_len)
    
    except Exception as ex:
        print("issue in func: merge_layers_results")
        print(ex)
    return

# process the words-tags according to layer 2 tags to building blocks and resolve the building block content
def process_by_layer_1( mergedResults):
    try: 
        BB = Ref_build_block()
        state = Words_tags_processing_state_obj()

        for word_set in mergedResults:
            # TODO do we need to log the 2 words before the building block like we did for the previous function:
            # process_by_layer_1
            
            # always adding the current word_set to be validate in the calling function
            # (build_refrences) to make sure the words processing is aligned between all the functions
            state.current_word_set = word_set
            #the word has no tag and we are not inside a BB, so just return 
            if word_set[1] == "O":
                if state.in_BB == False:
                    # the word_set is not interesting at all
                    yield state
                    #lets move to the next word_set
                    continue
                else: #we are inside a BB
                    if state.in_BB_0_counter >=2: #we already saw 3 "O" we probably finished the BB, lets resolve it
                        # TODO add a check that we are really popping out word set with tag O
                        try:
                            BB.word_set_list.pop()
                            BB.word_set_list.pop()
                        except Exception as ex:
                            print("exception in function: process_by_layer_1")
                            print("BB.word_set_list.pop")
                            print(ex)
                        resolve_BB(BB, Model_power.Layer_1_model)
                        yield state
                        
                        state = Words_tags_processing_state_obj()
                        BB = Ref_build_block()
                        #lets move to the next word_set
                        continue

                    else: #we are still inside but we didn't finish the BB
                        BB.word_set_list.append(word_set)
                        state.in_BB_0_counter += 1
                        yield state
                        #lets move to the next word_set
                        continue

            #if we are here it means we are not in a ref level word tags, but in a content tag like RT, TM, TR, TSR , RRN, RR etc...
            word_set_type = resolve_building_block_type2(word_set, Model_power.Layer_1_model)
            if BB.tag_type == None or BB.tag_type == word_set_type:
                BB.tag_type = word_set_type # eventually only relevant for the condition: BB.tag_type == None
                state.in_BB_0_counter = 0 # eventually only relevant for the condition: BB.tag_type == None
                BB.word_set_list.append(word_set)
                state.in_BB = True
                yield state
            
            else: # BB.tag_type != word_set_type:
                resolve_BB(BB, Model_power.Layer_1_model)
                yield state

                # we don't need to change the state, just creating a new building block
                state = Words_tags_processing_state_obj(in_BB = True)
                BB = Ref_build_block()
                BB.current_word_set = word_set
                BB.tag_type = word_set_type
                BB.word_set_list.append(word_set)
            
            
        #we completed the loop, lets see if we have some left over
        if state.in_BB == True:
            resolve_BB(BB, Model_power.Layer_1_model)
            yield state
    
    except Exception as ex:
        print("issue in func: process_by_layer_1")
        print(ex)        

# process the words-tags according to layer 2 tags to building blocks and resolve the building block content
def process_by_layer_2(mergedResults):
    try:
        BB = Ref_build_block()
        state = Words_tags_processing_state_obj()
        
        for word_set in mergedResults:
            # always adding the current word_set to be validate in the calling function
            # (build_refrences) to make sure the words processing is aligned between all the functions
            state.current_word_set = word_set
            #the word has no tag and we are not inside a BB, so just return 
            if word_set[2] == "O":
                if state.in_BB == False:
                    yield state
                    #lets move to the next word_set
                    continue
                else: #we are inside a BB
                    if state.in_BB_0_counter >=2: #we already saw 3 "O" we probably finished the BB, lets resolve it
                        # TODO add a check that we are really popping out word set with tag O
                        try:
                            BB.word_set_list.pop()
                            BB.word_set_list.pop()
                        except Exception as ex:
                            print("exception in function: process_by_layer_2")
                            print("BB.word_set_list.pop")
                            print(ex)
                        resolve_BB(BB, Model_power.Layer_2_model)
                        yield state

                        state = Words_tags_processing_state_obj()
                        BB = Ref_build_block()
                        #lets move to the next word_set
                        continue

                    else: #we are still inside but we didn't finish the BB
                        BB.word_set_list.append(word_set)
                        state.in_BB_0_counter += 1
                        yield state
                        #lets move to the next word_set
                        continue
            
            if word_set[0] in tag_Punctuation:
                BB.word_set_list.append(word_set)
                yield state
                #lets move to the next word_set
                continue
            
            #we found a break mark, lets log everything 
            if word_set[2] in BM_tags:
                state.ref_completed = True
                resolve_BB(BB, Model_power.Layer_2_model)
                yield state

                state = Words_tags_processing_state_obj()
                BB = Ref_build_block()
                if word_set[2] != "BM": # if its not BM (break mark) then the word contain important info we need to log
                    BB.tag_type = resolve_building_block_type2(word_set, Model_power.Layer_2_model)
                    BB.word_set_list.append(word_set)   
                    state.in_BB = True
                continue

            # Recursive ref handling
            # in this "if" the reference we currently FINISHED is INTERNAL, we must log it
            if word_set[2] in BM_Recursion_tags_post_ref:
                state.recursive_ref = True
                state.ref_completed = True
                resolve_BB(BB, Model_power.Layer_2_model)
                yield state

                state = Words_tags_processing_state_obj()
                BB = Ref_build_block()
                BB.word_set_list.append(word_set)
                continue

            # Recursive ref handling
            # in this "if" the reference we are currently STARTING is INTERNAL, we must log it
            if word_set[2] in BM_Recursion_tags:
                state.ref_completed = True
                resolve_BB(BB, Model_power.Layer_2_model)
                yield state

                state = Words_tags_processing_state_obj(recursive_ref = True)
                BB = Ref_build_block()
                if word_set[2] != "BMRS": # if its not BM (break mark) then the word contain important info we need to log
                    BB.tag_type = resolve_building_block_type2(word_set, Model_power.Layer_2_model)
                    BB.word_set_list.append(word_set)   
                    state.in_BB = True
                continue
                

            #we have an internal BM (IBM) for example same author on 2 base books
            if word_set[2] in BM_internal_tags:
                resolve_BB(BB, Model_power.Layer_2_model)
                yield state

                state = Words_tags_processing_state_obj(internal_BB = True)
                BB = Ref_build_block()
                if word_set[2] != "IBM": # if its not a BM (break mark) then the word contain important info we need to log
                    BB.tag_type = resolve_building_block_type2(word_set, Model_power.Layer_2_model)
                    BB.word_set_list.append(word_set)   
                    state.in_BB = True
                #if its a real IBM just need to move to the next word_set
                #anyhow lets continue
                continue

            #if we are here it means we are not in a ref level word tags, but in a content tag like RT, TM, TR, TSR , RRN, RR etc...
            word_set_type = resolve_building_block_type2(word_set, Model_power.Layer_2_model)
            if BB.tag_type == None or BB.tag_type == word_set_type:
                BB.tag_type = word_set_type # eventually only relevant for the condition: BB.tag_type == None
                state.in_BB_0_counter = 0 # eventually only relevant for the condition: BB.tag_type == None
                BB.word_set_list.append(word_set)
                state.in_BB = True
                yield state
            
            else: # BB.tag_type != word_set_type:
                resolve_BB(BB, Model_power.Layer_2_model)
                yield state

                # we don't need to change the state, just creating a new building block
                state = Words_tags_processing_state_obj(in_BB = True)
                BB = Ref_build_block()
                BB.current_word_set = word_set
                BB.tag_type = word_set_type
                BB.word_set_list.append(word_set)

        #we completed the loop, lets see if we have some left over
        if state.in_BB == True:
            resolve_BB(BB, Model_power.Layer_2_model)
            yield state

    except Exception as ex:
        print("issue in func: process_by_layer_2")
        print('Error on line {}'.format(sys.exc_info()
                      [-1].tb_lineno), type(ex).__name__, ex)
        print(ex)     

