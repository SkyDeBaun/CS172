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

# https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.TfidfVectorizer.html
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from numpy import dot
from numpy.linalg import norm

#os and other------------------------------------------------------
import os
import sys
import math

from time import sleep #for debugging and user feedback
from collections import Counter

#user friendly exception tracebacks--------------------------------
import traceback

#serialize data structures --> https://realpython.com/courses/pickle-serializing-objects/
import pickle


#Vars and setup------------------------------------------------------------------- SETUP
doc_regex = re.compile("<DOC>.*?</DOC>", re.DOTALL)
docno_regex = re.compile("<DOCNO>.*?</DOCNO>")
text_regex = re.compile("<TEXT>.*?</TEXT>", re.DOTALL)

data_dir = 'data' #path to directory used to save indexed docs

#my indices (dictionaries)---------------------------------------------------------
stopWordSet = set() #create empty set for stopwords
uniqueWordSet = set() #used to count distinct terms

docNoIndex = {} #dictionary for document reverse index (i.e. document name to document ID) ex: {ap890101-0001': 0}
termIndex = {} #dictionary of tokens
termCounter = {} #store count of term usage across entire corpus/collection
termInfoIndex = {} #dictionary of term to term info
docInfoIndex = {} #dictionary of doc key to doc info


query_dict = {} # query# to tokenized query string
corp_dict = {} # doc# to tokenized doc string

#query related(used to calculate term frequency score for queries)----------------
query_termIndex = {}
query_termCounter = {}

#init vectorizor--------------------------------------------------INIT VECTORIZOR
vectorizer = TfidfVectorizer()
my_counter = [0]

#FUNCTIONS------------------------------------------------------------------------- FUNCTIONS
#----------------------------------------------------------------------------------

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

    try: #exception added here for the case when terms added via query have no associated tuples
        info = index[term] #info is a list of tuples for term
    except Exception:
        return 0, [] #ie no id, and no list of positions

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




#get term frequency---------------------------------------------------TERM FREQUENCY
def get_tfidf(term, doc_no):

    #tokenize term and get its id--------------------
    stem = ps.stem(term) #get the stemmed term token
    term_id = get_token_id(stem) #get the term id #

    #get document info (it total terms in doc)-------
    doc_key = get_doc_id(doc_no)
    if doc_key != -1:
        terms_in_doc, unique = count_doc_terms(doc_key) 

    #get term count (for a given document)-----------
    doc_key = get_doc_id(doc_no)


    num_docs_with_term = count_docs(stem)
    num_docs_in_corp = len(docNoIndex)

    if doc_key > -1 and term_id > -1:
        term_count, positions = get_doc_term_info(term, term_id, doc_key)
        term_frequency = term_count/terms_in_doc

        idf = math.log(num_docs_in_corp/num_docs_with_term) + 1
        tfidf = idf *term_frequency
  
    '''
    #debugging----------------------------------------   
    if doc_key != -1:
        print("EXAMINING DOCUMENT: " + str(doc_key))
        print("Term: " + term)
        print("Term frequency in document: " + str(term_count))
        print("Total Terms in Doc: " + str(terms_in_doc))        
        print("Total number of documents containing term: " + str(num_docs_with_term))
        print("Total number of docs in corpus: " + str(num_docs_in_corp))
        print("Term Frequency score: " + str(term_count/terms_in_doc))
        print("IDF: " + str(idf))
        print("TFIDF: " + str (tfidf))
        print()
    '''
       

    return tfidf

        
        

#iterate through collection of docs (uses reverse index)******
def visit_docs(index=docNoIndex):
    for key in index.keys():
        print(key, '->', index[key])
        
        #get doc key----------------------
        doc_key = index[key]

        print(docInfoIndex[doc_key])
        sleep(3)

    
#read query doc-------------------------------------------------------READ QUERY DOC
def read_query_doc(query_path):
    with open (query_path, 'r') as file:
        query_text = file.readlines() #unprocesed list of queries
        
    return query_text


