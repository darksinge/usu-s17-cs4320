import os
from os import path, listdir
import re


class Index(object):
    @staticmethod
    def index_file(file_path):
        print("reading from " + file_path)
        try:
            content = ""
            pattern_1 = re.compile(r'\n')
            pattern_2 = re.compile(r'[\W][^a-zA-Z0-9]')
            with open(file_path, 'r') as f:
                for line in f:
                    # temp = re.sub(pattern_1, '\n', line)
                    # temp = re.sub(pattern_2, '', temp)
                    content += line
            return content
        except FileNotFoundError as e:
            print('File not found! ' + e.strerror + ".")
            return ""
        except:
            print("An unknown error occurred!")

    @staticmethod
    def clean(data):
        try:
            if isinstance(data, str):
                return re.sub(r".\"")
        except IOError as e:
            print(e.strerror)
        except:
            print('An unknown error occurred!')


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
