import os
import json
import requests
import sqlite3
from datetime import datetime

print(f'>>> {os.path.abspath("football_matches.db")} <<<')


# Function to add the correct suffix to the day
def add_suffix(day):
    if 11 <= day <= 13:
        return "th"
    return {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")


def get_fixtures(league_name):
    conn = sqlite3.connect('/Users/jason/PycharmProjects/soccer/templates/football_matches.db')
    cursor = conn.cursor()

    print(f"League is {league_name}")

    matchday = 1

    if league_name == "PL":
        matchday = 24
    elif league_name == "ELC":
        matchday = 24

    match_fixtures = f'https://api.football-data.org/v4/competitions/{league_name}/matches?matchday={matchday}'
    headers = {'X-Auth-Token': '611a49203eca499a90945814f14d0d8f'}

    fixtures_response = requests.get(match_fixtures, headers=headers)
    teams = []
    fixtures = []

    for match in fixtures_response.json()["matches"]:
        home_team = str(match['homeTeam']['name']).upper()
        away_team = str(match['awayTeam']['name']).upper()
        match_date = str(match['utcDate'])
        # Convert to datetime object
        dt = datetime.strptime(match_date, "%Y-%m-%dT%H:%M:%SZ")
        # Get the day with suffix
        day_with_suffix = f"{dt.day}{add_suffix(dt.day)}"
        # Format the datetime object
        match_date = dt.strftime(f"%I:%M %p - {day_with_suffix} of %B %Y")
        print(f"{home_team} versus {away_team} on {match_date}")
        fixtures.append(f"{home_team},{away_team},{match_date}")
        # Insert sample data (you can add more teams/matches here)
        # Insert match into the database
        cursor.execute('''
            INSERT OR IGNORE INTO matches (league, home_team, away_team, match_date) VALUES (?, ?, ?, ?)
        ''', (league_name, home_team, away_team, match_date))

    conn.commit()
    conn.close()


leagues = ('PL', 'ELC')
for league in leagues:
    get_fixtures(league)