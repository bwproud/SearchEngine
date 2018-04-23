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
from nltk.corpus import wordnet as wn
from nltk.corpus import stopwords

def query_parser(di, le, po, out, query, syn):
    ps = power_set(query)
    ans = []
    seen = {}
    for i in range(len(ps)):
        se = ps[i]
        level = []
        for j in se:
            level.append(get_positional_posts(di, po, j))
        for j in range(len(se)):
            scalar = 0
            for k in range(len(se[j])):
                if di.get(se[j][k][0],False):
                    scalar+=math.log((float(len(le))+1)/di[se[j][k][0]][0],10)
            factor = 0 if len(level[j]) == 0 else (float(1)/len(level[j]))* scalar
            level[j]=(factor,level[j])
        level = sorted(level, key = lambda x: x[0], reverse = True)
        for j in level:
            if len(j[1]) >= 500: continue
            for doc in j[1]:
                doc = str(doc)
                if not seen.get(doc, False):
                    ans.append(doc)
                    seen[doc]=True
    final = evaluate(di, le, po, out, query, syn)
    for doc in final:
        if not seen.get(doc, False):
            ans.append(doc)
            seen[doc] = True
    out.write(" ".join(ans)+"\n")

def power_set(q):
    li=[]
    count = len(q)
    if count > 4:
        count = 4
    while count > 1:
        a=[]
        for i in range(len(q)-count+1):
            syn_query = query2syn_query(q[i:i+count])
            a.append(syn_query)
        li.append(a)
        count-=1
    return li

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
    return get_final(candidates, q_vector, window)

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
    ma = 0
    for doc in candidates:
        su = 0
        #Gets the rankings of a given document through its cross product with the query vector
        for word in q_vector:
            su += q_vector[word]*candidates[doc].get(word, [0])[0]
        if su > ma:
            ma = su
        #adds it to the result set if the result set is less than 10. Then sorts the result set
        final.append((doc, su, len(candidates[doc]), window[doc]))
    print ma
    final = sort(final)
    #print(final[:10])
    #return just the document ids of the documents with the highest rankings
    return [i[0] for i in final if i[1]>(ma*.15)]

def positional(di, le, po, out, query, syn):
    """
        Gets a vectorized version of the query, gets the postings associated with
        each term in the query, gets the dictionary of documents who contain tokens
        in the query, and then gets the final listing of the 10 highest ranked documents
        for the query using the previous 3 results. These 10 documents are then written to a file
    """
    print "positional"
    phrases = [i for i in query if i.count(" ")]
    words = get_posts(di,po,syn)
    stops = set(stopwords.words("english"))
    pdocs = {}
    phrase_count = {}
    final = []
    docs = []
    f = []
    for i in words:
        li = list(set([j[0] for j in words[i]]))
        final.append(li)
    
    for i in phrases:
        q = i.split(" ")
        syn_query = query2syn_query([i for i in q if i not in stops])
        li = get_positional_posts(di, po, syn_query)
        final.append(li)

    for i in range(len(final)):
        for j in final[i]:
            if i >= len(words):
                phrase_count[j] = phrase_count.get(j,0)+1
            pdocs[j] = pdocs.get(j,0)+1
            if pdocs[j] == len(query):
                 f.append(str(j))
    for doc in pdocs:
        docs.append((str(doc), pdocs[doc], phrase_count.get(doc,0)))
    docs = sorted(docs, key = lambda x: x[1], reverse = True)
    docs = sorted(docs, key = lambda x: x[2], reverse = True)
    out.write(" ".join([i[0] for i in docs])+"\n")

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
        Gets the postings list for each unique token(and its synonyms) in 
        the positional phrase and only returns documents that has every
        token in the positional phrase consecutively
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

        #goes through each synonym and merges word positions
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

    #only returns documents that contain the exact positional phrase
    for i in docs:
        if len(docs[i])==count:
            li=[0]*count
            for j in docs[i]:
                li[ind[j]]=docs[i][j]
            if present(li, count):
                final.append(i)
    return final

def for_term(term, term_pos=None):
    """
        Given a word, return a list of synonyms
    """
    if term_pos == 'NN':
        search_poses = [ wn.NOUN, wn.VERB, wn.ADJ ]
    elif term_pos == 'VB':
        search_poses = [ wn.NOUN, wn.VERB, wn.ADV ]
    elif term_pos == 'JJ':
        search_poses = [ wn.NOUN, wn.ADJ ]
    elif term_pos == 'RB':
        search_poses = [ wn.VERB, wn.ADV ]
    else:
        search_poses = [ wn.VERB, wn.NOUN, wn.ADJ ]

    res = [ term ]
    for pos in search_poses:
        # get similar words for each part-of-speach (up to 3)
        i = 0
        ss = wn.synsets(term, pos=pos)
        for s in ss:
            s_name = s.lemma_names()[0]

            # check if alternate def for given term
            if s_name == term:
                # we need to go deeper!
                j = 0
                for s_prime in s.similar_tos(): # visit alternate def
                    res.append(str(s_prime.lemma_names()[0]))
                    j += 1
                    if j >= 2: break # max 2 from alternate def
            else:
                res.append(str(s_name))

            i += 1
            if i >= 3: break # max 3 from this part-of-speach
    return res

def get(query):
    """
        Given a query, return a list of lists of likely synonyms
    """
    query = [i for i in query if not i.count(" ")]
    query = nltk.pos_tag(query)
    res = []
    for tagged_term in query:
        res.append(for_term(tagged_term[0], tagged_term[1]))
    return res

def query2syn_query(query):
    """
        Given list of query terms, return list-of-lists of synonyms
    """
    ps = PorterStemmer()
    syn_query = get(query)
    for syns in syn_query:
       for idx, s in enumerate(syns):
           syns[idx] = str(ps.stem(s))
    return syn_query

def sanitize(phrase):
    """Sanitizes input by removing special characters, numbers, and collapsing whitespace"""
    return re.sub("[!@#$%^&()`:*;,.?/°_-]",'',phrase)

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
        Gets the query from the query file, sanities it, and creates
        a list of terms. If the query is a positional query, then it adds
        both the single terms(if any) and all positional phrases. It also
        returns a flag indicating whether there were any positional queries
    """
    q=[]
    pos=False
    o = open(queries, 'r') 
    stops = set(stopwords.words("english"))
    for line in o:
        query = line.lower().strip()

        #if there are any positional phrases
        if query.count('\"'):
            qu = query.split(" and ")
            qu = [i for i in qu if i not in stops]
            for i in range(len(qu)):

                #adds positional phrases
                if qu[i].count('\"'):
                    f = qu[i].find('\"')+1
                    s = qu[i].find('\"', f)
                    qu[i]= qu[i][f:s].strip()

                #adds single terms
                else:
                    qu[i]=qu[i].strip()
            q.append(qu)
            pos=True

        #if there are no positional phrases
        else:
            qu = sanitize(query).split(" ")
            q.append([i for i in qu if i not in stops])
    o.close()
    return q, pos

def search(dict, post, queries, out):
    """
        Gets the dictionary, gets the queries, gets the lengths, gets the synonyms
        for each term in the query and then evalutes the query. The method used to 
        evaluate the query depends on if the query is positional or not
    """
    print ("testing search queries")
    di = getdict(dict)
    q, pos = getqueries(queries)
    l = getlength()
    p = open(post, 'r')
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