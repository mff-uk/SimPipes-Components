# Translate JSON
Translate string descriptors, using [Lindat Service](https://lindat.mff.cuni.cz/services/translation).

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
- ```sourceLanguage``` - Language to translate from.
- ```targetLanguage``` - Language to translate to.
- ```join``` - If set, then the strings arrays on input are joined to a
  single string before translation. They are split again after the translation
  is done.
- ```waitTime``` - Wait time between requests in ms.

## Execution
[Script](script)
```shell
python translate-json.py --input ./input-sample --output ./output-sample --sourceProperty title keywords --targetProperty title-en keywords-en --sourceLanguage cs --targetLanguage en --join
```
