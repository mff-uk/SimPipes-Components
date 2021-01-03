# DCAT-AP Extractor
For a collection of [dataset](http://www.w3.org/ns/dcat#Dataset) extracts 
[title](http://purl.org/dc/terms/title), 
[description](http://purl.org/dc/terms/description) and 
[keywords](http://www.w3.org/ns/dcat#keyword) for each dataset. 
The datasets must be stored in TRIG file, one dataset per graph using 
[DCAT-AP](https://joinup.ec.europa.eu/collection/semantic-interoperability-community-semic/solution/dcat-application-profile-data-portals-europe)  
vocabulary. 
The extracted metadata are stored in JSON files, one dataset per file.
 
## Requirements
- Python 3.9
- Libraries as specified in ```requirements.txt```. 

## Input
- Format: [RDF TriG](https://www.w3.org/TR/trig/) file.
- Contents: Dump of DCAT-AP compatible catalog, e.g. 
    [Czech Open Data Catalog](http://data.gov.cz/soubor/nkod.trig).
- Sample: [Input sample](input-sample/nkod.trig)

## Output
- Format: Directory of [JSON](https://www.json.org/) files.
- Contents: Dataset descriptors: iri as @id, title, description, keywords.
- Sample: [Output sample](output-sample/datasets.jsonl)

## Execution
[Script](script)
```shell
python3 dcat-ap-extractor.py \
    --input ./input-sample/nkod.trig \
    --output ./output
```
