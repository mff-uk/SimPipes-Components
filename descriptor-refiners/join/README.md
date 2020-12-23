# Join descriptors

Joins two column-based descriptors in "two column"-based descriptor by sharing same key.

## Requirements

- Python 3.9

## Inputs

- Format: CSV file (`id,descriptor`)
- Contents: Descriptor
- Sample: [Input sample 1](input-sample/nkod-title.csv), [Input sample 2](input-sample/nkod-description.csv)

## Output

- Format: CSV file (`id,descriptor1,descriptor2`)
- Contents: Descriptor
- Sample: [Output sample](output-sample/nkod-_title_description_.join.csv)

## Configuration

- `-l`, `--left`, `--left-input` - path to CSV file containing left descriptor
- `--left-header` - determines if left CSV file has header
- `-r`, `--right`, `--right-input` - path to CSV file containing right descriptor
- `--right-header` - determines if right CSV file has header
- `-o`, `--out`, `--output` - path to output file
- `--rewrite` - rewrite existing output CSV file

## Execution

[Script](script)
```shell
python join.py \
  -l input-sample/nkod-title.csv --left-header \
  -r input-sample/nkod-descriptor.csv --right-header \
  -o output-sample/nkod-_title_description_.join.csv
```