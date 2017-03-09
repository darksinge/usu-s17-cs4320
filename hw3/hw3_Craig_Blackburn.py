# homework 4
# goal: ranked retrieval, PageRank, crawling
# exports:
#   student - a populated and instantiated ir470.Student object
#   PageRankIndex - a class which encapsulates the necessary logic for
#     indexing and searching a corpus of text documents and providing a
#     ranked result set

# ########################################
# first, create a student object
# ########################################

import ir4320
from bs4 import BeautifulSoup as bs
import requests
from requests.models import PreparedRequest
from pprint import pprint
import numpy
import markupbase   # Should I have used this?
import re

import threading
from multiprocessing.dummy import Pool as ThreadPool


MY_NAME = "Craig Blackburn"
MY_ANUM  = 952632 # put your UID here
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


# our index class definition will hold all logic necessary to create and search
# an index created from a web directory
#
# NOTE - if you would like to subclass your original Index class from homework
# 1 or 2, feel free, but it's not required.  The grading criteria will be to
# call the index_url(...) and ranked_search(...) functions and to examine their
# output.  The index_url(...) function will also be examined to ensure you are
# building the index sanely.

re_url_pattern = re.compile('(http:\/\/|https:\/\/)\w*\.')

class PageRankIndex(object):

    def __init__(self):
        # you'll want to create something here to hold your index, and other
        # necessary data members
        self._index = dict()

        # _documents: dictionary containing document meta data. Example:
        #
        # documents = {
        #   "http://doc_01.com": {
        #       "links": ["doc_2"],
        #       "content": "I like <a href="http://doc_2.com">cats</a>."
        #       "anchors": [
        #           ("http://doc_2.com", "cats")
        #       ],
        #       "page_rank": 1.0
        #   },
        #   "http://doc_2.com": {...}
        # }
        self._documents = dict()
        self._document_matrix = list()


    # index_url( url )
    # purpose: crawl through a web directory of html files and generate an
    #   index of the contents
    # preconditions: none
    # returns: num of documents indexed
    # hint: BeautifulSoup and urllib2 s
    # parameters:
    #   url - a string containing a url to begin indexing at
    def index_url(self, url):
        import time
        start_time = time.time()
        # scrape data from websites starting at root url
        self.crawl_web_graph(url)
        end_time = time.time()

        total_time = end_time - start_time
        print("\n-----\nTook %f seconds to crawl %i websites!\n-----" % (float(total_time), len(list(self._documents.keys()))))

        # build index
        for key in self._documents:
            content = self._documents[key]['content']
            tokens = self.tokenize(content)
            for token in tokens:
                if token not in self._index:
                    self._index[token] = [key]
                else:
                    self._index[token].append(key)
        # print("Index: ")
        # pprint(self._index)

        # create a document matrix
        self.construct_link_matrix()

        # calculate page rank score for web graph
        self.calc_page_rank()

        return 0

    def crawl_web_graph(self, url):
        # if url already exists in indexed documents, return
        if url in self._documents:
            return

        # Uncomment below code to limit number of pages indexed... otherwise it could keep going for a llllooonnngggg time
        #
        # if len(list(self._documents.keys())) > 50:
        #     return

        # make HTTP request to url and get document content
        try:
            request = requests.get(url, allow_redirects=False)
        except Exception:
            return

        # return if redirects occurred (not caught by `allow_redirects=False`)
        if len(request.history) > 0:
            return

        # return if HTTP status is not 200
        if not request.ok:
            return

        print("Indexing new document (#%i) %s" % (len(list(self._documents.keys())), url))

        content = bs(request.text, 'html.parser')

        self._documents[url] = {
            'content': '',
            'anchors': [],
            'page_rank': 0
        }

        self._documents[url]['content'] = content.get_text()

        # extract out-links
        links = content.find_all('a')

        # if no links are found, consider page as leaf document
        if links is None:
            return

        # get anchors links, and just for fun, get the anchor text too (although I don't think we use that for this assignment... I hope...)
        anchors = []
        for link in links:
            anchor_tag = link.string
            anchor_link = link.get('href')

            if anchor_link is None or anchor_tag is None:
                continue

            if re_url_pattern.match(anchor_link) is None:
                base_link = url.rsplit('/', 1)[0]
                if base_link[-1] == '/':
                    base_link += anchor_link
                else:
                    base_link += '/' + anchor_link
                anchor_link = base_link

            if self.is_valid_url(anchor_link):
                anchors.append((anchor_tag, anchor_link))

        self._documents[url]['anchors'] = anchors

        # continue crawling web graph recursively until all pages have been visited
        for anchor in anchors:
            thread = threading.Thread(target=self.crawl_web_graph(anchor[1]))
            thread.start()


    # L: The link matrix of document anchors
    # P: The probability matrix
    # T: The Transition Probability Matrix
    # R: The converged matrix of T
    def calc_page_rank(self):
        L = self._document_matrix

        # L = [[0, 0, 1, 0, 1, 0],
        #      [1, 0, 0, 0, 1, 0],
        #      [0, 1, 0, 1, 0, 1],
        #      [0, 0, 0, 1, 0, 0],
        #      [1, 0, 0, 1, 0, 0],
        #      [1, 0, 0, 0, 0, 0]]

        # print("\nLink Matrix:")
        # pprint(L)


        P = self.calc_probability_matrix(L)
        # print("\nProbability Matrix:")
        # pprint(P)

        T = self.calc_transition_matrix(P)

        # print("\nTransition Probability Matrix:")
        # pprint(T)

        # Create 1xn matrix where n = len(T)
        R = [1] + [0 for _ in range(len(T) - 1)]
        tolerance = 0.0001
        converged = False
        iteration_count = 0
        while not converged and iteration_count < 1000:
            previous_R = numpy.dot(R, T).tolist()
            converged = True
            for i in range(len(R)):
                cur_tol = abs(abs(R[i]) - abs(previous_R[i]))
                if cur_tol > tolerance:
                    converged = False
            iteration_count += 1
            if iteration_count == 100: converged = False
            R = previous_R

        if converged:
            print("\nPageRank Matrix Converged! PR -> " + str(R))
            print("Iterations taken to convergence: %i" % iteration_count)
        else:
            print("\nPageRank Matrix failed to converge within 100 iterations, ended with PR -> " + str(R))
        print("Sum of PageRank Matrix: " + str(numpy.sum(R)) + "\n")

        self._page_rank = []

        # sort keys to maintain a level of order in PageRank scores list
        keys = list(self._documents.keys())
        keys.sort()
        for i in range(len(keys)):
            self._page_rank.append((keys[i], R[i]))

        self._page_rank.sort(key=lambda x: x[1], reverse=True)

        print("---------------\nPage Ranks: ")
        for page in self._page_rank:
            print(page[0] + ": " + str(page[1]))
        print("---------------\n")
        return R


    def get_request(self, url):
        try:
            return requests.get(url)
        except requests.ConnectionError:
            print('ERROR: Connection Error, failed to get response from "' + url +'"')
        except requests.RequestException:
            print('Error: Request Exception (most likely malformed URL) to "' + url + '"')
        except Exception:
            print('ERROR: An unknown error occurred making an HTTP request to "' + url + '"')
        return None

    def is_valid_url(self, url):
        try:
            PreparedRequest().prepare_url(url, None)
            return True
        except Exception:
            return False

    def construct_link_matrix(self):
        matrix = []
        docs = self._documents
        keys = list(docs.keys())

        # sort keys to maintain a level of order in PageRank scores list
        keys.sort()

        for key in keys:
            links = [anchor[1] for anchor in self._documents[key]['anchors']]
            if links is None: continue

            intersection = set(links).intersection(set(keys))

            row = []
            for key in keys:
                if key in intersection:
                    row.append(1)
                else:
                    row.append(0)
            matrix.append(row)

        self._document_matrix = matrix


    # P: a probability matrix
    # returns: a matrix created by numpy.matrix(M)
    def calc_transition_matrix(self, P, alpha_val=0.9):
        n = len(P)
        teleporting_matrix = [[(1/n) for _ in range(n)] for _ in range(n)]
        P = numpy.multiply((1-alpha_val), P)
        teleporting_matrix = numpy.multiply(alpha_val, teleporting_matrix)
        return numpy.add(P, teleporting_matrix).tolist()


    def calc_probability_matrix(self, P):
        for i in range(len(P)):
            row_sum = numpy.sum(P[i])
            for j in range(len(P[i])):
                if row_sum > 0:
                    P[i][j] = P[i][j] / row_sum
                else:
                    P[i][j] = 0
        return P

    # tokenize( text )
    # purpose: convert a string of terms into a list of terms
    # preconditions: none
    # returns: list of terms contained within the text
    # parameters:
    #   text - a string of terms
    def tokenize(self, text):
        text = re.split('[\W_]', text.lower())
        tokens = [t for t in text if len(t) > 0]
        tokens = set(tokens)
        return list(tokens)

    # ranked_search( text )
    # purpose: searches for the terms in "text" in our index and returns
    #   AND results for highest 10 ranked results
    # preconditions: .index_url(...) has been called on our corpus
    # returns: list of tuples of (url,PageRank) containing relevant
    #   search results
    # parameters:
    #   text - a string of query terms
    def ranked_search(self, text):
        tokens = self.tokenize(text)
        retrieved_documents = []
        for token in tokens:
            if token in self._index:
                retrieved_documents.append(self._index[token])

        intersection = []
        for doc_list in retrieved_documents:
            if len(intersection) == 0:
                intersection = doc_list
            else:
                intersection = list(set(doc_list).intersection(set(intersection)))

        ranked_results = []
        for doc_id in intersection:
            ranked_results.append((doc_id, self.get_page_rank_score(doc_id)))
        ranked_results.sort(key=lambda x: x[1], reverse=True)
        return ranked_results

    def get_page_rank_score(self, doc_id):
        for page in self._page_rank:
            if page[0] == doc_id:
                return page[1]
        return 0

# now, we'll define our main function which actually starts the indexer and
# does a few queries
def main(args):
    print(student)
    index = PageRankIndex()
    url = 'http://digital.cs.usu.edu/~kyumin/cs4320/new10/index.html'
    index.index_url(url)
    search_queries = [
       'undersoil resolutioner trinitroxylene', 'palatial', 'college ', 'palatial college', 'college supermarket', 'famous aggie supermarket'
        ]
    for q in search_queries:
        results = index.ranked_search(q)
        print("searching: %s -- results: %s" % (q, results))


# this little helper will call main() if this file is executed from the command
# line but not call main() if this file is included as a module
if __name__ == "__main__":
    import sys
    main(sys.argv)

