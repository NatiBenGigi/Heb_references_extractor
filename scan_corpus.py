# Project: Hebrew Reference extractor
#
# Created by: Nati Ben-Gigi
# Date: 11/2023
#
# License: MIT
# Copyright: Nati Ben-Gigi 2023
#
# File: scan_corpus.py
# Description: 
# the main entry/API to the scan text/corpus functionality

from xls_logger import *
from configurations import *
from scan_functions_base import *
from formatting_functions import *

# this function goes over all the files in the corpus, extract all the references and save it to XLS
def extract_references_from_corpus(files_data_source, XLS_file_path, scan_tagged_corpus = False, save_tagged_files = False, encoding_value = "utf8"):
    print("==========================================")
    print("scan corpus execution started")
    print("==========================================")

    # the XLS file that will store the results
    my_XLS_logger = generalXls_logger(XLS_file_path)

    if scan_tagged_corpus == False:
        res_iter = iter(retrive_Refrences_from_corpuse(files_data_source, save_tagged_files, encoding_value))
    else:
        res_iter = iter(retrive_tagged_results_from_saved_tagged_corpus(files_data_source))

    num_of_references = 0
    while True:
        try:
            found_refrenses_list = next(res_iter)
            for reference in found_refrenses_list:
                # skip empty references
                if is_results_empty(reference) == True:
                    continue

                full_words_tags_layer_1_and_2, clean_words_list, refrence_str_with_delimiter = format_results(reference)

                # final logging
                my_XLS_logger.log_results_2_xls(
                    reference.text_source,
                    reference.text_author,
                    reference.text_author_ENGLISH,
                    reference.archi_book,
                    reference.base_book,
                    reference.base_book_details,
                    reference.book_name,
                    reference.author_name,
                    reference.refrence_deatils,
                    clean_words_list,
                    full_words_tags_layer_1_and_2,
                    str(reference.ref_quality),
                    reference.clean_file_name,
                    refrence_str_with_delimiter,
                    reference.author_name_ENGLISH,
                    reference.book_name_ENGLISH,
                    reference.file_path,
                    reference.file_name
                    )

                num_of_references += 1

        except Exception as ex:
            if type(ex).__name__ == "StopIteration":
                break
            else:
                print(ex)
                print("Issue in function: extract_references_from_corpus")
                print('Error on line {}'.format(sys.exc_info()
                      [-1].tb_lineno), type(ex).__name__, ex)
                return False, None

    # save the final results
    my_XLS_logger.saveToFile()

    print("==========================================")
    print("scan corpus using rabbinic BERT CRF completed")
    print("number of found refereences:",  num_of_references)
    print("Results saved to file: " + XLS_file_path)
    print("==========================================")
    return True, XLS_file_path


# This function serves as an example for an API to automatically extract references.
if __name__ == "__main__":

    root_folder = os.path.dirname(os.path.realpath(__file__))

    files_data_source = os.path.join(root_folder,"my corpus path")
    XLS_file_path = os.path.join(root_folder,"extracted_references_list.xls")

    final_result, _ = extract_references_from_corpus(files_data_source, XLS_file_path)
    if final_result == False:
        print("scan corpus could not be completed")
