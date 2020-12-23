# PR curve evaluation

Evaluates efficiency of similarity model considering baseline. It will compute 11-point PR curve.

## Requirements

- Python 3.9
    - `tqdm`
    - `json`
    - `numpy`


## Inputs

### Distance matrix

- Format: CSV file (NxN floats)
- Contents: Distance matrix
- Sample: [Input sample](input-sample/distance.csv)

### Mapping file

- Format: CSV file (`id,*`)
- Contents: Original keys before reduce
- Sample: [Input sample](input-sample/reduced.csv)

### Baseline

- Format: JSON file
- Contents: Baseline searches
- Sample [Input sample](input-sample/baseline.json)

## Output

- `array of number` - 11-point PR curve of model.

## Configuration

- `-d`, `--distance` - path to CSV file containing distance matrix
- `--distance-has-header-row` - determines if CSV file with distance matrix has first row as header
- `--distance-has-header-column` - determines if CSV file with distance matrix has first column as header
- `-m`, `--map` - path to mapping CSV rows into IDs.
- `--map-has-header-row` - determines if CSV file with mapping has first row as header
- `-b`, `--baseline` - path to JSON file with baseline
- `-agg`, `--aggregation` - aggregation of distances in case of multiple query objects
    - `min` - minimum¨
    - `avg` - average
    - `max` - maximum

## Execution

[Script](script)
```shell
python validation.py \
  -d input-sample/distance.csv \
  -m input-sample/reduced.csv \
  -b input-sample/baseline.json \
  --agg min
```