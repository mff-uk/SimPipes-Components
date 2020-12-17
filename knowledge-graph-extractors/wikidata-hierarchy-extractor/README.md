# Wikidata Hierarchy Extractor
Extracts hierarchy from Wikidata. Use ```P31``` as ```instanceOf``` and 
```P279``` as ```subclassOf```. 

## Requirements
- Python 3.9

## Input
- Format: [JSON](https://www.json.org/) file.
- Contents: Content of https://dumps.wikimedia.org/other/wikidata/ dump JSON file.
- Sample: [Input sample](input-sample/wikidata.json)

## Output
- Format: [JSON Lines](https://jsonlines.org/) file.
- Contents: Knowledge graph hierarchy.
- Sample: [Output sample](output-sample/hierarchy.jsonl)

## Configuration
- ```input``` - Path to input file.
- ```output``` - Path to output file.

## Execution
[Script](script)
```shell
python extract-wikidata-hierarchy.py \
    --input ./input-sample/hierarchy.json \
    --output ./hiearchy.jsonl
```
