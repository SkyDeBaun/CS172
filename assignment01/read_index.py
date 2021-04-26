#CS172 - Intro to Information Retrieval - UCR, Spring 2021
#Sky DeBaun

#imports----------------------------------------------------------------------- IMPORTS
import argparse
import re
import zipfile

#nltk-------------------------------------------------------------
import nltk
from nltk.tokenize import RegexpTokenizer
from nltk.stem import PorterStemmer
ps = PorterStemmer()

#os and other------------------------------------------------------
import os
from time import sleep

#user friendly exception tracebacks--------------------------------
import traceback


#Vars and setup------------------------------------------------------------------- SETUP
# Regular expressions to extract data from the corpus
doc_regex = re.compile("<DOC>.*?</DOC>", re.DOTALL)
docno_regex = re.compile("<DOCNO>.*?</DOCNO>")
text_regex = re.compile("<TEXT>.*?</TEXT>", re.DOTALL)

token_regex = "\w+(\.?\-?\w+)*" #allows periods and dashes within token

#my indices (dictionaries)---------------------------------------------------------
docNoIndex = {} #dictionary for document index
docIndex = {} #dictionary mapping Doc No to file name
termIndex = {} #dictionary of tokens
termInfoIndex = {} #dictionary of term to term info
stopWordSet = set() #create empty set for stopwords



#FUNCTIONS------------------------------------------------------------------------- FUNCTIONS
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

#add to term info index------------------------------------------------
def add_term_info(token_key, tpl_info, index=termInfoIndex):
    if token_key in termInfoIndex:
        termInfoIndex[token_key].append(tpl_info)
    else:
        termInfoIndex.__setitem__(token_key, [tpl_info]) #add new entry


#use input to present relevant information-----------------------------


def count_docs(term, index=termInfoIndex):
    if get_token_id(term) != -1:
        info = termInfoIndex[term]    
        return len(info)
    else:
        return 0




#get term info---------------------------------------------------------
def get_term_info(term):
    stem = ps.stem(term)
    term_id = get_token_id(stem)

    print("\nListing for term: " + term)
    if term_id != -1:
        print("Term ID: " + str(term_id))
    else:
        print("Sorry, " + term + " was not found in the corpus")
    print("Number of documents containing term: " + str(count_docs(stem)))

    




#-------------------------------------------------------------------------------------------------------------- 
#-------------------------------------------------------------------------------------------------------------- MAIN
#-------------------------------------------------------------------------------------------------------------- 
if __name__ == '__main__':

    #get user input from command line---------------------------------------------------------------- INPUT
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--doc", dest = "document", help="Enter Document Name (i.e. DocNo)" )
    parser.add_argument("-t", "--term", dest = "term", help="Enter Term")
    parser.add_argument("-c", "--collection", dest = "collection", default="ap89_collection_small", help="Document Collection")
    
    args = parser.parse_args()
    collection = args.collection

    print("\nUsing collection: " + collection + "\n")
    sleep(1)

   
#unzip utility------------------------------------------------------------------------------------- UNZIP
    '''
    with zipfile.ZipFile("ap89_collection_small.zip", 'r') as zip_ref:
        zip_ref.extractall()
    '''


    #create stopword list--------------------------------------------------------------------------- CREATE STOPWORD SET
    create_stopword_set("stopwords.txt")


    # Retrieve the names of all files to be indexed in folder ./ap89_collection_small of the current directory
    for dir_path, dir_names, file_names in os.walk(collection):
        allfiles = [os.path.join(dir_path, filename).replace("\\", "/") for filename in file_names if (filename != "readme" and filename != ".DS_Store")]


    #FOR EACH FILE IN COLLECTION-------------------------------------------------------------------- FOR EACH FILE
    #-----------------------------------------------------------------------------------------------
    for file in allfiles: 
        with open(file, 'r', encoding='ISO-8859-1') as f:
            filedata = f.read()
            result = re.findall(doc_regex, filedata)  # Match the <DOC> tags and fetch documents
                       
            #FOR EACH DOCUMENT IN FILE-------------------------------------------------------------- FOR EACH DOC NO
            #---------------------------------------------------------------------------------------
            for document in result[0:]:
                
                # Retrieve contents of DOCNO tag
                docno = re.findall(docno_regex, document)[0].replace("<DOCNO>", "").replace("</DOCNO>", "").strip()
                
                #add doc ID to doc index----------------------------------- INDEX DOC NUMBER  
                doc_index_key = add_document_number(docno) #add doc no

                #lets index the filename also------------------------------ INDEX DOCUMENT FILE (using Doc Number as key)
                add_document(file, docno)


                # Retrieve contents of TEXT tag----------------------------- TOKENIZE
                text = "".join(re.findall(text_regex, document))\
                        .replace("<TEXT>", "").replace("</TEXT>", "")\
                        .replace("\n", " ")

                text = re.sub('[()!@#$%^&*:;,.\']', '', text.lower()) #lower case and remove punctuation chars (leave hyphens)
               
                tk = RegexpTokenizer('\s+', gaps = True)
                tokens = tk.tokenize(text)
                

                position_counter = 0

                #process my list of tokens---------------------------------- FOR EACH TOKEN
                for token in tokens:

                    #stemming using porter --------------------------------- STEMMING (Porter)
                    token_porter = ps.stem(token)

                    #add to term index-------------------------------------- ADD STEM TO TERM INDEX
                    if token_porter not in stopWordSet: 
                        position_counter += 1 #position counter of token in current doc

                        token_id = add_token(token) #add stemmed token to dict and get its key#
                        
                        #create tuple of term informatin-------------------- TERM TUPLE CREATION
                        tpl_term_info = (token_id, doc_index_key, position_counter)  

                        #add tuple of info to term_info index--------------- TERM INFO INDEX
                        add_term_info(token_porter, tpl_term_info)
                       

                # step 1 - lower-case words, remove punctuation, remove stop-words, etc. 
                # step 2 - create tokens 
                # step 3 - build index

            

   
    print("Creation of Posting List Complete!")
    sleep(1)

    #print(termIndex) #debug

    if args.term or args.document:
        print("Now processing user input commands...")


    


    if args.document and args.term :
        pass
    if args.term and not args.document:        
        get_term_info(args.term)
    if args.document and not args.term:
        pass