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

def evaluate(di, le, po, out, query, syn):
    """
        Gets a vectorized version of the query, gets the postings associated with
        each term in the query, gets the dictionary of documents who contain tokens
        in the query, and then gets the final listing of the 10 highest ranked documents
        for the query using the previous 3 results. These 10 documents are then written to a file
    """
    print "not positional"
    q_vector = vectorize_query(di,len(le), query)
    postings = get_posts(di, po, syn)
    candidates = get_candidates(postings, le)
    window = get_window(candidates)
    final = get_final(candidates, q_vector, window)
    out.write(" ".join(final)+"\n")

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
            if candidates[doc].get(word, False):
                current = candidates[doc][word]
                if current[0] < i[1]/float(le[doc]):
                    current[0] = i[1]/float(le[doc])
                current[1]=list(set(current[1]+i[2]))
            else:
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
            tu=[mi[0],ma]
        p[mi[1]]+=1
        if(p[mi[1]]>=len(k[mi[1]])):
            return min_r
        else:
            num = k[mi[1]][p[mi[1]]]
            if num > ma:
                ma=num
            heapq.heappush(heap, (num,mi[1]))

def get_posts(di, po, syn):
    """ 
        Gets the postings list for each unique token in the query
    """
    words = {}
    #goes through each token in the query and returns its postings list
    for i in range(len(syn)):
        word = syn[i][0]  
        for k in range(len(syn[i])):

            j=syn[i][k]
            #only returns the first instance of a token
            if words.get(j, False): continue

            #only retrieves postings with corresponding dictionary entries
            resp = di.get(j, [])
            if len(resp) > 0:    
                po.seek(int(resp[1]))
                line=literal_eval(po.readline())
                words[word]=words.get(word,[])+line
    return words

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
    li = sorted(li,key=lambda x: x[3])
    
    #then sort on number of present words
    li = sorted(li,key=lambda x: x[2], reverse=True)
    return li

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
        final.append((doc, su, len(candidates[doc]), window[doc]))
    
    final = sort(final)
    #print(final[:10])
    #return just the document ids of the documents with the highest rankings
    return [i[0] for i in final]