# Bag of Words Mapper
Map values of datasets properties into entities of external knowledge.
The mapping utilizes textual values that are converted into bag of words.
The mapping is created if the knowledge entity bag of words share more than 
given percentage of words with the bag of words of the dataset property.  
 
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
- Sample: [Output sample](output-sample/mapping.json)

## Configuration
- ```input``` - Path to datasets descriptor files.
- ```entities``` - Path to knowledge graph labels data file.
- ```output``` - Path to output file.
- ```sourceProperty``` - Name of property to load values from mapping from.
- ```targetProperty``` - Name of property to save mappings into.
- ```sharedThreshold``` - How many of the words must be shared in order to 
                          create a mapping.

## Execution
[Script](script)
```shell
python3 map-bag-of-words.py \
    --input ./input-sample/datasets/ \
    --entities ./input-sample/labels.jsonl \
    --output ./output \
    --sourceProperty title \
    --targetProperty title_mapping \
    --sharedThreshold 0.66
```
