from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import re
import os
import sys
import json
import tempfile
import subprocess
import collections
import argparse
import util
import conll


class DocumentState(object):
  def __init__(self):
    self.doc_key = None
    self.text = []
    self.text_speakers = []
    self.speakers = []
    self.sentences = []
    self.start_times = []
    self.end_times = []
    self.video_npy_files = []
    #self.POS = []
    #self.head_POS = []
    self.constituents = {}
    self.const_stack = []
    self.ners = []
    self.ner_stacks = collections.defaultdict(list)
    self.clusters = collections.defaultdict(list)
    self.coref_stacks = collections.defaultdict(list)
    self.entities = []
    self.entity_stacks = collections.defaultdict(list)

  def assert_empty(self):
    assert self.doc_key is None
    assert len(self.text) == 0
    assert len(self.text_speakers) == 0
    assert len(self.speakers) == 0
    assert len(self.sentences) == 0
    assert len(self.constituents) == 0
    assert len(self.const_stack) == 0
    assert len(self.ners) == 0
    assert len(self.ner_stacks) == 0
    assert len(self.coref_stacks) == 0
    assert len(self.clusters) == 0

  def assert_finalizable(self):
    assert self.doc_key is not None
    assert len(self.text) == 0
    assert len(self.text_speakers) == 0
    assert len(self.speakers) > 0
    assert len(self.sentences) > 0
    assert len(self.constituents) > 0
    assert len(self.const_stack) == 0
    assert len(self.ner_stack) == 0
    assert all(len(s) == 0 for s in self.coref_stacks.values())

  def span_dict_to_list(self, span_dict):
    return [(s,e,l) for (s,e),l in span_dict.items()]

  def finalize(self):
    merged_clusters = []
    for c1 in self.clusters.values():
      existing = None
      for m in c1:
        for c2 in merged_clusters:
          if m in c2:
            existing = c2
            break
        if existing is not None:
          break
      if existing is not None:
        print("Merging clusters (shouldn't happen very often.)")
        existing.update(c1)
      else:
        merged_clusters.append(set(c1))
    merged_clusters = [list(c) for c in merged_clusters]
    all_mentions = util.flatten(merged_clusters)
    assert len(all_mentions) == len(set(all_mentions))
    
    return {
      "doc_key": self.doc_key,
      "sentences": self.sentences,
      "speakers": self.speakers,
      "constituents": self.span_dict_to_list(self.constituents),
      "ner": self.ners,
      "clusters": merged_clusters,
      "start_times": self.start_times,
      "end_times": self.end_times,
      "video_npy_files": self.video_npy_files,
      "entities": self.entities
    #"POS" : self.POS,
    #"head_POS" : self.head_POS
    }

def normalize_word(word, language):
  if language == "arabic":
    word = word[:word.find("#")]
  if word == "/." or word == "/?":
    return word[1:]
  else:
    return word

def handle_bit(word_index, bit, stack, spans):
  asterisk_idx = bit.find("*")
  if asterisk_idx >= 0:
    open_parens = bit[:asterisk_idx]
    close_parens = bit[asterisk_idx + 1:]
  else:
    open_parens = bit[:-1]
    close_parens = bit[-1]

  current_idx = open_parens.find("[")
  while current_idx >= 0:
    next_idx = open_parens.find("[", current_idx + 1)
    if next_idx >= 0:
      label = open_parens[current_idx + 1:next_idx]
    else:
      label = open_parens[current_idx + 1:]
    stack.append((word_index, label))
    current_idx = next_idx

  for c in close_parens:
    #assert c == ")"
    open_index, label = stack.pop()
    current_span = (open_index, word_index)
    print(current_span)
    """
    if current_span in spans:
      spans[current_span] += "_" + label
    else:
      spans[current_span] = label
    """
    spans[current_span] = label

