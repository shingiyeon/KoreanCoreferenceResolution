from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import sys
import json
import argparse


def get_char_vocab(input_filenames, output_filename):
  vocab = set()
  for filename in input_filenames:
    with open(filename) as f:
      for line in f.readlines():
        for sentence in json.loads(line)["sentences"]:
          for word in sentence:
            word = word.split("/")[0]
            vocab.update(word)
  vocab = sorted(list(vocab))
  with open(output_filename, "w", encoding='utf-8') as f:
    for char in vocab:
      f.write("{}\n".format(char))
  print("Wrote {} characters to {}".format(len(vocab), output_filename))

def get_char_vocab_language(input_path, language):
  get_char_vocab([input_path+"{}.{}.jsonlines".format(partition, language) for partition in ("train", "dev")], "char_vocab.{}.txt".format(language))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="")
    parser.add_argument('--input_path', type=str, default=None, metavar = 'input_path', help='')
    parser.add_argument('--file_name', type=str, default=None, metavar = 'file_name', help='')
    args = parser.parse_args()
    input_path = args.input_path
    file_name = args.file_name
       
    get_char_vocab_language(input_path, file_name)
#get_char_vocab_language("english")
#get_char_vocab_language("chinese")
#get_char_vocab_language("arabic")
