# CS172 - Assignment 1 (Tokenization)  

## Team: Sky DeBaun - Spring 2021


### This assignment is a simplified Information Retrieval system that consists of the following features:
   - Reads documents from a directory of docments, where each document uses a specialize IR (tagged) format
   - The documents are parsed and relevant information (DOCNO and TEXT) are extracted
   - The TEXT is tokenized, lower-cased, and stemmed (using the Porter method)
   - Tokens that are not part of the (provided) stop-word list are added to an inverted-index 

#### Indices 
   - Term Index (termIndex): dictionary that maps terms/tokens with a unique id number
   - Document Index (docNoIndex): dictionary that maps document names(DOCNO) to a unique id number
   - Term Info (termInfoIndex): dictionary that maps terms/tokens to a list of tuples (containing Term ID, Document ID, and Position)  

#### Other Data Structures
   - Term Counter (termCounter): dictionary used to count total occurences of each term
   - Stop Words (stopWordSet): set of stop words
   - Unique Words (uniqueWordSet): set used to count distinct terms across the corpus of documents


#### Language Used
The assignment is implemented using the Python language

#### Instructions
The project can be executed without any parameters (flags), however this will only create the various indices and NOT provide any output.
To use the project several flags (and their associated parameters) are needed, as follows:
   - --term (or -t) "term"  
     - Example: python read_index.py -t asparagus
   - --doc (or -d) "document name" 
     - Example: python read_index.py -d ap890101-0001
   - -c "collection directory"
     - Example: python read_index.py -c ap89_collection_minimal
     - Note: By default the project uses the provided ap89_collection_small corpus




###### Language used, how to run your code, if you attempted the extra credit (stemming), etc.  


#### Extra Credit
Tokens are stemmed using the Porter method (via the NLTK PorterStemmer)