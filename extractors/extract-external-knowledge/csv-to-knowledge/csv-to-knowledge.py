#!/usr/bin/env python
#
# Given CSV with two columns, create a JSON-lines file. Where each line has
# object with '@id' and 'label'.
#

import csv
import logging
import argparse
import json


def _parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True,
                        help="Path to input CSV file with labels.")
    parser.add_argument("--output", required=True,
                        help="Path to output JSON lines file.")
    return vars(parser.parse_args())


def main(arguments):
    _init_logging()
    create_knowledge_from_csv(arguments)


def _init_logging() -> None:
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] - %(message)s",
        datefmt="%m/%d/%Y %H:%M:%S")


def create_knowledge_from_csv(arguments):
    result = {
        iri: {
            "@id": iri,
            "label": [label]
        }
        for iri, label in _load_csv(arguments["input"]).items()
    }
    print("Number of entities:", len(result))
    _save_json_lines(result, arguments["output"])


def _load_csv(path):
    result = {}
    with open(path, encoding="utf-8") as stream:
        reader = csv.reader(stream)
        next(reader)
        for line in reader:
            result[line[0]] = line[1]
    return result


def _save_json_lines(content, path):
    with open(path, "w", encoding="utf-8", newline='') as stream:
        for item in content.values():
            json.dump(item, stream, ensure_ascii=False)
            stream.write("\n")


if __name__ == "__main__":
    main(_parse_arguments())
