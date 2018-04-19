#!/usr/bin/python
# encoding: utf-8
import _pickle as pickle

def get_postings(word, di, po):
    """
      word to get posting for
      di the dictionary object
      po the postings file
    """
    resp = di.get(word, [])
    if len(resp) > 0:    
        po.seek(int(resp[1]))
        return pickle.load(po)
    else:
        return None