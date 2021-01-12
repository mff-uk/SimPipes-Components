# Basic similarities

Computes distance matrix for specified descriptor and similarity/distance measure.

## Requirements

- Python 3.9
    - `tqdm`
    - `json`
    - `numpy`
    - `numba`
    - `linda.descriptors` (provided)
    - `linda.distances` (provided)


## Input

- Format: CSV file (`id,descriptor`)
- Contents: Descriptor
- Sample: [Input sample](input-sample/nkod-keywords.concat.reduce.csv)

## Output

- Format: CSV file (NxN floats)
- Contents: Distance matrix
- Sample: [Output sample](output-sample/nkod-keywords.concat.reduce.sets.jaccard.csv)

## Configuration

- `-i`, `--in`, `--input` - path to CSV file containing descriptors
- `--input-header` - determines if CSV file with descriptors has first row as header
- `--input-column` - determines if CSV file with descriptors has first column as header
- `-t`, `--type`, `--descriptor` - type of descriptor
    - `string` - text
    - `vector` - vector of floats
    - `words_count` - text is split into pairs word and count of occurence
    - `words_set` - text is split into set of words
    - `set` - set
    - `tlsh` - expect 2 columns, and perform TLSH hashing
- `-d`, `--dist`, `--distance` - distance measure
    - `levenshtein` - (type = `string`) Levenshtein distance
    - `jaccard` - (type = `set` or `words_set`) Jaccard distance
    - `angle` - (type = `vector` or `words_count`) Angular distance
    - `cosine` - (type = `words_count`) Cosine distance
    - `cosine_v` - (type = `vector`) Cosine distance
    - `tlsh` - (type = `tlsh`) TLSH distance (based on locally sensitive hashing)
- `-o`, `--out`, `--output` - path to output file
- `--rewrite` - rewrite existing output CSV file

## Execution

[Script](script)
```shell
python matrix.py \
  -i input-sample/nkod-keywords.concat.reduce.csv --input-column \
  -t set -d jaccard \
  -o output-sample/nkod-keywords.concat.reduce.sets.jaccard.csv
```