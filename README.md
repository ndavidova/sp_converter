# Reverse Engineering of SPs in Br-1 Format
Automated transformation of Security Policy documents leveraging FIPS 140-3 BR-1 submission format. This pipeline intents to convert PDF format into machine readable representations in 3 stages:

## PDF to text conversion
Using docling all the pdf files are converted to txt.

## Mapping chapters
Fuzzy-matching regex is used to map text into predefined structure of chapters.

The quality of the mapping is assessed by calculating:
* errors (non-optional chapter / subchapter is missing or is empty) and 
* warnings (optional subchapter is missing or is empty)

Information on errors and warnings is stored in a database as well as external metadata from the **sec-certs library** (that way it can be observed how many files are in this format from what year etc).

Currently only the chapters of files that have **less than 10 errors** are saved in json for furhter processing.

## Table extraction
The tables are modeled in advanced_parsing/model, where AdvancedProperties represent all tables in one file and different classes in advanced_data (such as Role, ErrorState etc.) represent different entities from the tables.
For this definition were used following 2 documents as well as the Template version 5.8:

- [Table Description](https://csrc.nist.gov/csrc/media/Projects/cryptographic-module-validation-program/documents/fips%20140-3/Module%20Processes/MIS%20Table%20Descriptions%20-%20V2.8.4.pdf)

- [Json Schema](https://csrc.nist.gov/csrc/media/Projects/cryptographic-module-validation-program/documents/fips%20140-3/Module%20Processes/SchemaMis-2.8.4.json)

The files from the previous step are the input for this stage, which parses specific chapters' contents to extract tables. Not all tables are modelled and extracted. Currently are supported 24/33 tables from the Template.

The extracted data for each file is stored in a new JSON file, which can be easily loaded back into its AdvancedProperties class.