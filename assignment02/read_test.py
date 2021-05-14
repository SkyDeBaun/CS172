#feature extraction --> https://scikit-learn.org/stable/modules/feature_extraction.html
from sklearn.feature_extraction.text import TfidfVectorizer





#read the queries from text file-----------------------
with open ('query_list.txt', 'r') as file:
  query_list = file.readlines() #unprocesed list of queries

queries = [text[5:].strip().lower() for text in query_list] #list comprehension

#print(queries)



tfidf = TfidfVectorizer()

vec = tfidf.fit_transform(queries)
print(vec)