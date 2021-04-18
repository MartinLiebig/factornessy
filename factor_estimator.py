import pandas as pd
import statsmodels.formula.api as sm
import requests
import json
from asset_allocation import AssetAllocation


def get_historic_stock_data(index_code, start_date="19900101", normalize=True, variant="GRTR",frequency="DAILY"):
    """
    Get historic index data directly from MSCI
    :type normalize: bool
    :param index_code: Code for the index
    :param start_date: start date in format YYYYMMdd
    :param normalize: If set to true the first value is 1, otherwise its the raw data
    :param variant: "GRTR", "NETR" or STDR. Wether to accumulate (GRTR), accumulate with taxes (NETR) or take the raw index
    :return: a data frame with the historic data for this given index
    """
    # frequency = "END_OF_MONTH"
    #frequency = "DAILY"
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
    """
    Get a dictionary with the index code we analyze. Also has the vendor, ISIN and region. For SPDR we include the ticker
    symbol which we need to get the holdings.
    :rtype: dict
    """
    index_codes = {
        "MSCI World": {"code": "990100", "region": "Developed", "ISIN": "IE00BJ0KDQ92", "vendor": "Xtrackers"},
        "Value": {"code": "705130", "region": "Developed", "ISIN": "IE00BL25JM42", "vendor": "Xtrackers"},
        "Quality": {"code": "702787", "region": "Developed", "ISIN": "IE00BL25JL35", "vendor": "Xtrackers"},
        "Multi-Factor": {"code": "706536", "region": "Developed", "ISIN": "IE00BZ0PKT83", "vendor": "iShares"},
        "Momentum": {"code": "703755", "region": "Developed", "ISIN": "IE00BL25JP72", "vendor": "Xtrackers"},
        "Small-Cap": {"code": "106230", "region": "Developed", "ISIN": "IE00BF4RFH31", "vendor": "iShares"},
        "Low Volatility (World)": {"code": "129896", "region": "Developed", "ISIN": "IE00BL25JN58",
                                   "vendor": "Xtrackers"},
        "Small-Cap (Value)": {"code": "139249", "region": "US", "ISIN": "IE00BSPLC413", "vendor": "SPDR",
                              "ticker": "zprv-gy"},
        "High-Dividend (World)": {"code": "136064", "region": "Developed", "ISIN": "IE00BCHWNQ94",
                                  "vendor": "Xtrackers"}
    }
    return index_codes

def get_em_index_codes():
    """
    Get a dictionary with the index code we analyze. Also has the vendor, ISIN and region. For SPDR we include the ticker
    symbol which we need to get the holdings.
    :rtype: dict
    """
    index_codes = {
        "EM": {"code": "664220", "region": "EM", "ISIN": "  IE00B4L5YC18", "vendor": "iShares"},
        "EM IMI": {"code": "664220", "region": "EM", "ISIN": " IE00BKM4GZ66", "vendor": "iShares"},
    }
    return index_codes



def create_index_of_indices(df, name, asset_alloc) -> pd.DataFrame:
    """
    :type asset_alloc: AssetAllocation
    :type name: str
    :type df: pd.DataFrame
    :param df: the original dataframe which holds the index prices
    :param name: the name of the new index of indices
    :param asset_alloc: the allocation of the new index of indices
    :return: df with a new column called name holding the prices of the mixed indices.
    """
    df[name] = 0

    for key, value in asset_alloc.allocations.items():
        df[name] += value * df.loc[:,key]
    return df


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
    factors = __get_ff_factors__(region).reindex().drop(["date", "RF"], axis=1)

    return factors.agg(['mean'])


def estimate(index_code, start_date, region="Developed"):
    data = get_historic_stock_data(index_code, start_date=start_date)

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
