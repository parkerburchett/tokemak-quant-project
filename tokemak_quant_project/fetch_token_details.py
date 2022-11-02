"""
Holds logic to fetch on-chain data about the tokens in the pools
"""

import pandas as pd

from abi import ERC20, UNISWAPV2_LP
from constants import w3


def build_token_df(pool_addresses: list[str]) -> pd.DataFrame:
    """
    Build a pd.DataFrame of token_address, decimals, symbol for each asset token in pool_addresses
    """
    asset_tokens = _get_unique_tokens(pool_addresses)
    token_df = _get_token_details(asset_tokens)
    return token_df


def _get_unique_tokens(pool_addresses: list[str]) -> set[str]:
    """
    Returns the set of unique asset tokens in pool_addresses
    """
    asset_tokens = set()
    for address in pool_addresses:
        pool_contract = w3.eth.contract(address, abi=UNISWAPV2_LP)
        token0 = pool_contract.functions.token0().call()
        token1 = pool_contract.functions.token1().call()
        asset_tokens.add(token0)
        asset_tokens.add(token1)
    
    return asset_tokens


def _get_token_details(asset_tokens: set[str]) -> pd.DataFrame:
    """
    Fetch on-chain a pd.DataFrame of token_address, decimals, symbol for each token in token_addresses
    """
    token_details = []

    for token_address in asset_tokens:
        erc20_token_contract = w3.eth.contract(token_address, abi=ERC20)
        details = {
            'address': erc20_token_contract.address, 
            'decimals': erc20_token_contract.functions.decimals().call(),
            'symbol': erc20_token_contract.functions.symbol().call()
        }
        token_details.append(details)

    return pd.DataFrame.from_records(token_details)
