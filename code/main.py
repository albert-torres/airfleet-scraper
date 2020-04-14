import time
import argparse
from datetime import datetime
from scraper import AirfleetScraper


def format_file_name(raw_name):
    if not raw_name:
        f_name = 'civil airfleets'
    else:
        f_name = [x.strip() for x in args.aircraft[0].split(',')]
        f_name = '-'.join(f_name)
        f_name = f_name.lower()

    return f_name


parser = argparse.ArgumentParser(description='Web scraper for airfleets.net supported aircraft')
parser.add_argument('-a', '--aircraft', nargs='+', metavar='',
                    help='Aircraft type to scrape (Ex.: "Comac C919, Boeing 737") / All types selected if no argument')
parser.add_argument('-q', '--quiet', action='store_true', help='Selenium performs silently')
args = parser.parse_args()

start_time = time.time()
print("Scraping selected aircraft from https://www.airfleets.net/")

scraper = AirfleetScraper(args.quiet)
file_name = format_file_name(args.aircraft)
airplane_data = scraper.start(args.aircraft)

print('Saving data...')
scraper.save_csv(airplane_data, file_name)

elapsed_time = round((time.time() - start_time) / 60, 2)
print("End of scraper: {}".format(datetime.now().time()))
print("Elapsed time: {} minutes".format(elapsed_time))