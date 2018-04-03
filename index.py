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
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords

def sanitize_sentence(phrase):
    """Sanitizes sentences by removing special characters"""
    return re.sub('[@#$“%”“’‘。&^\'`*/°]','',phrase)

def sanitize(phrase):
    """Sanitizes words by removing punctuation"""
    return re.sub('[!-():?.]','',phrase)

def index(input, dict, post):
    """
        Performs the indexing step which creates the dictionary and
        posting list. Does this by going through every word in every
        file, tokenizing it, and then adding it to the in memory dictionary.
        Also keeps track of term frequencies in each document and the lengths
        of each document for use in the searching steps.
    """
    print "creating dictionary and postings list"
    
    #instance variables used in indexing:
    #d is the dictionary, copy is the list of all the document ids
    #input is the input directory. Accounts for lack of '/'
    #df keeps track of the document frequency of words
    #documents keeps track of the term frequency of words inside each document
    #length keeps track of the length of every document
    d={}
    df={}
    documents={}  
    positions={}
    length={} 
    copy=[] 
    csv.field_size_limit(sys.maxsize)
    stops = set(stopwords.words("english"))
    print "starting csv parsing"
    with open(input, 'rb') as csvfile:
        dataset = csv.reader(csvfile, delimiter=',')
        for row in dataset:
            word_count=0
            try:
                file=int(row[0])
            except:
                continue
            copy.append(file)
            #goes through every file in the directory
            documents[file]={}
            positions[file]={}
            #goes through every line in each file
            ps = PorterStemmer()

            #tokenize each word and add it to the dictionary if its not a stopword
            #or a digit
            for i in nltk.sent_tokenize(row[2].decode('utf-8')):
                for j in nltk.word_tokenize(sanitize_sentence(i)):
                    res=ps.stem(sanitize(j.lower()))
                    

                    #don't add if a stopword or a digit or punctuation
                    if not res or res in stops or res in '.,/!@#$%^&*()_+-=[]{}|:;?' or res.isdigit():
                        continue

                    #increase the term frequency of a given word in a given document
                    documents[file][res]= documents[file].get(res,0)+1
                    if not positions[file].get(res,False):
                        positions[file][res]=[word_count]
                    else:
                        positions[file][res].append(word_count)
                    word_count+=1
                    #if the word has not been seen, make a new entry in the dictionary
                    #and increase the document frequency of the word
                    if res not in d:
                        d[res]=[file]
                        df[res]=1

                    #if the word has already been seen, add the doc_id to the dictionary entry
                    else:

                        #and if its the first time the word has been seen in a given document
                        #increase the document frequency of the word
                        if file not in d[res]:
                            d[res].append(file) 
                            df[res]=df[res]+1
        print "weight term frequencies"
        copy=sorted(copy)
        #weight the term frequencies of each document and calculate its length
        for file in copy:
            su = 0
            for word in documents[file]:
                documents[file][word]=1+math.log(documents[file][word],10)
                su += documents[file][word]**2
            length[file]=su**.5

        print "prepare dictionary"
        #prepare dictionary for output to postings list by including term freqencies
        for key in d:
            tf = []
            for doc in d[key]:
                tf.append((doc, documents[doc][key], positions[doc][key]))
            d[key]=tf

        o = open(dict, 'w')
        p = open(post, 'w')
        le = open("lengths.txt",'w')
        print "start write"
        #writes to the posting list and dictionary file                     
        for i in sorted(d):
            try:
                o.write("%s %s %s\n" % (i.encode('utf-8'), df[i], p.tell()))
                p.write("%s\n"%(d[i],))
            except:
                print i 

        #output out all document lengths
        for file in copy:
            le.write("%s %s\n" % (file, length[file]))  

        o.close()
        p.close()

def usage():
    print "usage: " + sys.argv[0] + " -i directory-of-documents -d dictionary-file -p postings-file"

input_directory = output_file_dictionary = output_file_postings = None

try:
    opts, args = getopt.getopt(sys.argv[1:], 'i:d:p:')
except getopt.GetoptError, err:
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
        assert False, "unhandled option"
        
if input_directory == None or output_file_postings == None or output_file_dictionary == None:
    usage()
    sys.exit(2)
start = time.time()
index(input_directory,output_file_dictionary,output_file_postings)
end = time.time()
print(end - start)