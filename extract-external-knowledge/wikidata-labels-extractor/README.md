# Wikidata Labels Extractor
Each [Wikidata](https://www.wikidata.org/) entity is identified using an entity
ID. Optionally each entity can have a label per language. In addition, each
entity can have one or mode aliases in each language. This script can be used
to extract label and aliases in given language from a Wikidata 
JSON [dump](https://dumps.wikimedia.org/other/wikidata/20181217.json.gz).

## Requirements
- Python 3.9

## Input
- Format: [JSON](https://www.json.org/) file.
- Contents: Content of https://dumps.wikimedia.org/other/wikidata/ dump JSON file.
- Sample: [Input sample](input-sample/wikidata.json)

## Output
- Format: [JSON Lines](https://jsonlines.org/) file.
- Contents: Knowledge graph entity labels.
- Sample: [Output sample](output-sample/labels.jsonl)

## Execution
[Script](script)
```shell
python3 wikidata-labels-extractor \
    --language cs \
    --input ./input-sample/wikidata.json \
    --output ./output/labels.jsonl
```
