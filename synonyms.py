import nltk
from nltk.corpus import wordnet as wn
from nltk.stem.lancaster import LancasterStemmer
st = LancasterStemmer()

def get(query):
	"""
		Given a query, return a list of lists of likely synonyms
	"""
	query = nltk.pos_tag(query)

	res = []
	for tagged_term in query:
		res.append(for_term(tagged_term[0], tagged_term[1]))

	return res

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