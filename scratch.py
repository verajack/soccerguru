import requests
import json

# uri = 'https://api.football-data.org/v4/matches'
uri = 'https://api.football-data.org/v4/competitions/PL/matches?matchday=24'
headers = {'X-Auth-Token': '611a49203eca499a90945814f14d0d8f'}

response = requests.get(uri, headers=headers)

for match in response.json()["matches"]:
    home_team = str(match['homeTeam']['name']).upper()
    away_team = str(match['awayTeam']['name']).upper()
    match_date= str(match['utcDate'])
    print(f"{home_team} versus {away_team} on {match_date}")

    print(match)

