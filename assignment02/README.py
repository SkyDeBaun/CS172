# CS172 - Assignment 2 (Retrieval)  

## Team: Sky DeBaun - Spring 2021


### This assignment is a simplified Information Retrieval system that builds on Assignment 1
   - This assignment uses the Vector Space Model to perform a full retrieval of matching documents from the corpus of documents (ap89_collection_small)
   - It reads the command line arguments for a text file of queries and a file to save the result to  

### Indices:
   - Term Index (termIndex): dictionary that maps terms/tokens with a unique id number
   - Document Index (docNoIndex): dictionary that maps document names(DOCNO) to a unique id number
   - Term Info (termInfoIndex): dictionary that maps terms/tokens to a list of tuples (containing Term ID, Document ID, and Position)  

### Other Data Structures:
   - Term Counter (termCounter): dictionary used to count total occurences of each term
   - Stop Words (stopWordSet): set of stop words
   - Unique Words (uniqueWordSet): set used to count distinct terms across the corpus of documents

Note: all data structures for this assignment are stored in memory and not on disc! 

### Language Used:
The assignment is implemented using the Python 3 language

### Instructions:

Example usage: 
   - python VSM.py data/query_list.txt results.txt

### Extra Credit:
