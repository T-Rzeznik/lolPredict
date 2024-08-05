import requests, csv, os

api_key = os.getenv('RIOT_GAMES_API_KEY')
if api_key is None:
    raise ValueError("No API key found. Please set the API_KEY environment variable.")

SUMMONER_NAMES = ['MiddleFoot#NA1']  #Up to 8 summoners   NAME#TAG
REGION = 'na1'  # Change to the appropriate region

def get_summoner_data(game_name, tag_line):
    url = f'https://{REGION}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{game_name}/#{tag_line}'
    response = requests.get(url, headers={'X-Riot-Token': api_key})
    if response.status_code != 200:
        raise ValueError(f"Error fetching summoner data: {response.status_code} - {response.text}")
    return response.json()

def get_puuid(account_id):
    url = f'https://{REGION}.api.riotgames.com/riot/account/v1/accounts/by-puuid/{account_id}'
    response = requests.get(url, headers={'X-Riot-Token': api_key})
    if response.status_code != 200:
        raise ValueError(f"Error fetching PUUID: {response.status_code} - {response.text}")
    return response.json()

def get_match_history(puuid):
    url = f'https://{REGION}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids'
    params = {
        'start': 0,
        'count': 10,  # Number of matches to retrieve
    }
    response = requests.get(url, headers={'X-Riot-Token': api_key}, params=params)
    return response.json()

def get_match_details(match_id):
    url = f'https://{REGION}.api.riotgames.com/lol/match/v5/matches/{match_id}'
    response = requests.get(url, headers={'X-Riot-Token': api_key})
    return response.json()

def extract_jungler_data(match_id):
    match_data = get_match_details(match_id)  # Fetch match details
    timeline_url = f'https://{REGION}.api.riotgames.com/lol/match/v5/matches/{match_id}/timeline'
    timeline_response = requests.get(timeline_url, headers={'X-Riot-Token': api_key})
    timeline_data = timeline_response.json()  # Get timeline data

    for participant in match_data['info']['participants']:
        if participant['teamPosition'] == 'JUNGLE':
            # Extract relevant data for the first 4 minutes
            kills_first_4_min = sum(event['killType'] == 'KILL' for event in timeline_data['info']['events'] if event['timestamp'] <= 240000)
            assists_first_4_min = sum(event['killType'] == 'ASSISTS' for event in timeline_data['info']['events'] if event['timestamp'] <= 240000)
            camps_cleared_first_4_min = sum(event['type'] == 'ELITE_MONSTER_KILL' for event in timeline_data['info']['events'] if event['timestamp'] <= 240000)
            gold_earned_first_4_min = sum(event['goldEarned'] for event in timeline_data['info']['events'] if event['timestamp'] <= 240000)
            kills_details = [(event['timestamp'], event['killerId']) for event in timeline_data['info']['events'] if event['killType'] == 'KILL' and event['timestamp'] <= 240000]
            summoner_spells = participant['spell1Id'], participant['spell2Id']
            champion = participant['championId']
            first_item = next((event['itemId'] for event in timeline_data['info']['events'] if event['type'] == 'ITEM_PURCHASE' and event['timestamp'] <= 120000), None)
            level_at_first_blood = participant['championLevel'] if participant['firstBloodKill'] else None
            firstBlood = participant['firstBloodKill']
            return {
                'kills_first_4_min': kills_first_4_min,
                'assists_first_4_min': assists_first_4_min,
                'camps_cleared_first_4_min': camps_cleared_first_4_min,
                'gold_earned_first_4_min': gold_earned_first_4_min,
                'win': participant['win'],
                'kills_details': kills_details,  
                'summoner_spells': summoner_spells,  
                'champion': champion,  
                'first_item': first_item,
                'level_at_first_blood': level_at_first_blood,
                'firstBlood': firstBlood
            }
    return None

def main():
    jungler_data_list = []
    
    for summoner_name in SUMMONER_NAMES:  # Loop through each summoner name
        game_name, tag_line = summoner_name.split('#', 1)  # Split only on the first occurrence of '#'
        summoner_data = get_summoner_data(game_name, tag_line)  # Update to use new endpoint
        puuid_data = get_puuid(summoner_data['accountId'])  # Get PUUID using new endpoint
        match_history = get_match_history(puuid_data['puuid'])  # Use the retrieved PUUID
        
        for match_id in match_history:
            jungler_data = extract_jungler_data(match_id)
            if jungler_data:
                jungler_data['summoner_name'] = summoner_name  # Add summoner name to data
                jungler_data_list.append(jungler_data)
    
    # Write jungler data to CSV
    file_path = 'jungler_data.csv'
    file_exists = os.path.isfile(file_path)  # Check if the file already exists

    with open(file_path, mode='a', newline='') as file:  # Open in append mode
        writer = csv.DictWriter(file, fieldnames=jungler_data_list[0].keys())
        if not file_exists:  # Write header only if the file is new
            writer.writeheader()
        writer.writerows(jungler_data_list)

if __name__ == "__main__":
    main()