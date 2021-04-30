# JSON To CSV
Given datasets descriptor files collect values of given descriptor and 
write them into a CSV file. 

This component can run in two modes: *default* and *linePerValue*.
The modes are connected to handling of multiple values, for example
let us have a dataset with following descriptor:
```
{
"iri": "dataset-iri",
"keywords": ["first", "second"]
}
```
In the default mode, all values of given descriptor are put on the same line.
Keep in mind that this may produce CSV that has lines of different length.
```
"iri", "keywords"
"dataset-iri", "first", "second"
```
The advantage of this mode is, that each dataset corresponds to exactly 
one line.

In the *linePerValue* mode, a single dataset can correspond to multiple lines. 
For the given example the output looks like this:
```
"iri", "keywords"
"dataset-iri", "first"
"dataset-iri", "second"
```

If the value is tokenized it is joined into a string using space before it 
is exported.

## Requirements
- Python 3.8

## Input
- Format: Directory of [JSON](https://www.json.org/) files.
- Contents: Dataset descriptor.
- Sample: [Input sample](input-sample/datasets)

## Output
- Format: [CSV](https://tools.ietf.org/html/rfc4180) file.
- Contents: CSV with ```iri``` and required property.
- Sample: [Output sample](output-sample/output.csv)

## Configuration
- ```input``` - Path to datasets descriptor files.
- ```output``` - Path to output file.
- ```property``` - Name of property to extract.
- ```linePerValue``` - For each value create a new line. 

## Execution
[Script](script)
```shell
python json-to-csv.py --input ./input-sample/datasets --output ./output-sample/description.csv --property description
```
or
```shell
python json-to-csv.py --input ./input-sample/datasets --output ./output-sample/keywords.csv --property keywords --linePerValue
```
