# Tokenize JSON
Split string values using spaces. If a value is already tokenized, array 
of strings, it is left unchanged.

## Requirements
- Python 3.8

## Inputs
- Format: Directory of [JSON](https://www.json.org/) files.
- Contents: Dataset metadata.
- Sample: [Input sample](input-sample/)

## Output
- Format: Directory of [JSON](https://www.json.org/) files.
- Contents: Dataset metadata.
- Sample: [Output sample](output-sample/)

## Configuration
- ```input``` - Path to input datasets descriptor files.
- ```output``` - Path to output directory.
- ```sourceProperty``` - Name(s) of property to load values from.
- ```targetProperty``` - Name(s) of property to save transformed values into.

## Execution
[Script](script)
```shell
python tokenize-json.py --input ./input-sample --output ./output-sample --sourceProperty description keywords --targetProperty description-tokens keywords-tokens
```
