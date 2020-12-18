# Add knowledge graph hierarchy
Add all ancestors for given entities to a dataset.

## Requirements
- Python 3.9

## Inputs

### Datasets
- Format: [JSON](https://www.json.org/) files.
- Contents: Dataset metadata.
- Sample: [Input sample](input-sample/dataset.json)

### Knowledge graph labels
- Format: [JSON Lines](https://jsonlines.org/) file.
- Contents: Knowledge graph hierarchy.
- Sample: [Input sample](input-sample/labels.jsonl)

## Output
- Format: [JSON](https://www.json.org/) files.
- Contents: Mapping of datasets metadata into knowledge graph.
- Sample: [Output sample](output-sample/mapping.json)

## Configuration
- ```datasets``` - Path to datasets metadata file
- ```knowledge-graph``` - Path to knowledge graph data.
- ```output``` - Path to output file.

## Execution
[Script](script)
```shell
python add-knowledge-graph-hierarchy.py \
    --datasets ./input-sample/datasets.jsonl \
    --knowledge-graph ./input-sample/hierarchy.jsonl \
    --output ./output \
```
