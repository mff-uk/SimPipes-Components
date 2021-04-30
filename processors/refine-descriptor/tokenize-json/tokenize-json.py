#!/usr/bin/env python

import json
import os
import logging
import typing
import argparse
import shutil


def _parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True,
                        help="Path to input descriptor directory.")
    parser.add_argument("--output", required=True,
                        help="Path to existing output directory.")
    parser.add_argument("--sourceProperty", required=True, nargs="+",
                        help="Name of a source property to transform.")
    parser.add_argument("--targetProperty", required=True, nargs="+",
                        help="Name of a property to store result into.")
    return vars(parser.parse_args())


def main(arguments):
    _init_logging()
    tokenize(arguments)


def _init_logging() -> None:
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] - %(message)s",
        datefmt="%m/%d/%Y %H:%M:%S")


def tokenize(arguments):
    def transform_property(property_value):
        if isinstance(property_value, list):
            # It is already a list of values, we do not need to do anything.
            return property_value
        return property_value.split()

    def transform(content):
        for source_prop, target_prop in \
                zip(arguments["sourceProperty"], arguments["targetProperty"]):
            _transform_dataset_property(
                source_prop,
                target_prop,
                content,
                {
                    "transformer": "tokenize-json",
                    "from": source_prop,
                },
                transform_property)
        return content

    _transform_files(arguments["input"], arguments["output"], transform)


# region Transformation

def _transform_dataset_property(
        source_property: str, target_property: str,
        content, metadata, transformer) -> None:
    property_values, property_metadata = \
        _select_property(source_property, content)
    content[target_property] = {
        "data": [
            transformer(value)
            for value in property_values
        ],
        "metadata": [*property_metadata, metadata]
    }


def _select_property(
        source_property: str, content) \
        -> typing.Tuple[typing.List, typing.List]:
    source_object = content.get(source_property, {})
    property_values = source_object.get("data", [])
    property_metadata = source_object.get("metadata", [])
    return property_values, property_metadata


def _transform_files(
        input_directory: str, output_directory: str, transformer) -> None:
    logging.info("Transforming files ...")
    for file_name, content in _iterate_input_files(input_directory):
        result = transformer(content)
        output_file = os.path.join(output_directory, file_name)
        _write_json(output_file, result)
    logging.info("Transforming files ... done")


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


def _write_json(path, content):
    temp_path = path + ".swp"
    with open(temp_path, "w", encoding="utf-8") as stream:
        json.dump(content, stream, ensure_ascii=False)
    shutil.move(temp_path, path)


# endregion


if __name__ == "__main__":
    main(_parse_arguments())
