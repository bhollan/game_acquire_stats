import pandas as pd
import numpy as np
import requests
import aiohttp
import asyncio
import time

print("Reading pickle file....")
players = pd.read_pickle("players.pkl")
print(players.info())
print("")

start_time = time.time()

async def get_stats(session, url):
    async with session.get(url) as resp:
        if resp.status == 404:
            return ""
        body = await resp.content.read()
        return body

async def main():

    async with aiohttp.ClientSession() as session:

        tasks = []
        for url in players['url']:
            tasks.append(asyncio.ensure_future(get_stats(session, url)))

        print(f"...fetching {len(tasks)} tasks...")
        print("--- %s seconds ---" % (time.time() - start_time))

        player_stats_pages = await asyncio.gather(*tasks)
        players["stats_page"] = player_stats_pages

asyncio.run(main())








print(f"Read in {len(players)} rows into players")
print("saving to pickle...")
players.to_pickle("./players.pkl")


