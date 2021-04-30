# CSV to Knowledge
Given CSV file with two columns. The first column is used as a entity identifier,
the second label as a entity label.

## Requirements
- Python 3.8

## Input
- Format: CSV file.
- Contents: Two columns, first with IRI second with label.
- Sample: [Input sample](input-sample/data.csv)

## Output
- Format: [JSON Lines](https://jsonlines.org/) file.
- Contents: Knowledge graph entities.
- Sample: [Output sample](output-sample/data.jsonl)

## Configuration
- ```input``` - Path to CSV file.
- ```output``` - Path to output file.

## Execution
[Script](script)
```shell
python3 csv-to-knowledge.py \
    --input ./input-sample/data.csv \
    --output ./output/data.jsonl
```