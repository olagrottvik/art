[![Build Status](https://travis-ci.com/olagrottvik/uart.svg?branch=master)](https://travis-ci.com/olagrottvik/uart)

# uart register tool

Utility for simply creating and modifying VHDL bus slave modules. uart does not refer to the hardware device!

## Concept

The main goal of the project is to able to automatically create and modify VHLD bus slave modules based on a simple definition format. By employing VHDL records the handling of the registers can be completely hidden in a module seperate from the rest of the designers logic. All referring to the registers are done via a record which specifies if the register is read-only or read-write, and also includes the name. All bus-specific signals are also wrapped in records. This increases the readability of the design as a whole.

## Bus support

uart currently supports these bus-types:

- AXI4-lite

## Requirements

uart is currently only tested with Python 3.5.2
  

## Getting Started

Install the latest relase by using pip (preferably pip3):

`pip3 install uart`


### Usage

`uart.py FILE [-o DIR]`

`uart.py -c FILE [-o DIR]`

`uart.py -e FILE [-o DIR]`

`uart.py --version`

`uart.py -h | --help`

### Output

The output VHDL files must be compiled with VHDL 2008.

## Latest Development Version (Bleeding Edge)

The latest development version can be found in the [dev branch](https://github.com/olagrottvik/uart/tree/dev) on Github. Clone the repo and checkout the branch.

`git clone https://github.com/olagrottvik/uart.git`
`cd uart`
`git checkout dev`
`pip3 install -r requirements.txt`
`python3 -m uart`

### Examples

The examples folder contain a JSON-file generated by the menu-system. This file is readable to the point that you can create your own from this template alone if you can't bothered with the menu-system. The folder also contain the output files generated based on the JSON-file.


## Release Notes

Release notes can be found at the [Releases page](https://github.com/olagrottvik/uart/releases).


## Contributing

If you have ideas on how to improve the project, please review [CONTRIBUTING.md](CONTRIBUTING.md) for details. Note that we also have a [Code of Conduct](CODE_OF_CONDUCT.md). 


## License

This project is licensed under the MIT license - see [LICENSE](LICENSE) for details.

