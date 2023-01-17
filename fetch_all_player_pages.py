import pandas as pd
import numpy as np
import requests
import json
from base64 import b64encode as b64
import asyncio
import aiohttp
import time
import itertools


from username_to_user_id import username_to_user_id   # from original repo
old_names = set(username_to_user_id.keys())

ratings_url = 'https://acquire.tlstyer.com/stats/data/ratings.json'
resp = requests.get(ratings_url)
stats = json.loads(resp.text)

rated_names = set()
for key in stats.keys():
    for rating in stats[key]:
        name = rating[0]
        rated_names.add(name)

# /encoded_username.json
player_page_root = 'https://acquire.tlstyer.com/stats/data/users/'
# extract all names from their JSON responses


print(f'Rated user rows: {len(list(rated_names))}')
print(f'Old user rows: {len(old_names)}')
print(f'Total: {len(rated_names.union(old_names))}')
print('')
print('Creating dataframe...')

starter_names = rated_names.union(old_names)

players = pd.DataFrame()
usernames = pd.Series(list(starter_names))
players['username'] = usernames
players['encoded_username'] = ''
players['url'] = ''
players['wave'] = np.nan
players['ratings'] = ''

flavors = ['S2', 'S3', 'S4', 'T']
attrs = ['record', 'last_played']

combos = list(itertools.product(flavors, attrs))
COLS = ['_'.join(combo) for combo in combos]

for col in COLS:
    players[f'{col}'] = np.nan


def encode_username(s_ascii='username'):
    s_code = b64(s_ascii.encode('utf-8')).decode('utf-8')
    s_code = s_code.replace('=', '')
    s_code = s_code.replace('+', '')
    s_code = s_code.replace('\/', '_')
    return s_code


async def get_stats(session, url):
    async with session.get(url) as resp:
        if resp.status == 404:
            return ''
        body = await resp.content.read()
        return body


def extract_ratings(page):
    print(page)
    return json.loads(page)['ratings']


async def main(players, wave):
    adding = players[players['url'] == '']

    adding['encoded_username'] = adding['username'].apply(encode_username)
    adding['url'] = player_page_root + adding['encoded_username'] + '.json'
    urls = adding['url']

    async with aiohttp.ClientSession() as session:

        tasks = []
        for url in urls:
            tasks.append(asyncio.ensure_future(get_stats(session, url)))

        print(f'...fetching wave {wave} with {len(tasks)} tasks...')
        print('--- %s seconds ---' % (time.time() - start_time))

        player_stats_pages = await asyncio.gather(*tasks)
        adding['stats_page'] = player_stats_pages
        adding['ratings'] = adding['stats_page'].str.decode("utf-8")
        adding['wave'] = wave
        return adding


start_time = time.time()

wave = 0

while(True):

    players = asyncio.run(main(players, wave))

    this_wave = players[players['wave'] == wave]
    blanks = this_wave['stats_page'].isna()
    this_wave['ratings'] = this_wave[~blanks]['stats_page'].apply(json.loads)

    COLS = ['_'.join(combo) for combo in combos]

    known_players = set(players['username'])
    new_players = set()

    wave += 1
    if wave > 2:
        print('breaking')
        break

print(f'Read in {len(players)} rows into players')
print('saving to CSV...')
# players.to_pickle('./players.pkl')
players.to_csv('./players.csv')
