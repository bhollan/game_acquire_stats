import pandas as pd
import numpy as np
import requests
import json
import asyncio
import aiohttp
import time
import itertools
from base64 import b64encode as b64


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


def create_df_from_set_of_usernames(names):
    usernames = pd.Series(list(names))

    df = pd.DataFrame()
    df['username'] = usernames
    df['encoded_username'] = ''
    df['url'] = ''
    df['wave'] = np.nan
    df['ratings'] = ''

    flavors = ['S2', 'S3', 'S4', 'T']
    attrs = ['record', 'last_played']

    combos = list(itertools.product(flavors, attrs))
    COLS = ['_'.join(combo) for combo in combos]

    for col in COLS:
        df[f'{col}'] = np.nan
    return df


players = create_df_from_set_of_usernames(starter_names)


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


def get_ratings(row, flavor):
    if flavor in row['ratings']:
        return row['ratings'][f'{flavor}']


async def main(players, wave):
    adding = players['url'] == ''

    players.loc[adding, 'encoded_username'] = players.loc[adding, 'username'].apply(encode_username)
    players.loc[adding, 'url'] = player_page_root + players.loc[adding, 'encoded_username'] + '.json'
    urls = players.loc[adding, 'url']

    async with aiohttp.ClientSession() as session:

        tasks = []
        for url in urls:
            tasks.append(asyncio.ensure_future(get_stats(session, url)))

        print(f'...fetching wave {wave} with {len(tasks)} tasks...')
        print('--- %s seconds ---' % (time.time() - start_time))

        if len(urls) == 0:
            return players

        player_stats_pages = await asyncio.gather(*tasks)
        players.loc[adding, 'stats_page'] = player_stats_pages
        players.loc[adding, 'stats_page'] = players.loc[adding, 'stats_page'].str.decode("utf-8")
        players.loc[adding, 'wave'] = wave
        return players


start_time = time.time()


wave = 0

while(True):
    players = asyncio.run(main(players, wave))
    blanks = players['stats_page'].isna()
    players.loc[~blanks, 'ratings'] = players.loc[~blanks, 'stats_page'].apply(json.loads)
    known_players = set(players['username'].unique())
    new_players = set()
    for idx, row in players.iterrows():
        if type(row['ratings']) is not dict:
            continue
        for game in row['ratings']['games']:
            results = game[2]
            for position in results:
                player = position[0]
                if player not in known_players:
                    known_players.add(player)
                    new_players.add(player)
    print(len(known_players))
    print(len(new_players))
    if len(new_players) > 0:
        newbies = create_df_from_set_of_usernames(new_players)
        players = pd.concat([players, newbies], ignore_index=True)

    wave += 1
    if wave > 12:
        print('breaking')
        break


# flavors = ['Singles2', 'Singles3', 'Singles4', 'Teams']
print(f'Read in {len(players)} rows into players')
print('saving to CSV...')
# players.to_pickle('./players.pkl')
players.to_csv('./players.csv')
