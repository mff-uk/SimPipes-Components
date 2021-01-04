#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import logging
import csv
import os

from functools import reduce


def main():
  logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] - %(message)s",
    datefmt="%H:%M:%S")
  
  args = read_configuration()

  if not valid_file_for_write(args["output"], args["rewrite"]):
    logging.warning("Existing output CSV file cannot be overrided.")
    return 0

  logging.info("Loading and left descriptors ... [from %s]" % args["left_input"])
  ldescriptors = load_descriptors(args["left_input"], args["left_header"])

  if ldescriptors is None:
    logging.error("Error occured during left descriptors reading.")
    return 1
  if len(ldescriptors) == 0:
    logging.warning("No left descriptors were loaded.")
    return 0
  
  logging.info("Loading and right descriptors ... [from %s]" % args["right_input"])
  rdescriptors = load_descriptors(args["right_input"], args["right_header"])

  if rdescriptors is None:
    logging.error("Error occured during right descriptors reading.")
    return 1
  if len(rdescriptors) == 0:
    logging.warning("No right descriptors were loaded.")
    return 0

  logging.info("Merging...")
  descriptors = {}
  for key in ldescriptors:
    descriptors[key] = [reduce(lambda x, y: x + " " + y, ldescriptors[key]) if len(ldescriptors) > 0 else ""]
  for key in rdescriptors:
    if key not in descriptors:
      descriptors[key] = []
    descriptors[key].append(reduce(lambda x, y: x + " " + y, rdescriptors[key]) if len(rdescriptors) > 0 else "")

  logging.info("Writing descriptors into file %s ..." % args["output"])
  if not save_descriptors(args["output"], args["rewrite"], descriptors):
    logging.error("File cannot be saved.")
    return 3
  
  logging.info("Finished ...")
  return 0


def read_configuration():
  parser = argparse.ArgumentParser(
    description="Calculate threshold from a CSV dense distance matrix file.")
  
  parser.add_argument("-l", "--left", "--left-input",
    type=str, dest="left_input", required=True,
    help="Path to left CSV file containing descriptors.")
  parser.add_argument("--left-header",
    action="store_true", dest="left_header", required=False, default=False,
    help="Determines if the left CSV file has header.")
  
  parser.add_argument("-r", "--right", "--right-input",
    type=str, dest="right_input", required=True,
    help="Path to right CSV file containing descriptors.")
  parser.add_argument("--right-header",
    action="store_true", dest="right_header", required=False, default=False,
    help="Determines if the right CSV file has header.")

  parser.add_argument("-o", "--out", "--output",
    type=str, dest="output", required=True,
    help="Path to output CSV file.")
  parser.add_argument("--rewrite",
    action="store_true", dest="rewrite", required=False, default=False,
    help="Rewrite existing output CSV file.")
  
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
