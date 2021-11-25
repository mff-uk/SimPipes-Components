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
    parser.add_argument("--knowledge", required=True,
                        help="Path to JSONL files with hierarchy.")
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
    refine_mapping(arguments)


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

def refine_mapping(arguments):
    entities = _collect_entities(
        arguments["input"], arguments["sourceProperty"])
    mapping = _collect_mapping(entities, arguments["knowledge"])
    logging.info("Mapping size: %s", len(mapping))
    transitive_mapping = _create_transitive_mapping(mapping)

    def file_transformer(content):
        _transform_dataset_property(
            arguments["sourceProperty"], arguments["targetProperty"],
            content,
            {
                "from": arguments["sourceProperty"],
                "transformer": "instance-to-class",
            },
            lambda values: _transform_property(transitive_mapping, values)
        )
        return content

    _transform_files(arguments["input"], arguments["output"], file_transformer)


def _collect_entities(input_directory: str, source_property: str) \
        -> typing.Set[str]:
    result = set()
    logging.info("Collecting entities ...")
    index = 0
    for index, _, content in _iterate_input_files(input_directory):
        values, _ = _select_property(source_property, content)
        for value in _flatten_array(values):
            result.add(value["id"])
        if index % 1000 == 0:
            logging.info("    %s", index)
    logging.info("    %s", index)
    logging.info("Entities count: %s", len(result))
    logging.info("Collecting entities ... done")
    return result


def _flatten_array(values):
    result = []
    for value in values:
        if isinstance(value, list):
            result.extend(value)
        else:
            result.append(value)
    return result


def _collect_mapping(entities: typing.Set[str], knowledge_file: str) \
        -> typing.Dict[str, str]:
    logging.info("Collecting mapping ... ")
    result = {}
    to_resolve = {key for key in entities}
    while len(to_resolve) > 0:
        mapping, new_to_resolve = _collect_from_hierarchy(
            to_resolve, knowledge_file)
        result.update(mapping)
        to_resolve = new_to_resolve
    logging.info("Collecting mapping ... done")
    return result


def _collect_from_hierarchy(to_resolve: typing.Set[str], knowledge_file: str):
    mapping = {}
    new_to_resolve = set()
    logging.info("Iterating the file with %s entities", len(to_resolve))
    index = 0
    for index, entity in _iterate_json_lines(knowledge_file):
        if index % 5000000 == 0:
            logging.info("    %s", index)
        #
        entity_id = entity["@id"]
        if entity_id not in to_resolve:
            continue
        if len(entity.get("subclassOf", [])) > 0:
            # If entity has subclassOf, we consider it to be a concept.
            mapping[entity_id] = [entity_id]
            continue
        if "instanceOf" not in entity:
            # This should not happen, entity should hove at leas one
            # of subclassOf or instanceOf. As we have none, we assume
            # this does not map to nowhere.
            logging.error(
                "Missing subclassOf and instanceOf for: %s", entity_id)
            mapping[entity_id] = [entity_id]
            continue
        # We have instances to map to.
        mapping[entity_id] = entity["instanceOf"]
        for instance_id in entity["instanceOf"]:
            if instance_id in to_resolve:
                continue
            if instance_id in mapping:
                continue
            new_to_resolve.add(instance_id)
    logging.info("    %s", index)
    return mapping, new_to_resolve


def _create_transitive_mapping(mapping: typing.Dict[str, str]) \
        -> typing.Dict[str, str]:
    # Given A -> B, B->C, produce A -> [C], B -> [C].
    result = {}
    logging.info("Creating transitive mapping ...")
    while len(result) < len(mapping):
        for source, targets in mapping.items():
            if source in result:
                continue
            # Add those with primitive mapping.
            if len(targets) == 1 and source == targets[0]:
                result[source] = targets
            # Add those whose targets are resolved or missing.
            for target in targets:
                if target not in mapping:
                    # Ignore targets without mapping.
                    continue
                if target not in result:
                    break
            else:
                # All targets were resolved.
                result[source] = list({
                    mapped_to
                    for target in targets
                    # Use mapping to it self as a default.
                    for mapped_to in result.get(target, [target])
                })
    logging.info("Creating transitive mapping ... done")
    return result


def _transform_property(transitive_mapping, values):
    if not isinstance(values, list):
        values = [values]
    result = []
    for value in _flatten_array(values):
        value_result = []
        for mapping in value["data"]:
            entity_id = mapping["id"]
            mapped_to = transitive_mapping.get(entity_id, None)
            if mapped_to is None:
                # No information about mapping.
                value_result.append(mapping)
                continue
            if len(mapped_to) == 1 and mapped_to[0] == entity_id:
                # Map item to it self, so no change in here.
                value_result.append(mapping)
                continue
            for new_entity_id in mapped_to:
                value_result.append({
                    "@id": new_entity_id,
                    "metadata": {
                        "reducedFrom": entity_id,
                        **mapping.get("metadata", {}),
                    }
                })
        result.append({
            "metadata": value.get("metadata", None),
            "data": value_result,
        })
    return result


# region Knowledge graph

def _iterate_json_lines(file_path: str) \
        -> typing.Generator[typing.Tuple[int, typing.Dict], None, None]:
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
            json.dump(result, stream, ensure_ascii=False)
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
