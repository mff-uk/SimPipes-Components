#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import csv
import argparse
import logging


def main():
  logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] - %(message)s",
    datefmt="%H:%M:%S")
  
  args = read_configuration()

  rows = load_rows(args["input"], args["input_header"])
  if rows is None:
    logging.error("Error occured during descriptors reading.")
    return 1
  
  idxs = load_idxs(args["sample"], args["sample_header"])
  if idxs is None:
    logging.error("Error occured during sample reading.")
    return 2

  if not save_sampled(rows, idxs, args["output"], args["rewrite"]):
    logging.error("Error occured during saving.")
    return 3
  
  logging.info("Sample created...")
  return 0


def read_configuration():
  parser = argparse.ArgumentParser(
    description="Precompute distance matrix for specified data.")
  
  parser.add_argument("-i", "--in", "--input",
    type=str, dest="input", required=True,
    help="Path to input CSV file containing descriptors.")
  parser.add_argument("--input-header",
    action="store_true", dest="input_header", required=False, default=False,
    help="Determines if the input CSV file has header.")
  
  parser.add_argument("-s", "--sample",
    type=str, dest="sample", required=True,
    help="Path to sample CSV file containing descriptors.")
  parser.add_argument("--sample-header",
    action="store_true", dest="sample_header", required=False, default=False,
    help="Determines if the sample CSV file has header.")
  
  parser.add_argument("-o", "--out", "--output",
    type=str, dest="output", required=True,
    help="Path to output NumPy array.")
  parser.add_argument("--rewrite",
    action="store_true", dest="rewrite", required=False, default=False,
    help="Rewrite existing output CSV file.")
  
  args = vars(parser.parse_args())

  return args


def load_rows(input_path, input_header):
  if not valid_file_for_read(input_path):
    return None
  
  with open(input_path, encoding="utf-8") as input_stream:
    reader = csv.reader(input_stream)
    if input_header:
      next(reader, None)
    
    descriptors = {}
    for row in reader:
      descriptors[row[0]] = row[1:]
    return descriptors


def load_idxs(sample_path, sample_header):
  if not valid_file_for_read(sample_path):
    return None
  
  with open(sample_path, encoding="utf-8") as input_stream:
    reader = csv.reader(input_stream)
    if sample_header:
      next(reader, None)
    
    samples = []
    for row in reader:
      samples.append(row[0])
    return samples


def save_sampled(rows, idxs, output_path, output_rewrite):
  if not valid_file_for_write(output_path, output_rewrite):
    return False
  
  with open(output_path, "w", newline='\n', encoding="utf-8") as output_stream:
    writer = csv.writer(output_stream)
    for idx in enumerate(idxs):
      writer.writerow( [idx[0]] + ( rows[idx[1]] if idx[1] in rows else [] ) )
    return True


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
