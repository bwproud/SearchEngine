#!/usr/bin/python
# encoding: utf-8
import re
import nltk
import sys
import getopt
import time
import math
import heapq
from ast import literal_eval
from Queue import Queue
from nltk.stem import PorterStemmer
import synonyms
import listops

def sanitize(phrase):
    """Sanitizes input by removing special characters, numbers, and collapsing whitespace"""
    return re.sub("[!@#$%^&()'`:*;,.?/°_-]",'',phrase)

def getdict(dict):
    """retrieves and populates the dictionary from the dictionary file"""
    di={}
    o = open(dict, 'r')
    for line in o:
        li=line.strip().split(' ')
        di[li[0]]=(int(li[1]), li[2])
    o.close()
    return di  

def getlength():
    """retrieves the length of every document and stores in a dictionary"""
    le={}
    o = open("lengths.txt", 'r')
    for line in o:
        li=line.strip().split(' ')
        le[li[0]]=li[1]
    o.close()
    return le  

def getqueries(queries):
    """ 
        Gets the queries from the queries file, sanities them, and creates
        a list of terms
    """
    q=[]
    o = open(queries, 'r') 
    for line in o:
        q.append(sanitize(line.lower().strip()).split(" "))
    o.close()
    return q 

def normalize(vector, size):
    """ 
        Normalizes a vector given the vector and the corresponding document length
    """
    for word in vector:
        vector[word]=vector[word]/float(size)
    return vector

def vectorize_query(di, N, query):
    """ 
        Vectorizes the query by getting the term frequencies of each token in the query,
        weighting these tokens, multiplying the weighted term frequency with the inverse
        document frequency, and then normalizing the resulting vector
    """
    vector = {}
    su = 0
    ps = PorterStemmer()

    #Gets the term frequencies of each term in the query
    for i in query:
        i = str(ps.stem(i))

        #only makes an dimension in the vector is the query token exists in the dictionary
        if di.get(i, False):
            vector[i] = vector.get(i, 0)+1

    #weights the term frequencies using logs, then multiplies this result with the inverse
    #document frequency. Also gets the size of the vector for use in normalization
    for i in vector:
        vector[i]=1+math.log(vector[i],10)
        mult = math.log((float(N)+1)/di[i][0],10)
        vector[i]=vector[i]*mult
        su += vector[i]**2

    #return the normalized vector
    return normalize(vector, su**.5)

def get_posts(di, po, syn_query):
    """ 
        Gets the postings list for each unique token in the query. Expects
        the tokens to be already stemmed
    """
    posts = {}

    # go through each token's synonym list
    for syns in syn_query:
        #goes through each token in the synonym list and returns its postings list
        for i in syns:  
            #only returns the first instance of a token
            if posts.get(i, False): continue

            #only retrieves postings with corresponding dictionary entries
            resp = di.get(i, [])
            if len(resp) > 0:    
                po.seek(int(resp[1]))
                posts[i]=literal_eval(po.readline())
    return posts

def get_candidates(postings, le):
    """ 
        Gets the possible document candidates from the postings list
        returned in get_posts(). If a document is seen in a postings list,
        it is added to a dictionary, along with the word(or words) it is
        associated with and the term frequencies of those words in the document
    """
    candidates = {}
    for word in postings:
        for i in postings[word]:
            doc = str(i[0])
            if not candidates.get(doc, False):
                candidates[doc]={}

            #normalizes the term frequencies of the words in each document
            candidates[doc][word]=[i[1]/float(le[doc]),i[2]]
    return candidates

def min_window(k):
    heap = []
    p=[0 for i in range(len(k))]
    min_r = 99999999
    ma=0
    #tu=[]
    for i in range(len(k)):
        if k[i][0]>ma:
            ma=k[i][0]
        heapq.heappush(heap,(k[i][0],i))
    while True:
        mi = heapq.heappop(heap)
        if ma-mi[0] < min_r:
            min_r = ma-mi[0]
            #tu=[mi[0],ma]
        p[mi[1]]+=1
        if(p[mi[1]]>=len(k[mi[1]])):
            return min_r
        else:
            num = k[mi[1]][p[mi[1]]]
            if num > ma:
                ma=num
            heapq.heappush(heap, (num,mi[1]))

def get_window(candidates):
    window={}
    for doc in candidates:
        li=[]
        for word in candidates[doc]:
            li.append(candidates[doc][word][1])
        if len(candidates[doc]) > 1:
            window[doc]=min_window(li)
        else:
            window[doc]=0
    return window

