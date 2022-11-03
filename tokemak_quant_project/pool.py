
import time

import requests

from abi import UNISWAPV2_LP
from constants import WETH, w3


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
        except requests.HTTPError:
            time.sleep(5)
            reserves_0, reserves_1, _ = self.contract.functions.getReserves().call(block_identifier=block_number)

        # except (web3.exceptions.BadFunctionCallOutput, web3.exceptions.BlockNumberOutofRange) as e:
        #     # thrwon if the fucntionc all failes
        #     print(type(e), e, 'block', block_number)
        #     exists = False
        #     reserves_0, reserves_1 = 0, 0

        return {
            'pool_address': self.address,
            'block_number': block_number,
            'token0_reserves': reserves_0 / 10**18, # all the tokens in our sample at 18 decimals so we can hard code this
            'token1_reserves': reserves_1 / 10**18,
        }
    
    def get_prices(self, block_number: int, eth_price: float) -> dict:
        """
        Get the prices of the assets in the pool at block number given the price of ETH at this block
        """
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

        else:
            raise ValueError('Expected at least one token in pool to be WETH and neither are pool:', self.__dict__())
        
        return reserves



