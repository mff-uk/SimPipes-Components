# Concatenate CSV rows

Concatenate CSV rows by first column.

## Requirements

- Python 3.9

## Input

- Format: CSV file (`id,descriptor`)
- Contents: Descriptor
- Sample: [Input sample](input-sample/nkod-keywords.csv)

## Output

- Format: CSV file (`id,descriptor,*`)
- Contents: Descriptor
- Sample: [Output sample](output-sample/nkod-keywords.concat.csv)

## Configuration

- `-i`, `--in`, `--input` - path to CSV file containing descriptors
- `--input-header` - determines if CSV file with descriptors has header
- `-o`, `--out`, `--output` - path to output file
- `--rewrite` - rewrite existing output CSV file

## Execution

[Script](script)
```shell
python concat.py \
  -i input-sample/nkod-keywords.csv --input-header \
  -o output-sample/nkod-keywords.concat.csv
```