def sort(li):
    """ 
        Performs a mini radix sort on the top ten documents by first sorting
        on document ids, then sorting on document ranking. As sorted() is stable,
        this ensures that any documents with identical rankings will be sorted on 
        their document ids in increasing order
    """
    #first sort on document id
    li = sorted(li,key=lambda x: x[0])
    
    #then sort on document ranking
    li = sorted(li,key=lambda x: x[1], reverse=True)
    
    #sort on window length
    #li = sorted(li,key=lambda x: x[3])
    
    #then sort on number of present words
    #li = sorted(li,key=lambda x: x[2], reverse=True)
    return li

def query2syn_query(query):
    """
        Given list of query terms, return list-of-lists of synonyms
    """
    ps = PorterStemmer()

    # TODO stop treating entire query as one positional query
    syn_query = synonyms.get(query)
    for syns in syn_query:
        for idx, s in enumerate(syns):
            syns[idx] = str(ps.stem(s))

    return syn_query

def get_positional(candidates, pos_queries):
    """
        Only pass through the candidates that pass the given positional queries
    """
    print(pos_queries)

    passed_candidates = {}
    for doc_id, doc in candidates.items():
        passed = True

        # Check all positional queries for this document
        for pq in pos_queries:
            # Merge all synonyms of the first word to be l1
            syns = pq[0]
            l1 = doc.get(syns[0],[None,None])[1]
            for i in range(1,len(syns)):
                l2 = doc.get(syns[i],[None,None])[1]
                l1 = listops.or_merge(l1,l2)

            # Iteratively join with other words
            for j in range(1,len(pq)):
                # Merge all synonyms of word j to be list 2
                syns = pq[j]
                l2 = doc.get(syns[0],[None,None])[1]
                for k in range(1,len(syns)):
                    l3 = doc.get(syns[k],[None,None])[1]
                    l2 = listops.or_merge(l2,l3)

                # AND together l1 and l2
                l1 = listops.positional_and(l1,l2)

            if len(l1) == 0:
                passed = False
                break

        if passed:

            passed_candidates[str(doc_id)] = doc

    return passed_candidates

def get_final(candidates, q_vector, window):
    """
        Performs the cross product of the query vector and every candidate document
        to obtain a ranking for each document. Only the ten highest rankings are stored
        at any given time for speed and storage reasons.
    """
    final=[]
    for doc in candidates:
        su = 0
        #Gets the rankings of a given document through its cross product with the query vector
        for word in q_vector:
            su += q_vector[word]*candidates[doc].get(word, [0])[0]

        #adds it to the result set if the result set is less than 10. Then sorts the result set
        #if len(final) < 10:
        final.append((doc, su, len(candidates[doc]), window[doc]))
    
    final = sort(final)
    print final[:10]
    #return just the document ids of the documents with the highest rankings
    return [i[0] for i in final]

def evaluate(di, le, po, out, query):
    """
        Gets a vectorized version of the query, gets the postings associated with
        each term in the query, gets the dictionary of documents who contain tokens
        in the query, and then gets the final listing of the 10 highest ranked documents
        for the query using the previous 3 results. These 10 documents are then written to a file
    """
    print query

    syn_query = query2syn_query(query)
    q_vector = vectorize_query(di,len(le), query)
    postings = get_posts(di, po, syn_query)
    candidates = get_candidates(postings, le)
    candidates = get_positional(candidates, [ syn_query ]) # TODO split query into the specific positional queries
    window = get_window(candidates)
    final = get_final(candidates, q_vector, window) # TODO how to handle synonym queries when vectorizing query and chosing final
    out.write(" ".join(final)+"\n")

def search(dict, post, queries, out):
    """
        Gets the dictionary, gets the queries, gets the lengths, and
        then evalutes each query
    """
    print "testing search queries"
    di = getdict(dict)
    q = getqueries(queries)
    l = getlength()
    p = open(post, 'r')
    o = open(out, 'w')
    for query in q:
        evaluate(di,l,p,o,query)
    p.close()
    o.close()    
        
def usage():
    print "usage: " + sys.argv[0] + " -d dictionary-file -p postings-file -q file-of-queries -o output-file-of-results"

dictionary_file = postings_file = file_of_queries = output_file_of_results = None
	
try:
    opts, args = getopt.getopt(sys.argv[1:], 'd:p:q:o:')
except getopt.GetoptError, err:
    usage()
    sys.exit(2)

for o, a in opts:
    if o == '-d':
        dictionary_file  = a
    elif o == '-p':
        postings_file = a
    elif o == '-q':
        file_of_queries = a
    elif o == '-o':
        file_of_output = a
    else:
        assert False, "unhandled option"

if dictionary_file == None or postings_file == None or file_of_queries == None or file_of_output == None :
    usage()
    sys.exit(2)

start = time.time()
search(dictionary_file, postings_file, file_of_queries, file_of_output)
end = time.time()
print(end - start)