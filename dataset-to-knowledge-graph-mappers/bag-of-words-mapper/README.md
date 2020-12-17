# Bag of Words Mapper
Map entities from a knowledge graph to dataset properties.

## Requirements
- Python 3.9

## Inputs

### Datasets
- Format: [JSON Lines](https://jsonlines.org/) file.
- Contents: Content of https://dumps.wikimedia.org/other/wikidata/ dump JSON file.
- Sample: [Input sample](input-sample/dataset.json)

### Knowledge graph labels
- Format: [JSON](https://www.json.org/) files.
- Contents: Content of https://dumps.wikimedia.org/other/wikidata/ dump JSON file.
- Sample: [Input sample](input-sample/labels.jsonl)

## Output
- Format: [JSON](https://www.json.org/) files.
- Contents: Knowledge graph entity metadata.
- Sample: [Output sample](output-sample/dataset.json)

## Configuration
- ```datasets``` - Path to datasets metadata file
- ```input``` - Path to input file.
- ```output``` - Path to output file.
- ```mapping``` - ```{source}:{target}``` property name pairs.

## Execution
[Script](script)
```shell
python map-bag-of-words.py \
    --datasets ./input-sample/datasets.jsonl \
    --knowledge-graph ./input-sample/labels.jsonl \
    --output ./mapping.jsonl \
    --mapping title:title_mapping \
    --mapping description:description_mapping
```
