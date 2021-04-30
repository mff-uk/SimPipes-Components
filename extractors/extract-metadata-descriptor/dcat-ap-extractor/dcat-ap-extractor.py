#!/usr/bin/env python

import argparse
import collections
import json
import os
import logging
import typing

import rdflib

VOCABULARY = {
    "type": "http://www.w3.org/1999/02/22-rdf-syntax-ns#type",
    "Dataset": "http://www.w3.org/ns/dcat#Dataset",
    "keyword": "http://www.w3.org/ns/dcat#keyword",
    "title": "http://purl.org/dc/terms/title",
    "description": "http://purl.org/dc/terms/description",
    "publisher": "http://purl.org/dc/terms/publisher",
    "theme": "http://www.w3.org/ns/dcat#theme",
    "Distribution": "http://www.w3.org/ns/dcat#Distribution",
}


def _parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True,
                        help="Path to DCAT-AP compatible TRIG.")
    parser.add_argument("--output", required=True,
                        help="Path to existing output directory.")
    parser.add_argument("--format", default="trig",
                        help="Specify file loader.")
    parser.add_argument("--language", required=True, nargs="+", metavar="L",
                        help="Languages to extract.")
    return vars(parser.parse_args())


def main(arguments):
    _init_logging()
    #
    logging.info("Processing input file ...")
    if arguments["format"] == "n3-sorted":
        dcat_ap_n3_to_json(
            arguments["input"], arguments["output"], arguments["language"])
    elif arguments["format"] == "trig":
        dcat_ap_trig_to_json(
            arguments["input"], arguments["output"], arguments["language"])
    else:
        raise Exception("Invalid input format.")
    logging.info("Processing input file ... done")


def _init_logging() -> None:
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] - %(message)s",
        datefmt="%m/%d/%Y %H:%M:%S")


def dcat_ap_n3_to_json(
        source_file: str, target_directory: str,
        languages: typing.List[str]) -> None:
    """Load N3 file, where triples are sorted."""
    check_for_dataset = lambda content: VOCABULARY["Dataset"] in content
    for index, graph in enumerate(
            _chunked_by_resource_str(source_file, check_for_dataset)):
        if index % 10000 == 0:
            logging.info("  %s", index)
        dataset = _rdf_graph_to_dataset(graph, languages)
        if dataset is None or len(dataset) == 1:
            # There is only IRI, perhaps the dataset is i na different language.
            continue
        target_path = os.path.join(
            target_directory,
            str(index).zfill(9) + ".json")
        _write_json(target_path, dataset)


def _chunked_by_resource_str(file: str, string_filter=None):
    header = None
    buffer = ""
    with open(file, "r", encoding="utf-8") as input_stream:
        for line in input_stream:
            if header is None:
                header = line[:line.find(" <")]
            if line.startswith(header):
                buffer += line
            else:
                if filter is not None or string_filter(buffer):
                    graph = rdflib.Graph()
                    graph.parse(data=buffer, format="n3")
                    yield graph
                buffer = line
                header = line[:line.find(" <")]
    graph = rdflib.Graph()
    graph.parse(data=buffer, format="n3")
    yield graph


def _rdf_graph_to_dataset(graph, languages: typing.List[str]):
    expected_entity_found = False
    for iri, entity in _rdf_graph_to_entities(graph).items():
        types = [str(x) for x in entity[VOCABULARY["type"]]]
        if VOCABULARY["Distribution"] in types:
            expected_entity_found = True
            continue
        if VOCABULARY["Dataset"] not in types:
            continue
        result = {
            "iri": str(iri),
            "publisher": {"data": entity.get(VOCABULARY["publisher"])},
            "themes": {"data": entity.get(VOCABULARY["theme"])},
        }
        for literal in entity.get(VOCABULARY["title"], []):
            if literal.language in languages:
                key = f"title-{literal.language}"
                result[key] = {"data": [literal.value]}

        for literal in entity.get(VOCABULARY["description"], []):
            if literal.language in languages:
                key = f"description-{literal.language}"
                result[key] = {"data": [literal.value]}

        for literal in entity.get(VOCABULARY["keyword"], []):
            if literal.language in languages:
                key = f"keywords-{literal.language}"
                if key not in result:
                    result[key] = {"data": []}
                result[key]["data"].append(literal.value)

        return result
    if expected_entity_found:
        return None
    for statement in graph:
        print(statement[0], statement[1], statement[2])
    raise Exception("No dataset found!")


def _rdf_graph_to_entities(graph):
    result = {}
    for s, p, o in graph:
        if s not in result:
            result[s] = collections.defaultdict(list)
        result[s][str(p)].append(o)
    return result


def _write_json(path, content):
    with open(path, "w", encoding="utf-8") as output_stream:
        json.dump(content, output_stream, ensure_ascii=False)


def dcat_ap_trig_to_json(
        source_file: str, target_directory: str,
        languages: typing.List[str]) -> None:
    """Load TRIG where each graph is only once."""
    for index, rdf_as_str in enumerate(_for_each_graph(source_file)):
        graph = rdflib.Graph()
        graph.parse(data=rdf_as_str, format="trig")
        dataset = _rdf_graph_to_dataset(graph, languages)
        target_path = os.path.join(
            target_directory,
            str(index).zfill(6) + ".json")
        _write_json(target_path, dataset)


def _for_each_graph(file: str):
    with open(file, "r", encoding="utf-8") as input_stream:
        buffer = ""
        multiline_escape = False
        for line in input_stream:
            strip_line = line.rstrip()
            if '"""' in strip_line:
                multiline_escape = not multiline_escape
            #
            if multiline_escape:
                buffer += line
            elif strip_line.startswith("<") and strip_line.endswith("> {"):
                buffer = ""
            elif strip_line == "}":
                yield buffer
                buffer = ""
            else:
                buffer += line


if __name__ == "__main__":
    main(_parse_arguments())
