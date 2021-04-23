import re
import os
import zipfile

import nltk
from time import sleep

import traceback

# Regular expressions to extract data from the corpus
doc_regex = re.compile("<DOC>.*?</DOC>", re.DOTALL)
docno_regex = re.compile("<DOCNO>.*?</DOCNO>")
text_regex = re.compile("<TEXT>.*?</TEXT>", re.DOTALL)

token_regex = "\w+(\.?\-?\w+)*" #allows periods and dashes within token

#my indices (dictionaries)---------------------------------------------------------
docNoIndex = {} #dictionary for document index
docIndex = {} #dictionary mapping Doc No to file name
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

    except Exception:
        print("Sorry an error occured reading from the stop word file: " )
        traceback.print_exc() 
        print()  




#add token------------------------------------------------------------ TOKENS: DICTIONARY
#add token to (reverse) index of tokens and return token's index # (ID)

def add_token(token, index=termIndex): 
    try:

        #if not in index, add it----------
        if token not in index:
            next_key = len(index)
            index.__setitem__(token, next_key) #mind the order here: its a reverse index!
            return next_key

        #else just get the key------------
        else:
            for term, key in index.items():
                if token == term:
                    return key

    except Exception:
        print("Sorry an error occured adding token: " + str(token) ) 
        traceback.print_exc() 
        print()   


#get token id-------------------------------------------------------
def get_token_id(token, index=termIndex):
    try:
        if token in index:
            return index[token]
        else:
            return -1 #warning flag

    except Exception:
        print("Sorry an error occured retrieving key for token: " + token )
        traceback.print_exc() 
        print()    

        
#add document number to (reverse) index of documents------------------------- DOCUMENT NUMBER: DICTIONARY
def add_document_number(doc_id, index=docNoIndex):
    try:
        if document not in index:
            next_key = len(index)
            index.__setitem__(doc_id, next_key) #mind the order here: its a reverse index!
            return next_key
        else:
            for doc, key in index.items():
                if doc_id == doc:
                    return key

    except Exception:
        print("Sorry an error occured adding document: " + document )
        traceback.print_exc() 
        print()  


#get document id-------------------------------------------------------
def get_doc_id(doc, index=docNoIndex):
    try:
        if doc in index:
            return index[doc]
        else:
            return -1

    except Exception:
        print("Sorry an error occured retrieving document key for: " + doc )
        traceback.print_exc() 
        print()  


#add document to (index of documents)--------------------------------- DOCUMENTS: DICTIONARY
def add_document(document, doc_id, index=docIndex):
    try:
        if document not in index:
            index.__setitem__(doc_id, document) #mind the order here: its a reverse index!
        
    except Exception:
        print("Sorry an error occured adding document to document index: " + document )
        traceback.print_exc() 
        print()  


#get document(file name) from doc index--------------------------------
def get_document_file(doc_no_key, index=docIndex):
    try:
        if doc_no_key in index:
            return index[doc_no_key]
        else: 
            return -1

    except Exception:
        print("Sorry an error occured retrieving filename for doc number key: " + doc_no_key )
        traceback.print_exc() 
        print()  

#--------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------- MAIN
#--------------------------------------------------------------------------------------------------------------
if __name__ == '__main__':




    '''
    with zipfile.ZipFile("ap89_collection_small.zip", 'r') as zip_ref:
        zip_ref.extractall()
    '''


    #create stopword list----------------------------------------------------- CREATE STOPWORD SET
    create_stopword_set("stopwords.txt")


    # Retrieve the names of all files to be indexed in folder ./ap89_collection_small of the current directory
    for dir_path, dir_names, file_names in os.walk("ap89_collection_small"):
        allfiles = [os.path.join(dir_path, filename).replace("\\", "/") for filename in file_names if (filename != "readme" and filename != ".DS_Store")]
        
    #FOR EACH FILE IN COLLECTION--------------------------------------------------------------------
    #-----------------------------------------------------------------------------------------------
    for file in allfiles: 
        with open(file, 'r', encoding='ISO-8859-1') as f:
            filedata = f.read()
            result = re.findall(doc_regex, filedata)  # Match the <DOC> tags and fetch documents
                       
            #FOR EACH DOCUMENT IN FILE--------------------------------------------------------------
            #---------------------------------------------------------------------------------------
            for document in result[0:]:
                
                # Retrieve contents of DOCNO tag
                docno = re.findall(docno_regex, document)[0].replace("<DOCNO>", "").replace("</DOCNO>", "").strip()
                
                #add doc ID to doc index----------------------------------- INDEX DOC NUMBER  
                doc_index_key = add_document_number(docno) #add doc and get its key back

                #lets index the filename also------------------------------ INDEX DOCUMENT FILE (using Doc Number as key)
                add_document(file, docno)


                # Retrieve contents of TEXT tag----------------------------- TOKENIZE
                text = "".join(re.findall(text_regex, document))\
                        .replace("<TEXT>", "").replace("</TEXT>", "")\
                        .replace("\n", " ")
                
                

                # step 1 - lower-case words, remove punctuation, remove stop-words, etc. 
                # step 2 - create tokens 
                # step 3 - build index

    sleep(2)


#test me------------------------------------------------------------------
    print("SHOW ME:")
    mylist = ["hello", "world", "how", "are", "yoooooooo", "hello", "world"]

    for i in mylist:
        mykey = add_token(i)
        print(mykey)


    sleep(1)    
    print(termIndex)



    print("Token ID: " + str(get_token_id('are')))


    sleep(1)
    print(docNoIndex)
    print ("Doc No: " + str(get_doc_id('AP890109-0349')))



    print("\nFiles: ")
    print(docIndex)
    print("document for DocNO: AP890109-0349 -->:" + get_document_file('AP890109-0349'))
