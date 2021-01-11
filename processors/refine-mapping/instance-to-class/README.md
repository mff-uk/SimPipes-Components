# Instance to Class Refiner
Update existing mapping. If a mapped entity has only ```instanceOf``` edge, then
the mapping is removed. Mapping to all values of the ```instanceOf``` are added
instead.

## Requirements
- Python 3.8

## Inputs

### Mapping
- Format: Directory of [JSON](https://www.json.org/) files.
- Contents: Metadata with mappings.
- Sample: [Input sample](input-sample/datasets/)

### Hierarchy
- Format: [JSON Lines](https://jsonlines.org/) file.
- Contents: External knowledge hierarchy.
- Sample: [Input sample](input-sample/hierarchy.jsonl)

## Output
- Format: [JSON Lines](https://jsonlines.org/)
- Contents: Metadata with mappings.
- Sample: [Output sample](output-sample/mapping.json)

## Configuration
- ```input``` - Path to input file.
- ```output``` - Path to output file.
- ```sourceProperty``` - Source property with mapping to refine.
- ```targetProperty``` - Property used to store refined mapping to.
- ```knowledge``` - Path to external knowledge hierarchy file.

## Execution
[Script](script)
```shell
python instance-to-class.py \ 
    --input ./input-sample/datasets \
    --output ./output \
    --sourceProperty title_mapping \
    --targetProperty title_mapping_refined \
    --knowledge wikidata-hierarchy.jsonl
```
