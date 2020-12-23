# UDPipe preprocessing

Preprocess text descriptor by lemmatizer UDPipe using pretrained model.

## Requirements

- Python 3.9
    - `tqdm`
    - `ufal.udpipe`

## Inputs

### Descriptor

- Format: CSV file (`id,descriptor`)
- Contents: Descriptor (text)
- Sample: [Input sample](input-sample/nkod-title.csv)

### Model

- Format: [UDPipe](http://ufal.mff.cuni.cz/udpipe/1/models#universal_dependencies_25_models)
- Contents: UDPipe model
- Sample [Input sample](https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-3131/czech-pdt-ud-2.5-191206.udpipe?sequence=19&isAllowed=y)

## Output

- Format: CSV file (`id,descriptor`)
- Contents: Descriptor (text lemmatized)
- Sample: [Output sample](output-sample/nkod-title.udpipe-f.csv)

## Configuration

- `-i`, `--in`, `--input` - path to CSV file containing descriptors
- `--input-header` - determines if CSV file with descriptors has header
- `-m`, `--model` - path to UDPipe model
- `-f`, `--filter` - filter only nouns, verbs, adjectives and adverbs
- `-o`, `--out`, `--output` - path to output file
- `--rewrite` - rewrite existing output CSV file

## Execution

[Script](script)
```shell
python udpipe.py \
  -i input-sample/nkod-title.csv --input-header \
  -m input-sample/czech-pdt-ud-2.5-191206.udpipe -f \
  -o output-sample/nkod-title.udpipe-f.csv
```
