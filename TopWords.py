#!/usr/bin/python
# encoding: utf-8
from ast import literal_eval
import math

TRACK_SCORES = 50

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

scores = {}
fp_p = open('postings.txt', 'r')
dict = getdict('dictionary.txt')

i = 1
N = len(getlength())
for token in dict:
    print("%d/%d" % (i,len(dict)))
    i += 1

    postings_def = dict[token]

    fp_p.seek(int(postings_def[1]))
    token_postings = literal_eval(fp_p.readline())

    for posting in token_postings:
        docID = posting[0]
        tf = posting[1]

        df = postings_def[0]
        if df < N*0.0025 or df > N*0.2: continue

        idf = math.log(N/df, 10)

        score = tf*idf
        top_scores = scores.get(docID, [])
        if len(top_scores) < TRACK_SCORES:
          top_scores.append([ token, score ])
        elif score > top_scores[-1][1]:
          top_scores[-1] = [ token, score ]

        top_scores.sort(key=lambda x: x[1], reverse=True)
        scores[docID] = top_scores
fp_p.close()

fp_top = open('topwords.txt', 'w')
topwords_dict = {}
for docID in scores:
    topwords_dict[docID] = fp_top.tell()

    to_out = {}
    for i, top_scores in scores[docID]:
        for j, entry in top_scores:
            to_out[entry[0]] = entry[1]
    fp_top.write(str(to_out))
    fp_top.write("\n")
fp_top.close()

# Save the dictionry
fp_top_dict = open('topwords_dict.txt', 'w')
fp_top_dict.write(str(topwords_dict))
fp_top_dict.close()