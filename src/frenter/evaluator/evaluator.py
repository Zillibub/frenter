import json
import os
from pydantic import BaseModel
from frenter.datasets.postcode_dataset import PostcodeDataset
from frenter.scrappers.zoopla_scrapper import ZooplaScrapper
from frenter.scrappers.crystalroof_scrapper import CrystalRoofScrapper
from frenter.senders.telegram_sender import TelegramSender


class FilterParameters(BaseModel):
    price_min: int
    price_max: int
    furnished_state: str
    beds_num: int
    zone: int


class Evaluator:
    """
    Evaluates main search logic like filtering and report creation
    """

    def __init__(
            self,
            filter_params: FilterParameters,
            state_path: str,
            postcode_dataset_path: str,
            sender: TelegramSender,
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
        self.sender = sender
        self._load_state()
        self.postcode_dataset = PostcodeDataset(postcode_dataset_path)
        self.property_scrapper = ZooplaScrapper()
        self.metadata_scrapper = CrystalRoofScrapper()

    def _load_state(self):
        if not os.path.exists(self.state_path):
            self.state = {"listing_ids": []}
            return
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
        if transport.zone > self.filter_params.zone:
            return None

        listing["postcode"] = postcode
        listing["ptal"] = transport.ptal

        return listing

    def _get_listing_report(self, listing):
        postcode = listing["postcode"]
        crime_rate = self.metadata_scrapper.get_crime(postcode)
        demographics_report = self.metadata_scrapper.get_main_demographics_group(postcode)
        return {
            "url": f"https://www.zoopla.co.uk/to-rent/details/{listing['listingId']}",
            "crime rate": crime_rate.crime_rate,
            "crime count": crime_rate.crime_count,
            "main group": demographics_report.main_group,
            "ptal": listing["ptal"]
        }

    def step(self):
        """
        Analyse listings
        :return:
        """
        for i in range(self.pages_amount):
            listings_short = self.property_scrapper.get_listings_page(
                page_number=i,
                price_min=self.filter_params.price_min,
                price_max=self.filter_params.price_max,
                furnished_state=self.filter_params.furnished_state,
                beds_num=self.filter_params.beds_num,
            )
            for listing_short in listings_short:
                try:
                    listing = self._filter_listing(listing_short["listingId"])
                    if listing:
                        self.sender.send(self._get_listing_report(listing))
                        self.state["listing_ids"].append(listing["listingId"])
                        self._save_state()
                except Exception:
                    print(f"Cannot retrieve data for crystalroof for {listing_short['listingId']}")
