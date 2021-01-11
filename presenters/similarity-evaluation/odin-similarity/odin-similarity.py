#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import json
import os
import logging
import typing
import csv


def _parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--datasets", required=True,
                        help="Path to directory with datasets.")
    parser.add_argument("--similarity", required=True,
                        help="Path to CSV dataset similarity matrix file.")
    parser.add_argument("--csvWithIri", required=True,
                        help="Path to a CSV with dataset's IRIs.")
    parser.add_argument("--similarityName", required=True,
                        help="How to name imported similarity.")
    parser.add_argument("--odinDirectory", required=True,
                        help="Path to an existing ODIN data directory.")
    return vars(parser.parse_args())


def main(arguments):
    _init_logging()
    _import_similarity_to_odin(arguments)


# region Utils

def _init_logging() -> None:
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] - %(message)s",
        datefmt="%m/%d/%Y %H:%M:%S")


# endregion


def _import_similarity_to_odin(arguments):
    # Prepare datasets metadata.
    iri_to_file_name = _prepare_iri_to_file_name(
        arguments["datasets"], arguments["odinDirectory"])
    # _prepare_datasets(
    #     arguments["datasets"], arguments["odinDirectory"], iri_to_file_name)
    # Import similarities.
    output_directory = os.path.join(
        arguments["odinDirectory"], "similarities", arguments["similarityName"])
    os.makedirs(output_directory, exist_ok=True)
    _import_similarity(
        iri_to_file_name,
        arguments["csvWithIri"], arguments["similarity"],
        output_directory)


def _import_similarity(
        iri_to_file_name: typing.Dict[str, str],
        iri_file: str, similarity_matrix_file: str,
        target_directory: str) -> None:
    iris = _prepare_datasets_csv_file(iri_file, target_directory)
    logging.info("importing similarity matrix ...")
    row_index = 0
    with open(similarity_matrix_file) as stream:
        reader = csv.reader(stream, delimiter=",")
        for row_index, [row, iri] in enumerate(zip(reader, iris)):
            rows = [
                [_str_to_float(x)]
                for index, x in enumerate(row)
            ]
            # We need to remove 'inf' values. So we replace them with max +1.
            output_path = os.path.join(
                target_directory, iri_to_file_name[iri] + ".csv")
            _write_csv(output_path, ["score"], rows)
            if row_index % 1000 == 0:
                logging.info("    %s", row_index)
    logging.info("    %s", row_index)
    logging.info("importing similarity matrix ... done")


def _prepare_datasets_csv_file(
        input_file: str, target_directory: str) -> typing.List[str]:
    output_file = os.path.join(target_directory, "datasets.csv")
    iris = _read_dataset_iris(input_file)
    _write_csv(output_file, ["iri"], [[iri] for iri in iris])
    return iris


def _read_dataset_iris(path):
    with open(path, encoding="utf-8") as stream:
        reader = csv.reader(stream, delimiter=",", quotechar='"')
        next(reader)
        return [line[0] for line in reader]


def _write_csv(file_path, header, rows):
    with open(file_path, "w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(
            stream, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL)
        if header is not None:
            writer.writerow(header)
        for row in rows:
            writer.writerow(row)


def _str_to_float(value: str) -> float:
    return float(value)


# region Open Data Inspector


def _prepare_iri_to_file_name(input_directory: str, odinDirectory: str) \
        -> typing.Dict[str, str]:
    logging.info("Preparing index ...")
    iri_to_file_name = _load_iri_to_file_name(odinDirectory)
    for _, _, content in _iterate_input_files(input_directory):
        iri = content["iri"]
        if iri in iri_to_file_name:
            continue
        new_file_name = str(len(iri_to_file_name)).zfill(6)
        iri_to_file_name[iri] = new_file_name
    _save_iri_to_file_name(odinDirectory, iri_to_file_name)
    logging.info("Preparing index ... done")
    return iri_to_file_name


def _load_iri_to_file_name(directory: str) -> typing.Dict[str, str]:
    mapping_file = os.path.join(
        directory, "dataset-iri-to-file-name.json")
    if not os.path.exists(mapping_file):
        return {}
    with open(mapping_file, "r", encoding="utf-8") as stream:
        return json.load(stream)


def _save_iri_to_file_name(
        directory: str, mapping: typing.Dict[str, str]) -> None:
    mapping_file = os.path.join(
        directory, "dataset-iri-to-file-name.json")
    _save_json(mapping_file, mapping)


def _save_json(file: str, content) -> None:
    with open(file, "w", encoding="utf-8") as stream:
        return json.dump(content, stream)


def _prepare_datasets(
        input_directory: str, odin_directory: str,
        iri_to_file_name: typing.Dict[str, str]) -> None:
    logging.info("Loading datasets to ODIN ...")
    os.makedirs(os.path.join(odin_directory, "datasets"), exist_ok=True)
    index = 0
    for index, _, content in _iterate_input_files(input_directory):
        if index % 1000 == 0:
            logging.info("    %s", index)
        #
        iri = content["iri"]
        file_name = iri_to_file_name[iri]
        file = os.path.join(odin_directory, "datasets", file_name + ".json")
        if os.path.exists(file):
            continue
        _save_json(
            file,
            {
                "iri": iri,
                "title": content["title"],
                "description": content["description"],
                "keywords": content["keywords"]
            }
        )
    logging.info("    %s", index)
    logging.info("Loading datasets to ODIN ... done")


# endregion


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


def _iterate_input_files(input_directory: str):
    for index, file_name in enumerate(os.listdir(input_directory)):
        input_file = os.path.join(input_directory, file_name)
        with open(input_file, "r", encoding="utf-8") as stream:
            input_content = json.load(stream)
        yield index, file_name, input_content


# endregion


if __name__ == "__main__":
    main(_parse_arguments())
