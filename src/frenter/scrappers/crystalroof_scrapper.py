import json
import requests
from enum import Enum
from bs4 import BeautifulSoup


class ReportType(Enum):
    demographics = "demographics"
    transport = "transport"
    crime = "crime"


class CrystalRoofScrapper:

    def __init__(self):
        self.base_url: str = "https://crystalroof.co.uk"

    def _fetch_data(self, postcode: str, report_type: ReportType) -> BeautifulSoup:
        report_response = requests.get(f"{self.base_url}/report/postcode/{postcode}/{report_type.value}")
        if report_response.status_code != 200:
            raise ValueError()
        return BeautifulSoup(report_response.content, 'html.parser')

    def get_crime(self, postcode):
        report_soup = self._fetch_data(postcode, ReportType.crime)
        crime = json.loads(list(
            report_soup.find(id="__NEXT_DATA__").children)[0])["props"]["initialReduxState"]["report"][
            "sectionResponses"]
        return crime["crime"]["data"]["lsoastats"]["bucket"] + 1

    def get_transport(self, postcode):
        report_soup = self._fetch_data(postcode, ReportType.transport)
        transport = json.loads(list(
            report_soup.find(id="__NEXT_DATA__").children)[0])["props"]["initialReduxState"]["report"][
            "sectionResponses"]
        return {
            "zone": transport["transport"]["data"]["zone"],
            "ptal": transport["transport"]["data"]["ptal"],
        }

    def get_main_demographics_group(self, postcode):
        report_soup = self._fetch_data(postcode, ReportType.demographics)
        demographics = json.loads(list(
            report_soup.find(id="__NEXT_DATA__").children)[0])["props"]["initialReduxState"]["report"][
            "sectionResponses"]
        total = demographics["demographics"]["data"]["ethnicgroup_ward"]["total"]
        rate = {x: y / total for x, y in demographics["demographics"]["data"]["ethnicgroup_ward"].items() if
                x != "total"}
        max_keys = [key for key, value in rate.items() if value == max(rate.values())][0]

        return rate, {max_keys: round(rate[max_keys], 2)}
