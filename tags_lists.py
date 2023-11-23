# Project: Hebrew Reference extractor
#
# Created by: Nati Ben-Gigi
# Date: 11/2023
#
# License: MIT
# Copyright: Nati Ben-Gigi 2023
#
# File: tags_lists.py
# Description: 
# the various type of tags we have for our project as well as all kind of combinations and permutations of those tag

# non entity tags
tags_2_skip = [ "!", "?", "SC", "EC"] 
tag_Punctuation = ["{", "}", "]", "[", ":", ";"]
parentezis_tags = ["{", "}", "]", "["]
Punctuation_full_tags =  [":", ";", ",", ".", "!", "?"]
None_tags = ["O"]

tags_2_log = ["{", "}", "RT", "RW", "R", "RFR", "RAB", "RWIBM", "RIBM", "IBM", "TM", "TR"]

# break mark tags - BM
BM_tags = ['BM', 'TRBM', 'TMBM', 'RWBM', 'RTBM', 'ABBM', 'BMR', 'RRNBM', "BMRR"]
BM_internal_tags = ['IBM', 'BMIRT' ,'ABIBM', 'RWIBM', 'TMIBM', 'RIBM', "RRIBM"]
BM_Recursion_tags = ['BMRS', 'BMRSAB', 'BMRSR'] 
BM_Recursion_tags_post_ref = ['BMPRS', 'BMPRSR', 'BMPRSRW']

# layer 2 tags: TM, TR, RW, AB, R, RT
TM_tags = ['TM', 'TMBM', 'TMIBM']
RR_tags = ["RRN", "RR", "RRNBM", "BMRR", "RRIBM"]
TR_tags = ["TR", 'TRBM']
RW_tags = ['RW', 'RWBM', 'RWIBM', 'BMPRSRW']
AB_tags = ['AB', 'ABBM', 'ABIBM', 'BMRSAB',]
R_tags = ['R', 'BMR', 'RIBM', 'BMRSR', 'BMPRSR']
RT_tags = ['RT', 'RTBM', 'BMIRT']
TSR_tags = ["TSR", "TSRBM", "TSRIBM"]

#layer 2 basic tags
basic_tags = ['BM', 'IBM', 'BMRS']

#in case a ref contains ONLY those tags its probably a model error
NO_data_tags = ['BM', 'RWBM', 'BMR', 'RW', 'RWBM', 'R', 'BMR', "SC", "EC","O", "RFR", "{", "}", "]", "[", "RC"]

#layer 1 tags
Author_tags = ["AN", "AA"]
Books_tag = ["BA", "BN"]
R_tags = ["R", "RW"]
Start_End_tags = ["SC", "EC"]
GA_tags = ["GA"]
RC_tags = ["RC"]

weak_tags = []
weak_tags.extend(tags_2_skip)
weak_tags.extend(tag_Punctuation)
weak_tags.extend(Punctuation_full_tags)
weak_tags.extend(None_tags)
weak_tags.extend(RC_tags)

#TODO move ref words to XLS
ref_words = ["פרק", "בפ", "פ´" , "פ״", "פ״", "´פ", "הלכ", "סימן", "סי´", "ז״ל", "ספר", "שו״ת", "מסכת"]
