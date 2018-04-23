#!/usr/bin/python
# encoding: utf-8
import _pickle as pickle

def get_postings(word, di, po):
  """
      word to get posting for
    di the dictionary object
    po the postings file 
    returns: [ (docID,wf,[positions,...]),... ]
  """
  resp = di.get(j, [])
  if len(resp) > 0:    
      po.seek(int(resp[1]))
      line=literal_eval(po.readline())
      return line
  else:
      return None
