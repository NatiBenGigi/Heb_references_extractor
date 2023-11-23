# Project: Hebrew Reference extractor
#
# Created by: Nati Ben-Gigi
# Date: 11/2023
#
# License: MIT
# Copyright: Nati Ben-Gigi 2023
#
# File: xls_logger.py
# Description: 
# xlsx logger class serving to store all extracted references

import sys
import pandas as pd

class generalXls_logger():
    def __init__(self, filePath):
        self.filePathToSave = filePath
        self.df = pd.DataFrame(columns=["text_source",
                                        "text_author", 
                                        "text_author_ENGLISH",
                                        "file_name",
                                        "archi_book",
                                        "base_book",
                                        "base_book_details",
                                        "book_name",
                                        "refrence_deatils",
                                        "author_name",
                                        "original_ref",
                                        "full_words_tags_layer_1_and_2",
                                        "ref_quality",
                                        "reference with delimiter",
                                        "author_name_ENGLISH",
                                        "book_name_ENGLISH",
                                        "file_path",
                                        "Original_file_name"
                                        ], dtype=object)

    # the actual logging function
    def log_results_2_xls(self, text_source, text_author, text_author_ENGLISH, archi_book, base_book, 
                                base_book_details, book_name, author_name, refrence_deatils,
                                original_ref, full_words_tags_layer_1_and_2, ref_quality, file_name,
                                refrence_str_with_delimiter, author_name_ENGLISH, book_name_ENGLISH, file_path, original_file_name):
        try:
            self.df.loc[len(self.df)] = [ text_source, 
                    text_author,
                    text_author_ENGLISH,
                    file_name,
                    archi_book,
                    base_book,
                    base_book_details,
                    book_name,
                    refrence_deatils,
                    author_name,
                    original_ref,
                    full_words_tags_layer_1_and_2,
                    ref_quality,
                    refrence_str_with_delimiter,
                    author_name_ENGLISH,
                    book_name_ENGLISH,
                    file_path,
                    original_file_name]
            
        except Exception as e:
            print("issue in function: log_results_2_xls")
            print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
            print(e)

    # once logging completed, save the data to file
    def saveToFile(self): 
        try:  
            # set the maximum number of rows per sheet
            max_rows_per_sheet = 1000000

            # write the data to multiple sheets
            with pd.ExcelWriter(self.filePathToSave) as writer:  
                for sheet_num, df_chunk in enumerate(self.df.groupby(self.df.index // max_rows_per_sheet)):
                    sheet_name = f'Sheet{sheet_num+1}'
                    df_chunk[1].to_excel(writer, sheet_name=sheet_name, index=False)

            
        except Exception as ex:
                print("issue in class.function: generalXls_logger.saveToFile")
                print ('type is:', ex.__class__.__name__)
                print ('type is:', ex)

