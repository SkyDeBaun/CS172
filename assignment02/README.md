# CS172 - Assignment 2 (Retrieval)   

## Team: Sky DeBaun - Spring 2021  


### This assignment is a simplified Information Retrieval system that builds on Assignment 1 as follows:  
   - It performs a full retrieval of documents matching a set of queries (read from text file)  
   - It adds support for complex queries (more than 1 term) using the Vector Space Model  
   - It uses Cosine Similarity to score and rank all documents within the corpus  
   

### Other information about this assignment:  
   - The set of queries is read from a text file  
   - After completion results are saved to a text file in the TREC Evaluation Code Format  
     - Example: <query−number> Q0 <docno> <rank> <score> Exp  
     - Output is limited to top 10 documents for each query

### This assignment uses the following:  
   - query_list.txt (input)   
   - vsm.py (the main program) 
   - ap89_collection_small (directory of files containing documents tagged using the SGML format)  
   - ap89_collection_select  (contains first half of the collection)
   - ap89_collection_min  (a minimal selection for testing the program)
   

### This assignment produced the following:
  - ap89_min_results.txt --> output from querying ap89_collection_min (has only one file: ap890101.txt) 
  - ap89_select_results.txt --> output from querying the ap89_collection_select (only first 10 files from ap89_collection_small)
  - ap89_small_results.txt --> output from querying ap89_collection_small
   
 

### Language Used:  
The assignment is implemented using the Python 3 language  

### Instructions:
Program input and output are specified using command line flags and their associated arguments (see examples below)

#### Note the following:
   - a different corpus can be specified using the -c (or --collection) flag to overide the default (i.e. ap89_collection_small)
   - query_list.txt and results.txt are the defaults if -q and -o flags are ommited

### Example usage: 
   - python vsm.py
   - python vsm.py -q query_list.txt -o results.txt     
   - python vsm.py -q query_list.txt -o results.txt -c ap89_collection_min  

