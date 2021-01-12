# Vectorize text descriptor

Converts text into average vector of provided Word2Vec embedding.

## Requirements

- Python 3.9
    - `numpy`
    - `json`
    - `tqdm`
    - `gensim.models`

## Inputs

### Descriptor

- Format: CSV file (`id,descriptor`)
- Contents: Descriptor (text)
- Sample: [Input sample](input-sample/nkod-title.udpipe-f.reduce.csv)

### Word2Vec Model

- Format: [Gensim Word2Vec Model](https://radimrehurek.com/gensim/models/word2vec.html)
- Contents: Word2Vec model
- Sample: [Input sample](https://doi.org/10.5281/zenodo.3975084)

## Output

- Format: CSV file (`id,descriptor,...`)
- Contents: Vector
- Sample: [Output sample](output-sample/nkod-title.udpipe-f.reduce.word2vec[law].csv)

## Configuration

- `-i`, `--in`, `--input` - path to CSV file containing descriptors
- `--input-header` - determines if CSV file with descriptors has header
- `-m`, `--model` - path to Gensim Word2Vec model
- `-o`, `--out`, `--output` - path to output file
- `--rewrite` - rewrite existing output CSV file

## Execution

[Script](script)
```shell
python reduce.py \
  -i input-sample/nkod-title.udpipe-f.reduce.csv \
  -m input-sample/law.word2vec \
  -o output-sample/nkod-title.udpipe-f.reduce.word2vec[law].csv
```
