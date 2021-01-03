#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import csv
import argparse
import logging
import numpy as np
import json
import re

from tqdm import tqdm
from functools import reduce

from gensim.models import Word2Vec


def main():
  logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] - %(message)s",
    datefmt="%H:%M:%S")
  
  args = read_configuration()

  if not valid_file_for_write(args["output"], args["rewrite"]):
    logging.warning("Existing output CSV file [%s] cannot be overrided." % args["output"])
    return 0

  logging.info("Loading descriptors ... [from %s]" % args["input"])
  descriptors = load_descriptors(args["input"], args["input_header"])
  if descriptors is None:
    logging.error("Error occured during descriptors loading.")
    return 1
  if len(descriptors) == 0:
    logging.warning("No descriptors were loaded.")
    return 0

  logging.info("Loading vector model ...")
  model = load_model(args["model"])
  if model is None:
    logging.error("Error occurred during model loading.")
    return 2

  logging.info("Computing average vectors for descriptors...")
  vectors = {}
  for d in tqdm(descriptors):
    vector = []
    for content in descriptors[d]:
      vs = list(map(lambda w: model.wv[w] if w in model.wv else model.wv[w.lower()], filter(lambda w: len(w) > 0 and (w in model.wv or w.lower() in model.wv), re.split('[^\w]+', content))))
      if len(vs) > 0:
        vector.append(reduce(lambda x, y: x+y, vs)/len(vs))
    
    vectors[d] = (reduce(lambda x, y: x+y, vector)/len(vector)).tolist() if len(vector) > 0 else []

  logging.info("Saving vector descriptors...")
  save_descriptors(args["output"], args["rewrite"], vectors)

  logging.info("Finished ...")
  return 0


def read_configuration():
  parser = argparse.ArgumentParser(
    description="Calculate distance matrix for input descriptors.")
  
  parser.add_argument("-i", "--in", "--input",
    type=str, dest="input", required=True,
    help="Path to input CSV file containing descriptors.")
  parser.add_argument("--input-header",
    action="store_true", dest="input_header", required=False, default=False,
    help="Determines if the input CSV file has header.")
  
  parser.add_argument("-m", "--model",
    type=str, dest="model", required=True,
    help="Path to Word2Vec model.")

  parser.add_argument("-o", "--out", "--output",
    type=str, dest="output", required=True,
    help="Path to output CSV file.")
  parser.add_argument("--rewrite",
    action="store_true", dest="rewrite", required=False, default=False,
    help="Rewrite existing output CSV file.")
  
  args = vars(parser.parse_args())

  return args


def load_model(model_path):
  return Word2Vec.load(model_path)


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
