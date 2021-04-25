import pandas as pd
import statsmodels.formula.api as sm
from index_data_handler import IndexDataHandler
from asset_allocation import AssetAllocation

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
        df[name] += value * df.loc[:, key]
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
    data_handler = IndexDataHandler(start_date=start_date, normalize=True)
    data = data_handler.get_historic_stock_data(index_code)

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


