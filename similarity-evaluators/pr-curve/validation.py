#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import csv
import argparse
import logging

from typing import Any, Dict, List

import json
import numpy as np
from tqdm import tqdm


def main():
  logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] - %(message)s",
    datefmt="%H:%M:%S")
  
  args = read_configuration()

  logging.info(f"Loading distance matrix file {args['distance']}")
  distance_matrix, ids = load_distance_matrix(args["distance"], args["distance_has_header_row"], args["distance_has_header_column"])
  if distance_matrix is None or len(distance_matrix) == 0:
    logging.error("Error occurred during loading distance matrix or no entities are present.")
    return 1
  
  if not args["map"] is None:
    logging.info(f"Loading mapping file {args['map']}")
    ids = load_map(args["map"], args["map_has_header_row"], ids)
    if ids is None:
      logging.error("Error occurred during loading mapping file.")
      return 1
  
  logging.info(f"Loading baseline file {args['baseline']}")
  baseline = load_baseline(args["baseline"])
  if baseline is None:
    logging.error("Error occurred during loading baseline file.")
    return 1

  evaluate_baseline(baseline, ids, distance_matrix, args['agg'])
  return 0


def read_configuration():
  parser = argparse.ArgumentParser(
    description="Calculate validation of similarity model against baseline file.")
  
  parser.add_argument("-d", "--distance",
    type=str, dest="distance", required=True,
    help="Path to input CSV file containing distance matrix.")
  parser.add_argument("--distance-has-header-row",
    action="store_true", dest="distance_has_header_row", required=False, default=False,
    help="Determines if the distance matrix CSV file has header row.")
  parser.add_argument("--distance-has-header-column",
    action="store_true", dest="distance_has_header_column", required=False, default=False,
    help="Determines if the distance matrix CSV file has header column.")
  
  parser.add_argument("-m", "--map",
    type=str, dest="map", required=False,
    help="Path to mapping CSV file containing IDs of rows.")
  parser.add_argument("--map-has-header-row",
    action="store_true", dest="map_has_header_row", required=False, default=False,
    help="Determines if the mapping CSV file has header row.")

  parser.add_argument("-b", "--baseline",
    type=str, dest="baseline", required=True,
    help="Path to baseline JSON file.")
  
  parser.add_argument("-agg", "--aggregation",
    type=str, dest="agg", required=False, default="max", choices=['min', 'max', 'avg'],
    help="Determines aggregation.")

  args = vars(parser.parse_args())

  assert args['distance_has_header_row'] or args['distance_has_header_column'] or args['map'],\
    "Mapping file must be set if distance matrix has no header row neither column."

  return args


def load_distance_matrix(file_path: str, has_header_row: bool, has_header_column: bool):
  if not valid_file_for_read(file_path):
    return None, None

  with open(file_path, encoding="UTF-8") as input_stream:
    reader = csv.reader(input_stream)

    row_ids = None
    column_ids = [] if has_header_column else None
    data = []
    
    if has_header_row:
      row_ids = next(reader)
      if has_header_column:
        row_ids = row_ids[1:]
    
    for row in reader:
      if has_header_column:
        column_ids.append(row[0])
      data.append(row[1:] if has_header_column else row)

    if not row_ids is None and not column_ids is None:
      assert row_ids == column_ids,\
        "If both headers specified, they must be same."
    
    if not row_ids is None:
      column_ids = row_ids
    if column_ids is None:
      column_ids = range(len(data))

    npdata = np.array(data, dtype=float)
    assert npdata.shape[0] == npdata.shape[1],\
      "Shape of matrix needs same size."

    return npdata, dict(zip(column_ids, range(len(column_ids))))


