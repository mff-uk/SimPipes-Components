# Exact Match Mapper
Map values of datasets properties into entities of external knowledge. The 
mapping requires exact match, where the value in the external knowledge
must be in the dataset descriptor.

We require the tokens to be in the given text in given order, for entity with 
label ```A B C``` and text ```0 A B C 1``` we do not got match, same for
```0 A 1 B 2 C``` or ```C B A```. We only get match for ```A B C``` or 
```G A B C H```.

## Requirements
- Python 3.8

## Inputs

### Datasets
- Format: Directory of [JSON](https://www.json.org/) files.
- Contents: Dataset metadata.
- Sample: [Input sample](input-sample/dataset/)

### Knowledge graph labels
- Format: [JSON Lines](https://jsonlines.org/) file.
- Contents: Knowledge graph hierarchy.
- Sample: [Input sample](input-sample/labels.jsonl)

## Output
- Format: Directory of [JSON](https://www.json.org/) files.
- Contents: Mapping of datasets metadata into knowledge graph.
- Sample: [Output sample](output-sample/000000.json)

## Configuration
- ```input``` - Path to datasets descriptor files.
- ```entities``` - Path to knowledge graph labels data file.
- ```output``` - Path to output file.
- ```sourceProperty``` - Name of property to load values from mapping from.
- ```targetProperty``` - Name of property to save mappings into.
- ```normalize``` - Normalize tokens before mapping, i.e., make lowercase.
- ```pretty``` - Pretty print the output.

## Execution
[Script](script)
```shell
python3 exact-match-mapper.py \
  --input ./input-sample/datasets/ \
  --entities ./input-sample/labels.jsonl \
  --output ./output-sample \
  --sourceProperty description keywords \
  --targetProperty description_mapped keywords_mapped \
  --normalize --pretty
```
