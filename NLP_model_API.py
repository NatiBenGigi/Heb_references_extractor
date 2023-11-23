# Project: Hebrew Reference extractor
#
# Created by: Nati Ben-Gigi
# Date: 11/2023
#
# License: MIT
# Copyright: Nati Ben-Gigi 2023
#
# File: NLP_model_API.py
# Description: 
# the API to the text processing models

import subprocess
from configurations import *
from find_ref_helper import *

# send the  text to the model for processing the merge the results
def prepare_words_tags(responsa_text, responsa_file):

    # invoking the 2 layers (1 and 2)
    taggedResposList_layer1, final_results_string_layer1 = find_ref_layer_1_or_2(
        responsa_text, responsa_file, '/refcrf" ')
    
    taggedResposList_layer2, final_results_string_layer2 = find_ref_layer_1_or_2(
        responsa_text, responsa_file, '/refcrf_layer2" ')
    

    if len(taggedResposList_layer1) != len(taggedResposList_layer2):
        return 0  # we had some issue with Mallet lets return with Zero value
    else:
        
        # merge the results of layer 1 and 2 to a single list
        # mergedResults format is: (word, tag layer1, tag layer2, 0)
        mergedResults = merge_layer_1_and_layer_2_results(taggedResposList_layer1, taggedResposList_layer2)
        
    return mergedResults, final_results_string_layer1, final_results_string_layer2


#merge the results of layer 1 and 2 to a single list 
def merge_layer_1_and_layer_2_results(taggedResposList_layer1, taggedResposList_layer2):
    # create a new list of sets, each set includes:
    # (word, tag from layer 1, tag from layer 2)
    mergedResults = []
    for i in range(len(taggedResposList_layer1)):
        word_1 = taggedResposList_layer1[i][0]
        word_2 = taggedResposList_layer2[i][0]
        if word_1 != word_2:
            print("words mismatch error: " + "the words of layer 1 are diffrent from the words in layer 2")
            break
        # format = (word, tag layer1, tag layer2, layer_1_res, layer_2_res , merged_res, NA to proccess) 
        # layer_1_res, layer_2_res are the list of canonized abbreviation result (for each layer) and the merge
        item = [taggedResposList_layer1[i][0], taggedResposList_layer1[i][1],
                taggedResposList_layer2[i][1], [], [], [], []]  
        mergedResults.append(item)
    
    return mergedResults


# this function does exactly as the function scan_respons_for_refs but w/out saving files, 
# this should improve performance
def scan_respons_for_refs_V2(clean_content, save2file, model_file, reponsaMalletFormatFile):
    
    # if no file was provided, then we are working in GUI and first need to create the responsa file for the mallet lib 
    if reponsaMalletFormatFile == None:
        #preparing the content in mallet format for mallet tagging process 
        malletFormatData = convertRowData2MalletFormat(clean_content)
            
        #saving the content (in mallet format)  
        reponsaMalletFormatFile = results_folder + "/reponsaMalletFormat.txt"
        reponsaMalletFormat = open(reponsaMalletFormatFile, "w")
        reponsaMalletFormat.write(malletFormatData)
        reponsaMalletFormat.close()
    else: # no need to create the file, it was already provided
        #extract the responsa file content for future usage
        FileHandler = open(reponsaMalletFormatFile, "r")
        malletFormatData = FileHandler.read()
        FileHandler.close()

    #invoking mallet tagging function on the saved file and saving the results
    ModelPath = "--model-file " + '"' + results_folder + model_file #'/refcrf" '
    bashCommand = 'java -cp "/Users/natibengigi/Library/Mobile Documents/com~apple~CloudDocs/PHD_scripts/Mallet_win/mallet-2.0.8/mallet-2.0.8/class' \
            + ':' + \
            '/Users/natibengigi/Library/Mobile Documents/com~apple~CloudDocs/PHD_scripts/Mallet_win/mallet-2.0.8/mallet-2.0.8/lib/mallet-deps.jar" ' + \
            'cc.mallet.fst.SimpleTagger ' \
            + ModelPath + ' ' + '"' + reponsaMalletFormatFile + '"' 

    MalletOutputTags = subprocess.getoutput(bashCommand)

    MalletOutputTagsList = MalletOutputTags.split()
    MalletOutputTagsList = MalletOutputTagsList[4:]
    malletFormatDataWordList = malletFormatData.split()

    FinalResultsFile, results, final_results_string = construct_single_layer_results(MalletOutputTagsList, malletFormatDataWordList, save2file)
    
    return FinalResultsFile, results, final_results_string
   
# consolidate the words and the tags to a single struct
def construct_single_layer_results(MalletOutputTagsList, malletFormatDataWordList, save2file):
    num_of_tags = len(MalletOutputTagsList)
    num_of_tokens = len(malletFormatDataWordList)

    if num_of_tags > num_of_tokens:
        index = num_of_tokens
    else:
        index = num_of_tags

    # saving the final results
    FinalResultsFile = ""
    if save2file:
        FinalResultsFile = results_folder + "/FinalResults.txt"
        finalResultsFileHandler = open(FinalResultsFile, "w")        
    results = []

    final_results_string = ""
    for i in range(index):
        
        results.append((malletFormatDataWordList[i].rstrip(), MalletOutputTagsList[i].rstrip(), False) )
        token2lable = malletFormatDataWordList[i].rstrip() + " = " + MalletOutputTagsList[i].rstrip()

        final_results_string += token2lable + "\n"
        if save2file:
            finalResultsFileHandler.write("%s\n" % token2lable)

    if save2file:
        # closing the final results file
        finalResultsFileHandler.close()
    
    return FinalResultsFile, results, final_results_string


def find_ref_layer_1_or_2(responsa_text, responsa_file, model_file):

    save_2_file = False
    # we work via the GUI so (and not via the prepared corpus in mallet format)  we need to save the text as a file
    if responsa_file == None:  # we didn't get a file, we will create one later, for lets clean previous files

        save_2_file = True  # since we work in GUI mode lets save the resulted file
        # lets clean the results folder
        files_2_delet = []
        files_2_delet.append('/reponsaMalletFormat.txt"')
        files_2_delet.append('/MalletOutput.txt"')
        files_2_delet.append('/FinalResults.txt"')
        for i in range(len(files_2_delet)):
            bashCommand = 'rm ' + '"' + results_folder + files_2_delet[i]
            print(bashCommand)
            os.system(bashCommand)

    FinalResultsFile, taggedResposList, final_results_string = scan_respons_for_refs_V2(
        responsa_text, save_2_file, model_file, responsa_file)

    return taggedResposList, final_results_string


