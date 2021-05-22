# CS172 - Assignment 2 (Retrieval)  

## Team: Sky DeBaun - Spring 2021


### This assignment is a simplified Information Retrieval system that builds on Assignment 1
   - This assignment uses the Vector Space Model to perform a full retrieval of matching documents from a corpus of documents (ap89_collection_small)

### Indices:
   - Term Index (termIndex): dictionary that maps terms/tokens with a unique id number
   - Document Index (docNoIndex): dictionary that maps document names(DOCNO) to a unique id number

### Other Details:
   - 


### Language Used:
The assignment is implemented using the Python 3 language

### Instructions:
User input is collected via the use of flags and associated arguments (see examples below)

Note the following:
   - a directory (relative to current) can be specified for saving indexed documents to disk (defaults to data/index/) using the -d (or --dir) flag
   - a specific corpus can be specified using the -c ) or --collection) flag to overide the default (i.e. ap89_collection_small)
   - query_list.txt and results.txt are the defaults if -q and -o flags are ommited

Example usage: 
   - python vsm.py
   - python vsm.py -q query_list.txt -o results.txt 
   - python vsm.py -q query_list.txt -o results.txt -d data/index/
   - python vsm.py -q query_list.txt -o results.txt -d data/index/ -c ap89_collection_min


### Extra Credit:
