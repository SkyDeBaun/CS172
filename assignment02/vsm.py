#CS172 - Intro to Information Retrieval - UCR, Spring 2021
#Sky DeBaun
#Assingment 02
#Read a text file of numbered queries and output a file of the top 10 results from the corpus (ap89_collection_small)
#Uses reverse index and the Vector Space Model to output Cosine Similarity between a particular query and each document in the corpus

#imports----------------------------------------------------------------------- IMPORTS
import argparse #parse user input
import re #regex
#import zipfile

#nltk-------------------------------------------------------------
import nltk
from nltk.tokenize import RegexpTokenizer
from nltk.stem import PorterStemmer
ps = PorterStemmer()

#numpy------------------------------------------------------------
import numpy as np
from numpy import dot
from numpy.linalg import norm

#os and other------------------------------------------------------
import os
import sys
import math #dot products and normals
from time import sleep #used for debugging

#counter magic(used for query vectors)-----------------------------
from collections import Counter #used with query string/lists

#user friendly exception tracebacks--------------------------------
import traceback



#Vars and setup------------------------------------------------------------------- SETUP
#---------------------------------------------------------------------------------
doc_regex = re.compile("<DOC>.*?</DOC>", re.DOTALL)
docno_regex = re.compile("<DOCNO>.*?</DOCNO>")
text_regex = re.compile("<TEXT>.*?</TEXT>", re.DOTALL)


#my indices (dictionaries)---------------------------------------------------------
stopWordSet = set() #create empty set for stopwords
uniqueWordSet = set() #used to count distinct terms

docNoIndex = {} #dictionary for document reverse index (i.e. document name to document ID) ex: {ap890101-0001': 0}
termIndex = {} #dictionary of tokens ex: {token:token_id}
termCounter = {} #store count of term usage across entire corpus/collection 
termInfoIndex = {} #dictionary of term to term info
docInfoIndex = {} #dictionary of doc key to doc info ex: {doc_key:tuple}

query_dict = {} # query# to tokenized query string i.e. {query_number:list_of_stemmed_tokens}


#FUNCTIONS------------------------------------------------------------------------- FUNCTIONS
#----------------------------------------------------------------------------------

#update term count (across the whole collection/corpus)----------------GET TERM COUNT(IN CORPUS)
def get_term_count(token_id, index=termCounter):

    if token_id in termCounter:
        counter = termCounter[token_id]
    else:
        counter = 0

    return counter


#add token-------------------------------------------------------------ADD TOKEN
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


#get token id----------------------------------------------------------GET TOKEN ID
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

        
#add document number to (reverse) index of documents--------------------DOCUMENT NUMBER: DICTIONARY
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


#get document id--------------------------------------------------------GET DOC ID
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


#get info for doc + term ----------------------------------------------GET DOC INFO 
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


#add to doc info dictionary--------------------------------------------ADD DOC INFO(TUPLE)
def add_doc_info(doc_key, tpl_info, index=docInfoIndex):
    if doc_key in docInfoIndex:
        docInfoIndex[doc_key].append(tpl_info) #tuple is: (token_counter, len(uniqueWordSet)
    else:
        docInfoIndex.__setitem__(doc_key, [tpl_info])


#count total terms used in doc-----------------------------------------GET TERM COUNT(IN DOC)
def count_doc_terms(doc_key, index=docInfoIndex):
    if doc_key != -1:
        info = index[doc_key] #list of tuples.. kind of redundant as its always a list of size 1
        tpl = info[0] #get tuple
   
        return tpl[0], tpl[1] #return: total terms and unique terms
    else:
        return 0, 0


#count docs(that use a specific term)----------------------------------COUNT DOCS(USING TERM)
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


#get term tfidf--------------------------------------------------------GET TFIDF(FOR A DOC)
def get_doc_tfidf(term, doc_no):

    tfidf=0 
    idf=0

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
 
    
#read query doc-------------------------------------------------------READ QUERY FILE
def read_query_doc(query_path):
    with open (query_path, 'r') as file:
        query_text = file.readlines() #unprocesed list of queries
        
    return query_text


#tokenize text--------------------------------------------------------TOKENIZE TEXT STRING(QUERIES ONLY)
def text_tokenizer(text):
    text = re.sub('[()!@#$%^&*:;,"._`\']', '', text.lower()) #lower case and remove punctuation chars (leave hyphens!)
               
    tk = RegexpTokenizer('\s+', gaps = True)
    tokens = tk.tokenize(text) #get list of tekenized text
    #tokenized_text = '' #stores string of token id's for indexed doc 

    stemmed_tokens = [] #will hold stemmed tokens

    #process my list of tokens---------------------------------- 
    for token in tokens:       

        #add to stemmed term to index--------------------------- 
        token_porter = ps.stem(token) #stemmed using porter tokenizer
        token_id = add_token(token_porter) #add stemmed token to dict (if not already in dict) and/or get its key#  

        #must account for new tokens (in query) not seen in corpus
        tpl_term_info = (token_id, 0, 0)  #token key, doc key, term position in doc

        #add tuple of info to term_info index------------------ 
        add_term_info(token_porter, tpl_term_info)
        
        #add stemmed token to query list
        stemmed_tokens.append(token_porter) 
    
    return stemmed_tokens #list of stemmed tokens


#prep query (convert to list of queries)------------------------------READ FILE & RETURN {QEURY_NUM:TOKEN_LIST}) DICT
def prep_query(query_path, query_dictionary=query_dict):
    query_text = read_query_doc(query_path)

    for text in query_text:
        q_num = text[:4].strip() #assumes the query number isn't too big..
        num = re.sub('[.]', '', q_num)
        query_string = text[5:].strip().lower()

        #add num : stemmed and tokenized query string (as a list of stemmed tokens) to dictionary
        query_dictionary.__setitem__(num, text_tokenizer(query_string))
    
    return query_dictionary #i.e {query_number:list_of_stemmed_tokens}


#compute tfidf for current query (as a list of tokens)----------------GET TFIDF OF A QUERY LIST
def get_query_tfidf(query_list):

    query_vector=[]
    length_of_query = len(query_list)

    for token in query_list:
           
        #count token use in query-----------
        tokenCounter = Counter(query_list) #counter magic makes this easy
        count = tokenCounter[token]

        #get tf for term used in query-----
        query_tf = count/len(query_list)

        #get idf for term used in query-----
        query_idf = math.log(length_of_query/count)
        query_vector.append(query_tf * query_idf)

    return query_vector #i.e. a list of tfidf values for the query


#return cosine similarity between two lists of tfidf values-----------GET COSINE SIMILARITY(OF QUERY TO A DOC)
def cosine_sim(vec1, vec2):

    #get normals-----------------------------
    norm1 = norm(vec1)
    norm2 = norm(vec2)

    #check for division by zero!-------------
    if norm1 == 0 or norm2 == 0:
        return 0
    else:        
        return dot(vec1, vec2)/(norm(vec1) * norm(vec2)) #dot product


#write query results to file-------------------------------------------WRITE RESULTS TO FILE
def write_results(sorted_results_dict, output_file, num_results=10): 

    num_results = min(len(sorted_results_dict), num_results) #stay within scope (ie don't try to write too many!)
    rank = 1
   
    with open(output_file, 'a') as outfile:

        for result in sorted_results_dict: #sorted_results is a {cosine_sim:(query_num, docno)} dict

            cos_sim = result 
            info = sorted_results_dict[result]
            query_num = info[0]
            docno = info[1] 
            
            output_string = '%3s Q0  %13s %2s %.16f Exp\n' % (str(query_num), str(docno),str(rank),(cos_sim))
            outfile.write(output_string)
            #print(output_string) 

            rank +=1
            if rank > num_results:
                break #quick fix to limit write out to a specified range


#reset output file on startup-----------------------------------------CLEAR OUTPUT FILE (BEFORE NEW QUERIES SEARCH)
def clear_ouput_file(output_file):
    with open(output_file, 'w') as outfile:
        outfile.write('') #overwrite any results from previous run of program




