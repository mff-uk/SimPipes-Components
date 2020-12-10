# NKOD
Extracts title, description and keywords from [NKOD](https://data.gov.cz).

## Requirements
- Shell
- Python 3.9

## Input
- Format: [RDF TriG](https://www.w3.org/TR/trig/) file
- Contents: Dump of NKOD http://data.gov.cz/soubor/nkod.trig
- Sample: [Input sample](input-sample/nkod.trig)

## Output
- Format: [JSON Lines](https://jsonlines.org/)
- Contents: 
- Sample: [Output sample](output-sample)

## Execution
[Script](script)
```shell
./extract-nkod.sh
```
