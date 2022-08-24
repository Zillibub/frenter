import os
import pandas as pd
from scipy.spatial.distance import cdist


class PostcodeDataset:
    """
    Contains data frame with all postcodes in London
    london_postcodes-ons-postcodes-directory-feb22.csv
    """

    def __init__(self, dataset_path: str):
        """

        :param dataset_path: path to csv file with postcodes
        """
        self.dataset_path = dataset_path
        if not os.path.exists(self.dataset_path):
            raise FileNotFoundError()
        self.postcodes = pd.read_csv(self.dataset_path)
        self.postcodes_coordinates = [(x, y) for x, y in zip(self.postcodes['lat'], self.postcodes['long'])]

    def find_postcode_by_coordinate(self, latitude: float, longitude: float):
        """

        :param latitude:
        :param longitude:
        :return: closest postcode to given coordinates
        """
        return self.postcodes.iloc[
            cdist([(latitude, longitude)], self.postcodes_coordinates).argmin()
        ]["pcd"].replace(" ", "")
