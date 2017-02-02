import os
from os import path, listdir
import re


class Index(object):
    def __init__(self):
        self.index_items = {}
        self.documents = []

    @staticmethod
    def extract_file(file_path):
        print("reading from " + file_path)
        content = ""
        try:
            with open(file_path, 'r') as f:
                content += Index.parse_text(f.read())
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
                print(e)

        result = " ".join(words)
        return result

    # indexes the given files.
    def index(self):
        for i in range(len(self.documents)):
            pass


    def add_doc(self, doc):
        self.documents.append(doc)


def main(args):
    index = Index()
    if not args:
        args = './data'

    if isinstance(args, list):
        args = args.pop()

    dir_path = path.abspath(args)
    files = listdir(dir_path)

    print("starting indexer...")

    content = ""
    f_delimiter = "/" if os.name is "posix" else "\\"
    for file in files:
        temp = Index.extract_file(dir_path + f_delimiter + file)
        content += temp
        temp = re.sub(r'([\n])+', ' ', temp).lower()
        f_name = re.sub(r'\.txt', '', file)

        # save parsed contents to file, because why not!
        of = open(os.path.join(path.abspath("." + f_delimiter), f_name + "_parsed.txt"), 'w')
        of.seek(0)
        of.write(temp)
        of.close()

        # add document content to indexer
        index.add_doc(temp)

    # write parsed content out to file to see what the heck my regex is doing. This is purely for academic reasons.
    # of = open(os.path.join(path.abspath("." + f_delimiter), 'content.txt'), 'w')
    # of.seek(0)
    # for c in content:
    #     of.write(c)
    # of.close()

    # index grabbed documents
    index.index()



main('data')
