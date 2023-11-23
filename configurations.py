# Project: Hebrew Reference extractor
#
# Created by: Nati Ben-Gigi
# Date: 11/2023
#
# License: MIT
# Copyright: Nati Ben-Gigi 2023
#
# File: configurations.py
# Description: 
# Path to all xlsx meta data files of teh project

import os

root_folder = os.path.dirname(os.path.realpath(__file__))

data_resources_folder = os.path.join(root_folder,"data_resources")

Talmud_lookups_path = os.path.join(data_resources_folder, "Talmud_lookups.xlsx" )
talmud_abbreviation_masechtot_path =  os.path.join(data_resources_folder, "talmud_abbreviation masechtot.xlsx")
talmud_abbreviation_chapters_path =  os.path.join(data_resources_folder, "talmud_abbreviation chapters.xlsx")
books_abreviations_path =  os.path.join(data_resources_folder, "books_abreviations.xlsx")
GeneralRefWords_abreviations_path =  os.path.join(data_resources_folder, "RefWordsAbreviations.xlsx")
Hayad_Hahazaka_path = os.path.join(data_resources_folder, "HayadHahazaka.xlsx")
AN_2_skip_path = os.path.join(data_resources_folder, "AN_2_skip.xlsx")
Biography_path = os.path.join(data_resources_folder, "Biography.xlsx")
Books_2_skip_path = os.path.join(data_resources_folder, "Books_2_skip.xlsx")
corpuse_books_author_path = os.path.join(data_resources_folder, "corpuse_books.xlsx")
Hebrew_alphabet_Gematria = os.path.join(data_resources_folder, "Hebrew_Gematria.xlsx")
low_confidance_authors_path = os.path.join(data_resources_folder, "low_confidance_author.xlsx")