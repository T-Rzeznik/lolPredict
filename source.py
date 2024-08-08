import requests, csv, os

api_key = os.getenv('RIOT_GAMES_API_KEY')
if api_key is None:
    raise ValueError("No API key found. Please set the API_KEY environment variable.")

SUMMONER_NAMES = ['']  #Up to 8 summoners   NAME#TAG
REGION = 'AMERICAS'  

def get_summoner_data(game_name, tag_line):
    url = f'https://{REGION}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}'
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
    
    import json 
    with open('lol.json', 'w') as f:
        json.dump(timeline_data, f, indent=4)

   
    with open('match.json', 'w') as f:
        json.dump(match_data, f, indent=4)


    # Extract game type or queue ID
    game_type = match_data['info']['gameType']  
    queue_id = match_data['info']['queueId']  

    #Map queue ID to human-readable match type
    queue_mapping = {
        420: 'Ranked Solo/Duo',
        440: 'Ranked Flex',
        400: 'Normal Draft',
        430: 'Normal Blind',
    }
    match_type = queue_mapping.get(queue_id, 'Other')  # Default to 'Other' if the queue ID is not in the mapping
 
    jungle_data = []

    for participant in match_data['info']['participants']:
        if participant['teamPosition'] == 'JUNGLE':
            participant_id = participant['participantId']

            kills_total_first_4_min = 0
            assists_first_4_min=0
            jungler_monsters_killed=0
            gold_earned_first_4_min=0
            kills_details = []
            assist_details = []
            items = []


            for frame in timeline_data['info']['frames']: #first 4 minute features
                for event in frame['events']:
                    if event['timestamp'] <= 240000:
                        if event.get('type') == 'CHAMPION_KILL':
                            if event.get('killerId') == participant_id:
                                kills_total_first_4_min += 1
                                kills_details.append(event['timestamp']) 

                            if participant_id in event.get('assistingParticipantIds', []):
                                assists_first_4_min += 1 
                                assist_details.append(event['timestamp'])

                        if event.get('type') == 'ITEM_PURCHASED' and event['participantId'] == participant_id:  items.append(event['itemId'])

                        jungler_monsters_killed = max(frame['participantFrames'][str(participant_id)].get('jungleMinionsKilled', 0), jungler_monsters_killed)                                        
                        gold_earned_first_4_min = max(frame['participantFrames'][str(participant_id)].get('totalGold', 0), gold_earned_first_4_min)
            gold_per_minute = gold_earned_first_4_min / 4
                                                      
            summoner_spells = participant['summoner1Id'], participant['summoner2Id']
            champion = participant['championName']
            
            first_item = items[0] if items else 'No Item'
            
            level_at_first_blood = participant['champLevel'] if participant['firstBloodKill'] else 'No'

            firstBlood = participant['firstBloodKill']
            jungle_data.append({
                'kills_first_4_min': kills_total_first_4_min,
                'assists_first_4_min': assists_first_4_min,
                'camps_cleared_first_4_min': jungler_monsters_killed,
                'gold_earned_first_4_min': gold_earned_first_4_min,
                'win': participant['win'],
                'kills_details': kills_details,  
                'summoner_spells': summoner_spells,  
                'champion': champion,  
                'first_item': first_item,
                'level_at_first_blood': level_at_first_blood,
                'firstBlood': firstBlood,
                'gold_per_minute': gold_per_minute,
                'game_type': match_type
            })
    return jungle_data

def main():
    jungler_data_list = []
    
    for summoner_name in SUMMONER_NAMES:  # Loop through each summoner name
        game_name, tag_line = summoner_name.split('#', 1)  # Split only on the first occurrence of '#'
        summoner_data = get_summoner_data(game_name, tag_line)  # Update to use new endpoint
        puuid_data = get_puuid(summoner_data['puuid'])  # Get PUUID using new endpoint
        match_history = get_match_history(puuid_data['puuid'])  # Use the retrieved PUUID
        
        for match_id in match_history:
            jungler_data = extract_jungler_data(match_id)
            if jungler_data:
                jungler_data_list.extend(jungler_data)
    
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