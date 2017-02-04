import os
import re

# needed this here because I worked in both a unix and windows environment
# and on windows the file path delimiter was the "\" and in unix it is the "/"
FP_DIL = "/" if os.name is "posix" else "\\"


# print warning
def printw(s):
    print('\033[93m' + str(s) + '\033[0m')


def contains(l, x):
    for value in l:
        if value is x:
            return True
    return False


def tokenize(doc_text):
    try:
        r_tokens = re.sub(r'[\W_]', ' ', doc_text).lower()
        tokens = re.sub(r'\s\s+', ' ', r_tokens).split(' ')
    except Exception as e:
        printw(e)
        tokens = doc_text.lower().split(' ')
    # print(tokens)
    return tokens


def process_file(base_path, file_name):
    dir_path = os.path.abspath(base_path)
    file_path = dir_path + FP_DIL + file_name
    content = ""
    try:
        with open(file_path, 'r') as f:
            content += f.read()
    except FileNotFoundError as e:
        print('File not found! ' + e.strerror + ".")
    except Exception as e:
        print(e)
    finally:
        return content

