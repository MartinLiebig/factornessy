import pandas as pd
import pandas_datareader as pdr
import statsmodels.formula.api as sm
import yfinance as yf
import requests
import json


def get_prices(index_code, start_date="19900101", normalize=True):
    """

    :rtype: pd.DataFrame
    """

    # frequency = "END_OF_MONTH"
    frequency = "DAILY"
    json_data = requests.get(
        "https://app2.msci.com/products/service/index/indexmaster/getLevelDataForGraph?currency_symbol=USD&index_variant=STRD&start_date=" + start_date + "&end_date=20210101&data_frequency=" + frequency + "&index_codes=" + index_code).content
    y = json.loads(json_data)
    data = y['indexes']['INDEX_LEVELS']

    df = pd.DataFrame.from_dict(data)

    if normalize is True:
        first_value = df["level_eod"].iloc[0]
        df["level_eod"] = df["level_eod"]/first_value
    df.rename(columns={'calc_date': 'date'}, inplace=True)
    df.set_index("date")


    df['date'] = pd.to_datetime(df['date'], format='%Y%m%d')
    return df


def get_common_index_codes():
    index_codes = {"MSCI World": "990100", "Value": "705130", "Quality": "702787", "Multi-Factor": "706536",
                   "Momentum": "703755", "Small-Cap": "106230", "High Dividend": "136064",
                   "Low Volatility (World)":"129896", "Small-Cap (Value)":"139249"
                   }
    return index_codes


class FactorEstimator:

    def estimate(self, index_code,start_date):
        data = get_prices(index_code,start_date=start_date)

        data['Returns'] = data['level_eod'].pct_change()  # Create daily returns column
        data['Returns'] = data['Returns'].dropna()  # Remove values of N/A

        stock_factor_mat = pd.merge(data,
                                    self.__get_ff_factors__(),
                                    left_on="date",
                                    right_on="date")  # Merging the stock and factor returns dataframes together

        stock_factor_mat['XsRet'] = (stock_factor_mat['Returns']
                                     - stock_factor_mat['RF'])  # Calculating excess returns

        FF5 = sm.ols(formula='XsRet ~ MKT + SMB + HML + RMW + CMA',
                     data=stock_factor_mat).fit()

        FF5_coeff = FF5.params

        return FF5_coeff, FF5, stock_factor_mat

    def __get_ff_factors__(self):
        # factors = pdr.DataReader(name='F-F_Research_Data_5_Factors_2x3_Daily',
        #                          data_source='famafrench')[0]
        factors = pd.read_csv("ressources/F-F_Research_Data_5_Factors_2x3_daily.CSV", skiprows=range(0, 3))

        factors.rename(columns={'Mkt-RF': 'MKT', "Unnamed: 0": "date"}, inplace=True)
        factors['date'] = pd.to_datetime(factors['date'], format='%Y%m%d')
        factors.set_index("date")
        factors['MKT'] = factors['MKT'] / 100
        factors['SMB'] = factors['SMB'] / 100
        factors['HML'] = factors['HML'] / 100
        factors['RMW'] = factors['RMW'] / 100
        factors['CMA'] = factors['CMA'] / 100
        return factors
