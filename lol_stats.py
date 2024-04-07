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
API_KEY = 'RGAPI-a49c3d87-5231-4fb0-8554-bf0293d94169'

# Replace 'SUMMONER_NAME' with your summoner name, and ensure you're using the correct region
SUMMONER_NAME = 'Lunesco'

COUNT = 47


def get_puuid_url(nickname, api_key):
    return f'https://eun1.api.riotgames.com/lol/summoner/v4/summoners/by-name/{nickname}?api_key={api_key}'


def get_matches_url(puuid, count, api_key):
    return f'https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start=0&count={count}&api_key={api_key}'


def get_match_data_url(match_id, api_key):
    return f'https://europe.api.riotgames.com/lol/match/v5/matches/{match_id}?api_key={api_key}'


def get_user_puuid(nickname, api_key):
    puuid_request_url = get_puuid_url(nickname, api_key)
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
            return player
    return None


# Main workflow starts here
puuid = get_user_puuid(SUMMONER_NAME, API_KEY)
if puuid:
    match_ids = get_user_matches_ids(puuid, COUNT, API_KEY)  # Fetching details for the latest 20 matches
    data = []

    for match_id in match_ids:
        match_details = fetch_match_details(match_id, API_KEY)
        if match_details:
            my_dict = find_player_data_by_name(match_details, SUMMONER_NAME)
            my_team_id = my_dict['teamId']
            # Extract necessary match details here and append to data list
            for participant in match_details['info']['participants']:
                role = participant['lane']
                team = 'YOUR TEAM' if participant['teamId'] == my_team_id else 'ENEMY TEAM'
                kda = f"{participant['kills']}/{participant['deaths']}/{participant['assists']}"
                dmg = participant['totalDamageDealtToChampions']
                gold = participant['goldEarned']
                data.append([team, role, kda, dmg, gold])

    df = pd.DataFrame(data, columns=['Team', 'Role', 'KDA', 'DMG', 'GOLD'])

    # Adjusting Role names to match expected format (e.g., converting MID to MIDDLE)
    # This can be expanded based on the data and how Riot API returns lane information
    df['Role'] = df['Role'].replace({'MID': 'MIDDLE', 'BOT': 'BOTTOM'})

    # Create the pivot table
    table = df.pivot_table(index='Team', columns='Role', values=['KDA', 'DMG', 'GOLD'],
                           aggfunc=lambda x: ' / '.join(x.astype(str)))

    print(table)

# After your DataFrame 'table' is created
print(tabulate(table, headers='keys', tablefmt='grid'))

# Setting the visual theme
sns.set_theme(style="whitegrid")

# Assuming 'df' is your DataFrame before pivoting
for stat in ['KDA', 'DMG', 'GOLD']:
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
