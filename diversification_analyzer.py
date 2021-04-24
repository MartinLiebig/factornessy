import requests
import pandas as pd

import numpy as np

def get_xtrackers(ISIN: str, name: str):
    dataset = pd.read_excel("https://etf.dws.com/etfdata/export/GBR/ENG/excel/product/constituent/" + ISIN,
                            skiprows=[0, 1, 2])
    dataset = dataset.rename(columns={"Weighting": name})
    dataset = dataset[["ISIN", "Name", "Country", "Industry Classification", name]]
    # dataset = dataset.set_index("Name")

    return dataset


def get_spdr(ticker: str, name: str):
    dataset = pd.read_excel(
        "https://www.ssga.com/de/en_gb/intermediary/etfs/library-content/products/fund-data/etfs/emea/holdings-daily-emea-en-" + ticker + ".xlsx",
        skiprows=[0, 1, 2, 3, 4])
    dataset = dataset[["ISIN", "Security Name", "Trade Country Name", "Industry Classification", "Percent of Fund"]]
    dataset = dataset.rename(
        columns={"Security Name": "Name", "Percent of Fund": name, "Trade Country Name": "Country"})
    dataset[name] = dataset[name].replace('-', np.NaN).astype(float)

    dataset[name] = dataset[name] / 100
    # dataset = dataset.set_index("Name")
    return dataset


# https://www.ishares.com/us/products/239696/ishares-msci-world-etf/1521942788811.ajax?fileTyp
def get_iShares(key: str, name: str):
    dataset = pd.read_csv('ressources/iShares/' + key + '.csv', skiprows=[0, 1])
    dataset = dataset[["ISIN", "Name", "Weight (%)", "Sector", "Location"]]
    dataset = dataset.rename(columns={"Weight (%)": name, "Location": "Country", "Sector": "Industry Classification"})
    dataset[name] = dataset[name].astype(float)
    dataset[name] = dataset[name] / 100
    return dataset