def handle_line(line, document_state, language, labels, stats):
  begin_document_match = re.match(conll.BEGIN_DOCUMENT_REGEX, line)
  if begin_document_match:
    document_state.assert_empty()
    document_state.doc_key = conll.get_doc_key(begin_document_match.group(1), begin_document_match.group(2))
    print(document_state.doc_key)
    return None
  elif line.startswith("#end document"):
    #document_state.assert_finalizable()
    finalized_state = document_state.finalize()
    stats["num_clusters"] += len(finalized_state["clusters"])
    stats["num_mentions"] += sum(len(c) for c in finalized_state["clusters"])
    labels["{}_const_labels".format(language)].update(l for _, _, l in finalized_state["constituents"])
    #labels["ner"].update(l for _, _, l in finalized_state["ner"])
    return finalized_state
  else:
    row = line.split()
    if len(row) == 0:
      stats["max_sent_len_{}".format(language)] = max(len(document_state.text), stats["max_sent_len_{}".format(language)])
      stats["num_sents_{}".format(language)] += 1
      document_state.sentences.append(tuple(document_state.text))
      del document_state.text[:]
      document_state.speakers.append(tuple(document_state.text_speakers))
      del document_state.text_speakers[:]
      return None
    assert len(row) >= 12

    doc_key = conll.get_doc_key(row[0], row[1])
    word = normalize_word(row[3], language)
    #POS = row[4]
    #head_POS = row[7]
    parse = row[5]
    speaker = row[9]
    ner = row[10]
    st_time = -1 if(row[-4] == 'NOTIME') else int(row[-4])
    en_time = -1 if(row[-3] == 'NOTIME') else int(row[-3])
    video_npy_file = row[-2]
    coref = row[-1]
    entity = row[-5]

    word_index = len(document_state.text) + sum(len(s) for s in document_state.sentences)
    document_state.text.append(word)
    document_state.text_speakers.append(speaker)
    #document_state.POS.append(pos)
    #document_state.head_POS.append(head_POS)
    if (len(document_state.start_times) == 0 or (not (document_state.start_times[-1] == st_time and document_state.end_times[-1] == en_time))):
      document_state.start_times.append(st_time)
      document_state.end_times.append(en_time)
      document_state.video_npy_files.append(video_npy_file)
    #print(word_index, parse)
    #handle_bit(word_index, parse, document_state.const_stack, document_state.constituents)
    #handle_bit(word_index, ner, document_state.ner_stack, document_state.ner)
    #coref_number = 0
    #entity_number = 0
    if coref != "-":
      for segment in coref.split("|"):
        if segment[0] == "(":
          if segment[-1] == ")":
            cluster_id = int(segment[1:-1])
            document_state.clusters[cluster_id].append((word_index, word_index))
            #coref_number += 1
          else:
            cluster_id = int(segment[1:])
            document_state.coref_stacks[cluster_id].append(word_index)
        else:
          cluster_id = int(segment[:-1])
          #print(segment,cluster_id)
          start = document_state.coref_stacks[cluster_id].pop()
          #coref_number += 1
          document_state.clusters[cluster_id].append((start, word_index))
    if entity != "-":
      for segment in entity.split("|"):
        if segment[0] == "<":
          if segment[-1] == ">":
            entity_id = int(segment[1:-1])
            document_state.entities.append((word_index, word_index, entity_id))
            #entity_number += 1
          else:
            entity_id = int(segment[1:])
            document_state.entity_stacks[entity_id].append(word_index)
        else:
          entity_id = int(segment[:-1])
          #print(segment,entity_id)
          start = document_state.entity_stacks[entity_id].pop()
          #entity_number += 1
          document_state.entities.append((start,word_index,entity_id))
    if ner != "*":
        for segment in ner.split("|"):
            if segment[0] == "[":
                if segment[-1] == "]":
                    ner_id = int(segment[1:-1])
                    document_state.ners.append((word_index, word_index, ner_id))
                else:
                    ner_id = int(segment[1:])
                    document_state.ner_stacks[ner_id].append(word_index)
            else:
                ner_id = int(segment[:-1])
                #print(segment, ner_id)
                start = document_state.ner_stacks[ner_id].pop()
                document_state.ners.append((start, word_index, ner_id))


    return None

def minimize_partition(name, language, extension, labels, stats,input_path2, output_path2):
  input_path = "{}{}.{}".format(input_path2, language, extension)
  output_path = "{}{}.jsonlines".format(output_path2, language)
  count = 0
  print("Minimizing {}".format(input_path))
  with open(input_path, "r") as input_file:
    with open(output_path, "w") as output_file:
      document_state = DocumentState()
      for line in input_file.readlines():
        document = handle_line(line, document_state, language, labels, stats)
        if document is not None:
          output_file.write(json.dumps(document))
          output_file.write("\n")
          count += 1
          document_state = DocumentState()
  print("Wrote {} documents to {}".format(count, output_path))

def minimize_language(language, input_path, output_path, labels, stats):
  minimize_partition("", language, "v4_gold_conll", labels, stats, input_path, output_path)
  #minimize_partition("dev", language, "v4_gold_conll", labels, stats)
  #minimize_partition("train", language, "v4_gold_conll", labels, stats)
  #minimize_partition("test", language, "v4_gold_conll", labels, stats)

if __name__ == "__main__":
  parser = argparse.ArgumentParser()

  parser.add_argument('--input_file', type=str, default='data', metavar='input_file', help = 'input_file')
  parser.add_argument('--input_path', type=str, default='./', metavar='input_path', help = 'input_path')
  parser.add_argument('--output_path', type=str, default='./', metavar='output_path', help = 'output_path')
  args = parser.parse_args()
  input_file = args.input_file
  input_path = args.input_path
  output_path = args.output_path

  labels = collections.defaultdict(set)
  stats = collections.defaultdict(int)
  minimize_language(input_file,input_path, output_path, labels, stats)
  for k, v in labels.items():
    print("{} = [{}]".format(k, ", ".join("\"{}\"".format(label) for label in v)))
  for k, v in stats.items():
    print("{} = {}".format(k, v))
