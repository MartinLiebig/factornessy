import pandas as pd
import pandas_datareader as pdr
import statsmodels.formula.api as sm
import yfinance as yf
import requests
import json


def get_prices(index_code, start_date="19900101", normalize=True, variant="GRTR"):
    """

    :rtype: pd.DataFrame
    """

    # frequency = "END_OF_MONTH"
    frequency = "DAILY"
    json_data = requests.get(
        "https://app2.msci.com/products/service/index/indexmaster/getLevelDataForGraph?currency_symbol=USD&index_variant=" + variant + "&start_date=" + start_date + "&end_date=20210101&data_frequency=" + frequency + "&index_codes=" + index_code).content
    y = json.loads(json_data)
    data = y['indexes']['INDEX_LEVELS']

    df = pd.DataFrame.from_dict(data)

    if normalize is True:
        first_value = df["level_eod"].iloc[0]
        df["level_eod"] = df["level_eod"] / first_value
    df.rename(columns={'calc_date': 'date'}, inplace=True)
    df.set_index("date")

    df['date'] = pd.to_datetime(df['date'], format='%Y%m%d')
    return df


def get_common_index_codes():
    index_codes = {
        "MSCI World": {"code": "990100", "region": "Developed"},
        "Value": {"code": "705130", "region": "Developed"},
        "Quality": {"code": "702787", "region": "Developed"},
        "Multi-Factor": {"code": "706536", "region": "Developed"},
        "Momentum": {"code": "703755", "region": "Developed"},
        "Small-Cap": {"code": "106230", "region": "Developed"},
        "Low Volatility (World)": {"code": "129896", "region": "Developed"},
        "Small-Cap (Value)": {"code": "139249", "region": "US"}
    }
    return index_codes


def __get_path__(region):
    if region == "US":
        return "ressources/F-F_Research_Data_5_Factors_2x3_daily.CSV"
    elif region == "Developed":
        return "ressources/Developed_5_Factors_Daily.CSV"


def __get_ff_factors__(region) -> pd.DataFrame:
    # factors = pdr.DataReader(name='F-F_Research_Data_5_Factors_2x3_Daily',
    #                          data_source='famafrench')[0]
    factors = pd.read_csv(__get_path__(region), skiprows=range(0, 3))

    factors.rename(columns={'Mkt-RF': 'MKT', "Unnamed: 0": "date"}, inplace=True)
    factors['date'] = pd.to_datetime(factors['date'], format='%Y%m%d')
    factors.set_index("date")
    factors['MKT'] = factors['MKT'] / 100
    factors['SMB'] = factors['SMB'] / 100
    factors['HML'] = factors['HML'] / 100
    factors['RMW'] = factors['RMW'] / 100
    factors['CMA'] = factors['CMA'] / 100
    return factors


def get_average_factors(region) -> pd.DataFrame:
    factors = __get_ff_factors__(region).reindex().drop(["date","RF"],axis=1)

    return factors.agg(['mean'])


def estimate(index_code, start_date, region="Developed"):
    data = get_prices(index_code, start_date=start_date)

    data['Returns'] = data['level_eod'].pct_change()  # Create daily returns column
    data['Returns'] = data['Returns'].dropna()  # Remove values of N/A

    stock_factor_mat = pd.merge(data,
                                __get_ff_factors__(region=region),
                                left_on="date",
                                right_on="date")  # Merging the stock and factor returns dataframes together

    stock_factor_mat['XsRet'] = (stock_factor_mat['Returns']
                                 - stock_factor_mat['RF'])  # Calculating excess returns

    FF5 = sm.ols(formula='XsRet ~ MKT + SMB + HML + RMW + CMA',
                 data=stock_factor_mat).fit()

    FF5_coeff = FF5.params

    return FF5_coeff, FF5, stock_factor_mat


