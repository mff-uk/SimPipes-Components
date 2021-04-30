#!/usr/bin/env python

import json
import os
import logging
import typing
import argparse
import shutil
import requests
import time
import random


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
    parser.add_argument("--sourceLanguage", required=True,
                        help="Language of source")
    parser.add_argument("--targetLanguage", required=True,
                        help="Language of target")
    parser.add_argument("--join", default=False, action="store_true",
                        help="Allow handling of tokenized values.")
    parser.add_argument("--waitTime", default=270,
                        help="Delay between requests.")
    return vars(parser.parse_args())


def main(arguments):
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] - %(message)s",
        datefmt="%m/%d/%Y %H:%M:%S")
    translate(arguments)


def translate(arguments):
    def transform_property(property_value):
        sleep_time = (arguments["waitTime"] / 1000) + \
                     (random.random() / 100) - 0.005
        time.sleep(sleep_time)
        is_list = isinstance(property_value, list)
        if is_list:
            if not arguments["join"]:
                raise Exception(
                    "Tokenized value detected, use --join to handle that.")
            property_value = " ".join(property_value)
        return _translate_value(
            arguments["sourceLanguage"], arguments["targetLanguage"],
            is_list, property_value)

    def transform(content):
        for source_prop, target_prop in \
                zip(arguments["sourceProperty"], arguments["targetProperty"]):
            _transform_dataset_property(
                source_prop,
                target_prop,
                content,
                {
                    "transformer": "translate-json",
                    "language": {
                        "from": arguments["sourceLanguage"],
                        "to": arguments["targetLanguage"],
                    },
                    "from": source_prop,
                },
                transform_property)
        return content

    _transform_files(arguments["input"], arguments["output"], transform)


def _translate_value(
        source_language: str, target_language: str,
        splitAfter: bool, value: str):
    url = "https://lindat.mff.cuni.cz/services/translation/api/v2/languages/" \
          f"?src={source_language}&tgt={target_language}"
    response = requests.post(
        url,
        headers={
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
        },
        data={"input_text": value})
    response.encoding = "utf-8"
    if not response.status_code == 200:
        print("URL :", url)
        print("data:", value)
        raise RuntimeError("Status code is not 200.")
    result = response.text.rstrip()
    if splitAfter:
        result = result.split()
    return result


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
