import requests
import json
from bs4 import BeautifulSoup
from typing import Dict


class ZooplaScrapper:
    """
    Retrieves data from zoopla
    """

    def __init__(self):
        self.base_url: str = "https://www.zoopla.co.uk"

    def get_listings_page(
            self,
            page_number: int,
            price_min: int,
            price_max: int,
            furnished_state: str = "furnished",
            beds_num: int = 1,
    ):
        """

        :param page_number:
        :param price_min:
        :param price_max:
        :param furnished_state:
        :param beds_num:
        :return: list of all regular listings for this page
        """
        listings_response = requests.get(
            f"{self.base_url}/to-rent/property/london/?price_frequency=per_month&q=London&search_source=home"
            f"&beds_min={beds_num}&price_min={price_min}&price_max={price_max}"
            f"&furnished_state={furnished_state}&pn={page_number}")
        if listings_response.status_code != 200:
            raise ValueError(f"Status code{listings_response.status_code} for listing details")
        listings_soup = BeautifulSoup(listings_response.content, 'html.parser')
        return json.loads(
            list(listings_soup.find(id="__NEXT_DATA__").children)[0])["props"]["pageProps"]["initialProps"][
            "searchResults"]["listings"]["regular"]

    def get_listing_details(self, listing_id: int) -> Dict:
        """
        fetches html listing response and retrieves data with beautiful soup
        :param listing_id:
        :return: listing details
        """
        listing_response = requests.get(f"{self.base_url}/to-rent/details/{listing_id}")
        if listing_response.status_code != 200:
            raise ValueError(f"Status code {listing_response.status_code} for listing details")

        listing_soup = BeautifulSoup(listing_response.content, 'html.parser')
        return json.loads(list(listing_soup.find(id="__NEXT_DATA__").children)[0])["props"]["pageProps"][
            "listingDetails"]
