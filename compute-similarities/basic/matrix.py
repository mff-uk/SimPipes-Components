#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import csv
import argparse
import logging
import numpy as np
import json

from tqdm import tqdm

from linda.descriptors import descriptor_factory
from linda.distances import distance_factory


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
  descriptors = load_descriptors_type(args["input"], args["input_header"], args["input_column"], descriptor_factory(args["type"]))
  if descriptors is None:
    logging.error("Error occured during descriptors loading.")
    return 1
  if len(descriptors) == 0:
    logging.warning("No descriptors were loaded.")
    return 0
  
  logging.info("Computing the distances for ...")
  distances = distance_matrix(descriptors, distance_factory(args["distance"]))

  if args["output"].endswith(".npy"):
    np.save(args["output"], np.array(distances))
  elif args["output"].endswith(".csv"):
    np.savetxt(args["output"], np.array(distances), delimiter=',')
  elif args["output"].endswith(".json"):
    with open(args["output"], "w") as output_stream:
      output_stream.write(json.dumps(distances) + '\n')
  else:
    logging.error("Unknown output format.")
    return 2

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
  parser.add_argument("--input-column",
    action="store_true", dest="input_column", required=False, default=False,
    help="Determines if the input CSV file has first column as header.")

  parser.add_argument("-o", "--out", "--output",
    type=str, dest="output", required=True,
    help="Path to output CSV file.")
  parser.add_argument("--rewrite",
    action="store_true", dest="rewrite", required=False, default=False,
    help="Rewrite existing output CSV file.")

  parser.add_argument("-t", "--type", "--descriptor",
    type=str, dest="type", required=True,
    help="Type of descriptor.")
  parser.add_argument("-d", "--dist", "--distance",
    type=str, dest="distance", required=True,
    help="Distance measure.")
  
  args = vars(parser.parse_args())

  return args


def distance_matrix(descriptors, distance):
  result = []
  for d1 in tqdm(descriptors):
    result.append([ distance(d1, d2) for d2 in descriptors ])
  return result


def load_descriptors_type(input_path, input_header, input_column, convert):
  if not valid_file_for_read(input_path):
    return None
  
  with open(input_path, encoding="UTF-8") as input_stream:
    reader = csv.reader(input_stream)

    if input_header:
      logging.debug("Skipping header info ...")
      next(reader, None)

    descriptors = []
    for row in reader:
      descriptors.append(convert(row[1:] if input_column else row))
    return descriptors


def valid_file_for_read(file_path):
  if not os.path.exists(file_path):
    return False
  if not os.path.isfile(file_path):
    return False
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
