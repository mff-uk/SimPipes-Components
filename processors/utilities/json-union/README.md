# Instance to Class Refiner
Perform union of dataset descriptors. Effectively append one array of values
at the end of another.

## Requirements
- Python 3.8

## Input
- Format: Directory of [JSON](https://www.json.org/) files.
- Contents: Dataset descriptors.
- Sample: [Input sample](input-sample/datasets)

## Output
- Format: Directory of [JSON](https://www.json.org/) files.
- Contents: Dataset descriptors.
- Sample: [Output sample](output-sample/datasets)

## Configuration
- ```input``` - Path to input file.
- ```output``` - Path to output file.
- ```sourceProperty``` - List of names of properties to join.
- ```targetProperty``` - Name of a property to save result into.

## Execution
[Script](script)
```shell
python3 json-union.py \ 
    --input ./input-sample/datasets \
    --output ./output \
    --sourceProperty title keywords \
    --targetProperty title_keywords
```
