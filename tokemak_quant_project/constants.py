"""
Holds some global constants
"""
import os

import web3
from dotenv import load_dotenv

load_dotenv()
w3 = web3.Web3(web3.Web3.HTTPProvider(os.getenv('PROVIDER_URL')))
latest_block = 15876780 # hard coded for reproducibility

pool_addresses = [
    "0xecBa967D84fCF0405F6b32Bc45F4d36BfDBB2E81",
    "0x470e8de2eBaef52014A47Cb5E6aF86884947F08c",
    "0xdC08159A6C82611aEB347BA897d82AC1b80D9419",
    "0xCE84867c3c02B05dc570d0135103d3fB9CC19433",
    "0x43AE24960e5534731Fc831386c07755A2dc33D47",
    "0xAd5B1a6ABc1C9598C044cea295488433a3499eFc",
    "0xC3f279090a47e80990Fe3a9c30d24Cb117EF91a8",
    "0x53162D78dCa413d9e28cf62799D17a9E278B60E8",
    "0xA1d7b2d891e3A1f9ef4bBC5be20630C2FEB1c470",
    "0x795065dCc9f64b5614C407a6EFDC400DA6221FB0",
    "0xe55c3e83852429334A986B265d03b879a3d188Ac",
    "0x61eB53ee427aB4E007d78A9134AaCb3101A2DC23",
    "0x54138c3d494ec7edE33ed08EE6e0f7BC6149e2fC"
]
pool_addresses = [web3.Web3.toChecksumAddress(p) for p in pool_addresses]

USDC = web3.Web3.toChecksumAddress('0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48')
WETH = web3.Web3.toChecksumAddress('0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2')