#tokenize text---------------------------------------------------------TOKENIZE TEXT STRING(QUERIES ONLY)
def text_tokenizer(text):
    text = re.sub('[()!@#$%^&*:;,"._`\']', '', text.lower()) #lower case and remove punctuation chars (leave hyphens!)
               
    tk = RegexpTokenizer('\s+', gaps = True)
    tokens = tk.tokenize(text) #get list of tekenized text
    #tokenized_text = '' #stores string of token id's for indexed doc 

    stemmed_tokens = [] #will hold stemmed tokens

    #process my list of tokens---------------------------------- FOR EACH TOKEN
    for token in tokens:       

        #add to term index-------------------------------------- ADD STEM TO TERM INDEX (stopwords included)
        token_porter = ps.stem(token) #stemmed using porter tokenizer
        token_id = add_token(token_porter) #add stemmed token to dict (if not already in dict) and/or get its key#  
        
        #add stemmed token to query list
        stemmed_tokens.append(token_porter) 
    
    return stemmed_tokens


#prep query (convert to list of queries)-----------------------------PREP QUERY 
def prep_query(query_path, query_dictionary=query_dict):
    query_text = read_query_doc(query_path)

    for text in query_text:
        q_num = text[:4].strip() #assumes the query number isn't too big..
        num = re.sub('[.]', '', q_num)
        query_string = text[5:].strip().lower()

        #add num : stemmed and tokenized query string (as a list of stemmed tokens) to dictionary
        query_dictionary.__setitem__(num, text_tokenizer(query_string))
    
    return query_dictionary



#return cosine similarity between two 1D vectors (lists)--------------COSINE SIMILARITY
def cosine_sim(vec1, vec2):
    return dot(vec1, vec2)/(norm(vec1) * norm(vec2))
    



#create directory of indexed docs-------------------------------------CREATE DATA DIR
def create_data_dir(data_dir):
    current_dir = os.getcwd()
    data_dir = os.path.join(current_dir, data_dir)

    if not os.path.exists(data_dir):
        os.makedirs(data_dir)


#save tokenized and indexed doc to disk-------------------------------SAVE TO DISK
def write_to_disk(filename, text):
    with open(data_dir + '/' + filename, 'wb') as save:
                    pickle.dump(text, save)



  

def get_tf_idf_query_similarity(docs_tfidf, query, vectorizer=vectorizer):    
    query_tfidf = vectorizer.transform([query])
    return cosine_similarity(query_tfidf, docs_tfidf).flatten()
     



#store tokenized doc to dict----------------------------------------
def prep_doc_dictionary(docno, tokenized_text, corp_dict=corp_dict):
    corp_dict.__setitem__(docno, tokenized_text)
    return corp_dict


