# Project: Hebrew Reference extractor
#
# Created by: Nati Ben-Gigi
# Date: 11/2023
#
# License: MIT
# Copyright: Nati Ben-Gigi 2023
#
# File: Hebrew_Gematria_helper.py
# Description: 
# This file contains functions related to Hebrew Gematria, like checking 
# if a string in Hebrew can actually be a number using the Hebrew Gematria

from Ontology import  ontology #*
import sys

# Check if the number is טז  or טו
def check_TZ_and_TV(Hebrew_number):
    try:
        if len(Hebrew_number) != 2:
            return False
        
        first_digit = Hebrew_number[0]
        second_digit = Hebrew_number[1]
        if first_digit == "ט":
            if second_digit in ["ו", "ז"]:
                return True
            else:
                return False
    except Exception as ex:
        print(ex)
        print("Issue in function: check_TZ_and_TV")
        print('Error on line {}'.format(sys.exc_info()
                      [-1].tb_lineno), type(ex).__name__, ex)
        
    return False

#check the correctness of a 2 digit hebrew number
def check_2_digit_Hebrew_number(Hebrew_number):
    try:
        if len(Hebrew_number) != 2:
            return False
        
        if check_TZ_and_TV(Hebrew_number) == True:
                return True

        first_digit = Hebrew_number[0]
        second_digit = Hebrew_number[1] 
        
        if ontology.alphabet_Gematria[first_digit] < 10 or ontology.alphabet_Gematria[first_digit] > 100:
            return False
        
        if ontology.alphabet_Gematria[second_digit] > 9: 
            return False

        return True
    except Exception as ex:
        print(ex)
        print("Issue in function: check_2_digit_Hebrew_number")
        print('Error on line {}'.format(sys.exc_info()
                      [-1].tb_lineno), type(ex).__name__, ex)
        
    return False

#check the correctness of a 3 digit hebrew number
def check_3_digit_Hebrew_number(Hebrew_number):
    try:
        if len(Hebrew_number) != 3:
            return False
        
        first_digit = Hebrew_number[0]
        if first_digit in ["ך", "ם", "ן", "ף", "ץ"]:
            # the first digit is OK, lets check the rest
            return check_2_digit_Hebrew_number(Hebrew_number[1:])

        # a 3 digit hbrew number can not start by thos laters
        if ontology.alphabet_Gematria[first_digit] < 100:
            return False
        
        # the first digit is OK, lets check the rest
        return check_2_digit_Hebrew_number(Hebrew_number[1:])
    except Exception as ex:
        print(ex)
        print("Issue in function: check_3_digit_Hebrew_number")
        print('Error on line {}'.format(sys.exc_info()
                      [-1].tb_lineno), type(ex).__name__, ex)
        
    return False

#check the correctness of a 4 digit hebrew number
def check_4_digit_Hebrew_number(Hebrew_number):
    try:
        if len(Hebrew_number) != 4:
            return False
        
        # we can have multipl options:
        # A. its a number in a range off 500-1000
        # B. its a number above 1000
        
        # lets check B.
        first_digit = Hebrew_number[0]
        if ontology.alphabet_Gematria[first_digit] < 10:
            return check_3_digit_Hebrew_number(Hebrew_number[1:])
        
        # lets check A. (num is between 500 to 1000)
        if ontology.alphabet_Gematria[first_digit] == 400:
            return check_3_digit_Hebrew_number(Hebrew_number[1:])
    except Exception as ex:
        print(ex)
        print("Issue in function: check_4_digit_Hebrew_number")
        print('Error on line {}'.format(sys.exc_info()
                      [-1].tb_lineno), type(ex).__name__, ex)
        
    return False

# given a Hebrew string can this be a number?
# this function don't check number above 9999
def check_Hebrew_number_correctness(Hebrew_number):
    try:
        # remove " and '
        Hebrew_number = Hebrew_number.replace('״', "")
        Hebrew_number = Hebrew_number.replace("´", "")
        # this is workrround of a bug, as this sign should be removed at the original taging process
        Hebrew_number = Hebrew_number.replace("+", "")
        Hebrew_number = Hebrew_number.replace("*", "")
        Hebrew_number = Hebrew_number.replace("-", "")
        Hebrew_number = Hebrew_number.replace(">", "")
        Hebrew_number = Hebrew_number.replace("<", "")

        if len(Hebrew_number) == 1:
            return True 
        
        if len(Hebrew_number) == 2:
            return check_2_digit_Hebrew_number(Hebrew_number)
            
        if len(Hebrew_number) == 3:
            return check_3_digit_Hebrew_number(Hebrew_number)
        
        if len(Hebrew_number) == 4:
            return check_4_digit_Hebrew_number(Hebrew_number)

        if len(Hebrew_number) == 5:
            # this condition check numbers betyween 900 to 999
            if Hebrew_number[:3] == "תתק":
                return check_2_digit_Hebrew_number(Hebrew_number)
            else:
                return False


        if len(Hebrew_number) == 6:
            # this condition check numbers above 1000
            if Hebrew_number[:3] == "תתר":
                return check_3_digit_Hebrew_number(Hebrew_number)
            else:
                return False
    except Exception as ex:
        print(ex)
        print("Issue in function: check_Hebrew_number_correctness")
        print('Error on line {}'.format(sys.exc_info()
                      [-1].tb_lineno), type(ex).__name__, ex)

# check if the word is a chapter like פי״ח if yes, return the real value
def check_if_chapter(chapter):
    try:
        # remove " and '
        chapter = chapter.replace('״', "")
        chapter = chapter.replace("´", "")

        # first remove hbrew prefixes
        if (chapter[:1] == "ו"):
            chapter = chapter[1:]
        if (chapter[:1] == "ב"):
            chapter = chapter[1:]

        # Must start with a פ
        if (chapter[:1] == "פ"):
            chapter = chapter[1:]
        else:
            return False

        # that will mean פרק קמא, lets skip
        if chapter == "ק":
            return False

        if check_Hebrew_number_correctness(chapter) == True:
            return chapter
        else:
            return False
    
    except Exception as ex:
        print(ex)
        print("Issue in function: check_if_chapter")
        print('Error on line {}'.format(sys.exc_info()
                [-1].tb_lineno), type(ex).__name__, ex)
        return False
    
if __name__ == "__main__":
    num = "מ״ט"
    print(check_Hebrew_number_correctness(num))
    print(check_if_chapter("פח״י"))