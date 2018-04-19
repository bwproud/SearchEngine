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
from nltk.stem import PorterStemmer
from nltk.corpus import wordnet as wn
from Evaluate import query_parser
from Positional import positional
from Synonym import query2syn_query
from _pickle import Unpickler

def sanitize(phrase):
    """Sanitizes input by removing special characters, numbers, and collapsing whitespace"""
    return re.sub("[!@#$%^&()`:*;,.?/°_-]",'',phrase)

def getdict(dict):
    """retrieves and populates the dictionary from the dictionary file"""
    di={}

    fp_o = open(dict, 'rb')

    # get length of file
    fp_o.seek(0,2)
    end = fp_o.tell()
    fp_o.seek(0,0)

    o = Unpickler(fp_o)
    while fp_o.tell() < end:
        word = o.load()

        df = o.load()
        tell_idx = o.load()

        di[word] = (df, tell_idx)
    fp_o.close()

    return di  

def getlength():
    """retrieves the length of every document and stores in a dictionary"""
    le={}

    fp_o = open("lengths.txt", 'rb')

    # get length of file
    fp_o.seek(0,2)
    end = fp_o.tell()
    fp_o.seek(0,0)

    o = Unpickler(fp_o)
    while fp_o.tell() < end:
        file = o.load()
        length = o.load()

        le[file] = length
    fp_o.close()

    return le  

def getqueries(queries):
    """ 
        Gets the queries from the queries file, sanities them, and creates
        a list of terms
    """
    q=[]
    pos=False
    o = open(queries, 'r') 
    for line in o:
        query = line.lower().strip()
        if query.count('\"'):
            qu = query.split(" and ")
            for i in range(len(qu)):
                if qu[i].count('\"'):
                    f = qu[i].find('\"')+1
                    s = qu[i].find('\"', f)
                    qu[i]= qu[i][f:s].strip()
                else:
                    qu[i]=qu[i].strip()
            q.append(qu)
            pos=True
        else:
            q.append(sanitize(query).split(" "))
    o.close()
    return q, pos

def search(dict, post, queries, out):
    """
        Gets the dictionary, gets the queries, gets the lengths, and
        then evalutes each query
    """
    print ("testing search queries")
    di = getdict(dict)
    q, pos = getqueries(queries)
    l = getlength()
    p = open(post, 'rb')
    o = open(out, 'w')
    for query in q:
        syn_query = query2syn_query(query)
        if not pos:
            query_parser(di,l,p,o,query,syn_query)
        else:
            positional(di,l,p,o,query,syn_query)
    p.close()
    o.close()    
        
def usage():
    print( "usage: " + sys.argv[0] + " -d dictionary-file -p postings-file -q file-of-queries -o output-file-of-results")

dictionary_file = postings_file = file_of_queries = output_file_of_results = None
  
try:
    opts, args = getopt.getopt(sys.argv[1:], 'd:p:q:o:')
except:
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
        raise "unhandled option"

if dictionary_file == None or postings_file == None or file_of_queries == None or file_of_output == None :
    usage()
    sys.exit(2)

start = time.time()
search(dictionary_file, postings_file, file_of_queries, file_of_output)
end = time.time()
print(end - start)