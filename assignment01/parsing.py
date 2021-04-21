import re
import os
import zipfile

import nltk
from time import sleep

# Regular expressions to extract data from the corpus
doc_regex = re.compile("<DOC>.*?</DOC>", re.DOTALL)
docno_regex = re.compile("<DOCNO>.*?</DOCNO>")
text_regex = re.compile("<TEXT>.*?</TEXT>", re.DOTALL)

token_regex = "\w+(\.?\-?\w+)*" #allows periods and dashes within token

#my indices (dictionaries)---------------------------------------------------------
docIndex = {} #dictionary for document index
termIndex = {} #dictionary of tokens





#FUNCTIONS-------------------------------------------------------------------------
#----------------------------------------------------------------------------------


#add token------------------------------------------------------------
def add_token(token, index = termIndex): #add token to (reverse) index of tokens and return token's index # (ID)

    #if not in index, add it----------
    if token not in index:
        next_key = len(index)
        index.__setitem__(token, next_key)
        return next_key

    #else just get the key------------
    else:
        for term, key in index.items():
            if token == term:
                return key


#get token id-------------------------------------------------------
def get_token_id(token, index = termIndex):
    if token in index:
        return index[token]
    else:
        return -1 #warning flag

        
#add docuement to (reverse) index of documents-------------------------
def add_document(doc_name, index = docIndex):
    if doc_name not in index:
        next_key = len(index)
        index.__setitem__(doc_name, next_key)
        return next_key
    else:
        for doc, key in index.items():
            if doc_name == doc:
                return key

#get document id-------------------------------------------------------
def get_doc_id(doc, index = docIndex):
    if doc in index:
        return index[doc]
    else:
        return -1


'''
with zipfile.ZipFile("ap89_collection_small.zip", 'r') as zip_ref:
    zip_ref.extractall()
'''




# Retrieve the names of all files to be indexed in folder ./ap89_collection_small of the current directory
for dir_path, dir_names, file_names in os.walk("ap89_collection_small"):
    allfiles = [os.path.join(dir_path, filename).replace("\\", "/") for filename in file_names if (filename != "readme" and filename != ".DS_Store")]
    
    
for idx, file in enumerate(allfiles): #adding index to loop using enumerate function (to provide index for the doc dictionary)
    with open(file, 'r', encoding='ISO-8859-1') as f:
        filedata = f.read()
        result = re.findall(doc_regex, filedata)  # Match the <DOC> tags and fetch documents
        
        

        for document in result[0:]:
            # Retrieve contents of DOCNO tag
            docno = re.findall(docno_regex, document)[0].replace("<DOCNO>", "").replace("</DOCNO>", "").strip()
            
            #create index of docno to doc path/name
            #print(str(idx) + ".) docno: " + docno)
            docIndex.__setitem__(docno, file) #document index -> key: docno, value: document path/name


            # Retrieve contents of TEXT tag
            text = "".join(re.findall(text_regex, document))\
                      .replace("<TEXT>", "").replace("</TEXT>", "")\
                      .replace("\n", " ")
            
            

            # step 1 - lower-case words, remove punctuation, remove stop-words, etc. 
            # step 2 - create tokens 
            # step 3 - build index

sleep(2)


print("SHOW ME:")
mylist = ["hello", "world", "how", "are", "yoooooooo", "hello", "world"]

for i in mylist:
    mykey = add_token(i)
    print(mykey)


sleep(1)    
print(termIndex)



print("Token ID: " + str(get_token_id("are")))