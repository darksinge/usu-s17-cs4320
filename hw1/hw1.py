# homework 1
# goal: tokenize, index, boolean query
# exports: 
#   student - a populated and instantiated ir4320.Student object
#   Index - a class which encapsulates the necessary logic for
#     indexing and searching a corpus of text documents


# ########################################
# first, create a student object
# ########################################

import ir4320
import PorterStemmer
import indexHelper
import os

MY_NAME = "Craig Blackburn"
MY_ANUM = 952632  # put your A number here without 'A'
MY_EMAIL = "craig.blackburn@usu.edu"

# the COLLABORATORS list contains tuples of 2 items, the name of the helper
# and their contribution to your homework
COLLABORATORS = []

# Set the I_AGREE_HONOR_CODE to True if you agree with the following statement
# "An Aggie does not lie, cheat or steal, or tolerate those who do."
I_AGREE_HONOR_CODE = True

# this defines the student object
student = ir4320.Student(
    MY_NAME,
    MY_ANUM,
    MY_EMAIL,
    COLLABORATORS,
    I_AGREE_HONOR_CODE
)


# ########################################
# now, write some code
# ########################################

# helper function index_of(l, v) where l is a list and v is an object
# returns index of v in l or -1 if v is not in l
# if truthy is True, will return a boolean value instead of the index
def index_of(l, v, truthy=False):
    if isinstance(l, list):
        try:
            index = l.index(v)
            if not truthy:
                return index
            else:
                return True
        except ValueError:
            if not truthy:
                return -1
            else:
                return False


# our index class definition will hold all logic necessary to create and search
# an index created from a directory of text files
class Index(object):
    def __init__(self):
        # _inverted_index contains terms as keys, with the values as a list of
        # document indexes containing that term
        self._inverted_index = {}
        # _documents contains file names of documents
        self._documents = []
        # example:
        #   given the following documents:
        #     doc1 = "the dog ran"
        #     doc2 = "the cat slept"
        #   _documents = ['doc1', 'doc2']
        #   _inverted_index = {
        #      'the': [0,1],
        #      'dog': [0],
        #      'ran': [0],
        #      'cat': [1],
        #      'slept': [1]
        #      }

    # index_dir( base_path )
    # purpose: crawl through a nested directory of text files and generate an
    #   inverted index of the contents
    # preconditions: none
    # returns: num of documents indexed
    # hint: glob.glob()
    # parameters:
    #   base_path - a string containing a relative or direct path to a
    #     directory of text files to be indexed
    def index_dir(self, base_path):

        # get full file paths
        dir_path = os.path.abspath(base_path)
        files = os.listdir(dir_path)

        # grab contents of files
        for file in files:
            doc = {}
            doc['name'] = file
            doc['content'] = indexHelper.process_file(base_path, file)
            self._documents.append(doc)

        # tokenize documents
        for i in range(len(self._documents)):
            self._documents[i]['tokens'] = indexHelper.tokenize(self._documents[i]['content'])

        # stem tokens
        for i in range(len(self._documents)):
            self._documents[i]['tokens'] = self.stemming(self._documents[i]['tokens'])

        # build inverted_index
        index = {}
        for i in range(len(self._documents)):
            for token in self._documents[i]['tokens']:
                if token not in index.keys():
                    index[token] = [i]
                else:
                    l = index[token]
                    if isinstance(l, list):
                        pos = index_of(l, i)
                        if pos is -1:
                            l.append(i)
                            l.sort()
                            index[token] = l

        self._inverted_index = index

        # print(json.dumps(self._inverted_index, indent=3))
        return len(files)

    # tokenize( text )
    # purpose: convert a string of terms into a list of tokens.        
    # convert the string of terms in text to lower case and replace each character in text, 
    # which is not an English alphabet (a-z) and a numerical digit (0-9), with whitespace.
    # preconditions: none
    # returns: list of tokens contained within the text
    # parameters:
    #   text - a string of terms
    def tokenize(self, text):
        return indexHelper.tokenize(text)

    # purpose: convert a string of terms into a list of tokens.        
    # convert a list of tokens to a list of stemmed tokens,     
    # preconditions: tokenize a string of terms
    # returns: list of stemmed tokens
    # parameters:
    #   tokens - a list of tokens
    def stemming(self, tokens):
        stemmed_tokens = []
        porter = PorterStemmer.PorterStemmer()
        for i in range(len(tokens)):
            stemmed_tokens.append(porter.stem(tokens[i], 0, len(tokens[i]) - 1))
        return stemmed_tokens

    # boolean_search( text )
    # purpose: searches for the terms in "text" in our corpus using logical OR or logical AND. 
    # If "text" contains only single term, search it from the inverted index. If "text" contains three terms including "or" or "and", 
    # do OR or AND search depending on the second term ("or" or "and") in the "text".  
    # preconditions: _inverted_index and _documents have been populated from
    #   the corpus.
    # returns: list of document names containing relevant search results
    # parameters:
    #   text - a string of terms
    def boolean_search(self, text):
        results = []

        queries = text.split(' ')

        is_or = False
        is_and = False
        for query in queries:
            if query == str('OR'):
                is_or = True
                continue
            elif query == str('AND'):
                is_and = True
                continue

            stem_query = self.stemming(self.tokenize(query))
            for token in stem_query:
                if token in self._inverted_index.keys():
                    doc_ids = self._inverted_index[token]
                    results.append(self.get_doc_name(doc_ids))

        if is_or:
            q1_docs = results[0]
            q2_docs = results[1]
            results = q1_docs
            for doc in q2_docs:
                if not index_of(results, doc, truthy=True):
                    results.append(doc)
        elif is_and:
            q1_docs = results[0]
            q2_docs = results[1]
            results = []
            for doc in q1_docs:
                if index_of(q2_docs, doc, truthy=True):
                    results.append(doc)

        # flatten results
        flat = []
        for value in results:
            if isinstance(value, list):
                for val in value:
                    flat.append(val)
            else:
                flat.append(value)
        results = sorted(flat)
        return results

    def found(self, token, document):
        if token in self._inverted_index.keys():
            doc_ids = self._inverted_index[token]
            if isinstance(doc_ids, list):
                for pos in doc_ids:
                    if document is self._documents[pos]['name']:
                        return True
        return False

    def get_doc_name(self, doc_ids):
        names = []
        for i in doc_ids:
            names.append(self._documents[i]['name'])
        return names


# now, we'll define our main function which actually starts the indexer and
# does a few queries
def main(args):
    print(student)
    index = Index()
    print("starting indexer")
    num_files = index.index_dir('data/')
    print("indexed %d files" % num_files)
    for term in ('football', 'mike', 'sherman', 'mike OR sherman', 'mike AND sherman'):
        results = index.boolean_search(term)
        print("searching: %s -- results: %s" % (term, ", ".join(results)))


# this little helper will call main() if this file is executed from the command
# line but not call main() if this file is included as a module
if __name__ == "__main__":
    import sys

    main(sys.argv)

