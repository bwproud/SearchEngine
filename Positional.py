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
from Synonym import query2syn_query

def positional(di, le, po, out, query, syn):
    """
        Gets a vectorized version of the query, gets the postings associated with
        each term in the query, gets the dictionary of documents who contain tokens
        in the query, and then gets the final listing of the 10 highest ranked documents
        for the query using the previous 3 results. These 10 documents are then written to a file
    """
    print "positional"
    print syn
    phrases = [i for i in query if i.count(" ")]
    words = get_posts(di,po,syn)
    pdocs = {}
    final = []
    f = []
    for i in words:
        final.append(list(set([j[0] for j in words[i]])))
    for i in phrases:
        syn_query = query2syn_query(i.split(" "))
        final.append(get_positional_posts(di, po, syn_query))
    for i in final:
        for j in i:
            pdocs[j] = pdocs.get(j,0)+1
            if pdocs[j] == len(query):
                f.append(str(j))
    print f
    out.write(" ".join(f)+"\n")

def present(lists, end):
    p={}
    for i in range(len(lists)):
        for j in lists[i]:
            p[j-i] = p.get(j-i, 0) + 1
    for i in p:
        if p[i] == end: 
            return True
    return False

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

def get_positional_posts(di, po, query):
    """ 
        Gets the postings list for each unique token in the query
    """
    docs = {}
    ps = PorterStemmer()
    ind = {}
    final = []
    count=0
    #goes through each token in the query and returns its postings list
    for i in range(len(query)):  
        syn_list = query[i]
        o_word = query[i][0]
        ind[o_word] = count
        count+=1
        for k in range(len(syn_list)):
            word = syn_list[k]

            #only retrieves postings with corresponding dictionary entries
            resp = di.get(word, [])
            if len(resp) > 0:    
                po.seek(int(resp[1]))
                posts = literal_eval(po.readline())
                for j in posts:
                    li = docs.get(j[0], {})
                    listings = li.get(o_word, [])
                    listings=sorted(list(set(listings+j[2])))
                    li[o_word] = listings
                    docs[j[0]] = li
    for i in docs:
        if len(docs[i])==count:
            li=[0]*count
            for j in docs[i]:
                li[ind[j]]=docs[i][j]
            if present(li, count):
                final.append(i)
    return final