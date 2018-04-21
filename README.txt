This is the README file for A0179332B's submission

== Python Version ==

I'm using Python Version 3.5.2

== General Notes about this assignment ==

Indexing:
------------------------------------------------------

Tokenizes, stems, and case-folds all the tokens in all the files in the given directory, tracking the token occurances in a dictionary of lists. This is then converted to an in-memory dictionary (PtrIndex) that references lists in a file located on disk. THe lists are loaded from disk as needed during searching

Choosing Tokens
------------------------------------------------------

For a given file, I split into sentences, then into words, then stem, then case-fold, then ignore stop-tokens ('.', '-', ',') when they are alone.

Searching:
------------------------------------------------------

Loads the PtrIndex in-memory dictionary created during the indexing stage. This helper class does the loading of postings lists from disk as needed during searches. All of the requested queries are read, parsed, and evaluated line-by-line from the input file. The parser is a recursive-decent parser that creates an abstract syntax tree (AST). This AST is then directly used (in conjunction with the PtrIndex helper) to evaluate the given query. The results of the queries are written line-by-line to the output file.

Handling NOT:
------------------------------------------------------

A special posting list contains all the postings indexed. NOT is done by evaluating <ALL> AND NOT <X>

Posting List On-Disk Format:
------------------------------------------------------

<LEN OF LIST>;<ITEM>,<ITEM>,...\n

The in-memory dictionary points to the first byte of the posting list in the file, and stores the length of the list's line in bytes. This allows the list to be efficiently read with:
    file_pointer.seek(start)
    file_pointer.read(len)
And parsed in one pass

Why Recursive-Decent and Not Shunting-Yard:
------------------------------------------------------

Recursive descent is more intuitive, as it is simply a set of recursive functions, where each function represents a logical block. It also generates an AST that can be essentually directly evaluated. If I had more time, it would have allowed me to create a logical block for AND NOT (using one-token look ahead). This would let me evaluate AND NOT as one O(n+m) function. 

Merging Functions
------------------------------------------------------

I implemented three functions for merging posting lists, which return posting lists. This allows them to be called directly from the AST, working bottom up, to generate the resulting posting list. The three functions are

AND, OR, AND NOT

The implementations can be found in listops


== Files included with this submission ==

index.py     - the root file for indexing
search.py    - the root file for searching
ptrindex.py  - the helper class for managing the on-disk posting lists
tokenizer.py - the helper file for tokenizing queries before parsing them
parser.py    - the helper functions for parsing posting lists from disk, as well as parsing queries
query_ast.py - contains the AST helper classes
listops.py   - contains the helper functions for evaluating queries (AND/OR/AND NOT posting list merging functions)
link.py      - the helper classes for pointer list linked lists

== Statement of individual work ==

Please initial one of the following statements.

[X] I, A0179332B, certify that I have followed the CS 3245 Information
Retrieval class guidelines for homework assignments.  In particular, I
expressly vow that I have followed the Facebook rule in discussing
with others in doing the assignment and did not take notes (digital or
printed) from the discussions.  

[ ] I, A0179332B, did not follow the class rules regarding homework
assignment, because of the following reason:

I suggest that I should be graded as follows:

== References ==


