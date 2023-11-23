# Project: Hebrew Reference extractor
#
# Created by: Nati Ben-Gigi
# Date: 11/2023
#
# License: MIT
# Copyright: Nati Ben-Gigi 2023
#
# File: Ontology.py
# Description: 
# The ontology class contains all the pre-prepared meta data, like:
# all the talmud tractate and their chapter
# abbreviation the following:
#   author, books, talmud tractate, talmud chapter and more
# Authors BIO
# additional meta data

from configurations import *
from find_ref_helper import *
import pandas as pd

class Ontology():
    
    # Load all the items files and their abbreviations
    def load_abbreviation(self):
        for abbrev_dict_key, file_path in self.abbreviation_resources.items():
            abbrev_dict = self.resources_keys[abbrev_dict_key]
            #reminder: in the xls file 
            # column 0 is the canonized name 
            # column 1 is the list of abbreviations 
            
            df = pd.read_excel(file_path, sheet_name=0, header=None)
            df = df.fillna('') 

            self.build_abbrev_dict(abbrev_dict, df)

    # Given the abbreviation sheet, build the final abbreviation dict
    def build_abbrev_dict(self, abbrev_dict, df):

        for _, row in df.iterrows():
            #lets build the list of all the abbreviation of the given item 
            abbr_list_str =  row.iloc[1]
            clean_abbreviations = self.build_abbrev_list(abbr_list_str)
            
            # now lets build the dict:
            key_item, _ = clean_text2(row.iloc[0])
            abbrev_dict[key_item] = clean_abbreviations
    
    # Build the full list of abbreviations for a single entry
    def build_abbrev_list(self, abbr_list_str):
        if len(abbr_list_str) == 0:
            return []
        abbreviations= abbr_list_str.split("; ")
        clean_abbreviations = []
        clean_item = ""
        for item in abbreviations:
            clean_item, _ = clean_text2(item)
            clean_abbreviations.append(clean_item)
        return clean_abbreviations

    def __init__(self):
        # dicts of items and their abbreviations
        self.TR_chapters = {}
        self.TM_Masechtot = {}
        self.Archi_books = {}
        self.Authors = {}
        self.Authors_Biography = {}
        self.Books = {}
        self.Books_details = {}
        self.Authors_2_skip = []
        self.books_2_skip = []
        self.low_confidance_authors = []
        self.Corpuse_books = {}
        self.alphabet_Gematria = {}
        self.General_Ref_Words = {}
        self.Hayad_Hahazaka_mapping = {}
        self.Hayad_Hahazaka_abbr = {}

        self.resources_keys = {"TM": self.TM_Masechtot, \
                            "TR": self.TR_chapters, \
                            "GRF": self.General_Ref_Words}
        #Lookups table
        self.Masechet_2_chapter = {}
        self.Masechet_2_seder = {}
        self.Masechet_2_Archi_books = {}

        #the abbreviations dict and their file path all in a single dict for easier initialization (see below)
        self.abbreviation_resources = {"TM": talmud_abbreviation_masechtot_path, \
                                        "TR": talmud_abbreviation_chapters_path, \
                                        "GRF": GeneralRefWords_abreviations_path}
        #file 
        self.lookUp_resources = Talmud_lookups_path
        self.Authors_2_skip_path = AN_2_skip_path
        self.Biography_path = Biography_path
        self.Books_2_skip_path = Books_2_skip_path
        self.corpuse_books_author_path = corpuse_books_author_path
        self.Hebrew_alphabet_Gematria = Hebrew_alphabet_Gematria
        self.Hayad_Hahazaka_path = Hayad_Hahazaka_path
        self.books_abreviations_path = books_abreviations_path
        self.low_confidance_authors_path = low_confidance_authors_path

        #Now lets really load the files
        self.load_abbreviation()
        self.load_Lookups_tables()
        self.load_author_2_skip()
        self.load_Books_2_skip()
        self.load_low_confidance_authors()
        self.load_Biography()
        self.load_Book_details()
        self.load_corpus_authors_deatils()
        self.load_Hebrew_alphabet_Gematria()
        self.load_Hayad_Hahazaka_mapping()
        
    # Load all the meta data about the Yad Hahazaka written by Mimonides
    def load_Hayad_Hahazaka_mapping(self):

        df = pd.read_excel(self.Hayad_Hahazaka_path, sheet_name=0, header=0)
        # convert nan (float) values coming from the xlsx by Pandas
        df = df.fillna('')

        for _, row in df.iterrows():
            Hayad_Hahazaka_Hilchot_obj = Hayad_Hahazaka_Hilchot()
            Hayad_Hahazaka_Hilchot_obj.idx = int(row.iloc[0])
            Hayad_Hahazaka_Hilchot_obj.book, _ = clean_text2(row.iloc[1])
            
            # Load the mapping representing the number simanim for each chapter
            for i in range(5, 32):
                num_of_simanim = row.iloc[i]
                if num_of_simanim != "":
                   #temp = df.iloc[0, i]
                   chapter, _ = clean_text2(df.columns[i])   #sheet.cell_value(0, i))
                   Hayad_Hahazaka_Hilchot_obj.chapter_2_simanim_mapping[chapter] = int(num_of_simanim)

            Hilchot, _ = clean_text2(row.iloc[2])
            self.Hayad_Hahazaka_mapping[Hilchot] = Hayad_Hahazaka_Hilchot_obj

            # build the chapters abbrev list
            abbr_list_str =  row.iloc[3]
            clean_abbreviations = self.build_abbrev_list(abbr_list_str)
            self.Hayad_Hahazaka_abbr[Hilchot] = clean_abbreviations

        print("debug completed")

    # load the author and their book's path in our corpus
    def load_corpus_authors_deatils(self):
        df = pd.read_excel(self.corpuse_books_author_path, sheet_name=0)
        for _, row in df.iterrows():
            book_in_corpus_obj = book_in_corpus()
            book_in_corpus_obj.book_name, _  = clean_text2(row.iloc[0])
            book_in_corpus_obj.author_name, _ = clean_text2(row.iloc[2]) #the author canonized name
            book_in_corpus_obj.author_name = book_in_corpus_obj.author_name.strip()
            book_in_corpus_obj.book_folder, _ = clean_text2(row.iloc[1]) #the folder of the book in the corpus
            book_in_corpus_obj.num_of_words = row.iloc[3]
            self.Corpuse_books[book_in_corpus_obj.book_name] = book_in_corpus_obj

    # load the name we would like to ignore like הגאון, הרב etc...
    def load_author_2_skip(self):
        df = pd.read_excel(self.Authors_2_skip_path, sheet_name=0)
        for _, row in df.iterrows():
            name = row.iloc[0]
            if name != "":
                clean_name, _ = clean_text2(name)
                self.Authors_2_skip.append(clean_name)

    def load_Books_2_skip(self):
        df = pd.read_excel(self.Books_2_skip_path, sheet_name=0)
        for _, row in df.iterrows():
            name = row.iloc[0]
            if name != "":
                clean_name, _ = clean_text2(name)
                self.books_2_skip.append(clean_name)

    def load_low_confidance_authors(self):
        df = pd.read_excel(self.low_confidance_authors_path, sheet_name=0)
        for _, row in df.iterrows():
            name = row.iloc[0]
            if name != "":
                clean_name, _ = clean_text2(name)
                self.low_confidance_authors.append(clean_name)

    # load the books details
    def load_Book_details(self):
        df = pd.read_excel(self.books_abreviations_path, sheet_name=0)
        # convert nan (float) values coming from the xlsx by Pandas
        df = df.fillna('')

        for _, row in df.iterrows():
            book_details_obj = book_details()
            book_details_obj.Name, _  = (clean_text2(row.iloc[0]))
            book_details_obj.Name = book_details_obj.Name.strip()
            book_details_obj.ENGLISH_name = row.iloc[2]
            book_details_obj.ENGLISH_name = book_details_obj.ENGLISH_name.strip()
            book_details_obj.commentary_of,_ = (clean_text2(row.iloc[3]))
            book_details_obj.commentary_of = book_details_obj.commentary_of.strip()
            self.Books_details[book_details_obj.Name] = book_details_obj
        
            abbr_list_str =  row.iloc[1]
            clean_abbreviations = self.build_abbrev_list(abbr_list_str)
            is_ArchiBook = row.iloc[4]

            if is_ArchiBook == "AB":
                self.Archi_books[book_details_obj.Name] = clean_abbreviations
            else:
                self.Books[book_details_obj.Name] = clean_abbreviations  
     
    # load the details about the authors
    def load_Biography(self):
        df = pd.read_excel(self.Biography_path, sheet_name=0)
        # convert nan (float) values coming from the xlsx by Pandas
        df = df.fillna('')

        for _, row in df.iterrows():
            Biography_obj = Author_biography()
            Biography_obj.Name, _  = (clean_text2(row.iloc[0]))
            Biography_obj.Name = (Biography_obj.Name).strip()
            Biography_obj.ENGLISH_name = row.iloc[1]
            # TODO the idx 2 is overridden!!!
            Biography_obj.NickName,_ = clean_text2(row.iloc[2]) # should be may be replace by the abbreviations of the author
            
            #build the author abbrev list
            abbr_list_str =  row.iloc[2]
            clean_abbreviations = self.build_abbrev_list(abbr_list_str)
            if len(clean_abbreviations) != 0:
                self.Authors[Biography_obj.Name] = clean_abbreviations
            else:
                # if this author has no abbrev then lets just create a list with his name 
                self.Authors[Biography_obj.Name] = [Biography_obj.Name]
            
            DATE_OF_BIRTH = row.iloc[3]
            if DATE_OF_BIRTH != "":
                Biography_obj.DATE_OF_BIRTH = int(DATE_OF_BIRTH)
            
            DATE_DIED = row.iloc[4]
            if DATE_DIED != "":
                Biography_obj.DATE_DIED = int(DATE_DIED)
        
            Biography_obj.city = row.iloc[5]
            Biography_obj.Country = row.iloc[6]
            Biography_obj.other_cities = row.iloc[7]
            books = row.iloc[8].split(";")
            clean_books = []
            for book in books:
                clean_book, _ = clean_text2(book)
                clean_books.append(clean_book.strip())
            Biography_obj.books = clean_books
            if row.iloc[9] != "":
                Biography_obj.approx_death = True
            
            if row.iloc[10] != "":
                Biography_obj.approx_location = True
            
            if row.iloc[11] != "":
                Biography_obj.Region = row.iloc[11]

            Mentioned_in_books_as_author = row.iloc[12].split(";")
            clean_Mentioned_in_books = []
            for book in Mentioned_in_books_as_author:
                clean_clean_Mentioned, _ = clean_text2(book)
                clean_Mentioned_in_books.append(clean_clean_Mentioned.strip())
            Biography_obj.Mentioned_in_book_as_author = clean_Mentioned_in_books

            #add the details of the author to the dict that holds ALL the authors
            self.Authors_Biography[Biography_obj.Name] = Biography_obj

        return True
        
    # Load all the look up tables
    def load_Lookups_tables(self):   
        df = pd.read_excel(self.lookUp_resources, sheet_name=0, header=None)
        # convert nan (float) values coming from the xlsx by Pandas
        df = df.fillna('')

        line_index = 0 
        talmud_chapters = []
        for _, row in df.iterrows():
            if (row.iloc[2]) != "":
                if len(talmud_chapters) == 0:  # this line support the first line of the xls
                    masechet = remove_nikud(row.iloc[2]) #collecting all the chapters of the current masechet:
                    masechet, _ = clean_text2(masechet)
                else:
                    self.Masechet_2_chapter[masechet] = talmud_chapters #saving the previous masechet chapters
                    masechet = remove_nikud(row.iloc[2]) #moving to the new masechet
                    masechet, _ = clean_text2(masechet)
                    talmud_chapters = [] #cleaning the previous masechet chapters
            temp_chapter, _ = clean_text2(remove_nikud(row.iloc[3]))
            talmud_chapters.append(temp_chapter)
            line_index += 1  

        #building the Masechet_2_seder
        line_index = 0
        masechtot = []
        for _, row in df.iterrows():
            if (row.iloc[1]) != "":
                if len(masechtot) == 0:  # this line support the first line of the xls
                    seder = remove_nikud(row.iloc[1]) #collecting all the masechtot of the current seder:
                    seder, _ = clean_text2(seder)
                else:
                    self.Masechet_2_seder[seder] = masechtot #saving the previouse masechet chapters
                    seder = remove_nikud(row.iloc[1]) #moving to the new masechet
                    seder, _ = clean_text2(seder)
                    masechtot = [] #cleaning the previous seder masechtot
            
            if (row.iloc[2] != ""):
                temp_masechet, _ = clean_text2(remove_nikud(row.iloc[2]))
                masechtot.append(temp_masechet)

        for _, row in df.iterrows():
            archi_book = remove_nikud(row.iloc[0]) # masechtot are in column 0
            archi_book, _ = clean_text2(archi_book)
            masechet = remove_nikud(row.iloc[2]) # masechtot are in column 2
            masechet, _ = clean_text2(masechet)
            if masechet != "":
                if archi_book in self.Masechet_2_Archi_books:
                    (self.Masechet_2_Archi_books[archi_book]).append(masechet)
                else:
                    self.Masechet_2_Archi_books[archi_book] = [masechet]

    # Given a book return its author
    def retrieve_author_of_a_book(self, book):
        for author in self.Authors_Biography:
            try:
                authors_books = self.Authors_Biography[author].books # lets get all the books of the current author
            except Exception as ex:
                print("exception in function: resolve_author_books")
                print("authors_books = mapping_dict[author].books")
                print("could not find author: ", author[::-1])
                continue
            
            if book in authors_books:
                return author
        # we could not find the author of that book
        return None

    def load_Hebrew_alphabet_Gematria(self):
        try:
            df = pd.read_excel(self.Hebrew_alphabet_Gematria, sheet_name=0, header=None)
            for _, row in df.iterrows():
                letter, _  = (clean_text2(row.iloc[0]))
                letter = letter.strip()
                self.alphabet_Gematria[letter] = row.iloc[1]
        
        except Exception as ex:
            print("issue in function: load_Hebrew_alphabet_Gematria")
            print(ex)
            print('Error on line {}'.format(sys.exc_info()
                        [-1].tb_lineno), type(ex).__name__, ex)
        

        print("load Gematria completed")

        

ontology = Ontology()