#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os
import logging
import typing
import argparse
import itertools
import collections
import shutil

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
    parser.add_argument("--sourceProperty", required=True, nargs="+",
                        help="Name of a source property to transform.")
    parser.add_argument("--targetProperty", required=True, nargs="+",
                        help="Name of a property to store result into.")
    parser.add_argument("--sharedThreshold", type=float, default=0.6,
                        help="How many of entity tokens must be shared.")
    parser.add_argument("--normalize", default=False, action="store_true",
                        help="Normalize tokes before mapping.")
    parser.add_argument("--pretty", action="store_true",
                        help="Pretty print the output.")
    return vars(parser.parse_args())


def main(arguments):
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] - %(message)s",
        datefmt="%m/%d/%Y %H:%M:%S")
    create_mapping(arguments)


def create_mapping(arguments):
    tokens = _load_tokens(
        arguments["input"], arguments["sourceProperty"],
        arguments["normalize"])
    token_to_entity = _load_knowledge(
        arguments["entities"], tokens, arguments["normalize"])

    def file_transformer(content):
        for source_prop, target_prop in \
                zip(arguments["sourceProperty"], arguments["targetProperty"]):
            _transform_dataset_property(
                source_prop,
                target_prop,
                content,
                {
                    "transformer": "bag-of-words-mapper",
                    "from": source_prop,
                    "threshold": arguments["sharedThreshold"],
                },
                lambda values: _mapping_function(
                    token_to_entity, values,
                    arguments["sharedThreshold"], arguments["normalize"]))
        return content
    _transform_files(
        arguments["pretty"], arguments["input"], arguments["output"],
        file_transformer)


def _load_tokens(
        input_directory: str, source_properties: typing.List[str],
        normalize: bool
) -> typing.Set[str]:
    logging.info("Loading tokens ...")
    tokens = set()
    normalizer = _create_normalize(normalize)
    for _, content in _iterate_input_files(input_directory):
        for source_property in source_properties:
            values, _ = _select_property(source_property, content)
            for value in values:
                for token in _tokenize(value):
                    tokens.add(normalizer(token))
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


def _create_normalize(normalize: bool):
    if normalize:
        return lambda value: value.lower()
    else:
        return lambda value: value


def _load_knowledge(
        knowledge_file: str, tokens: typing.Set[str], normalize: bool):
    result = collections.defaultdict(list)
    logging.info("Loading entities ... ")
    index = 0
    shared_entities = 0
    normalizer = _create_normalize(normalize)
    for index, entity in _iterate_json_lines(knowledge_file):
        stored_entity = {
            "@id": entity["@id"],
            "tokens": [
                [
                    normalizer(value)
                    for value in _tokenize(text)
                ]
                for text in itertools.chain(
                    entity.get("label", []),
                    entity.get("aliases", [])
                )
            ]
        }
        shared_tokens = {
            token
            for entity_tokens in stored_entity["tokens"]
            for token in entity_tokens
            if token in tokens
        }
        if len(shared_tokens) > 0:
            shared_entities += 1
            for shared_token in shared_tokens:
                result[shared_token].append(stored_entity)
        if index % 100000 == 0:
            logging.info("    %s", index)
    logging.info("    %s / %s", index, index)
    logging.info("Shared tokens count: %s", len(result))
    logging.info("Mapped to entities count: %s", shared_entities)
    logging.info("Loading entities ... done")
    return result


def _mapping_function(
        token_to_entity: dict, values,
        shared_threshold: float, normalize: bool):
    """
    This method take as an input either array of tokens or single string.

    We only require the tokens to be in the given text, for
    entity "A B C" and text "0 A B C 1" we got match, but also
    with "0 A 1 B 2 C" or "C B A".
    """
    normalizer = _create_normalize(normalize)
    tokens = {normalizer(value) for value in _tokenize(values)}
    result = []
    # Found all entities that takes part in the text.
    resolved_entities = {}
    for token in tokens:
        if token in INVALID_STANDALONE_MAPPING_TOKENS:
            continue
        for entity in token_to_entity.get(token, []):
            resolved_entities[entity["@id"]] = entity
    # As we do not know it the entity tokens are from label or alias
    # we need to try for each entity.
    for entity in resolved_entities.values():
        mapping = _token_set_to_entity_mapping(
            tokens, entity, shared_threshold)
        if mapping is not None:
            result.append(mapping)
    return result


def _token_set_to_entity_mapping(
        tokens: typing.Set[str], entity, shared_threshold: float
) -> typing.Optional:
    best_shared = 0
    best_shared_tokens = []
    for entity_tokens in entity["tokens"]:
        entity_tokens_set = set(entity_tokens)
        shared_tokens = tokens & entity_tokens_set
        shared = len(shared_tokens) / len(entity_tokens_set)
        if shared < shared_threshold:
            continue
        if shared < best_shared:
            continue
        best_shared = shared
        best_shared_tokens = shared_tokens
    if best_shared == 0:
        return None
    return {
        "id": entity["@id"],
        "metadata": {
            "shared": best_shared,
            "shared_tokens": list(best_shared_tokens)
        }
    }


# region Knowledge graph

def _iterate_json_lines(file_path: str) \
        -> typing.Generator[typing.Tuple[int, dict], None, None]:
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
        pretty: bool, input_directory: str, output_directory: str,
        transformer) -> None:
    logging.info("Transforming files ...")
    for file_name, content in _iterate_input_files(input_directory):
        result = transformer(content)
        output_file = os.path.join(output_directory, file_name)
        _write_json(pretty, output_file, result)
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


def _write_json(pretty: bool, path: str, content):
    temp_path = path + ".swp"
    with open(temp_path, "w", encoding="utf-8") as stream:
        json.dump(content, stream, ensure_ascii=False,
                  indent=2 if pretty else None)
    shutil.move(temp_path, path)


# endregion

if __name__ == "__main__":
    main(_parse_arguments())
