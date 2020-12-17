# Bag of Words Mapper
Map entities from a knowledge graph to dataset properties.

## Requirements
- Python 3.9

## Inputs

### Datasets
- Format: [JSON Lines](https://jsonlines.org/) file.
- Contents: Dataset metadata.
- Sample: [Input sample](input-sample/dataset.json)

### Knowledge graph labels
- Format: [JSON](https://www.json.org/) files.
- Contents: Knowledge graph hierarchy.
- Sample: [Input sample](input-sample/labels.jsonl)

## Output
- Format: [JSON](https://www.json.org/) files.
- Contents: Mapping of datasets metadata into knowledge graph.
- Sample: [Output sample](output-sample/mapping.json)

## Configuration
- ```datasets``` - Path to datasets metadata file
- ```input``` - Path to input file.
- ```output``` - Path to output file.
- ```mapping``` - ```{source}:{target}``` property name pairs.
- ```knowledge-graph``` - Path to knowledge graph data.

## Execution
[Script](script)
```shell
python map-bag-of-words.py \
    --datasets ./input-sample/datasets.jsonl \
    --knowledge-graph ./input-sample/labels.jsonl \
    --output ./output \
    --mapping title:title_mapping \
    --mapping description:description_mapping
```
