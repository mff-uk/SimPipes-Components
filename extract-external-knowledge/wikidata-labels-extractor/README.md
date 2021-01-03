# Wikidata Labels Extractor
Extracts label and aliases for given language from Wikidata.

## Requirements
- Python 3.9

## Input
- Format: [JSON](https://www.json.org/) file.
- Contents: Content of https://dumps.wikimedia.org/other/wikidata/ dump JSON file.
- Sample: [Input sample](input-sample/wikidata.json)

## Output
- Format: [JSON Lines](https://jsonlines.org/) file.
- Contents: Knowledge graph entity metadata.
- Sample: [Output sample](output-sample/labels.jsonl)

## Configuration
- ```language``` - Extract metadata for given language.
- ```input``` - Path to input file.
- ```output``` - Path to output file.

## Execution
[Script](script)
```shell
python extract-wikidata-labels.py \
    --language cs \
    --input ./input-sample/wikidata.json \
    --output ./labels.jsonl
```
