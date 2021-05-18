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
doc_regex = re.compile("<DOC>.*?</DOC>", re.DOTALL)
docno_regex = re.compile("<DOCNO>.*?</DOCNO>")
text_regex = re.compile("<TEXT>.*?</TEXT>", re.DOTALL)

#my indices (dictionaries)---------------------------------------------------------
stopWordSet = set() #create empty set for stopwords
uniqueWordSet = set() #used to count distinct terms

docNoIndex = {} #dictionary for document reverse index (i.e. document name to document ID) ex: {ap890101-0001': 0}
termIndex = {} #dictionary of tokens
termCounter = {} #store count of term usage across entire corpus/collection
termInfoIndex = {} #dictionary of term to term info
docInfoIndex = {} #dictionary of doc key to doc info


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


#update term count (across the whole collection/corpus)----------------
def get_term_count(token_id, index=termCounter):

    if token_id in termCounter:
        counter = termCounter[token_id]
    else:
        counter = 0

    return counter


#add token------------------------------------------------------------ TOKENS: DICTIONARY
#add token to (reverse) index of tokens and return token's index # (ID)
def add_token(token, index=termIndex, counter=termCounter): 
    try:

        #if not in index, add it----------
        if token not in index:
            next_key = len(index)
            index.__setitem__(token, next_key) #mind the order here: its a reverse index!
            termCounter.__setitem__(next_key, 1) #first count
            return next_key

        #else get key (and update count)---
        else: 
            for term, key in index.items():
                if token == term:
                    #print("Grabbing current count for: " + token) #debug
                    count = termCounter[key]
                    count += 1 #update the count
                    termCounter.update({key:count}) 
                    #print("My Count: " + str(count))
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

        
#add document number to (reverse) index of documents-------------------- DOCUMENT NUMBER: DICTIONARY
def add_document_number(doc_id, index=docNoIndex):
    try:
        doc_id = doc_id.lower() #lets make this uniform...

        if doc_id not in index:
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


#add to term info dictionary-------------------------------------------
def add_term_info(token_key, tpl_info, index=termInfoIndex):
    if token_key in termInfoIndex:
        termInfoIndex[token_key].append(tpl_info)
    else:
        termInfoIndex.__setitem__(token_key, [tpl_info]) #add new entry


#get info for doc + term ---------------------------------------------- 
def get_doc_term_info(term, term_id, doc_id, index=termInfoIndex):

    counter = 0 #count term frequency in doc
    positions = []
    info = index[term] #info is a list of tuples for term

    for item in info: #item is a tuple 
        if doc_id == item[1]: #if doc id matches element 1 of tuple
            counter += 1 #increment counter
            positions.append(item[2]) #lets append positions to list of positions
    
    return counter, positions


#add to doc info dictionary--------------------------------------------
def add_doc_info(doc_key, tpl_info, index=docInfoIndex):
    if doc_key in docInfoIndex:
        docInfoIndex[doc_key].append(tpl_info)
    else:
        docInfoIndex.__setitem__(doc_key, [tpl_info])


#count total terms used in doc-----------------------------------------
def count_doc_terms(doc_key, index=docInfoIndex):
    if doc_key != -1:
        info = index[doc_key] #list of tuples.. kind of redundant as its always a list of size 1
        tpl = info[0] #get tuple
   
        return tpl[0], tpl[1] #return: total terms and unique terms
    else:
        return 0, 0


#count docs(that use a specific term)-------------------------------------
def count_docs(term, index=termInfoIndex):
    
    if get_token_id(term) != -1:
        uniqueDocSet = set() #set used to hold unique Doc id's
        info = index[term] #info is a list of tuples

        for item in info: #each item is a tuple
            uniqueDocSet.add(item[1]) #use set to acrue unique doc numbers

        counter = len(uniqueDocSet) #then, just count the size of the set for total count of docs with the term
    
    else:
        counter = 0

    return counter


#get term information--------------------------------------------------
def get_term_info(term):
    stem = ps.stem(term)
    term_id = get_token_id(stem)

    print("\nListing for term: " + term)
    if term_id != -1:
        print("Term ID: " + str(term_id))
    else:
        print("Sorry, " + term + " was not found in the corpus")

    print("Number of documents containing term: " + str(count_docs(stem)))
    print("Term frequency in corpus: " + str(get_term_count(term_id)) )


#get document information----------------------------------------------
def get_doc_info(doc_no):
    doc_key = get_doc_id(doc_no)

    print("\nListing for document: " + doc_no.lower())

    if doc_key != -1:
        total, unique = count_doc_terms(doc_key) 
        print("DOCID: " + str(doc_key))
        print("Distinct terms: " + str(unique))
        print("Total terms: " + str(total))

    else:
        print("Sorry, " + str(doc_no) + " not found in collection!")


