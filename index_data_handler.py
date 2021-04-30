import pathlib
from datetime import datetime
import os
import requests
import json
import pandas as pd


class IndexDataHandler():
    def __init__(self, variant="GRTR", start_date="19900101", end_date=None, frequency="DAILY", normalize=True):
        """
        Get historic index data directly from MSCI
        :param name: name of the index
        :param index_code: Code for the index
        :param start_date: start date in format YYYYMMdd
        :param variant: "GRTR", "NETR" or STRD. Whether to accumulate (GRTR), accumulate with taxes (NETR) or take the raw index (STRD)
        :param normalize if True all values will be normalized to its startdate
        """
        self.frequency = frequency
        self.end_date = end_date or datetime.today()
        self.start_date = start_date
        self.variant = variant
        self.available_indices = self._load_index_codes()
        self.normalize = normalize

    def get_available_indices(self, region="Developed"):

        return {k: v for k, v in self.available_indices.items() if v["region"] == region}

    def get_historic_stock_data(self, index_code, reload=False):
        """
        Get the data for a given index_code
        :param reload: if set to true we will reload the data from the API. Otherwise the cache is used
        :param index_code: index code from MSCI, can be obtained in available_indices or from MSCI website
        :return: a dataframe with two columns: date and level_eod. If normalize was set to true its normalized.
        """
        path = os.path.join("cache", str(index_code) + "_" + self.frequency + ".csv")
        if pathlib.Path(path).is_file() is False or reload is True:
            df = self._reload_stock_data_from_api(index_code)
            df.to_csv(path)
            return df
        else:
            print("reading",path)
            df = pd.read_csv(path)
            df['date'] = pd.to_datetime(df['date'])
            df = df.set_index("date")
            return df

    def _reload_stock_data_from_api(self, index_code) -> pd.DataFrame:
        """
        :param index_code: index_code: index code from MSCI, can be obtained in available_indices or from MSCI website
        :return:
        """
        url = "https://app2.msci.com/products/service/index/indexmaster/getLevelDataForGraph?currency_symbol=USD" \
              f"&index_variant={self.variant}" \
              f"&start_date={self.start_date}" \
              f"&end_date={self.end_date.strftime('%Y%m%d')}" \
              f"&data_frequency={self.frequency}" \
              f"&index_codes={index_code}"

        response = json.loads(requests.get(url).content)

        try:
            data = pd.DataFrame(response['indexes']['INDEX_LEVELS'])
        except KeyError:
            print(response)
            raise
        if self.normalize is True:
            first_value = data["level_eod"].iloc[0]
            data["level_eod"] = data["level_eod"] / first_value

        data = data.rename(columns={'calc_date': 'date'})
        data['date'] = pd.to_datetime(data['date'], format='%Y%m%d')
        data = data.set_index("date")

        return data

    def _load_index_codes(self):
        # index_codes = {
        #     "MSCI World": {"code": "990100", "region": "Developed", "ISIN": "IE00BJ0KDQ92", "vendor": "Xtrackers"},
        #     "Value": {"code": "705130", "region": "Developed", "ISIN": "IE00BL25JM42", "vendor": "Xtrackers"},
        #     "Quality": {"code": "702787", "region": "Developed", "ISIN": "IE00BL25JL35", "vendor": "Xtrackers"},
        #     "Multi-Factor": {"code": "706536", "region": "Developed", "ISIN": "IE00BZ0PKT83", "vendor": "iShares"},
        #     "Momentum": {"code": "703755", "region": "Developed", "ISIN": "IE00BL25JP72", "vendor": "Xtrackers"},
        #     "Small-Cap": {"code": "106230", "region": "Developed", "ISIN": "IE00BF4RFH31", "vendor": "iShares"},
        #     "Low Volatility (World)": {"code": "129896", "region": "Developed", "ISIN": "IE00BL25JN58",
        #                                "vendor": "Xtrackers"},
        #     "Small-Cap (Value)": {"code": "139249", "region": "US", "ISIN": "IE00BSPLC413", "vendor": "SPDR",
        #                           "ticker": "zprv-gy"},
        #     "High-Dividend (World)": {"code": "136064", "region": "Developed", "ISIN": "IE00BCHWNQ94",
        #                               "vendor": "Xtrackers"}
        # }
        df = pd.read_excel("ressources/index_codes.xlsx")
        df = df.set_index("name")
        return df.T.to_dict()


if __name__ == "__main__":
    ih = IndexDataHandler()
    print(ih._load_index_codes())
