# DCAT-AP Extractor
Extracts title, description and keywords from 
[DCAT-AP](https://joinup.ec.europa.eu/collection/semantic-interoperability-community-semic/solution/dcat-application-profile-data-portals-europe)  
metadata.

## Requirements
- Python 3.9

## Input
- Format: [RDF TriG](https://www.w3.org/TR/trig/) file.
- Contents: Dump of DCAT-AP compatible catalog, e.g. [Czech Open Data Catalog](http://data.gov.cz/soubor/nkod.trig).
- Sample: [Input sample](input-sample/nkod.trig)

## Output
- Format: [JSON](https://www.json.org/) files.
- Contents: Dataset metadata: id, title, description, keywords.
- Sample: [Output sample](output-sample/datasets.jsonl)

## Configuration
- ```input``` - Path to input file.
- ```output``` - Path to output file.

## Execution
[Script](script)
```shell
python extract-dcat-ap.py \
    --input input-sample/nkod.trig \
    --output ./output
```
