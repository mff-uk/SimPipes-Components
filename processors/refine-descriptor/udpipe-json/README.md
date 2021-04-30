# UDPipe JSON
Similar to UDPipe but apply transformation on JSON files.

## Requirements
- Python 3.8
- Libraries as specified in ```requirements.txt```.

## Inputs
- Format: Directory of [JSON](https://www.json.org/) files.
- Contents: Dataset metadata.
- Sample: [Input sample](input-sample/)

## Output
- Format: Directory of [JSON](https://www.json.org/) files.
- Contents: Dataset metadata.
- Sample: [Output sample](output-sample/)

## Configuration
- ```input``` - Path to input datasets descriptor files.
- ```output``` - Path to output directory.
- ```sourceProperty``` - Name(s) of property to load values from.
- ```targetProperty``` - Name(s) of property to save transformed values into.
- ```model``` - Path to the [UDPipe model](https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-3131/czech-pdt-ud-2.5-191206.udpipe?sequence=19&isAllowed=y).
- ```transformation``` - Specification of filter function, see code for more details.

## Execution
[Script](script)
```shell
python udpipe-json.py --input ./input-sample --output ./output-sample --model ./czech-pdt-ud-2.5-191206.udpipe --sourceProperty description keywords --targetProperty description-udpipe keywords-udpipe
```
