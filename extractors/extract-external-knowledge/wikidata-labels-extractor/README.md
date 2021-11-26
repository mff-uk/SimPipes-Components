# Wikidata Labels Extractor
Each [Wikidata](https://www.wikidata.org/) entity is identified using an entity
ID. Optionally each entity can have a label per language. In addition, each
entity can have one or mode aliases in each language. This script can be used
to extract label and aliases in given language from a Wikidata 
JSON [dump](https://dumps.wikimedia.org/other/wikidata/20181217.json.gz).

## Requirements
- Python 3.8

## Input
- Format: [JSON](https://www.json.org/) file.
- Contents: Content of https://dumps.wikimedia.org/other/wikidata/ dump JSON file.
- Sample: [Input sample](input-sample/wikidata.json)

## Output
- Format: [JSON Lines](https://jsonlines.org/) file.
- Contents: Knowledge graph entity labels.
- Sample: [Output sample](output-sample/labels.jsonl)

## Configuration
- ```input``` - Path to Wikidata JSON dump file.
- ```output``` - Path to output file.
- ```language``` - Language to extract.

## Execution
[Script](script)
```shell
python3 wikidata-labels-extractor.py \
    --input ./input-sample/wikidata.json \
    --output ./output-sample/labels.jsonl \
    --language cs
```
