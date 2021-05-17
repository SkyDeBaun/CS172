# CS172 - Assignment 2 (Retrieval)  

## Team: Sky DeBaun - Spring 2021


### This assignment is a simplified Information Retrieval system that builds on Assignment 1
   - Reads documents from a directory of docments, where each document uses a specialize IR (tagged) format
   - The documents are parsed and relevant information (DOCNO and TEXT) are extracted
   - The TEXT is tokenized, lower-cased, and stemmed (using the Porter method)
   - Tokens that are not part of the (provided) stop-word list are added to an inverted-index 

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

Examples: 
   - helo

### Extra Credit:
