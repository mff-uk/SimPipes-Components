# Mapping summary
Print out statistics about mappings.

## Requirements
- Python 3.8
- Libraries as specified in ```requirements.txt```.

## Inputs
- Format: Directory of [JSON](https://www.json.org/) files.
- Contents: Dataset metadata.
- Sample: [Input sample](input-sample/)

## Output

## Configuration
- ```input``` - Path to input datasets descriptor files.
- ```property``` - Name of properties to load mappings from.

## Execution
[Script](script)
```shell
python mapping-summary.py  \
  --input ./input-sample \ 
  --property title_mapping description_mapping
```
