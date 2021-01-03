# Reduce database

Reduce database of descriptors by provided keys. Only provided keys are in output file.

## Requirements

- Python 3.9

## Inputs

### Descriptor

- Format: CSV file (`id,descriptor`)
- Contents: Descriptor
- Sample: [Input sample](input-sample/nkod-keywords.concat.csv)

### Keys

- Format: CSV file (`id,*`)
- Contents: Keys
- Sample: [Input sample](input-sample/reduced.csv)

## Output

- Format: CSV file (`row_id,descriptor`)
- Contents: Descriptor
- Sample: [Output sample](output-sample/nkod-keywords.concat.reduce.csv)

## Configuration

- `-i`, `--in`, `--input` - path to CSV file containing descriptors
- `--input-header` - determines if CSV file with descriptors has header
- `-s`, `--sample` - path to CSV file containing keys
- `--sample-header` - determines if CSV file with keys has header
- `-o`, `--out`, `--output` - path to output file
- `--rewrite` - rewrite existing output CSV file

## Execution

[Script](script)
```shell
python reduce.py \
  -i input-sample/nkod-keywords.concat.csv \
  -s input-sample/reduced.csv --sample-header \
  -o output-sample/nkod-keywords.concat.reduce.csv
```
