# Wikidata Hierarchy Extractor
Each [Wikidata](https://www.wikidata.org/) entity is identified using an entity
ID. Optionally each entity can have multiple snacks/annotations. Those may 
represent a connection/relation to another Wikidata entity. We consider these
annotations to be edges in the Wikidata knowledge graph. This component can be
used extract to ```P31``` as ```instanceOf``` and ```P279``` as ```subclassOf```
edges from a Wikidata JSON 
[dump](https://dumps.wikimedia.org/other/wikidata/20181217.json.gz).

## Requirements
- Python 3.8

## Input
- Format: [JSON](https://www.json.org/) file.
- Contents: Content of https://dumps.wikimedia.org/other/wikidata/ dump JSON file.
- Sample: [Input sample](input-sample/wikidata.json)

## Output
- Format: [JSON Lines](https://jsonlines.org/) file.
- Contents: Knowledge graph entity outcoming annotations/edges.
- Sample: [Output sample](output-sample/hierarchy.jsonl)

## Configuration
- ```input``` - Path to Wikidata JSON dump file.
- ```output``` - Path to output file.

## Execution
[Script](script)
```shell
python3 wikidata-hierarchy-extractor.py \
    --input ./input-sample/wikidata.json \
    --output ./output-sample/hierarchy.jsonl
```
