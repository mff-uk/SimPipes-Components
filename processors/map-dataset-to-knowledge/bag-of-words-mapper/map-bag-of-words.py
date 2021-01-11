#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os
import logging
import typing
import argparse
import itertools
import collections

# For example "-" can be used to map to: Q11879093 or Q10689378, with "-"
# as the only shared term. While we allow "-" to be used as a shared term it
# must not be the only shared term. For this reason the "-" can not be removed
# from the data during pre-processing.
# Similar idea apply to all values in this list.
INVALID_STANDALONE_MAPPING_TOKENS = {
    "(", ")", ".", "?", "!", "-", ",", "}", "{"
}


def _parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True,
                        help="Path to input descriptor directory.")
    parser.add_argument("--output", required=True,
                        help="Path to output descriptor directory.")
    parser.add_argument("--entities", required=True,
                        help="Path to JSONL files with entities.")
    parser.add_argument("--sourceProperty", required=True,
                        help="Name of a source property to transform.")
    parser.add_argument("--targetProperty", required=True,
                        help="Name of a property to store result into.")
    parser.add_argument("--sharedThreshold", type=float, default=0.6,
                        help="How many of entity tokens must be shared.")
    return vars(parser.parse_args())


def main(arguments):
    _init_logging()
    _create_directory(arguments["output"])
    create_mapping(arguments)


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

def create_mapping(arguments):
    tokens = _load_tokens(arguments["input"], arguments["sourceProperty"])
    token_to_entity = _load_wikidata_entities(arguments["entities"], tokens)

    def file_transformer(content):
        _transform_dataset_property(
            arguments["sourceProperty"],
            arguments["targetProperty"],
            content,
            {
                "transformer": "bag-of-words-mapper",
                "from": arguments["sourceProperty"],
                "threshold": arguments["sharedThreshold"],
            },
            lambda values: _mapping_function(
                token_to_entity, values, arguments["sharedThreshold"])
        )
        return content

    _transform_files(arguments["input"], arguments["output"], file_transformer)


def _load_tokens(input_directory: str, source_property: str) -> typing.Set[str]:
    logging.info("Loading tokens ...")
    tokens = set()
    index = 0
    for index, _, content in _iterate_input_files(input_directory):
        values, _ = _select_property(source_property, content)
        for value in values:
            for token in _tokenize(value):
                tokens.add(token)
        if index % 1000 == 0:
            logging.info("    %s", index)
    logging.info("    %s", index)
    logging.info("Tokens count: %s", len(tokens))
    logging.info("Loading tokens ... done")
    return tokens


def _tokenize(value) -> typing.List[str]:
    if value is None:
        return []
    elif isinstance(value, list):
        return value
    else:
        return value.split(" ")


def _load_wikidata_entities(wikidata_file: str, tokens: typing.Set[str]):
    token_to_entity = collections.defaultdict(list)
    logging.info("Loading entities ... ")
    index = 0
    shared_entities = 0
    for index, entity in _iterate_json_lines(wikidata_file):
        entity_tokens = {
            token
            for value in itertools.chain(
                entity.get("label", []),
                entity.get("aliases", [])
            )
            for token in _tokenize(value)
        }
        shared_tokens = tokens & entity_tokens
        for shared_token in shared_tokens:
            token_to_entity[shared_token].append(entity)
        if len(shared_tokens) > 0:
            shared_entities += 1
        if index % 100000 == 0:
            logging.info("    %s", index)
    logging.info("    %s", index)
    logging.info("Shared tokens count: %s", len(token_to_entity))
    logging.info("Mapped to entities count: %s", shared_entities)
    logging.info("Loading entities ... done")
    return token_to_entity


def _mapping_function(token_to_entity, values, shared_threshold):
    """
    We require the wikidata entity to be in the given text, for
    entity "A B C" and text "0 A B C 1" we got match, but also
    with "0 A 1 B 2 C" or "C B A".
    """
    # shared_for_entity = collections.defaultdict(list)
    # entities = {}
    # entities_shared_by_count = collections.Counter()
    result = []
    resolved_entities = set()
    for value in values:
        tokens = _tokenize(value)
        for token in tokens:
            if token in INVALID_STANDALONE_MAPPING_TOKENS:
                continue
            for entity in token_to_entity.get(token, []):
                entity_id = entity["@id"]
                if entity_id in resolved_entities:
                    continue
                resolved_entities.add(entity_id)
                mapping = _tokens_to_entity_mapping(tokens, entity,
                                                    shared_threshold)
                if mapping is not None:
                    result.append(mapping)
    return result


def _tokens_to_entity_mapping(
        tokens: typing.List[str], entity, shared_threshold: int
) -> typing.Optional:
    # ['ustav', '-', 'platny', '(', 'Usti', 'nad', 'Labe', '-', '2015', ')']
    # {'@id': 'Q44383619', 'label': [['Shenzhe', 'Open', '2015']]}
    tokens_set = set(tokens)
    best_shared, best_tokens = _tokens_to_shared_shared(
        tokens_set, entity.get("label", []),
        [], [],
        shared_threshold)
    best_shared, best_tokens = _tokens_to_shared_shared(
        tokens_set, entity.get("aliases", []),
        best_shared, best_tokens,
        shared_threshold)
    if len(best_shared) == 0:
        return None
    return {
        "id": entity["@id"],
        "metadata": {
            "shared": best_shared,
            "entity": best_tokens
        }
    }


def _tokens_to_shared_shared(
        tokens_set: typing.Set[str], values: typing.List[str],
        best_shared: typing.List[str], best_tokens: typing.List[str],
        shared_threshold: int):
    for label in values:
        label_tokens = _tokenize(label)
        shared = list(set(label_tokens) & tokens_set)
        if len(best_shared) < len(shared) and \
                len(shared) / len(label_tokens) > shared_threshold:
            best_shared = shared
            best_tokens = label_tokens
    return best_shared, best_tokens


# region Knowledge graph

def _iterate_json_lines(file_path: str) \
        -> typing.Generator[typing.Tuple[int, object], None, None]:
    with open(file_path, encoding="utf-8") as stream:
        for index, line in enumerate(stream):
            entity = json.loads(line)
            yield index, entity


# endregion

# region Transformation

def _transform_dataset_property(
        source_property: str, target_property: str,
        content, metadata, transformer) -> None:
    property_values, property_metadata = \
        _select_property(source_property, content)
    property_metadata.append(metadata)
    content[target_property] = {
        "data": transformer(property_values),
        "metadata": property_metadata
    }


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
