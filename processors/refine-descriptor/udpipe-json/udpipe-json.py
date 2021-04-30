#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Download model from:
#   https://lindat.mff.cuni.cz/repository/xmlui/handle/11234/1-2898?show=full
#

import json
import os
import logging
import typing
import functools
import unidecode
import argparse
import shutil

from ufal.udpipe import Model, Sentence, ProcessingError


class UdPipe:

    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.error = None

    def load(self, model_path: str):
        logging.info("Loading UdPipe model ...")
        self.model = Model.load(model_path)
        if not self.model:
            raise Exception("Cannot load model from file '%s'." % model_path)
        self.tokenizer = self.model.newTokenizer(self.model.DEFAULT)
        if not self.tokenizer:
            raise Exception("The model does not have a tokenizer")
        self.error = ProcessingError()

    def transform(self, string: str):
        self.tokenizer.setText(string)

        sentences = []
        sentence = Sentence()
        while self.tokenizer.nextSentence(sentence, self.error):
            self.model.tag(sentence, self.model.DEFAULT)
            sentences.append(sentence)
            sentence = Sentence()

        if self.error.occurred():
            raise Exception(self.error.message)

        words = functools.reduce(
            lambda x, y: x + y,
            [[(w.lemma, w.upostag) for w in s.words] for s in sentences],
            [])
        return [word for word in words if word[1] not in ['<root>']]


def _parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True,
                        help="Path to input descriptor directory.")
    parser.add_argument("--output", required=True,
                        help="Path to existing output directory.")
    parser.add_argument("--model", required=True,
                        help="Path to a udpipe model, e.g. "
                             "'czech-pdt-ud-2.3-181115.udpipe'.")
    parser.add_argument("--transformation", required=False, default="v3",
                        help="Specify filter to apply for transformation of "
                             "UdPipe results.")
    parser.add_argument("--sourceProperty", required=True, nargs="+",
                        help="Name of a source property to transform.")
    parser.add_argument("--targetProperty", required=True, nargs="+",
                        help="Name of a property to store result into.")
    return vars(parser.parse_args())


def main(arguments):
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] - %(message)s",
        datefmt="%m/%d/%Y %H:%M:%S")
    transform_descriptor_with_udpipe(arguments)


def transform_descriptor_with_udpipe(arguments):
    udpipe = UdPipe()
    udpipe.load(arguments["model"])
    refine_fnc = _select_refine_function(arguments["transformation"])

    def transform_property(property_value):
        if isinstance(property_value, list):
            result = [
                refine_fnc(udpipe.transform(value))
                for value in property_value
            ]
        else:
            result = refine_fnc(udpipe.transform(property_value))
        return result

    def transform(content):
        for source_prop, target_prop in \
                zip(arguments["sourceProperty"], arguments["targetProperty"]):
            _transform_dataset_property(
                source_prop,
                target_prop,
                content,
                {
                    "transformer": "udpipe-json",
                    "from": source_prop,
                },
                transform_property)
        return content

    _transform_files(arguments["input"], arguments["output"], transform)


# region Refine function

def _select_refine_function(name: str):
    if name == "v2":
        return _refine_v2
    elif name == "v3":
        return _refine_v3
    else:
        raise Exception("Unknown transformation function:" + name)


def _refine_v2(value: typing.List[str]) -> typing.List[str]:
    """Extract values from UdPipe, keep only words of given types."""
    # https://universaldependencies.org/u/pos/
    allowed = {"NOUN", "PROPN", "ADJ", "ADP", "NUM", "DET", "VERB"}
    return [unidecode.unidecode(lemma)
            for lemma, lemma_type in value if lemma_type in allowed]


def _refine_v3(value: typing.List[str]) -> typing.List[str]:
    """
    v2 have issues where "zleva doprava" was changed to "doprava", as "zleva"
    is marked to be adverb. For this reason we keep all word types.
    """
    return [unidecode.unidecode(lemma) for lemma, lemma_type in value]


# endregion

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
