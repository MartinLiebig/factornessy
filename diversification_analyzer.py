import requests
import pandas as pd
from factor_estimator import get_common_index_codes


# https://etf.dws.com/etfdata/export/DEU/DEU/excel/product/constituent/IE00BL25JM42
# https://www.ssga.com/de/en_gb/intermediary/etfs/library-content/products/fund-data/etfs/emea/holdings-daily-emea-en-zprv-gy.xlsx

def get_xtrackers(ISIN: str, name: str):
        dataset = pd.read_excel("https://etf.dws.com/etfdata/export/DEU/DEU/excel/product/constituent/" + ISIN,
                                skiprows=[0, 1, 2])
        dataset = dataset.rename({"Weighting": name})
        dataset = dataset.set_index("Name")
        return dataset

def get_spdr(ticker: str, name: str):
    dataset = pd.read_excel("https://www.ssga.com/de/en_gb/intermediary/etfs/library-content/products/fund-data/etfs/emea/holdings-daily-emea-en"+ticker+".xlsx",
                            skiprows=[0, 1, 2])
    dataset = dataset.rename({"Weighting": name})
    dataset = dataset.set_index("Name")
    return dataset
if __name__ == '__main__':
    indices = get_common_index_codes()
    data = []
    for key in indices:
        # print(key)
        # if (indices[key]["vendor"] == "Xtrackers"):
        #     data.append(get_data(indices[key]["ISIN"],key))
        if (indices[key]["vendor"] == "SPDR"):
            get_spdr(indices["ticker"])
    df = data[0]
    for i in range(1,len(data)):
        print(i)
        df = df.merge(data[i],how="outer",on="Name")
    print(df)
    print(df.columns)