#get information for doc + term (ie -t and -d flags set)---------------
def get_both_info(doc_no, term):
    print("Inverted list for term: " + term)
    print("In document: " + doc_no)

    stem = ps.stem(term) #get the stemmed term token
    term_id = get_token_id(stem) #get the term id #

    if term_id != -1:
        print("TERMID: " + str(term_id))
    else:
        print(term + " not found in the corpus")
    

    doc_key = get_doc_id(doc_no)
    if doc_key != -1:
        print("DOCID: " + str(doc_key))
    else:
        print("Sorry, " + doc_no + " not found in the collection")

    if doc_key > -1 and term_id > -1:
        count, positions = get_doc_term_info(term, term_id, doc_key)
        print("Term frequency in document: " + str(count))
        print("Positions: ", end='')
        
        for pos in positions:
            print(str(pos) + ', ', end='')

#get term frequency---------------------------------------------------TERM FREQUENCY
def get_tf(term, doc_no):

    #tokenize term and get its id--------------------
    stem = ps.stem(term) #get the stemmed term token
    term_id = get_token_id(stem) #get the term id #

    #get document info (it total terms in doc)-------
    doc_key = get_doc_id(doc_no)
    if doc_key != -1:
        total, unique = count_doc_terms(doc_key) 

    #get term count (for a given document)-----------
    doc_key = get_doc_id(doc_no)


    num_docs_with_term = count_docs(stem)
    num_docs_in_corp = len(docNoIndex)



    #debugging----------------------------------------    



    if doc_key != -1:
        print("DOCID: " + str(doc_key))
    else:
        print("Sorry, " + doc_no + " not found in the collection")

    if doc_key > -1 and term_id > -1:
        count, positions = get_doc_term_info(term, term_id, doc_key)
        print("Term: " + term)
        print("Term frequency in document: " + str(count))
        print("Number of documents containing term: " + str(num_docs_with_term))
        print("Total number of docs in corpus: " + str(num_docs_in_corp))

        print("Total Terms in Doc: " + str(total))
        print("Term Frequency: " + str(count/total))


    



#-------------------------------------------------------------------------------------------------------------- 
#-------------------------------------------------------------------------------------------------------------- MAIN
#-------------------------------------------------------------------------------------------------------------- 
if __name__ == '__main__':

    #get user input from command line---------------------------------------------------------------- INPUT -->MIND THE DEFAULTS HERE USED FOR TESTING 
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--doc", dest = "document", help="Enter Document Name (i.e. DocNo)" , default='')
    parser.add_argument("-t", "--term", dest = "term", help="Enter Term", default='')
    parser.add_argument("-c", "--collection", dest = "collection", default="ap89_collection_small", help="Document Collection Directory")
    
    args = parser.parse_args()
    collection = args.collection

    print("\nCollection: \t" + collection)
    sleep(1)
   

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
                #add_document(file, docno) #--->>> not used!!!


                # Retrieve contents of TEXT tag----------------------------- TOKENIZE
                text = "".join(re.findall(text_regex, document))\
                        .replace("<TEXT>", "").replace("</TEXT>", "")\
                        .replace("\n", " ")

                text = re.sub('[()!@#$%^&*:;,.`\']', '', text.lower()) #lower case and remove punctuation chars (leave hyphens!)
               
                tk = RegexpTokenizer('\s+', gaps = True)
                tokens = tk.tokenize(text) 
                

                position_counter = 0 #track term position (in current doc)
                token_counter = 0

                #process my list of tokens---------------------------------- FOR EACH TOKEN
                for token in tokens:                    

                    #add to term index-------------------------------------- ADD STEM TO TERM INDEX
                    if token not in stopWordSet: 

                        #add tokens/terms to set for count of distinct------
                        uniqueWordSet.add(token) 

                        #stemming using porter ----------------------------- STEMMING (Porter) -> consider another stemmer
                        token_porter = ps.stem(token) #stemmed using porter tokenizer

                        position_counter += 1 #position counter of token in current doc
                        token_counter += 1 #count total tokens/terms in current doc
                        token_id = add_token(token) #add stemmed token to dict and get its key#
                      
                        
                        #create tuple of term information------------------- TERM TUPLE CREATION
                        tpl_term_info = (token_id, doc_index_key, position_counter)  #token key, doc key, term position, term count in corpus

                        #add tuple of info to term_info index--------------- TERM INFO INDEX
                        add_term_info(token_porter, tpl_term_info)
                       

                #store count of terms in a doc------------------------------
                add_doc_info(doc_index_key, (token_counter, len(uniqueWordSet)))
                uniqueWordSet.clear()

     
    
    #execute output based on combination of input flags--------------------------------------------
    if args.document and args.term :
        #get_both_info(args.document.lower(), args.term.lower())
        get_tf(args.term.lower(), args.document.lower())
    if args.term and not args.document:        
        get_term_info(args.term.lower())
    if args.document and not args.term:
        get_doc_info(args.document.lower())
