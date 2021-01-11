#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os
import logging
import typing
import argparse
import itertools
import collections


def _parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True,
                        help="Path to input descriptor directory.")
    parser.add_argument("--output", required=True,
                        help="Path to output descriptor directory.")
    parser.add_argument("--sourceProperty", required=True,
                        help="Name of a source properties to union.",
                        metavar="S", nargs="+", type=str)
    parser.add_argument("--targetProperty", required=True,
                        help="Name of a property to store result into.")
    return vars(parser.parse_args())


def main(arguments):
    _init_logging()
    _create_directory(arguments["output"])
    union_properties(arguments)


# region Utils

def _init_logging() -> None:
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] - %(message)s",
        datefmt="%m/%d/%Y %H:%M:%S")


def _create_directory(path: str) -> None:
    if path == "" or path == "." or path == "..":
        return
    os.makedirs(path, exist_ok=True)


# endregion

def union_properties(arguments):
    def transform_file(content):
        result_data = []
        result_metadata = []
        for source_property in arguments["sourceProperty"]:
            property_values, property_metadata = \
                _select_property(source_property, content)
            result_data.extend(property_values)
            result_metadata.append(property_metadata)
        content[arguments["targetProperty"]] = {
            "data": result_data,
            "metadata": [{
                "transformer": "json-union",
                "joined": result_metadata
            }]
        }
        return content

    _transform_files(arguments["input"], arguments["output"], transform_file)


# region Transformation

def _select_property(
        source_property: str, content) \
        -> typing.Tuple[typing.List, typing.List]:
    property_values = content.get(source_property, None)
    property_metadata = None
    if isinstance(property_values, dict):
        property_metadata = property_values.get("metadata", None)
        property_values = property_values.get("data", None)
    if property_values is None:
        return [], []
    if property_metadata is None:
        property_metadata = []
    if not isinstance(property_values, list):
        # Property is always a list, to support multiple values.
        property_values = [property_values]
    return property_values, property_metadata


def _transform_files(
        input_directory: str, output_directory: str, transformer) -> None:
    logging.info("Transforming files ...")
    index = 0
    for index, file_name, content in _iterate_input_files(input_directory):
        result = transformer(content)
        output_file = os.path.join(output_directory, file_name)
        with open(output_file, "w", encoding="utf-8") as stream:
            json.dump(result, stream)
        if index % 1000 == 0:
            logging.info("    %s", index)
    logging.info("    %s", index)
    logging.info("Transforming files ... done")


def _iterate_input_files(input_directory: str):
    for index, file_name in enumerate(os.listdir(input_directory)):
        input_file = os.path.join(input_directory, file_name)
        with open(input_file, "r", encoding="utf-8") as stream:
            input_content = json.load(stream)
        yield index, file_name, input_content


# endregion

if __name__ == "__main__":
    main(_parse_arguments())
