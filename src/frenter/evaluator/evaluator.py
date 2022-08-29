import json
import os
import logging
from dateutil.parser import parse
from datetime import datetime, timedelta
from typing import Dict
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

        if os.getenv("DEBUG", False):
            self._inner_method = self._debug_inner
        else:
            self._inner_method = self._inner

    def _load_state(self):
        if not os.path.exists(self.state_path):
            self.state = {
                "listing_ids": []
            }
            return
        with open(self.state_path, "r") as f:
            self.state = json.load(f)

    def _save_state(self):
        with open(self.state_path, "w") as f:
            json.dump(self.state, f)

    def _filter_listing(self, listing_short: Dict):
        """
        Checks if this listing has been already checked or if it is out of interested zone.
        :param listing_short:
        :return:
        """

        if listing_short["listingId"] in self.state["listing_ids"]:
            return None

        published_on = parse(listing_short["publishedOn"], fuzzy=True)

        if published_on < datetime.now() - timedelta(days=1):
            self._log_listing(listing_short["listingId"])
            return None

        listing = self.property_scrapper.get_listing_details(listing_short["listingId"])
        postcode = self.postcode_dataset.find_postcode_by_coordinate(
            latitude=listing["location"]["coordinates"]["latitude"],
            longitude=listing["location"]["coordinates"]["longitude"]
        )
        transport = self.metadata_scrapper.get_transport(postcode)
        if transport.zone > self.filter_params.zone:
            self._log_listing(listing_short["listingId"])
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
            "crime count": "".join([f"\t{key}: {value}\n" for key, value in crime_rate.crime_count.items()]),
            "main group": demographics_report.main_group,
            "ptal": listing["ptal"]
        }

    def step(self):
        """
        Analyse listings
        :return:
        """
        for i in range(self.pages_amount):
            logging.info(f"Viewing page {i}")
            listings_short = self.property_scrapper.get_listings_page(
                page_number=i,
                price_min=self.filter_params.price_min,
                price_max=self.filter_params.price_max,
                furnished_state=self.filter_params.furnished_state,
                beds_num=self.filter_params.beds_num,
            )
            for listing_short in listings_short:
                self._inner_method(listing_short)

    def _debug_inner(self, listing_short):
        listing = self._filter_listing(listing_short)
        if listing:
            self.sender.send(self._get_listing_report(listing))
            self._log_listing(listing["listingId"])

    def _log_listing(self, listing_id: int):
        self.state["listing_ids"].append(listing_id)
        self._save_state()

    def _inner(self, listing_short):
        try:
            self._debug_inner(listing_short)
        except Exception as e:
            print(f"Cannot retrieve data for {listing_short['listingId']}, got {e}")
