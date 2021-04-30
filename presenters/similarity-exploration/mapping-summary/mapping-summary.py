#!/usr/bin/env python3

import json
import os
import logging
import typing
import argparse
import itertools
import collections
from pprint import pprint
import dataclasses


@dataclasses.dataclass
class Statistics:
    def __init__(self):
        # Entities mapped to.
        self.entities = set()
        # Datasets mapped to.
        self.mapped_datasets = set()


def _parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True,
                        help="Path to input descriptor directory.")
    parser.add_argument("--output", required=True,
                        help="Path to output json file.")
    parser.add_argument("--property", metavar="P", nargs="+",
                        help="Properties with mappings.")
    parser.add_argument("--labels",
                        help="Path to json lines file with labels.")
    return vars(parser.parse_args())


def main(arguments):
    _init_logging()
    create_summary(arguments)


# region Utils

def _init_logging() -> None:
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] - %(message)s",
        datefmt="%m/%d/%Y %H:%M:%S")


# endregion

def create_summary(arguments):
    labels = _load_labels(arguments)

    properties = arguments["property"]
    statistics = {
        property: Statistics()
        for property in properties
    }

    statistics_global = Statistics()
    dataset_count = 0

    print("## Datasets")
    with open(arguments["output"], "w", encoding="utf-8") as output_stream:
        output_stream.write("[")
        first = True
        for path in with_progress(_iterate_files(arguments["input"])):
            content = _load_json(path)
            dataset_count += 1
            iri = content["iri"]
            for property, stats in statistics.items():
                _update_statistics(iri, content.get(property, None), stats)
                _update_statistics(iri, content.get(property, None), statistics_global)
            dataset = _transform_dataset(labels, properties, content)
            if first:
                first = False
            else:
                output_stream.write(",")
            output_stream.write("\n")
            json.dump(dataset, output_stream, indent=2, ensure_ascii=False)
        output_stream.write("\n]")

    print("## Statistics")
    for property, stats in statistics.items():
        print(property)
        print(f"  entities       : {len(stats.entities)}")
        print(f"  mapped datasets: {len(stats.mapped_datasets)}")
    print("global")
    print(f"  entities       : {len(statistics_global.entities)}")
    print(f"  mapped datasets: {len(statistics_global.mapped_datasets)}")
    print(f"  datasets count : {dataset_count}")


def _load_labels(arguments):
    if "labels" not in arguments:
        return {}
    result = {}
    with open(arguments["labels"], encoding="utf-8") as stream:
        for line_as_str in stream:
            line_json = json.loads(line_as_str)
            result[line_json["@id"]] = line_json["label"][0]
    return result


def with_progress(generator, step=1000):
    index = 0
    logging.info("Processing ...")
    for index, item in enumerate(generator):
        yield item
        if index % step == 0:
            logging.info("  %i", index)
    logging.info("  %i", index)
    logging.info("Processing ... done")


def _iterate_files(directory):
    for file_name in os.listdir(directory):
        yield os.path.join(directory, file_name)


def _load_json(path):
    with open(path, encoding="utf-8") as stream:
        return json.load(stream)


def _transform_dataset(labels, properties, dataset):
    result = {
        "iri": dataset["iri"],
        "title": dataset["title"],
        "description": dataset["description"],
        "keywords": dataset["keywords"],
        "themes": [
            {
                "@id": iri,
                "label": labels.get(iri, None)
            }
            for iri in dataset.get("themes", [])
        ],
        "mapping": {}
    }
    for property in properties:
        mapped_themes = [
            item["id"]
            for item in dataset.get(property, {"data": []})["data"]
        ]
        if len(mapped_themes) == 0:
            continue
        result["mapping"][property] = {}

        new_themes = _collect_mappings(labels, mapped_themes, lambda iri: iri not in result["themes"])
        if len(new_themes) > 0:
            result["mapping"][property]["new"] = new_themes

        new_themes = _collect_mappings(labels, mapped_themes, lambda iri: iri in result["themes"])
        if len(new_themes) > 0:
            result["mapping"][property]["confirmed"] = new_themes

    return result


def _collect_mappings(labels, mappings, condition_fnc):
    return [
        {
            "@id": iri,
            "label": labels.get(iri, None)
        }
        for iri in mappings if condition_fnc(iri)
    ]


def _update_statistics(dataset_iri, mappings, statistics:Statistics):
    if mappings is None:
        return
    for item in mappings["data"]:
        statistics.entities.add(item["id"])
    if len(mappings["data"]) > 0:
        statistics.mapped_datasets.add(dataset_iri)

if __name__ == "__main__":
    main(_parse_arguments())
