#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import json
import logging
import os


def _parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True,
                        help="Path to Wikidata JSON dump.")
    parser.add_argument("--output", required=False,
                        help="Path to output JSON file.")
    parser.add_argument("--language", required=False,
                        help="Language to extract.")
    return vars(parser.parse_args())


def main(arguments):
    _init_logging()
    _create_parent_directory(arguments["output"])
    extract_hierarchy(
        arguments["input"], arguments["output"], arguments["language"])


def _init_logging() -> None:
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] - %(message)s",
        datefmt="%m/%d/%Y %H:%M:%S")


def _create_parent_directory(path: str):
    directory = os.path.dirname(path)
    os.makedirs(directory, exist_ok=True)


def extract_hierarchy(source_file, output_file, language):
    with open(output_file, "w", encoding="utf-8") as stream:
        for content in _iterate_wikidata(source_file):
            result = _wikidata_to_entity(content, language)
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


def _wikidata_to_entity(wikidata, language):
    result = {
        "@id": wikidata["id"],
    }
    label = _collect_strings(wikidata.get("labels", None), language)
    if label is not None:
        result["label"] = label
    aliases = _collect_strings(wikidata.get("aliases", None), language)
    if aliases is not None:
        result["aliases"] = aliases
    return result


def _collect_strings(values, language):
    if values is None:
        return None
    values_in_language = values.get(language, [])
    # For example labels are single values while aliases are arrays.
    if not isinstance(values_in_language, list):
        values_in_language = [values_in_language]
    return [
        item["value"]
        for item in values_in_language
        if item["language"] == language
    ]


if __name__ == "__main__":
    main(_parse_arguments())
