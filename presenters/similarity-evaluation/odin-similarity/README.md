# Open Data Inspector Similarity
Given a collection of datasets metadata and similarity export data into 
[Open Data Inspector](https://github.com/mff-uk/open-dataset-inspector) (ODIN)
for evaluation.  

After the data are exported user must create an evaluation group in 
```{odin-data-directory}/evaluation/{evaluation-name}.json```. 
The ```evaluation-name``` is used to identify the evaluation in ODIN 
user interface. The file must include names of the similarities that should be 
part of the evaluation. The file may look like this:
```
{
  "description": "Description shown in the UI.",
  "methods": [
    "nkod-_title_description_.join.reduce.tlsh.tlsh",
    "nkod-description.udpipe-f.reduce.hausdorff[cswiki]",
  ],
  "fusion": "min"
}
``` 

The evaluation is available at:
```{odin-url}/#/evaluation?group={evaluation-name}```.  

The similarity input consists of two files, one is the similarity matrix and 
other is a CSV file with IRIs. The reason is that the similarity matrix, 
does not contain IRIs of the datasets.

## Requirements
- Python 3.8

## Inputs

### Datasets
- Format: Directory of [JSON](https://www.json.org/) files.
- Contents: Dataset metadata with iri, title, description, keywords.
- Sample: [Input sample](input-sample/datasets/)

### Similarity
- Format: [CSV](https://tools.ietf.org/html/rfc4180) files.
- Contents: Dataset similarity matrix and CSV with datasets IRIs.
- Sample: [Similarity matrix](input-sample/dataset-similarity.csv), 
          [Dataset IRI](input-sample/file-with-iri.csv)

## Configuration
- ```datasets``` - Path to datasets metadata file
- ```knowledge-graph``` - Path to knowledge graph data.
- ```output``` - Path to output file.
- ```mapping``` - ```{source}:{target}``` property name pairs.

## Execution
[Script](script)
```shell
python3 odin-similarity.py \
    --datasets ./input-sample/datasets \
    --similarity ./input-sample/dataset-similarity.csv \
    --csvWithIri ./input-sample/file-with-iri.csv \
    --odinDirectory ./odin-data-directory \ 
    --similarityName nkod-title.udpipe-f.reduce.words_set.jaccard
```
