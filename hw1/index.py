import os, re, pprint
from os import path, listdir

# needed this here because I worked in both a unix and windows environment
# and on windows the file path delimiter was the "\" and in unix it is the "/"
sys_file_path_delimiter = "/" if os.name is "posix" else "\\"


# Class that color prints to the terminal, because why not?!
HEADER = '\033[95m'
OKBLUE = '\033[94m'
OKGREEN = '\033[92m'
WARNING = '\033[93m'
FAIL = '\033[91m'
ENDC = '\033[0m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'

# print warning
def printw(s):
    print(WARNING + str(s) + ENDC)

# print error
def printe(s):
    print(FAIL + str(s) + ENDC)

# print success
def prints(s):
    print(OKGREEN + str(s) + ENDC)

# print info
def printi(s):
    print(OKBLUE + str(s) + ENDC)

# print header
def printh(s):
    print(HEADER + str(s) + ENDC)

# pretty print
def printp(s, indent=1):
    pp = pprint.PrettyPrinter(indent=indent)
    pp.pprint(s)

def contains(l, x):
    for value in l:
        if value is x:
            return True
    return False

class Indexer:
    index = {}
    documents = []

    def __init__(self):
        self.index = {}
        self.documents = []

    @staticmethod
    def extract_file(file_path):
        print("reading from " + file_path)
        content = ""
        try:
            with open(file_path, 'r') as f:
                content += Indexer.parse_text(f.read())
        except FileNotFoundError as e:
            print('File not found! ' + e.strerror + ".")
        except Exception as e:
            print(e)
        finally:
            return content

    @staticmethod
    def parse_text(text):
        pattern = re.compile(r'([^\w\n])')
        email_pattern = re.compile(r'[^@]+@[^@]+\.[^@]+')
        new_line_pattern = re.compile(r'(\n\n)+')
        text = re.sub(new_line_pattern, ' $', text)
        words = text.split(" ")
        for i in range(len(words)):
            word = words[i]
            try:
                if "http" in word:
                    continue
                if re.match(email_pattern, word):
                    continue
                if re.match(pattern, word[-1]):
                    words[i] = re.sub(pattern, '', word)
                if re.match(pattern, word[0]):
                    words[i] = re.sub(pattern, '', word)
                words[i] = re.sub(pattern, '', word)

            except Exception as e:
                words[i] = ""
                printw("Warning: " + str(e))

        result = " ".join(words)
        return result

    # def index :: indexes the given files
    def index_docs(self):
        for i in range(len(self.documents)):
            document = self.documents[i].split(" ")
            for word in document:
                if word not in self.index.keys():
                    self.index[word] = [i]
                    if self.index[word] is '':
                        print('WHAT?!?!')
                else:
                    temp = self.index[word]
                    try:
                        if isinstance(temp, list):
                            if not contains(temp, i):
                                temp.append(i)
                            self.index[word] = sorted(temp)
                    except Exception as e:
                        printw(e)
        # if '' in self.index:
        #     del self.index['']

    def add_doc(self, doc):
        if isinstance(doc, str):
            doc.strip()
        self.documents.append(doc)


def main(args):

    # make sure args is present, if not, look for a folder named 'data' in the current directory
    if not args:
        args = '.' + sys_file_path_delimiter + 'data'

    dir_path = path.abspath(args)
    files = listdir(dir_path)

    print("starting indexer...")
    indexer = Indexer()

    content = ""

    for file in files:
        temp = Indexer.extract_file(dir_path + sys_file_path_delimiter + file)
        content += temp
        temp = re.sub(r'([\n])+', ' ', temp).lower()
        f_name = re.sub(r'\.txt', '', file)

        # save parsed contents to file, because why not!
        of = open(os.path.join(path.abspath("." + sys_file_path_delimiter), f_name + "_parsed.txt"), 'w')
        of.seek(0)
        of.write(temp)
        of.close()

        # add document content to indexer
        indexer.add_doc(temp)

    # write parsed content out to file to see what the heck my regex is doing. This is purely for academic reasons.
    of = open(os.path.join(path.abspath("." + sys_file_path_delimiter), 'content.txt'), 'w')
    of.seek(0)
    for c in content:
        of.write(c)
    of.close()

    # index the documents!
    indexer.index_docs()
    printp(indexer.index, 3)


main('data')


