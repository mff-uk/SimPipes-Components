#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Transform TRIG file into JSON-LINES.
#

import argparse
import collections
import json
import os
import logging

import rdflib

VOCABULARY = {
    "type": "http://www.w3.org/1999/02/22-rdf-syntax-ns#type",
    "Dataset": "http://www.w3.org/ns/dcat#Dataset",
    "keyword": "http://www.w3.org/ns/dcat#keyword",
    "title": "http://purl.org/dc/terms/title",
    "description": "http://purl.org/dc/terms/description"
}


def _parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True,
                        help="Path to DCAT-AP compatible TRIG.")
    parser.add_argument("--output", required=False,
                        help="Path to output directory.")
    return vars(parser.parse_args())


def main(arguments):
    _init_logging()
    if not os.path.exists(arguments["output"]):
        os.makedirs(arguments["output"], exist_ok=True)
    dcat_ap_trig_to_json(arguments["input"], arguments["output"])


def _init_logging() -> None:
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] - %(message)s",
        datefmt="%m/%d/%Y %H:%M:%S")


def dcat_ap_trig_to_json(source_file, target_directory):
    for index, rdf_as_str in enumerate(_for_each_graph(source_file)):
        graph = rdflib.Graph()
        graph.parse(data=rdf_as_str, format="trig")
        dataset = _rdf_graph_to_dataset(graph)
        if dataset is None:
            continue
        target_path = os.path.join(
            target_directory,
            str(index).zfill(6) + ".json")
        with open(target_path, "w", encoding="utf-8") as output_stream:
            json.dump(dataset, output_stream)


def _for_each_graph(file):
    with open(file, "r", encoding="utf-8") as input_stream:
        buffer = ""
        for line in input_stream:
            strip_line = line.rstrip()
            if strip_line.startswith("<") and strip_line.endswith("> {"):
                buffer = ""
            elif strip_line == "}":
                yield buffer
                buffer = ""
            else:
                buffer += line


def _rdf_graph_to_dataset(graph):
    for iri, entity in _rdf_graph_to_entities(graph).items():
        types = [str(x) for x in entity[VOCABULARY["type"]]]
        if VOCABULARY["Dataset"] not in types:
            continue
        title = str(entity[VOCABULARY["title"]][0])
        description = str(entity[VOCABULARY["description"]][0])
        keywords = [str(keyword) for keyword in entity[VOCABULARY["keyword"]]]
        return {
            "iri": str(iri),
            "title": title,
            "description": description,
            "keywords": keywords,
        }


def _rdf_graph_to_entities(graph):
    result = {}
    for s, p, o in graph:
        if s not in result:
            result[s] = collections.defaultdict(list)
        result[s][str(p)].append(o)
    return result


if __name__ == "__main__":
    main(_parse_arguments())
