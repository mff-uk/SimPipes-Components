# Hausdorff

Computes Hausdorff distance matrix for specified (text) descriptor, Word2Vec model and ground similarity/distance measure. It computes Word2Vec vector for every word in text. Set of these vectors is used to compute Hausdorff distance.

## Requirements

- Python 3.9
    - `tqdm`
    - `json`
    - `numpy`
    - `numba`
    - `multiprocessing`
    - `gensim.models`
    - `linda.descriptors` (provided)
    - `linda.distances` (provided)


## Inputs

### Descriptor

- Format: CSV file (`id,descriptor`)
- Contents: Descriptor (text)
- Sample: [Input sample](input-sample/nkod-description.udpipe-f.reduce.csv)

### Word2Vec Model

- Format: [Gensim Word2Vec Model](https://radimrehurek.com/gensim/models/word2vec.html)
- Contents: Word2Vec model
- Sample: [Input sample](https://doi.org/10.5281/zenodo.3975084)

## Output

- Format: CSV file (NxN floats)
- Contents: Distance matrix
- Sample: [Output sample](output-sample/nkod-description.udpipe-f.reduce.set.hausdorff[cosine_v].csv)

## Configuration

- `-i`, `--in`, `--input` - path to CSV file containing descriptors
- `--input-header` - determines if CSV file with descriptors has first row as header
- `--input-column` - determines if CSV file with descriptors has first column as header
- `-v`, `--vectors` - Word2Vec model
- `-t`, `--type`, `--descriptor` - type of descriptor
    - `words_set` - text is split into set of words
    - `set` - set
- `-d`, `--dist`, `--distance` - distance measure
    - `angle` - Angular distance
    - `cosine`, `cosine_v` - Cosine distance (`_v` optimized variant)
- `-o`, `--out`, `--output` - path to output file
- `--rewrite` - rewrite existing output CSV file
- `--parallel` - use parallel computing

## Execution

[Script](script)
```shell
python hausdorff.py \
  -i input-sample/nkod-description.udpipe-f.reduce.csv --input-column \
  -m input-sample/law.word2vec \
  -t set -d cosine_v \
  -o output-sample/nkod-description.udpipe-f.reduce.set.hausdorff[law].csv \
  --parallel
```

