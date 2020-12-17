# Instance to Class Refiner
Update mapping from entities for concepts. If a mapped entity has
```instanceOf``` edge remove mapping from this entity and add mapping
to all entities on the other side of the edge.

## Requirements
- Python 3.9

## Inputs

### Mapping
- Format: [JSON](https://www.json.org/) files.
- Contents: Metadata with mappings.
- Sample: [Input sample](input-sample/mapping.json)

### Hierarchy
- Format: [JSON Lines](https://jsonlines.org/) file.
- Contents: Knowledge graph hierarchy.
- Sample: [Input sample](input-sample/hierarchy.jsonl)

## Output
- Format: [JSON Lines](https://jsonlines.org/)
- Contents: Metadata with mappings.
- Sample: [Output sample](output-sample/mapping.json)

## Configuration
- ```input``` - Path to input file.
- ```output``` - Path to output file.
- ```refine``` - ```{source}:{target}``` property name pairs.

## Execution
[Script](script)
```shell
python instace-to-class-refiner.py \ 
    --input ./input-sample/mapping.json
    --output ./mapping.json \
    --refine title_mapping:title_mapping_refined
```
