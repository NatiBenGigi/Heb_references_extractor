# Project: Hebrew Reference extractor
#
# Created by: Nati Ben-Gigi
# Date: 11/2023
#
# License: MIT
# Copyright: Nati Ben-Gigi 2023
#
# File: 
# Description: shared_classes.py
# base classes serving as building blocks for references related ingredients

from enum import Enum
from find_ref_helper import *

#the results of evry layer on a given tag and for how may words its already like this
class Layers_tag_value():
    def __init__(self) -> None:
        self.layer_1_res = None #a list of abbr_canonized object produced by layer 1
        self.layer_1_res_len = 0 # the number of words the above res apply to
        self.layer_2_res = None #a list of abbr_canonized object produced by layer 2
        self.layer_2_res_len = 0 # the number of words the above res apply to


class Words_tags_processing_state_obj():
    def __init__(self, in_BB = False, in_BB_0_counter = 0, recursive_ref = False, internal_BB = False, word_set = None, ref_completed = False) -> None:
        # common layer 1 and layer2 info
        self.in_BB = in_BB
        self.in_BB_0_counter = in_BB_0_counter
        self.current_word_set = word_set
        self.word_set_list = []

        #layer 2 only
        self.recursive_ref = recursive_ref
        self.internal_BB = internal_BB
        self.ref_completed = ref_completed


#an abbreviation and its canonized string
class Cnonize_abbrv():
    def __init__(self, abbreviation, canonizedStr, quality, Building_block_type): 
        try:
            self.canonizedStr = canonizedStr
            self.abbreviation = abbreviation
            self.quality = quality
            self.type = Building_block_type
        
        except Exception as ex:
            print("issue in contractor func: Cnonize_abbrv")
            print(ex)

class book_details():
    def __init__(self):
        self.Name = ""
        self.ENGLISH_name = ""
        self.publication_data = ""
        self.commentary_of = ""
        
#all the details about a single authors
class Author_biography():
    def __init__(self):
        self.Name = ""
        self.ENGLISH_name = "" 
        self.NickName = ""
        self.DATE_OF_BIRTH = None 
        self.DATE_DIED = None 
        self.city = ""
        self.Country = ""
        self.other_cities = ""
        self.books = []
        self.approx_death = False
        self.approx_location = False
        self.Region = ""
        # this is used to handle rabbi's that are mentioned a lot in a book for example Ri HaZaken in Tosfot 
        self.Mentioned_in_book_as_author = []



class Ref_quality(Enum):
    High = 1
    Medium = 2
    Low = 3
    self_mentioned = 4 # the author ref is the  author of the text
    anachronistic_ref = 5 # the ref ingredients don't match meta data about the ref, example the mentioned author didn't live when the text was written


# define if we are resolving a ref by 2 models are just one model
class Model_power(Enum):
    Layer_1_model = 1
    Layer_2_model = 2
    Dual_model = 3


# this class hold the building blocks of a reference
class Ref_build_block():
     def __init__(self):
        self.tag_type = None
        self.word_set_list = []
        self.str = ""
        self.res_list = []
        self.final_type = None


# this object represents a book in the corpus
class book_in_corpus():
    def __init__(self):
        self.book_name = ""
        self.author_name = "" 
        self.book_folder = ""
        self.num_of_words = 0

# enum for the various types that can construct a full reference
class Building_block_type_Enum(Enum):
    AB = 0  # archiBook
    TM = 1  # Talmud Masechet
    TR = 2  # Talmud reference (e.g. chapter)
    AN = 3  # author
    BN = 4  # Book name
    RR = 5  # Rambam reference
    R = 6 # reference related work
    RT = 7 # reference top (by layer 2)
    No_Tag = 8 # "O"
    TSR = 9 # Tur and Shulhan Aruch

# this class holds metadata for every Halacha in the Yad Hahazaka (Mimonides)
class Hayad_Hahazaka_Hilchot():
    def __init__(self):
        self.book = ""
        self.idx = 0
        self.chapter_2_simanim_mapping = {}


# this class holds all the data of a reference
class RefObject():
    def __init__(self, text_source = "", file_path = ""):
        
        self.text_source = text_source
        self.text_source_ENGLISH = ""
        self.text_author = ""
        self.text_author_ENGLISH = ""
          
        self.clean_file_name = ""
        self.file_name = ""
        self.file_path = file_path
        
        # meta data about the reference
        self.recursive_ref = False
        self.in_ref = False # indicating we are still processing the reference
        self.internal_ref = False  # this field notify if the ref is an internal/recursive ref     

        # the words and their layer_1 and layer_2 tags + pre-words ,this if better understanding of the tagging results
        self.extended_words_tags_list = []
        self.ref_quality = Ref_quality.High
        self.base_book = []  # books like talmud, Rambam, Tour, shulhan aruch. Those books are the base book, tones ot other books or authors are based on those base books
        # the chapter of Talmud, Yad Hahazaka, etc...
        self.base_book_details = []
        self.archi_book = []  # books like Yerushalmi/Tosfeta/Shulhan aruch those books has some global name name and then we go down to lower level name like Tour-> Orach haim, Bavli -> Megila
        
        self.book_name = []
        self.book_name_ENGLISH = ""
        
        self.author_name = []
        self.author_name_ENGLISH = ""

        self.refrence_deatils = []
        self.publication = []
        self.publication_data = []

