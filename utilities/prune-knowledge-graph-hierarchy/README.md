# Prune knowledge graph hierarchy
Repeatedly remove all leaves from the knowledge graph hierarchy, that 
are not part of the dataset mapping nor are ancestors of mapped node.

## Requirements
- Python 3.9

## Inputs
- Format: [JSON](https://www.json.org/) files.
- Contents: Dataset metadata.
- Sample: [Input sample](input-sample/dataset.json)

## Output
- Format: [JSON](https://www.json.org/) files.
- Contents: Dataset metadata.
- Sample: [Output sample](output-sample/mapping.json)

## Configuration
- ```datasets``` - Path to datasets metadata file
- ```output``` - Path to output file.

## Execution
[Script](script)
```shell
python prune-knowledge-graph-hierarchy.py \
    --datasets ./input-sample/datasets.jsonl \
    --output ./output \
```
