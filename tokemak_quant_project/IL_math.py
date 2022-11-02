"""
Math for IL
"""
def compute_il(token0_p0: float, token0_p1: float, token1_p0: float, token1_p1: float) -> float: 
    """
    Compute the IL as a percent given the starting and ending token prices of two tokens

    token0_p0 : token0 priced at period0,
    token0_p1 : token0 priced at period1,

    token1_p0 : token0 priced at period0,
    token1_p1 : token0 priced at period1,
    """
    price_ratio = (token0_p1 / token0_p0) / (token1_p1 / token1_p0) # ending price / starting price
    return 100 * (2 * (price_ratio**.5) / (1+price_ratio) - 1)