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

stopWordSet = set()



#FUNCTIONS-------------------------------------------------------------------------
#----------------------------------------------------------------------------------

#create set of stop words------------------------------------------- STOPWORDS: SET
def create_stopword_set(stopword_file):
    try:
        print("Opening: \t" + stopword_file + " for set creation")
        sleep(.5)
        with open(stopword_file, 'r') as readfile:
            text = readfile.read()
            stopwords = nltk.word_tokenize(text)
            for word in stopwords:
                stopWordSet.add(word.lower())
        print("Done: \t\tstopword set created!\n")
        sleep(.5)

    except Exception as e :
        print("Sorry an error occured reading from the stop word file: " )
        print(e, end="\n\n")   



#add token------------------------------------------------------------ TOKENS: DICTIONARY
#add token to (reverse) index of tokens and return token's index # (ID)

def add_token(token, index = termIndex): 
    try:

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

    except Exception as e :
        print("Sorry an error occured adding token: " + str(token) ) 
        print(e, end="\n\n")  


#get token id-------------------------------------------------------
def get_token_id(token, index = termIndex):
    try:
        if token in index:
            return index[token]
        else:
            return -1 #warning flag

    except Exception as e :
        print("Sorry an error occured retrieving key for token: " + token )
        print(e, end="\n\n")   

        
#add docuement to (reverse) index of documents------------------------- DOCUMENTS: DICTIONARY
def add_document(doc_id, doc_name, index = docIndex):
    try:
        if doc_id not in index:
            index.__setitem__(doc_name, doc_id)
        else:
            for doc, key in index.items():
                if doc_name == doc:
                    return key

    except Exception as e :
        print("Sorry an error occured adding document: " + doc_id )
        print(e, end="\n\n")   

#get document id-------------------------------------------------------
def get_doc_id(doc, index = docIndex):
    try:
        if doc in index:
            return index[doc]
        else:
            return -1

    except Exception as e :
        print("Sorry an error occured retrieving document key for: " + doc )
        print(e, end="\n\n") 




#--------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------- MAIN
#--------------------------------------------------------------------------------------------------------------


'''
with zipfile.ZipFile("ap89_collection_small.zip", 'r') as zip_ref:
    zip_ref.extractall()
'''


#create stopword list--------------------------

create_stopword_set("stopwords.txt")


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


sleep(1)
print(stopWordSet)
