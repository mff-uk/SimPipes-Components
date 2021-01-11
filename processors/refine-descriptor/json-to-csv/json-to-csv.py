#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import json
import os
import logging
import csv
import typing


def _parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True,
                        help="Path to DCAT-AP compatible TRIG.")
    parser.add_argument("--output", required=True,
                        help="Path to output directory.")
    parser.add_argument("--property", required=True,
                        help="Name of a property to extract.")
    parser.add_argument("--linePerValue", action="store_true",
                        help="If set there is only one value on each line.")
    return vars(parser.parse_args())


def main(arguments):
    _init_logging()
    _create_parent_directory(arguments["output"])
    export_property(arguments)


# region Utils

def _init_logging() -> None:
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] - %(message)s",
        datefmt="%m/%d/%Y %H:%M:%S")


def _create_parent_directory(path: str) -> None:
    directory = os.path.dirname(path)
    if directory == "" or directory == "." or directory == "..":
        return
    os.makedirs(directory, exist_ok=True)


# endregion

def export_property(arguments):
    if arguments["linePerValue"]:
        _convert_to_csv(arguments, _write_mode_line_per_value)
    else:
        _convert_to_csv(arguments, _write_mode_default)


def _write_mode_line_per_value(writer, iri, values):
    for value in _values_to_list(values):
        writer.writerow([iri, value])


def _write_mode_default(writer, iri, values):
    writer.writerow([iri, *_values_to_list(values)])


def _convert_to_csv(arguments, write_values_fnc):
    logging.info("Transforming files ...")
    index = 0
    with open(arguments["output"], "w", newline="") as output_stream:
        writer = csv.writer(output_stream, delimiter=",", quoting=csv.QUOTE_ALL)
        writer.writerow(["iri", arguments["property"]])
        for index, _, content in _iterate_input_files(arguments["input"]):
            values, _ = _select_property(arguments["property"], content)
            write_values_fnc(writer, content["iri"], values)
            if index % 1000 == 0:
                logging.info("    %s", index)
    logging.info("    %s", index)
    logging.info("Transforming files ... done")


def _values_to_list(values) -> typing.List[str]:
    values_as_list = values if isinstance(values, list) else [values]
    result = []
    for item in values_as_list:
        if not isinstance(item, object):
            result.append(item)
            continue
        # It is an object.
        if "id" in item:
            result.append(item["id"])
            continue
        if "@id" in item:
            result.append(item["@id"])
            continue
        print(item)
        raise Exception("Can't convert an object to CSV root.")
    return result


def _export_mode_default(arguments):
    logging.info("Transforming files ...")
    index = 0
    with open(arguments["output"], "w", newline="") as output_stream:
        writer = csv.writer(output_stream, delimiter=",", quoting=csv.QUOTE_ALL)
        writer.writerow(["iri", arguments["property"]])
        for index, _, content in _iterate_input_files(arguments["input"]):
            values, _ = _select_property(arguments["property"], content)
            writer.writerow([content["iri"], *_values_to_list(values)])
            if index % 1000 == 0:
                logging.info("    %s", index)
    logging.info("    %s", index)
    logging.info("Transforming files ... done")


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
