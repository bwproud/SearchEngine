Student Number: A0179356N, JOHN_ESPENHAHN
Email: E0268725@u.nus.edu, JOHN_ESPENHAHN@u.nus.edu

== Python Version ==

We're using Python Version 2.7 for this assignment.

== General Notes about this assignment ==

GENERAL OVERVIEW:

This program performs the indexing step by going through the directory of files to index and one by one indexing the individual files. This consists of going through every word, tokenizing it, and adding it to an in-memory dictionary file if its not a stop word or a number. We also strip the sentences for punctuation to minimize the postings list. In addition we store the document frequency of each word, calculate and store the term frequency of each word for each document using 1+log(tf), and calculate and store the length of each document for use in the searching steps. We then output this to a dictionary file, postings list file, and document length file. The difference between this indexer and the indexer in hw3 is that the indexer is now parallelized to greatly reduce runtime(as was necessary with the large legal corpus) and we now also store the position of words inside of each document. This is used in positional queries.

The searching step is performed as such: first we get the document lengths, dictionary of tokens, and queries from input files and store these in memory. After we have the query, we generate the synonyms for every token in the query to be used in its evalution. This is a form of query expansion that is described in greater detail in BONUS.docx. Then we determine if the query is positional or not. If the query is positional then we get all the documents that contain the individual terms(or their synonyms) in a positional query (the "and" seperated terms) and all the documents that contain the phrasal queries (the quoted portions of positional queries) and then rank the resulting documents based on how many terms/phrases they contain using a modified radix sort. If the query is nonpositional then we perform a series of steps to act as a query parser as described in lecture. We first generate a set of queries based off the original query. For example, if the original query was "good grade exchange scandal" then the resulting set would be 
["good grade exchange scandal", 
"good grade exchange", 
"grade exchange scandal",
"good grade",
"grade exchange",
"exchange scandal"].

We then use this set of queries and perform positional queries on each query and get all the documents that contain that phrase and add it to the result set if the positional query didn't return too many results(which would indicate it was a common phrase). The queries are structured into levels where a level contains all the query permutations with the same number of words; these levels are sorted by term rarity so that documents with phrases that are more rare appear earlier in the result set. Finally after performing all the positional queries, an initial tf-idf evaluation of the query is performed and we use the most relevant documents from these results to hone the query vector as Rocchios algorithm mandates and then we perform a final tf-idf evaluation and add the results. The tf-idf evaluation process is as follows:

We evaluate each query by vectorizing the query(described below), getting the postings list for each token(and the synonyms of that token) in the query, and then getting a listing of every document that contains one or more of the query tokens using the postings list retrieved earlier. A minimum window algorithm is then performed on each candidate document to see what the minimum window is that covers every relevant term in the query. By the end of this last step, each potential document will be its own vector which has the normalized term frequency of each query token that appears inside of it. A cross product is then performed between every document vector and the query vector to calculate each documents ranking. Finally a radix sort is performed which ranks documents highest that contain the most words, then those that have the smallest window among those words, and then by the tf-idf ranking.

A query is vectorized by getting the term frequencies of each token in the query,
weighting these tokens, multiplying the weighted term frequency with the inverse document frequency, and then normalizing the resulting vector.


NOTES:
I perform basic input sanitation to make the postings list smaller by removing punctuation and not allowing numbers or stop words.

I only add a query token to the query vector if it can be found in the dictionary as it’s weight is going to be zero in any case if it can’t be found in any document.

I only make vectors for documents that contain one or more of the query tokens, and as I do this using a dictionary, the size of each candidate vector varies according to how many query tokens it contains. This cuts down on wasted space.

Performance Experiments:
Right now our search.py can accurately fulfill queries very accurately and within a minute for both positional and nonpositional queries. Adding in the query parsing step for nonpositional queries greatly increased the runtime but also increased accuracy. Including the synonyms as part of the query expansion had a great effect on the overall search results, but unfortunately including rocchios algorithm did not have the same performance gains.


== Files included with this submission ==

index.py: Indexes a collection of files passed in as input and stores them in dictionary, length, and postings files.
search.py: Takes in the dictionary, length, and postings file created in the indexing stage and uses them to fulfill queries and output the results

== Statement of individual work ==

Please initial one of the following statements.

[X] I, A0179356N, certify that I have followed the CS 3245 Information
Retrieval class guidelines for homework assignments.  In particular, I
expressly vow that I have followed the Facebook rule in discussing
with others in doing the assignment and did not take notes (digital or
printed) from the discussions.  

[X] I, JOHN_ESPENHAHN, certify that I have followed the CS 3245 Information
Retrieval class guidelines for homework assignments.  In particular, I
expressly vow that I have followed the Facebook rule in discussing
with others in doing the assignment and did not take notes (digital or
printed) from the discussions.  


== We suggest that we should be graded as follows: ==

We should get full marks as we completed the assignment, and got it running very effectively and relatively efficiently.
