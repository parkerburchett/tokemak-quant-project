"""
Price tokens using the UniswapV2RouterContract
"""
from abi import UNISWAPV2_ROUTER 
import web3
from constants import USDC, WETH, w3



ROUTER = w3.eth.contract('0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D', abi=UNISWAPV2_ROUTER)


def get_eth_price(block: int) -> float:
    """Returns the price of ETH at block according to the uniswap router contract"""
    if not isinstance(block, int):
        block = int(block)
    response = ROUTER.functions.getAmountsOut(
        10**18, [WETH, USDC]).call(block_identifier=block)
    return response[1] / 10**6 # because usdc has 6 decimal places

# this sometimes fails and gives wrong answers
# def get_token_to_eth(token_address: str, block: int):
#     """Return the price of token_address in terms of eth at block""" # note this is buggy fd
#     if not isinstance(block, int):
#         block = int(block)
#     response = ROUTER.functions.getAmountsOut(
#         10**18, [web3.Web3.toChecksumAddress(token_address), WETH]).call(block_identifier=block)
#     return response[1] / 10**18 


def compute_il(token0_p0, token0_p1, token1_p0, token1_p1) -> float: 
    # returns the IL as a percent
    if 0 in [token0_p0, token0_p1, token1_p0, token1_p1]:
        return 0.0
    price_ratio = (token0_p1 / token0_p0) / (token1_p1 / token1_p0) # ending price / starting price
    return 100 * (2 * (price_ratio**.5) / (1+price_ratio) - 1)
