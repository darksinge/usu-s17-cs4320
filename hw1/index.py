import os
from os import path, listdir
import re


class Index(object):
    @staticmethod
    def index_file(file_path):
        print("reading from " + file_path)
        try:
            content = ""
            with open(file_path, 'r') as f:
                for line in f:
                    content += parseText(line)
            return content
        except FileNotFoundError as e:
            print('File not found! ' + e.strerror + ".")
        except:
            print("An unknown error occurred!")
        finally:
            return ""

    @staticmethod
    def clean(data):
        try:
            if isinstance(data, str):
                return re.sub(r".\"")
        except IOError as e:
            print(e.strerror)
        except:
            print('An unknown error occurred!')


def parseText(text):
    words = text.split(" ")
    result = ""
    w_pattern = re.compile(r'\W')
    for word in words:
        if "http" in word:
            result += word + " "
            print(word)
        if re.match(w_pattern, word[0]):
            word = word[1:]
        if re.match(w_pattern, word[-1]):
            word = word[:-1]

    result = " ".join(words) + "\n"
    print(result)
    return result


def main(args):
    if not args:
        args = './data'

    if isinstance(args, list):
        args = args.pop()

    dir_path = path.abspath(args)
    files = listdir(dir_path)

    print("starting indexer...")

    content = []
    for file in files:
        content.append(Index.index_file(dir_path + "/" + file))

    of = open(os.path.join(path.abspath('./'), 'content.txt'), 'r+')
    of.seek(0)
    for c in content:
        of.write(c)

    of.close()


main('data')
