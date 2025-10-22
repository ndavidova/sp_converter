# sp_converter
Automated transformation of Security Policy (SP) documents (FIPS 140-3) from PDF format into machine readable representations.


## File hierarchy
data directory - contains processed files

data/input - contains txt files processed by docling, the PDF files are not in this project
data/input/SP - the actual SP files
data/input/SP/fullset - all files processed by docling from the sec-certs dataset
data/input/sample - sample files for testing, not actual valid SPs

data/output - contains json files processed by custom parsers
data/output/advanced - advanced parsing (algorithm, json dump of custom classes)
data/output/mapping - chapter mapping, json files that only divide the chapters, this is further processed by advanced parser

