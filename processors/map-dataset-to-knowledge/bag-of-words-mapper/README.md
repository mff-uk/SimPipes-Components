# Bag of Words Mapper
Map values of datasets properties into entities of external knowledge.
The mapping utilizes textual values that are converted into bag of words.
The mapping is created if the knowledge entity bag of words share more than 
given percentage of words with the bag of words of the dataset property. 

We only require the tokens to be in the given text, for entity with label 
```A B C``` and text ```0 A B C 1``` we got match with 100%. We also get with 
```0 A 1 B 2 C``` or ```C B A```.
 
Tokens as  ```"(", ")", ".", "?", "!", "-", ",", "}", "{"``` can not on its 
own initiate check for mapping, but they can contribute to it.

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
- ```sharedThreshold``` - How many of the words must be shared in order to 
                          create a mapping.
- ```normalize``` - Normalize tokens before mapping, i.e., make lowercase. 
- ```pretty``` - Pretty print the output.

## Execution
[Script](script)
```shell
python3 map-bag-of-words.py \
  --input ./input-sample/datasets/ \
  --entities ./input-sample/labels.jsonl \
  --output ./output-sample \
  --sourceProperty description keywords \
  --targetProperty description_mapped keywords_mapped \ 
  --sharedThreshold 0.66 --normalize --pretty
```
