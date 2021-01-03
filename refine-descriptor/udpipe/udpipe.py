#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import logging
import csv
import os

from functools import reduce

from tqdm import tqdm
from ufal.udpipe import Model, Sentence, ProcessingError


def main():
  logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] - %(message)s",
    datefmt="%H:%M:%S")
  
  args = read_configuration()

  if not valid_file_for_write(args["output"], args["rewrite"]):
    logging.warning("Existing output CSV file cannot be overrided.")
    return 0

  logging.info("Loading and merging descriptors ... [from %s]" % args["input"])
  descriptors = load_descriptors(args["input"], args["header"])

  if descriptors is None:
    logging.error("Error occured during descriptors reading.")
    return 1
  if len(descriptors) == 0:
    logging.warning("No descriptors were loaded.")
    return 0

  logging.info("Loading model %s" % args["model"])
  model = Model.load(args["model"])
  if not model:
    logging.error("Cannot load model from file '%s'." % args["model"])
    return 2
  logging.info("Model loaded...")

  if not udpipe_descriptors(model, descriptors, args["filter"]):
    logging.error("Error occurred during UDPipe.")
    return 3

  logging.info("Writing descriptors into file %s ..." % args["output"])
  if not save_descriptors(args["output"], args["rewrite"], descriptors):
    logging.error("File cannot be saved.")
    return 3
  
  logging.info("Finished ...")
  return 0


def udpipe_descriptors(model, descriptors, filter_words=False):
  tokenizer = model.newTokenizer(model.DEFAULT)
  if not tokenizer:
    raise Exception("The model does not have a tokenizer")
  error = ProcessingError()

  for d in tqdm(descriptors):
    lemmas = []
    for s in descriptors[d]:
      tokenizer.setText(s)

      sentences = []
      sentence = Sentence()
      while tokenizer.nextSentence(sentence, error):
        model.tag(sentence, model.DEFAULT)
        sentences.append(sentence)
        sentence = Sentence()
      
      if error.occurred():
        raise Exception(error.message)

      words = reduce(lambda x, y: x+y, [[( w.lemma, w.upostag ) for w in s.words] for s in sentences], [])
      if not filter_words:
        words = list(map(lambda w: w[0], filter(lambda w: w[1] not in ['<root>'], words)))
      else:
        words = list(map(lambda w: w[0], filter(lambda w: w[1] in ['NOUN', 'ADJ', 'VERB', 'ADV', 'PROPN', 'X'], words)))
      lemmas.append(reduce(lambda x, y: x + " " + y, words) if len(words) > 0 else "")  
      

    descriptors[d] = lemmas

  return not error.occurred()

def read_configuration():
  parser = argparse.ArgumentParser(
    description="Calculate threshold from a CSV dense distance matrix file.")
  
  parser.add_argument("-i", "--in", "--input",
    type=str, dest="input", required=True,
    help="Path to input CSV file containing descriptors.")
  parser.add_argument("--header",
    action="store_true", dest="header", required=False, default=False,
    help="Determines if the input CSV file has header.")

  parser.add_argument("-o", "--out", "--output",
    type=str, dest="output", required=True,
    help="Path to output CSV file.")
  parser.add_argument("--rewrite",
    action="store_true", dest="rewrite", required=False, default=False,
    help="Rewrite existing output CSV file.")

  parser.add_argument("-m", "--model",
    type=str, dest="model", required=True,
    help="Path to UDPIPE model")
  parser.add_argument("-f", "--filter",
    action="store_true", dest="filter", required=False, default=False,
    help="Filter only nouns, verbs, adjectives and adverbs.")
  
  args = vars(parser.parse_args())

  return args


def load_descriptors(descriptors_path, header):
  if not valid_file_for_read(descriptors_path):
    return None
  
  with open(descriptors_path, encoding="UTF-8") as input_stream:
    reader = csv.reader(input_stream)

    if header:
      logging.debug("Skipping header info ...")
      next(reader, None)

    descriptors = {}
    for row in reader:
      if not row[0] in descriptors:
        descriptors[row[0]] = []
      descriptors[row[0]].extend(row[1:])
    return descriptors


def valid_file_for_read(file_path):
  if not os.path.exists(file_path):
    return False
  if not os.path.isfile(file_path):
    return False
  return True


def save_descriptors(descriptors_path, rewrite, descriptors):
  if not valid_file_for_write(descriptors_path, rewrite):
    return False
  
  with open(descriptors_path, "w", encoding="UTF-8", newline='') as output_stream:
    writer = csv.writer(output_stream)
    for d in descriptors:
      writer.writerow( [ d ] + descriptors[d] )
    return True


def valid_file_for_write(file_path, rewrite = False):
  if not os.path.exists(file_path):
    return True
  if not os.path.isfile(file_path):
    return False
  if rewrite:
    return True
  return False


if __name__ == "__main__":
  exit(main())
