#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import json
import logging
import os

MAPPING = {
    "P31": "instanceOf",
    "P279": "subclassOf",
}


def _parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True,
                        help="Path to Wikidata JSON dump.")
    parser.add_argument("--output", required=False,
                        help="Path to output JSON file.")
    return vars(parser.parse_args())


def main(arguments):
    _init_logging()
    _create_parent_directory(arguments["output"])
    extract_hierarchy(arguments["input"], arguments["output"])


def _init_logging() -> None:
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] - %(message)s",
        datefmt="%m/%d/%Y %H:%M:%S")


def _create_parent_directory(path: str):
    directory = os.path.dirname(path)
    os.makedirs(directory, exist_ok=True)


def extract_hierarchy(source_file, output_file):
    with open(output_file, "w", encoding="utf-8") as stream:
        for content in _iterate_wikidata(source_file):
            result = _wikidata_to_entity(content)
            json.dump(result, stream)
            stream.write("\n")


def _iterate_wikidata(input_file):
    with open(input_file, "r", encoding="utf-8") as stream:
        # Skip first line '['
        next(stream)
        for line in stream:
            if line.startswith(']'):
                break
            yield json.loads(line[:-1])


def _wikidata_to_entity(wikidata):
    result = {
        "@id": wikidata["id"]
    }
    for predicate, claim in wikidata.get("claims", {}).items():
        if predicate not in MAPPING:
            continue
        main_snak = claim.get("mainsnak", None)
        if main_snak is None:
            continue
        data_value = main_snak.get("datavalue", None)
        if data_value is None:
            continue
        values = data_value["value"]["id"]
        key = MAPPING[predicate]
        result[key] = [values, *result.get(key, [])]
    return result


if __name__ == "__main__":
    main(_parse_arguments())
