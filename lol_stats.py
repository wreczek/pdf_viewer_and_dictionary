"""Przydatne staty ktorych uzyjemy:
1. teamDamagePercentage
2. kda
3. ... (przegladnac tego jsona) TODO [participants]
"""
import json

import matplotlib.pyplot as plt
import pandas as pd
import requests
import seaborn as sns
from tabulate import tabulate

# Replace 'YOUR_API_KEY' with your actual API key
# API_KEY = 'RGAPI-899a4d72-7c10-4085-8a98-8cfb624744d2'
API_KEY = 'RGAPI-010023e0-531b-4083-88d7-e23aac5e2087'

# Replace 'SUMMONER_NAME' with your summoner name, and ensure you're using the correct region
SUMMONER_NAME = 'Lunesco'
TAG_LINE = 'EUNE'

TAG_LINES = {
    'ja': 'EUNE',
    'lysy': '59411%20'  # %20
}

COUNT = 8
SOLO_QUEUE_ID = 420
FLEX_QUEUE_ID = 440

QUEUE_ID = SOLO_QUEUE_ID


def get_puuid_url_new(nickname, tag_line, api_key):
    url = f'https://europe.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{nickname}/{tag_line}?api_key={api_key}'
    print(url)
    return url


def get_matches_url(puuid, count, api_key):  # TODO: add args: type, queue
    url = f'https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start=0&count={count}&api_key={api_key}&type=ranked&queue={QUEUE_ID}'
    print(url)
    return url


def get_match_data_url(match_id, api_key):
    url = f'https://europe.api.riotgames.com/lol/match/v5/matches/{match_id}?api_key={api_key}'
    print(url)
    return url


def get_user_puuid(nickname, tag_line, api_key):
    # puuid_request_url = get_puuid_url(nickname, api_key)
    puuid_request_url = get_puuid_url_new(nickname, tag_line=TAG_LINE, api_key=api_key)
    resp = requests.get(puuid_request_url)
    if resp.status_code == 200:
        return resp.json()['puuid']
    else:
        print(f"Error fetching PUUID: {resp.text}")
        return None


def get_user_matches_ids(puuid, count, api_key):
    matches_request_url = get_matches_url(puuid, count, api_key)
    resp = requests.get(matches_request_url)
    if resp.status_code == 200:
        return json.loads(resp.text)
    else:
        print(f"Error fetching matches: {resp.text}")
        return []


def fetch_match_details(match_id, api_key):
    match_data_url = get_match_data_url(match_id, api_key)
    resp = requests.get(match_data_url)
    if resp.status_code == 200:
        return json.loads(resp.text)
    else:
        print(f"Error fetching match details for {match_id}: {resp.text}")
        return None


def find_player_data_by_name(match_info, summoner_name):
    for player in match_info['info']['participants']:
        if player.get('riotIdGameName') == summoner_name:
            print(f'{player=}')
            return player
    return None


table = None
# List of teammates' nicknames
team_nicknames = {"Lunesco", "badgar", "Gralfindel", "Derrezed", "GTraxX"}

# Main workflow starts here
puuid = get_user_puuid(SUMMONER_NAME, TAG_LINE, API_KEY)
match_ids = []

if puuid:
    match_ids = get_user_matches_ids(puuid, COUNT, API_KEY)  # Fetching details for the latest 20 matches
    data = []

print(f'{puuid=}')

# Initialize counters
total_kills = 0
total_deaths = 0
total_assists = 0
matches_analyzed = 0

for match_id in match_ids:
    players = set()
    match_details = fetch_match_details(match_id, API_KEY)
    if match_details:
        if match_details['info']['gameDuration'] < 900 or match_details['info']['queueId'] != QUEUE_ID:
            continue
        if match_details is None:
            break
        my_dict = find_player_data_by_name(match_details, SUMMONER_NAME)
        if my_dict is None:
            continue
        my_team_id = my_dict['teamId']
        participant_nicknames = {participant['riotIdGameName'] for participant in
                                 match_details['info']['participants']}
        # if not team_nicknames.issubset(participant_nicknames):
        #     continue

        for participant in match_details['info']['participants']:
            # lane = participant['lane']
            role = participant['individualPosition']
            team = 'YOUR TEAM' if participant['teamId'] == my_team_id else 'ENEMY TEAM'
            kills = participant['kills']
            deaths = participant['deaths']
            assists = participant['assists']
            kda = round(participant['challenges']['kda'], 2)
            dmg = participant['totalDamageDealtToChampions']
            gold = participant['goldEarned']
            turret_dmg = participant['damageDealtToTurrets']
            data.append([team, role, kda, dmg, gold, turret_dmg])

df = pd.DataFrame(data, columns=['Team', 'Role', 'KDA', 'DMG', 'GOLD', 'TURRET_DMG'])

# Adjusting Role names to match expected format
# This can be expanded based on the data and how Riot API returns lane information
df['Role'] = df['Role'].replace({'MIDDLE': 'MID', 'UTILITY': 'SUPP', 'BOTTOM': 'ADC'})

# Create the pivot table
table = df.pivot_table(index='Team', columns='Role', values=['KDA', 'DMG', 'GOLD', 'TURRET_DMG'],
                       aggfunc=lambda x: ' / '.join(x.astype(str)))

print(table)

# After your DataFrame 'table' is created
print(tabulate(table, headers='keys', tablefmt='grid'))

# Setting the visual theme
sns.set_theme(style="whitegrid")

# Assuming 'df' is your DataFrame before pivoting
for stat in ['KDA', 'DMG', 'GOLD', 'TURRET_DMG']:
    plt.figure(figsize=(10, 6))
    sns.barplot(data=df, x='Role', y=stat, hue='Team')
    plt.title(f'Team Comparison by {stat}')
    plt.ylabel(stat)
    plt.xlabel('Role')
    plt.xticks(rotation=45)
    plt.legend(title='Team')
    plt.tight_layout()
    plt.show()

print()
