# Airfleets-scraper

## Description
Extracts data from _airfleets.net_. It iterates through all or the selected aircraft types extracting several data.
Developed in Python language and 

## Author
Albert Torres Rubio

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
  -h, --help            show this help message and exit
  -a  [ ...], --aircraft  [ ...] Aircraft type to scrape (Ex.: "Comac C919, Boeing 737") / All types selected if no argument

  -q, --quiet           Selenium performs silently


## License

_CC BY-NC-SA 4.0_