#-------------------------------------------------------------------------------------------------------------- 
#-------------------------------------------------------------------------------------------------------------- MAIN
#-------------------------------------------------------------------------------------------------------------- 
if __name__ == '__main__':
    

    #parse user input from command line------------------------------------------------------------- USER INPUT --> NOTE THE DEFAULTS HERE! 
    parser = argparse.ArgumentParser()
    parser.add_argument("-q", "--query", dest = "query_path", help="Enter Path to Query document (i.e. query_list.txt)" , default='query_list.txt')
    parser.add_argument("-o", "--ouput", dest = "output_path", help="Enter Path to Output document (i.e. results.txt", default='results.txt')
    parser.add_argument("-c", "--collection", dest = "collection", default="ap89_collection_small", help="Document Collection Directory")
    
    args = parser.parse_args() #get user args
    collection = args.collection
    query_path = args.query_path
    output_path = args.output_path

    #erase any previous results (ie from previous runs of program)--------- CLEAR OLD RESULTS
    clear_ouput_file(output_path) #clean output file in prep. for new run through corpus/query list    

    #user feedback--------------------------------------------------------- USER FEEDBACK
    print("\nCrawling Corpus: \t" + collection)
   


    #begin processing the collection---------------------------------------------------------------- BEGIN PROCESSING CORPUS
    # Retrieve the names of all files to be indexed in folder ./ap89_collection_small of the current directory
    for dir_path, dir_names, file_names in os.walk(collection):
        allfiles = [os.path.join(dir_path, filename).replace("\\", "/") for filename in file_names if (filename != "readme" and filename != ".DS_Store")]


    #FOR EACH FILE IN COLLECTION------------------------------------------- FOR EACH FILE
    #----------------------------------------------------------------------
    for file in allfiles: 
        with open(file, 'r', encoding='ISO-8859-1') as f:
            filedata = f.read()
            result = re.findall(doc_regex, filedata)  # Match the <DOC> tags and fetch documents
                       
            #FOR EACH DOCUMENT IN FILE-------------------------------------- FOR EACH DOC NO
            #---------------------------------------------------------------
            for document in result[0:]:
                
                # Retrieve contents of DOCNO tag
                docno = re.findall(docno_regex, document)[0].replace("<DOCNO>", "").replace("</DOCNO>", "").strip()
                
                #add doc ID to doc index------------------------------------ INDEX DOC NUMBER  
                doc_index_key = add_document_number(docno) #add doc no

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

                    #add tokens/terms to set for count of distinct----------
                    uniqueWordSet.add(token) 

                    #stemming using porter --------------------------------- STEMMING (Porter)
                    token_porter = ps.stem(token)

                    position_counter += 1 #position counter of token in current doc
                    token_counter += 1 #count total tokens/terms in current doc
                    token_id = add_token(token_porter) #add stemmed token to dict and get its key#
                    
                    
                    #create tuple of term information----------------------- TERM TUPLE CREATION
                    tpl_term_info = (token_id, doc_index_key, position_counter)  #token key, doc key, term position in doc

                    #add tuple of info to term_info index------------------- TERM INFO INDEX
                    add_term_info(token_porter, tpl_term_info)


                #store count of unique terms in a doc-----------------------
                add_doc_info(doc_index_key, (token_counter, len(uniqueWordSet)))
                uniqueWordSet.clear()

 

    #processing corpus complete--------------------------------------------------------------------- PROCESSING CORPUS COMPLETE
    #-----------------------------------------------------------------------------------------------
    print("Pre-processing: \tcomplete")
    print("Reading Query: \t\t" + query_path)


    #ready queries ------------------------------------------------- PREPARE QUERY DICT
    query_dict = prep_query(query_path) #read file and get {query_num:list_of_stemmed_tokens}    

    #iterate through queries---------------------------------------- FOR EACH QUERY
    for query_number in query_dict: 
        current_query = query_dict[query_number] #current query is a list of stemmed work tokens  
        
        query_vector = [] #reset for each new query (used to compute cosine similarity)
        result_dictionary = {} #dictionary to hold {rank : tuple of {query_no, docno}} for results of cosine similarity-> reset for each new query

        #get tfidf for current query "string" (is list of tokens)----
        query_vector = get_query_tfidf(current_query)


        #iterate through corpus documents---------------------------- FOR EACH DOC IN COLLECTION
        for doc in docNoIndex:  #use the reverse index for fast lookups

            doc_vector = [] #reset for each new document (for tfidf values)

            #for token in query-------------------------------------- FOR EACH TOKEN IN QUERY
            for token in current_query:

                #get termID------------------------------------------ 
                term_id = get_token_id(token) #get the term id #  

                #iterate through current queries tokens and add tfidf(from doc) to doc's vector---
                term_freq = get_doc_tfidf(token, doc)
                doc_vector.append(term_freq)


            #get cosine similarity----------------------------------- COSINE SIMILARITY (QUERY TO DOCUMENT)
            cs = cosine_sim(query_vector, doc_vector) 
            result_tuple = (query_number,doc) 
            result_dictionary.__setitem__(cs, result_tuple) #add to result dict
           


        #results for a particular query-------------------------------
        results = dict(sorted(result_dictionary.items(), key=lambda item: item[0], reverse=True))

        #write to file------------------------------------------------ WRITE RESULTS TO FILE (FOR SINGLE QUERY)
        write_results(results, output_path, 10) #limit resulst to top 10



    #user feedback---------------------------------------------------------------------------------- DONE!
    print("\nRetrieval Complete!")
    print("Results written to: \t" + output_path)
