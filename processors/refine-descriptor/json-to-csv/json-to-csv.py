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
                        help="Path to input descriptor directory.")
    parser.add_argument("--output", required=True,
                        help="Path to existing directory.")
    parser.add_argument("--property", required=True,
                        help="Name of a property to extract.")
    parser.add_argument("--linePerValue", action="store_true",
                        help="If set there is only one value on each line.")
    return vars(parser.parse_args())


def main(arguments):
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] - %(message)s",
        datefmt="%m/%d/%Y %H:%M:%S")
    export_property(arguments)


def export_property(arguments):
    if arguments["linePerValue"]:
        _convert_to_csv(arguments, _write_mode_line_per_value)
    else:
        _convert_to_csv(arguments, _write_mode_default)


def _write_mode_line_per_value(writer, iri, values):
    for value in _values_to_list(values):
        writer.writerow([iri, value])


def _values_to_list(values) -> typing.List[str]:
    values_as_list = values if isinstance(values, list) else [values]
    result = []
    for item in values_as_list:
        if isinstance(item, list):
            result.append(" ".join(item))
        else:
            result.append(item)
    return result


def _write_mode_default(writer, iri, values):
    writer.writerow([iri, *_values_to_list(values)])


def _convert_to_csv(arguments, write_values_fnc):
    logging.info("Transforming files ...")
    with open(arguments["output"], "w", newline="",
              encoding="utf-8") as output_stream:
        writer = csv.writer(output_stream, delimiter=",", quoting=csv.QUOTE_ALL)
        writer.writerow(["iri", arguments["property"]])
        for _, content in _iterate_input_files(arguments["input"]):
            values, _ = _select_property(arguments["property"], content)
            write_values_fnc(writer, content["iri"], values)
    logging.info("Transforming files ... done")


def _export_mode_default(arguments):
    logging.info("Transforming files ...")
    with open(arguments["output"], "w", newline="",
              encoding="utf-8") as output_stream:
        writer = csv.writer(output_stream, delimiter=",", quoting=csv.QUOTE_ALL)
        writer.writerow(["iri", arguments["property"]])
        for _, content in _iterate_input_files(arguments["input"]):
            values, _ = _select_property(arguments["property"], content)
            writer.writerow([content["iri"], *_values_to_list(values)])
    logging.info("Transforming files ... done")


# region Transformation

def _select_property(
        source_property: str, content) \
        -> typing.Tuple[typing.List, typing.List]:
    source_object = content.get(source_property, {})
    property_values = source_object.get("data", [])
    property_metadata = source_object.get("metadata", [])
    return property_values, property_metadata


def _iterate_input_files(input_directory: str):
    files = os.listdir(input_directory)
    for index, file_name in enumerate(files):
        input_file = os.path.join(input_directory, file_name)
        with open(input_file, "r", encoding="utf-8") as stream:
            input_content = json.load(stream)
        yield file_name, input_content
        if index % 1000 == 0:
            logging.info("    %s / %s", index, len(files))
    logging.info("    %s / %s", len(files), len(files))


# endregion


if __name__ == "__main__":
    main(_parse_arguments())
