"""
Use binary search to map timestamps to block numbers
"""

import datetime
import time
import pandas as pd

from constants import latest_block, w3

def estimate_block_height_by_timestamp(desired_timestamp: int, close_in_seconds:int = 60 ):
    """
    Get the block nearest to timestamp with in close_in_seconds using binary search
    """
    # adapted from https://ethereum.stackexchange.com/questions/62007/how-to-get-the-blocks-between-timestamp
    block_found = False
    #max_block = w3.eth.block_number
    max_block = latest_block # hard coded for reproducibility 
    min_block = 0
    
    while not block_found:
        mid_block = (max_block +  min_block) // 2
        try:
            block = w3.eth.getBlock(mid_block)
        except Exception as e:
            print(e) # avoid rate limits
            time.sleep(1)
            
        found_timestamp = block.timestamp
        difference_in_seconds = desired_timestamp - found_timestamp
        if abs(difference_in_seconds) < close_in_seconds:
            return mid_block

        if desired_timestamp > found_timestamp:
            # we need to go right
            min_block = mid_block
        else:
            # the block is to the left
            max_block = mid_block


def get_timestamps_for_the_previous_N_days(N_days: int=180) -> list[int]:
    """
    Build a list of the last N timestamps at 12AM GMT for the previous N_days
    """
    #today = datetime.datetime.now().date()
    today = datetime.date(2022, 11, 1) # hard coded for reproducibility 
    last_6_months_of_days = [today - (i * datetime.timedelta(days=1)) for i in range(N_days)]
    timestamps = [int(pd.Timestamp(day).timestamp()) for day in last_6_months_of_days]
    return timestamps


def build_timestamp_df(n_days: int) -> pd.DataFrame:
    """
    Build a dataframe of with columns timestamp, block_number for each timestamp in of the previous N days
    """
    timestamps = get_timestamps_for_the_previous_N_days(n_days)
    block_timestamps = [{'timestamp': t, 'block_number': estimate_block_height_by_timestamp(t)} for t in timestamps]
    return pd.DataFrame.from_records(block_timestamps)