def load_map(file_path: str, has_header_row: bool, ids: Dict[Any, int]) -> Dict[Any, int]:
  if not valid_file_for_read(file_path):
    return None
  
  with open(file_path, encoding="UTF-8") as input_stream:
    reader = csv.reader(input_stream)

    if has_header_row:
      next(reader)
    
    mapping = {}
    for row in reader:
      key = row[0]
      value = len(mapping)
      assert value in ids,\
        "ID must be in distance matrix."
      mapping[key] = ids[value]
    
    assert len(ids) == len(mapping),\
      "Length of mapping must be equal to number of rows."
    
    return mapping


def load_baseline(file_path: str):
  if not valid_file_for_read(file_path):
    return None
  
  with open(file_path, encoding="UTF-8") as input_stream:
    return json.load(input_stream)


def evaluate_baseline(baseline, ids, distance_matrix, agg):
  gresult = { 0.0: [ 1, 1 ], 0.1: [ 0, 0 ], 0.2: [ 0, 0 ], 0.3: [ 0, 0 ], 0.4: [ 0, 0 ], 0.5: [ 0, 0 ], 0.6: [ 0, 0 ], 0.7: [ 0, 0 ], 0.8: [ 0, 0 ], 0.9: [ 0, 0 ], 1.0: [ 0, 0 ] }
  for i, case in enumerate(baseline):
    logging.info(f"{i+1}/{len(baseline)} ... \"{case['title']}\" by {case['author']}")

    for inp in case["inputs"]:
      logging.debug(f"Input: {inp}")

    similarity = query_baseline_case(case["inputs"], ids, distance_matrix, agg)
    if similarity is None:
      logging.warning(f"Test {i+1} is skipped (has no valid input)...")
      continue
    
    result = evaluate_baseline_case(case["outputs"], ids, similarity)
    if result is None:
      logging.warning(f"Test {i+1} is skipped (has no valid output)...")
      continue

    result = [ ( (idx + 1)/len(result), (idx + 1)/pos ) for idx, pos in enumerate(sorted(map(lambda x: result[x], result))) ]

    for recall, precision in result:
        r = min(filter(lambda threshold: threshold >= recall, gresult))
        gresult[ r ][ 0 ] += precision
        gresult[ r ][ 1 ] += 1
  
  gsorted = sorted(map(lambda x: (x, gresult[x][0] / gresult[x][1] if gresult[x][1] != 0 else 0), gresult))
  print("recall," + ",".join(map(lambda x: str(x[0]), gsorted)))
  print("precision," + ",".join(map(lambda x: str(x[1]), gsorted)))


def query_baseline_case(inputs, ids, distance_matrix, agg):
  input_ids = []
  for i in inputs:
    if not i in ids:
      logging.info(f"Skipping {i} (not present in ID keys).")
      continue
    input_ids.append(ids[i])
  
  if len(input_ids) == 0:
    logging.warning(f"No valid input is present.")
    return None
  
  mind = None
  if agg == "min":
    mind = np.min(distance_matrix[:,input_ids], axis=1)
  elif agg == "max":
    mind = np.max(distance_matrix[:,input_ids], axis=1)
  elif agg == "avg":
    mind = np.average(distance_matrix[:,input_ids], axis=1)
  else:
    assert False, "Unknown argument."

  res = dict(zip(range(len(ids)), mind))
  for i in input_ids:
    del res[i]
  
  return res


def evaluate_baseline_case(outputs, ids, similarity):
  sort = dict(zip(
    map(
      lambda x: x, 
      sorted(similarity, key=lambda x: similarity[x])
    ),
    range(1, 1+len(similarity))
  ))

  result = {}
  for o in outputs:
    if not o in ids:
      logging.info(f"Skipping {o} (not present in ID keys).")
      continue 
    if not ids[o] in sort:
      logging.info(f"Skipping {o} (was in input).")
      continue
    result[o] = sort[ids[o]]
  
  if len(result) == 0:
    logging.warning(f"No valid output is present.")
    return None

  return result


def valid_file_for_read(file_path):
  if not os.path.exists(file_path):
    return False
  if not os.path.isfile(file_path):
    return False
  return True


if __name__ == "__main__":
  exit(main())
