import os
from os import path, listdir
import re


class Index(object):
    def __init__(self):
        self.index_items = {}

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

    def index(self, data, doc_id):
        for item in data:
            if self.index_items[item] is None:
                self.index_items[item] = [doc_id]
            else:
                docs = list(self.index_items[item])
                self.index_items[item] = docs.append(doc_id)


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
        foo = Index.extract_file(dir_path + f_delimiter + file)
        content += foo

    # write parsed content out to file to see what the heck my regex is doing. This is purely for academic reasons.
    of = open(os.path.join(path.abspath("." + f_delimiter), 'content.txt'), 'w')
    of.seek(0)
    for c in content:
        of.write(c)
    of.close()

    # grab parsed content, then index
    content = re.sub(r'([\n\',\-])+', ' ', content)
    print(content)



main('data')
