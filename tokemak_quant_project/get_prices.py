"""
Price tokens using the UniswapV2RouterContract and the ETH price
"""
from abi import UNISWAPV2_ROUTER 
import web3
from constants import USDC, WETH, w3
import pandas as pd
from pool import Pool


ROUTER = w3.eth.contract('0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D', abi=UNISWAPV2_ROUTER)


def get_eth_price(block: int) -> float:
    """Returns the price of ETH at block according to the uniswap router contract"""
    if not isinstance(block, int):
        block = int(block)
    response = ROUTER.functions.getAmountsOut(
        10**18, [WETH, USDC]).call(block_identifier=block)
    return response[1] / 10**6 # because usdc has 6 decimal places


def get_token_to_eth(token_address: str, block: int):
    """Return the price of token_address in terms of eth at block"""
    if not isinstance(block, int):
        block = int(block)
    response = ROUTER.functions.getAmountsOut(
        10**18, [web3.Web3.toChecksumAddress(token_address), WETH]).call(block_identifier=block)
    return response[1] / 10**18 


def build_eth_prices(timestamp_df: pd.DataFrame):
    """Build a  pd.DataFrame of the ETH prices"""
    eth_prices = []
    for timestamp, block in zip(timestamp_df['timestamp'], timestamp_df['block_number']):
        eth_price = get_eth_price(block)
        eth_prices.append({'token_address': WETH, 'price': eth_price, 'timestamp': timestamp, 'block': block})
            
    return pd.DataFrame.from_records(eth_prices)


def build_price_df(token_address: str, timestamp_df: pd.DataFrame, eth_price_df: pd.DataFrame) -> pd.DataFrame:
    """
    Build a pd.DataFrame with columns 'token_address', 'block', 'timestamp', 'price' for each block in timestamp_df
    """
    token_in_terms_of_eth = []
    for timestamp, block in zip(timestamp_df['timestamp'], timestamp_df['block_number']):
        token_price_in_eth = get_token_to_eth(token_address, block)
        token_in_terms_of_eth.append({'token_price_in_eth': token_price_in_eth, 'timestamp': timestamp, 'block': block})
    
    price_df = pd.DataFrame.from_records(token_in_terms_of_eth)
    price_df['price'] = price_df['token_price_in_eth'] * eth_price_df['price']
    price_df['token_address'] = token_address
    return price_df[['token_address', 'block', 'timestamp', 'price']]


def build_shifted_lagged_price_df(price_df: pd.DataFrame, days_lag: int=7):
    """
    Build a lagged_price df with the price, price + days_lag in the future
    """
    lagged_price_df = lagged_price_df.rename(columns={'starting_price':'price'})
    lagged_price_df['lag_price'] = price_df.shift(days_lag)['price']
    return lagged_price_df


def compute_il(token0_p0, token0_p1, token1_p0, token1_p1) -> float: 
    # returns the IL as a percent
    price_ratio = (token0_p1 / token0_p0) / (token1_p1 / token1_p0) # ending price / starting price
    return 100 * (2 * (price_ratio**.5) / (1+price_ratio) - 1)


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




# from get_prices import get_token_to_eth, ROUTER
# # quoter is bad. it is giving the wrong prices for some data
# alcx = '0xdBdb4d16EdA451D0503b854CF79D55697F90c8DF'
# eth_price = get_eth_price(latest_block)
# alex_price_in_eth = get_token_to_eth(alcx, latest_block)
# alex_price_in_eth * eth_price

# # price_dfs = {WETH:eth_price_df}
# for address in token_df['address']:
#     try:
#         price_df = build_price_df(address, timestamp_df, eth_price_df)
#         print(price_df.shape)
#         price_dfs[address] = price_df
#     except Exception as e:
#         print(address, type(e), e)
#price_df = pd.concat(price_dfs.values())
