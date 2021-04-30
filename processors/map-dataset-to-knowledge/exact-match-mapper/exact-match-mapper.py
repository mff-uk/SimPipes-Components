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
    parser.add_argument("--normalize", default=False, action="store_true",
                        help="Normalize tokes before mapping.")
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
                    "transformer": "exact-match-mapper.py",
                    "from": source_prop,
                },
                lambda values: _mapping_function(
                    token_to_entity, values, arguments["normalize"]))
        return content

    _transform_files(arguments["input"], arguments["output"], file_transformer)


def _load_tokens(
        input_directory: str, source_properties: list[str], normalize: bool
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
        token_to_entity: dict, values, normalize: bool):
    """
    This method take as an input either array of tokens or single string.
    """
    normalizer = _create_normalize(normalize)
    tokens = [normalizer(value) for value in _tokenize(values)]
    result = []
    # Found all entities that takes part in the text.
    resolved_entities = {}
    for token in set(tokens):
        for entity in token_to_entity.get(token, []):
            resolved_entities[entity["@id"]] = entity
    # As we do not know it the entity tokens are from label or alias
    # we need to try for each entity.
    for entity in resolved_entities.values():
        mapping = _token_set_to_entity_mapping(tokens, entity)
        if mapping is not None:
            result.append(mapping)
    return result


def _token_set_to_entity_mapping(tokens: list[str], entity) -> typing.Optional:
    best_shared_tokens = []
    for entity_tokens in entity["tokens"]:
        if not _is_sub_array(tokens, entity_tokens):
            continue
        if len(entity_tokens) > len(best_shared_tokens):
            best_shared_tokens = entity_tokens
    if len(best_shared_tokens) == 0:
        return None
    return {
        "id": entity["@id"],
        "metadata": {
            # We add this as there can be multiple values for an entity.
            "shared_tokens": list(best_shared_tokens)
        }
    }


def _is_sub_array(tokens: list[str], entity_tokens: list[str]) -> bool:
    entity_index = 0
    for token in tokens:
        if token == entity_tokens[entity_index]:
            entity_index += 1
            if entity_index == len(entity_tokens):
                return True
        else:
            entity_index = 0
    return False


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
