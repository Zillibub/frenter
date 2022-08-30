import json
import requests
from pydantic import BaseModel
from enum import Enum
from bs4 import BeautifulSoup
from typing import Dict


class ReportType(Enum):
    demographics = "demographics"
    transport = "transport"
    crime = "crime"


class CrimeReport(BaseModel):
    crime_rate: int
    crime_count: Dict[str, int]


class TransportReport(BaseModel):
    zone: int
    ptal: str


class DemographicReport(BaseModel):
    rate: Dict[str, float]
    main_group: Dict[str, float]


class CrystalRoofScrapper:
    """
    Retrieves data from crystalroof
    """

    def __init__(self):
        self.base_url: str = "https://crystalroof.co.uk"
        self.crime_type_mapping = {
            8: "robbery",
            14: "other theft",
            10: "theft from the person",
            3: "bulgary"
        }

    def _fetch_data(self, postcode: str, report_type: ReportType) -> BeautifulSoup:
        report_response = requests.get(f"{self.base_url}/report/postcode/{postcode}/{report_type.value}")
        if report_response.status_code != 200:
            raise ValueError(f"Status code {report_response.status_code}, {report_response.content}")
        return BeautifulSoup(report_response.content, 'html.parser')

    def get_crime(self, postcode) -> CrimeReport:
        """
        Creates crime report
        :param postcode:
        :return:
        """
        report_soup = self._fetch_data(postcode, ReportType.crime)
        crime = json.loads(list(
            report_soup.find(id="__NEXT_DATA__").children)[0])["props"]["initialReduxState"]["report"][
            "sectionResponses"]
        return CrimeReport(
            crime_rate=crime["crime"]["data"]["lsoastats"]["bucket"] + 1,
            crime_count={
                self.crime_type_mapping[x["type"]]: x["count"]
                for x in crime["crime"]["data"]["crimes_count"]
                if x["type"] in self.crime_type_mapping.keys()
            }
        )

    def get_transport(self, postcode) -> TransportReport:
        report_soup = self._fetch_data(postcode, ReportType.transport)
        transport = json.loads(list(
            report_soup.find(id="__NEXT_DATA__").children)[0])["props"]["initialReduxState"]["report"][
            "sectionResponses"]
        return TransportReport(
            zone=transport["transport"]["data"]["zone"],
            ptal=transport["transport"]["data"]["ptal"]["ptal"]
        )

    def get_main_demographics_group(self, postcode) -> DemographicReport:
        report_soup = self._fetch_data(postcode, ReportType.demographics)
        demographics = json.loads(list(
            report_soup.find(id="__NEXT_DATA__").children)[0])["props"]["initialReduxState"]["report"][
            "sectionResponses"]
        total = demographics["demographics"]["data"]["ethnicgroup_ward"]["total"]
        rate = {x: y / total for x, y in demographics["demographics"]["data"]["ethnicgroup_ward"].items() if
                x != "total"}
        max_keys = [key for key, value in rate.items() if value == max(rate.values())][0]
        return DemographicReport(
            rate=rate,
            main_group={max_keys: round(rate[max_keys], 2)}
        )
