import json
from typing import List, Dict
from frenter.datasets.postcode_dataset import PostcodeDataset
from frenter.scrappers.zoopla_scrapper import ZooplaScrapper
from frenter.scrappers.crystalroof_scrapper import CrystalRoofScrapper


class Evaluator:
    """
    Evaluates main search logic like filtering and report creation
    """

    def __init__(
            self,
            filter_params,
            state_path: str,
            postcode_dataset_path: str,
            pages_amount: int = 10,
    ):
        """

        :param filter_params:
        :param state_path: path to json file with already views listings
        :param postcode_dataset_path: path to datasets with postcodes
        :param pages_amount: amout of pages to analyze on search
        """
        self.filter_params = filter_params
        self.state_path = state_path
        self.pages_amount = pages_amount

        self.state = None
        self._load_state()
        self.postcode_dataset = PostcodeDataset(postcode_dataset_path)
        self.property_scrapper = ZooplaScrapper()
        self.metadata_scrapper = CrystalRoofScrapper()

    def _load_state(self):
        with open(self.state_path, "r") as f:
            self.state = json.load(f)

    def _save_state(self):
        with open(self.state_path, "w") as f:
            json.dump(self.state, f)

    def _filter_listing(self, listing_id: int):
        """
        Checks if this listing has been already checked or if it is out of interested zone.
        :param listing_id:
        :return:
        """

        if listing_id in self.state["listing_ids"]:
            return None

        listing = self.property_scrapper.get_listing_details(listing_id)
        postcode = self.postcode_dataset.find_postcode_by_coordinate(
            latitude=listing["location"]["coordinates"]["latitude"],
            longitude=listing["location"]["coordinates"]["longitude"]
        )
        transport = self.metadata_scrapper.get_transport(postcode)
        if transport["zone"] > self.filter_params["zone"]:
            return None

        listing["postcode"] = postcode

        return listing

    def _get_listing_report(self, listing):
        postcode = listing["postcode"]
        crime_rate = self.metadata_scrapper.get_crime(postcode)
        rate, main_demographics_group = self.metadata_scrapper.get_main_demographics_group(postcode)

        return {
            "url": f"https://www.zoopla.co.uk/to-rent/details/{listing['listingId']}",
            "crime_rate": crime_rate,
            "main_demographics_group": main_demographics_group,
        }

    def step(self) -> List[Dict]:
        """
        Analyse listings
        :return:
        """
        listings = []
        for i in range(self.pages_amount):
            listing_short = self.property_scrapper.get_listings_page(
                page_number=i,
                price_min=self.filter_params["price_min"],
                price_max=self.filter_params["price_max"],
                furnished_state=self.filter_params["furnished_state"],
                beds_num=self.filter_params["beds_num"],
            )
            listing = self._filter_listing(listing_short["listingId"])
            if listing:
                listings.append(listing)

        listing_reports = [
            self._get_listing_report(listing) for listing in listings
        ]

        return listing_reports
