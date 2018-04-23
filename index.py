#!/usr/bin/python
# encoding: utf-8
import re
import nltk
import sys
import getopt
import math
import csv
import os
import time
import asyncio
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
from concurrent.futures import ThreadPoolExecutor
import multiprocessing
from multiprocessing import Pool
from _pickle import Pickler

def sanitize_sentence(phrase):
    """Sanitizes sentences by removing special characters"""
    return re.sub('[@#$“%”“’‘。&^\'`*/°]','',phrase)

def sanitize(phrase):
    """Sanitizes words by removing punctuation"""
    return re.sub('[!-():?.]','',phrase)

# shared state for indexing
ps = PorterStemmer()
stops = set(stopwords.words("english"))

def index_row(row):
    word_count=0
    try:
        file=int(row[0]) # get docID
    except:
        return None, None, None

    #goes through every file in the directory
    documents={}
    positions={}

    #tokenize each word and add it to the dictionary if its not a stopword
    #or a digit
    for i in nltk.sent_tokenize(row[2]):
        for j in nltk.word_tokenize(sanitize_sentence(i)):
            token=ps.stem(sanitize(j.lower()))

            #don't add if a stopword or a digit or punctuation
            if not token or token in stops or token in '.,/!@#$%^&*()_+-=[]{}|:;?' or token.isdigit():
                continue

            #increase the term frequency of a given word in a given document
            documents[token]= documents.get(token,0)+1
            if not positions.get(token,False):
                positions[token]=[word_count]
            else:
                positions[token].append(word_count)
            word_count+=1

    print("Done %d" % (file,))

    return [ file, documents, positions ]

def index(input, dict, post):
    """
        Performs the indexing step which creates the dictionary and
        posting list. Does this by going through every word in every
        file, tokenizing it, and then adding it to the in memory dictionary.
        Also keeps track of term frequencies in each document and the lengths
        of each document for use in the searching steps.
    """
    print("creating dictionary and postings list")
    
    #instance variables used in indexing:
    #input is the input directory. Accounts for lack of '/'
    #documents keeps track of the term frequency of words inside each document
    #length keeps track of the length of every document
    documents={}  
    positions={}
    length={} 
    copy=[] 

    csv.field_size_limit(2000000000)
    print("starting csv parsing")
    with open(input, encoding='utf8') as csvfile:
        reader = csv.reader(iter(csvfile.readline, ''))
        reader.__next__() # skip header

        cpus = multiprocessing.cpu_count()-1
        with Pool(processes=cpus) as pool:
            result = pool.map(func=index_row, iterable=reader)
            for row in result:
                docID = int(row[0])
                doc_documents = row[1]
                doc_positions = row[2]

                documents[docID] = doc_documents
                positions[docID] = doc_positions
                copy.append(docID)
                print("Merged %d" % (docID))

    print("weight term frequencies")
    copy=sorted(copy)

    #d is the dictionary, copy is the list of all the document ids
    #df keeps track of the document frequency of words
    
    #weight the term frequencies of each document and calculate its length
    df = {} # while also computing document frequency
    d  = {} # while also computing document list (postings for each token)  
    for file in copy:
        su = 0
        for word in documents[file]:
            df[word] = df.get(word, 0) + 1 # document frequency

            # document list
            postings = d.get(word, [])
            postings.append(file)
            d[word] = postings

            # term frequencies and length accumulation
            documents[file][word]=1+math.log(documents[file][word],10)
            su += documents[file][word]**2
        length[file]=su**.5

    print("prepare dictionary")
    #prepare dictionary for output to postings list by including term freqencies
    for key in d:
        tf = []
        for doc in d[key]:
            tf.append((doc, documents[doc][key], positions[doc][key]))
        d[key]=tf

    o = open(dict, 'w')
    p = open(post, 'w')
    le = open("lengths.txt",'w')

    print("start write")
    #writes to the posting list and dictionary file                     
    for i in sorted(d):
        try:
            o.write("%s %s %s\n" % (i.encode('utf-8'), df[i], p.tell()))
            p.write("%s\n"%(d[i],))
        except:
            print(i) 


    #output out all document lengths
    for file in copy:
        le.write("%s %s\n" % (file, length[file]))  

    o.close()
    p.close()

def usage():
    print("usage: " + sys.argv[0] + " -i directory-of-documents -d dictionary-file -p postings-file")

input_directory = output_file_dictionary = output_file_postings = None

if __name__ == "__main__":
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'i:d:p:')
    except:
        usage()
        sys.exit(2)
        
    for o, a in opts:
        if o == '-i': # input directory
            input_directory = a
        elif o == '-d': # dictionary file
            output_file_dictionary = a
        elif o == '-p': # postings file
            output_file_postings = a
        else:
            raise "unhandled option"
            
    if input_directory == None or output_file_postings == None or output_file_dictionary == None:
        usage()
        sys.exit(2)
    start = time.time()
    index(input_directory,output_file_dictionary,output_file_postings)
    end = time.time()
    print(end - start)