"""
Script to build the datasets to use later for analysis

"""
from datetime import datetime

import pandas as pd

from block_to_time_stamp import build_timestamp_df
from constants import pool_addresses
from fetch_dataframes import (build_eth_price_df, build_historical_dfs,
                              build_il_df, build_price_df)
from fetch_token_details import build_token_df


def main(n_days=360):
    # build token_df
    start = datetime.now()
    print('start', start)
    token_df = build_token_df(pool_addresses)
    token_df.to_csv('tokemak_quant_project/data/token_df.csv', index=False)
    print('saved token_df')

    timestamp_df = build_timestamp_df(n_days=n_days) # takes a while
    timestamp_df.to_csv('tokemak_quant_project/data/timestamp_df.csv', index=False)
    print('saved timestamp_df')

    eth_price_df = build_eth_price_df(timestamp_df)
    eth_price_df.to_csv('tokemak_quant_project/data/eth_price_df.csv', index=False)
    print('saved eth_price_df')

    historical_dfs = build_historical_dfs(pool_addresses, timestamp_df, eth_price_df)
    historical_df = pd.concat(historical_dfs)
    historical_df.to_csv('tokemak_quant_project/data/historical_df.csv', index=False)
    print('saved historical_df')

    il_df = build_il_df(historical_dfs, day_lag=7)
    il_df.to_csv('tokemak_quant_project/data/il_df.csv', index=False)
    print('saved il_df')

    price_df = build_price_df(historical_dfs)
    price_df.to_csv('tokemak_quant_project/data/price_df.csv', index=False)
    print('saved price_df')

    flat_price_df = price_df.pivot(index='block_number', values='price', columns='token_address')
    flat_price_df.to_csv('tokemak_quant_project/data/flat_price_df.csv', index=False)
    print('saved flat_price_df')
    print('time taken', datetime.now() - start)


if __name__ == '__main__':
    main()
