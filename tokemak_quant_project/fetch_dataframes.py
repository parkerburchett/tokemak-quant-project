"""
Build the summary dataframes to use for analysis
"""
import pandas as pd

from pool import Pool
import web3

from constants import WETH
from get_prices import compute_il, get_eth_price



def build_eth_price_df(timestamp_df: pd.DataFrame):
    """Build a pd.DataFrame of the ETH prices using the uniswapV2 router WETH->USDC"""
    eth_prices = []
    for timestamp, block in zip(timestamp_df['timestamp'], timestamp_df['block_number']):
        eth_price = get_eth_price(block)
        eth_prices.append({'token_address': WETH, 'price': eth_price, 'timestamp': timestamp, 'block_number': block})
            
    return pd.DataFrame.from_records(eth_prices)


def build_token_price_and_reserves_by_block_df(pool: Pool, timestamp_df: pd.DataFrame,
                                               eth_price_df: pd.DataFrame) -> pd.DataFrame:
    """
    Build a pd.DataFrame of reserves and prices in pool by block given the eth_prices for each block in timestamp_df
    """
    timestamp_df = timestamp_df.sort_values('block_number', ascending=False).reset_index()
    data = []
    for timestamp, block in zip(timestamp_df['timestamp'], timestamp_df['block_number']):
        eth_price = eth_price_df[eth_price_df['block_number'] == block]['price'] 

        try:
            pool_data = pool.get_prices(block, eth_price)
            pool_data['timestamp'] = timestamp
            data.append(pool_data)
        except (web3.exceptions.BadFunctionCallOutput, web3.exceptions.BlockNumberOutofRange) as e:
            print(type(e), e, pool.address, block)
            break
    
    historial_df = pd.DataFrame.from_records(data)
    historial_df['token0_address'] = pool.token0_address
    historial_df['token1_address'] = pool.token1_address
    return historial_df


def build_historical_dfs(pool_addresses: list[str], timestamp_df: pd.DataFrame, eth_price_df: pd.DataFrame
                         ) -> list[pd.DataFrame]:

    historical_dfs = []
    for p in pool_addresses:
        try:
            historical_df = build_token_price_and_reserves_by_block_df(Pool(p), timestamp_df, eth_price_df)
            historical_dfs.append(historical_df)
            print('success building a historical_df for', p, historical_df.shape)
        except Exception as e:
            print(e, type(e), p)
    
    return historical_dfs


def build_price_df(historical_dfs: pd.DataFrame):
    df = pd.concat(historical_dfs)
    token0_prices = df[['block_number', 'token0_address', 'token0_price']]
    token1_prices = df[['block_number', 'token1_address', 'token1_price']]
    token0_prices.columns = ['block_number', 'token_address', 'price']
    token1_prices.columns = ['block_number', 'token_address', 'price']
    price_df = pd.concat([token0_prices, token1_prices]).groupby(['token_address', 'block_number'])['price'].mean()
    return price_df.reset_index()


def build_asset_il_df(price_df: pd.DataFrame, days_lag: int=7):
    """Build a dataframe of the prices of the token assets in pool for a 7 day lag"""
    il_df = price_df[['block_number','timestamp', 'pool_address']].sort_values('block_number').copy()
    il_df['token0_p0'] = price_df['token0_price']
    il_df['token0_p1'] = price_df.shift(days_lag)['token0_price']

    il_df['token1_p0'] = price_df['token1_price']
    il_df['token1_p1'] = price_df.shift(days_lag)['token1_price']
    il_df = il_df.dropna() 
    il_df['il'] = il_df[
        ['token0_p0', 'token0_p1', 'token1_p0', 'token1_p1']].apply(lambda row: compute_il(*row), axis=1)

    return il_df


def build_il_df(historical_dfs: list[pd.DataFrame], day_lag: int=7) -> pd.DataFrame:
    """Build a dataframe holding IL loss by day lag for each df in historical_dfs"""
    return pd.concat([build_asset_il_df(df, day_lag) for df in historical_dfs])

