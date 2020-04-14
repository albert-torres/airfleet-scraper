# Airfleets-scraper

## Description
Extracts data from _airfleets.net_. It iterates through all or the selected aircraft types extracting several data.

Developed in Python.

## Project structure
* **code/main.py**: Entrypoint of the .
* **code/scraper.py**: Web scraper.
* **data/**: stores output datasets from the scraper.
* **log/scraper.log**: Logs failed connections from scraper.
* **requirements.txt**: Needed libraries.

## Requirements
* Python 3+

To install requirements:

`pip3 install -r requirements.txt`

## Entrypoint
`python3 main.py`

optional arguments:

  -h, --help show this help message and exit
  
  -a  [ ...], --aircraft  [ ...] Aircraft type to scrape (Ex.: "Comac C919, Boeing 737") / All types selected if no argument

  -q, --quiet, Selenium driver performs silently
  
## Author
Albert Torres Rubio

## License
_CC BY-NC-SA 4.0_

## Zenodo DOI

* Software [![DOI](https://zenodo.org/badge/253335140.svg)](https://zenodo.org/badge/latestdoi/253335140)
* Dataset [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.3752107.svg)](https://doi.org/10.5281/zenodo.3752107)


