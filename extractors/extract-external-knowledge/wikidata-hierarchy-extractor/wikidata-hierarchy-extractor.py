#!/usr/bin/env python

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
    parser.add_argument("--output", required=True,
                        help="Path to output JSON file.")
    return vars(parser.parse_args())


def main(arguments):
    _init_logging()
    extract_hierarchy(arguments["input"], arguments["output"])


def _init_logging() -> None:
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] - %(message)s",
        datefmt="%m/%d/%Y %H:%M:%S")


def extract_hierarchy(source_file: str, output_file: str) -> None:
    with open(output_file, "w", encoding="utf-8") as stream:
        for content in _iterate_wikidata(source_file):
            result = _wikidata_to_entity(content)
            if result is None:
                continue
            json.dump(result, stream, ensure_ascii=False)
            stream.write("\n")


def _iterate_wikidata(input_file: str):
    with open(input_file, "r", encoding="utf-8") as stream:
        # Skip first line '['
        next(stream)
        for line in stream:
            if line.startswith(']'):
                break
            line = line.rstrip()
            if line.endswith(","):
                line = line[:-1]
            yield json.loads(line)


def _wikidata_to_entity(wikidata):
    result = {
        "@id": wikidata["id"]
    }
    data_available = False
    for predicate, claims in wikidata.get("claims", {}).items():
        if predicate not in MAPPING:
            continue
        if not isinstance(claims, list):
            claims = [claims]
        for claim in claims:
            main_snak = claim.get("mainsnak", None)
            if main_snak is None:
                continue
            data_value = main_snak.get("datavalue", None)
            if data_value is None:
                continue
            values = data_value["value"]["id"]
            key = MAPPING[predicate]
            result[key] = [values, *result.get(key, [])]
            data_available = True
    return result if data_available else None


if __name__ == "__main__":
    main(_parse_arguments())