#-------------------------------------------------------------------------------------------------------------- 
#-------------------------------------------------------------------------------------------------------------- MAIN
#-------------------------------------------------------------------------------------------------------------- 
if __name__ == '__main__':
    
    #parse user input from command line---------------------------------------------------------------- INPUT -->NOTE THE DEFAULTS HERE! 
    parser = argparse.ArgumentParser()
    parser.add_argument("-q", "--query", dest = "query_path", help="Enter Path to Query document (i.e. query_list.txt)" , default='query_list.txt')
    parser.add_argument("-o", "--ouput", dest = "output_path", help="Enter Path to Output document (i.e. results.txt", default='results.txt')
    parser.add_argument("-d", "--dir", dest = "data_dir", help="Enter Directory to save indexed docs to (i.e. indexed_docs)", default="data/index")
    parser.add_argument("-c", "--collection", dest = "collection", default="ap89_collection_small", help="Document Collection Directory")
    
    args = parser.parse_args() #get user args

    collection = args.collection
    query_path = args.query_path
    output_path = args.output_path
    data_dir = args.data_dir

    #clean user input and create data directory-----------------------DATA DIRECTORY
    data_dir = data_dir.rstrip("/")
    create_data_dir(data_dir)


    print("\nUsing Corpus: \t\t" + collection)
   


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

                text = re.sub('[()!@#$%^&*:;,._`\']', '', text.lower()) #lower case and remove punctuation chars (leave hyphens!)
               
                tk = RegexpTokenizer('\s+', gaps = True)
                tokens = tk.tokenize(text) 
                

                position_counter = 0 #track term position (in current doc)
                token_counter = 0 #track count of tokens in doc

                doc_text = '' #stores sting of token id's for indexed doc (is written to disk)


                #process my list of tokens---------------------------------- FOR EACH TOKEN
                for token in tokens:       

                    #add to term index-------------------------------------- ADD STEM TO TERM INDEX (stopwords included)

                    #add tokens/terms to set for count of distinct------
                    uniqueWordSet.add(token) 

                    #stemming using porter ----------------------------- STEMMING (Porter) -> consider another stemmer
                    token_porter = ps.stem(token) #stemmed using porter tokenizer

                    position_counter += 1 #position counter of token in current doc
                    token_counter += 1 #count total tokens/terms in current doc
                    token_id = add_token(token_porter) #add stemmed token to dict and get its key#
                    
                    
                    #create tuple of term information------------------- TERM TUPLE CREATION
                    tpl_term_info = (token_id, doc_index_key, position_counter)  #token key, doc key, term position in doc

                    #add tuple of info to term_info index--------------- TERM INFO INDEX
                    add_term_info(token_porter, tpl_term_info)

                    #save token to string-------------------------------
                    doc_text += str(token_id) + ' ' #doc text as string of token id's
                    #doc_file = docno + '.sav' #create unique filename for doc (will save to disc)
                       

                #store count of unique terms in a doc------------------------
                add_doc_info(doc_index_key, (token_counter, len(uniqueWordSet)))
                uniqueWordSet.clear()

                #save processed doc to disk----------------------------------WRITE TO DISK
                #write_to_disk(doc_file, doc_text) 

                #save tokenized doc to dictionary(with docno)----------------WRITE TO MEMORY  
                 
                prep_doc_dictionary(docno, vectorizer.fit_transform([doc_text]))  
                
                #big_corpus.append(doc_text) #nneded for fitting vectorizor?????
                #docs_tfidf = vectorizer.fit_transform([doc_text]) #tfidf for entire corpus...
                #print(docs_tfidf)
                #big_corpus.clear()
                #sleep(3)
                




    print("Pre-processing: \tComplete")
    print("Corpus indexed: \tWritten to disk at: " + data_dir + "/")
    sleep(1)

    


    print("Reading Query: \t\t" + query_path)

    #ready queries -------------------------------------------------
    query_dict = prep_query(query_path) #creates dictionary of query# to tokenized query strings from file of queries    

    #iterate through queries-------------------------------
    for item in query_dict: 
        current_query = query_dict[item] #current query is a list of stemmed work tokens

        length_of_query = len(current_query)
        #print("Tokens in query: " + str(length_of_query))        
        query_vector = []

        #compute tfidf for current query string------------
        for token in current_query:
           #get tf for term used in query-----
            tokenCounter = Counter(current_query)
            count = tokenCounter[token]

            query_tf = count/len(current_query)
            query_idf = math.log(length_of_query/count)
            query_vector.append(query_tf * query_idf)

            #print("Term count for: " + token + " in query is " + str(count))

        #print("Query Vector------------------------------------------")
        #print(query_vector)
        #print(current_query)
        #sleep(1)

        
       

        


        #iterate through corpus documents-------
        for doc in docNoIndex:  

            doc_vector = []

            for token in current_query:

                #get termID-----------------
                term_id = get_token_id(token) #get the term id #  
               
                #print(str(term_id) + "-> Token: " + token )  

                #iterate through current queries tokens and add tfidf(from doc) to doc's vector---
                tf = get_tfidf(token, doc)
                doc_vector.append(tf)

            
           
            
            print("My vectors for: " + doc + "------------------------------")
            print(doc_vector)
            print("Query vector-------------------------------------------------")
            print(query_vector)
            sleep(.5)


            cs = cosine_sim(query_vector, doc_vector)           

            print("Cos Sim")
            print(cs)





        '''
        tokenized_query = [] #list to hold tokenized and stemmed query

        tk = RegexpTokenizer('\s+', gaps = True) #init tokenizer
        token_list = tk.tokenize(current_query) #create list of query tokens

        for item in token_list:
            item = ps.stem(item) #stem the token
            tokenized_query.append(item) #add stemmed token to list of tokens ()
        #print(tokenized_query)
        '''
            





    #get term frequency for a given term and document
    #tf = get_tf("china", "ap890101-0001")
    #print(tf)

   

    #query_tfidf = vectorizer.transform(["34 556 17 3"])

    #cosineSimilarities = cosine_similarity(query_tfidf, docs_tfidf).flatten()
    #print(cosineSimilarities)


    '''
    qt = query_tokenizer(q) #tokenizes a single query
    print(qt)
    sleep(2)

    query_tfidf = vectorizer.transform([qt])
    print(query_tfidf)
    sleep(3)

    cosineSimilarities = cosine_similarity(query_tfidf, docs_tfidf).flatten()
    print(cosineSimilarities)

    cosineSimilarities.sort()
    print(cosineSimilarities)
    '''


        
    #execute output based on combination of input flags--------------------------------------------    
    #get_tf(args.term.lower(), args.document.lower()) #tmp experimental
    #visit_docs()


