import re
import time
import csv
import logging
from datetime import datetime
from os import path
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException


class AirfleetScraper:

    def __init__(self, quiet):
        self.base_url = "https://www.airfleets.net/"
        self.selenium_driver_path = self._get_driver_path()
        self.browser = self._get_browser(quiet)
        self.requests_number = 0
        self.logger = self._setup_logger()

    def _setup_logger(self):
        project_base_path = path.dirname(path.dirname(path.abspath(__file__)))
        log_name = '{}{}log{}{}.log'.format(project_base_path, path.sep, path.sep, 'scraper')
        logging.basicConfig(filename=log_name, level=logging.WARNING)
        return logging.getLogger('scraper')

    def _get_driver_path(self):
        dir_name = path.dirname(path.abspath(__file__))
        driver_path = '{}{}chromedriver.exe'.format(dir_name, path.sep)
        return driver_path

    def _get_browser(self, quiet):
        options = Options()
        if quiet:
            options.add_argument('--headless')
        browser = webdriver.Chrome(self.selenium_driver_path, options=options)
        return browser

    def _get_url_with_delay(self, url):
        """
        Delays request action 1.5 seconds in order to follow airfleet.net robots.txt.
        The crawl-delay must be at least of 1 second according robots.txt.

        """

        if self.requests_number <= 264:
            self.browser.get(url)
            self.requests_number += 1
        else:
            print('Sleeping 5 minutes to avoid being banned due to "To many requests"')
            print('Starting at: {}'.format(datetime.now().time()))
            print('Please wait...')
            time.sleep(300)  # Sleep during 5 minutes to avoid "To many requests" issue
            self.browser.get(url)
            self.requests_number = 1

        # To be nice with the server and not be banned, sleep for 2 seconds for the next request to come
        # It also ensures that the requested webpage is fully loaded after performing browser.get(url)
        time.sleep(2.5)
        print('Request number: {}'.format(self.requests_number))

    def _extract_airplane_data(self, html, type_name):
        data = []

        soup = BeautifulSoup(html, 'lxml')
        tableaus = soup.findAll("table", {"class": "tableau"})

        try:
            status = self._extract_status(tableaus[0])
        except IndexError:  # html page has not been properly loaded or it has an abnormal condition
            pass
        else:
            serial_number, ln_number, subtype, first_flight_date, plane_age, test_registration = self._extract_general_data(tableaus[1])
            engines_type, engines_number = self._extract_engines_info(tableaus[1])
            operators_data = self._extract_operartors(soup, status)

            a_list = [serial_number, ln_number, type_name, subtype, first_flight_date, plane_age, test_registration,
                      engines_type, engines_number]

            for row in operators_data:
                data.append(a_list + row)
                print(a_list + row)

        return data

    def _aircraft_type_selector(self, aircraft_type_urls, selected_types):
        selected_urls = aircraft_type_urls
        if selected_types:
            selected_types = [x.strip() for x in selected_types[0].split(',')]
            selected_urls = [x for x in aircraft_type_urls if x[0] in selected_types]
        return selected_urls

    def _extract_status(self, tableau):
        raw_status = tableau.findAll("td", {"class": "texten"})
        status = raw_status[1].find('b').contents[0].strip().replace('Status : ', '')

        return status

    def _extract_general_data(self, tableau):
        serial_number, ln_number, subtype, first_flight_date, plane_age, test_registration = '', '', '', '', '', ''

        general_info = tableau.find("div", {"class": "six columns"})
        tds = general_info.find("table").findAll("td")
        grouped_tds = list(zip(*[iter(tds)] * 2))
        for td_label, td_value in grouped_tds:
            label = td_label.text
            value = td_value.text

            if label == 'Serial number':
                if 'LN' in value:
                    index = value.find(':')
                    serial_number = value[:index-4]
                    ln_number = value[index+1:]
                else:
                    serial_number = value
            elif label == 'Type':
                subtype = value
            elif label == 'First flight date':
                first_flight_date = value
            elif label == 'Plane age':
                number = re.findall(r"\d+\.\d+", value) or re.findall(r"\d+", value)
                if number:
                    plane_age = number[0]
            elif label == 'Test registration':
                test_registration = value

        return serial_number, ln_number, subtype, first_flight_date, plane_age, test_registration

    def _extract_engines_info(self, tableau):
        engines_type, engines_number = '', ''

        engines_info = tableau.find("div", {"class": "five columns"}).find_next_sibling("table")
        if engines_info.text.find('x') != -1:
            engines_info_text = engines_info.text.replace('Engines', '')
            engines_info_text = engines_info_text.replace('\t', '')
            engines_info_text = engines_info_text.replace('\n', '')
            index = engines_info_text.find('x')
            engines_number = engines_info_text[index-2]
            engines_type = engines_info_text[index+2:]

        return engines_type, engines_number

    def _extract_operartors(self, soup, final_status):
        operators_data = []
        ten_columns = soup.find("div", {"class": "ten columns"})
        tr_tabs = ten_columns.findAll("tr", {"class": "trtab"})
        for i in range(len(tr_tabs)):
            registration, delivery_date, airline, remark, status = '', '', '', '', ''
            tab = tr_tabs[i]
            tds = tab.findAll("td")
            if len(tds) == 5:  # Normal format
                registration = tds[0].text
                delivery_date = tds[1].text
                airline = tds[2].text
                remark = tds[3].text.strip().replace('\n', '')
                status = 'Transferred'

            elif len(tds) == 4 or len(tds) == 3:  # Incorrect format according to textmenu labels
                delivery_date = tds[0].text
                airline = tds[1].text
                registration = tds[2].text
                status = 'Transferred'

            if i == len(tr_tabs) - 1:
                status = final_status

            operators_data.append([registration, delivery_date, airline, remark, status])
        return operators_data

    def start(self, selected_types):
        dataset = []

        self._get_url_with_delay(self.base_url)
        # We begin entering 'Supported planes' menu from homepage
        action = ActionChains(self.browser)
        time.sleep(2)
        aircraft_menu = self.browser.find_element_by_xpath(
            "//button[@class='dropbtn' and text()='Aircraft				  ']")
        action.move_to_element(aircraft_menu).perform()
        aircraft_url = self.browser.find_element_by_xpath("//a[text()='Supported planes']").get_attribute('href')
        self._get_url_with_delay(aircraft_url)

        aircraft_type_urls = []
        for a_type_element in self.browser.find_elements_by_class_name("trtab"):
            child = a_type_element.find_element_by_class_name("lien")
            url = child.get_attribute('href')
            name = child.text
            aircraft_type_urls.append((name, url))

        aircraft_type_urls = self._aircraft_type_selector(aircraft_type_urls, selected_types)

        # Loop to search in each aircraft_type
        for type_name, type_url in aircraft_type_urls:
            print('Scraping {} aircraft type...'.format(type_name))
            continue_next_page = True
            airplanes_msn_urls = []
            self._get_url_with_delay(type_url)

            # Get all urls corresponding to the airplanes MSNs from all pages
            while continue_next_page:
                airplanes_msn_urls.extend([msn.find_element_by_class_name("lien").get_attribute('href') for msn
                                           in self.browser.find_elements_by_class_name("trtab")])
                try:
                    next_page_url = self.browser.find_element_by_xpath("//a[@class='page' and text()='Next page ']").get_attribute('href')
                except NoSuchElementException:
                    continue_next_page = False
                else:
                    self._get_url_with_delay(next_page_url)

            for msn_url in airplanes_msn_urls:
                self._get_url_with_delay(msn_url)
                # If a redirect is performed, it means that aircraft does not have any kind of data
                if self.browser.current_url != 'https://www.airfleets.net/home/':
                    html = self.browser.page_source
                    data = self._extract_airplane_data(html, type_name)
                    if not data:  # A problem has ocurred and skipped, logging it.
                        self.logger.warning('A problem has occurred with: {} - {}'.format(type_name, msn_url))
                    else:
                        dataset.extend(data)

        self.browser.close()
        return dataset

    def save_csv(self, data, name):
        name = name.replace('/', '')
        project_base_path = path.dirname(path.dirname(path.abspath(__file__)))
        file_name = '{}{}data{}{} status.csv'.format(project_base_path, path.sep, path.sep, name)
        with open(file_name, mode='w', newline='', encoding="utf-8") as csvfile:
            row_writer = csv.writer(csvfile, delimiter=',')
            first_row = ['serialNumber', 'lnNumber', 'familyType', 'Type', 'firstFlight', 'planeAge',
                         'testRegistration', 'enginesType', 'enginesNumber', 'registration', 'deliveryDate',
                         'operator', 'remark', 'status']
            row_writer.writerow(first_row)
            for row in data:
                row_writer.writerow(row)