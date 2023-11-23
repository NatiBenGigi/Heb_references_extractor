# Heb_references_extractor
Ver: 1.0
Author: Nati Ben-Gigi
App license: MIT

The tool specializes in scanning rabbinic corpora, 
extracting references from a wide range of texts. 
It's Designed for ease the process of analyzing rabbinic literature, 
making it an invaluable asset for scholars and researchers.

Currently, the Hebrew Reference Extractor is designed to process rabbinic texts from 1000-1500 C.E. 
Start it by running main.py. It accommodates three text encodings; select yours from the 
combobox at the top-right.

The app allows single file loading and viewing, with in-app reference extraction. 
Use the "Load Single Response File" and "Extract References" buttons for these functions. 

For larger corpora, use "Scan Corpus". The results will be saved in an xlsx file at the a
pp's location, or "Scan Corpus and Save Tags" to also preserve the tags found. 
For re-scanning tagged files, choose "Scan Tagged Corpus" and provide the folder from the 
previous step, ensuring it contains 'layer1' and 'layer2' subfolders.

Install the app from GitHub, and separately download the BERT-CRF model and codefrom the 
below link. 
Next to the files from GitHub creat a folder named BERT and copy all the content from the below 
link to that folder.
https://www.dropbox.com/scl/fo/872pnzxqxl378t64syeyl/h?rlkey=oxtcc2px7nqvuvkof39cneddg&dl=0

Afterward, in the BERT folder creat a new folder named BEREL.
copy the content of the folder BEREL_PyTorch_Model (from the below like), and place it in the BEREL folder 
https://bit.ly/3vzlvgG

Eventually, your final folder should like:
Heb_references_extractor/
│
├── [All GitHub .py files]
│
├── Data_resources/ (folder)
│
└── BERT/ (folder)
    ├── [Additional .py files]
    │
    ├── BEREL/ (folder)
    │
    └── BERT_CRF_Rabbinic_Models/ (folder)

