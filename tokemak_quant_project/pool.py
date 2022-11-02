
import time
from collections.abc import Iterable

import pandas as pd
import requests
import web3

from abi import UNISWAPV2_LP
from constants import w3, WETH


class Pool:
    """
    Simple wrapper around a uniswap v2 pool
    """
    
    def __init__(self, address: str):
        self.contract = w3.eth.contract(address, abi=UNISWAPV2_LP)
        self.address = self.contract.address
        self.token0_address = self.contract.functions.token0().call()
        self.token1_address = self.contract.functions.token1().call()
    

    def get_reserves(self, block_number: int) -> dict:
        try:
            reserves_0, reserves_1, _ = self.contract.functions.getReserves().call(block_identifier=block_number)
            exists = True
        except requests.HTTPError:
            time.sleep(1)
            try:
                reserves_0, reserves_1, _ = self.contract.functions.getReserves().call(block_identifier=block_number)
                exists = True
            except:
                raise web3.exceptions.BlockNumberOutofRange
        except web3.exceptions.BlockNumberOutofRange as e:
            print(type(e), e)
            exists = False
            reserves_0, reserves_1 = 0, 0

        return {
            'pool_address': self.address,
            'exists': exists,
            'block_number': block_number,
            'token0_reserves': reserves_0 / 10**18, # all the tokens in our sample at 18 decimals so we can hard code this
            'token1_reserves': reserves_1 / 10**18,
        }
    
    def get_prices(self, block_number: int, eth_price: float) -> dict:
        """
        Get the prices of the assets in the pool at block number given the price of ETH at this block
        """
        if not isinstance(eth_price, float):
            eth_price = float(eth_price)
        reserves = self.get_reserves(block_number)

        # Because amount_other_token * other_token_price = value_of_weth_in_pool
        # we can infer the other token price because the value of each side of the pool must equal
        if self.token0_address == WETH:
            # how much weth is in the pool * price of weth = weth value
            value_of_weth_in_pool = reserves['token0_reserves'] * eth_price
            amount_other_token = reserves['token1_reserves']
            reserves['token0_price'] = eth_price
            reserves['token1_price'] = value_of_weth_in_pool / amount_other_token

        elif self.token1_address == WETH:
            value_of_weth_in_pool = reserves['token1_reserves'] * eth_price
            amount_other_token = reserves['token0_reserves']
            reserves['token1_price'] = eth_price
            reserves['token0_price'] = value_of_weth_in_pool / amount_other_token

        return reserves


def build_historial_df(pool: Pool, timestamp_df: Iterable[int], eth_price_df: pd.DataFrame) -> pd.DataFrame:
    """
    Build a pd.DataFrame holding the token reserves and prices in pool by block given the eth_prices for each block
    you are interested in
    """
    timestamp_df = timestamp_df.sort_values('block_number', ascending=False).reset_index()
    data = []
    for _, row in timestamp_df.iterrows():
        eth_price = eth_price_df[eth_price_df['block_number'] == int(row['block_number'])]['price']
        pool_data = pool.get_prices(int(row['block_number']), eth_price)
        pool_data['timestamp'] = row['timestamp']
        if pool_data['exists'] == False:
            break
        data.append(pool_data)
    
    historial_df = pd.DataFrame.from_records(data)
    historial_df['token0_address'] = pool.token0_address
    historial_df['token1_address'] = pool.token1_address
    return historial_df

