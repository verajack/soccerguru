import sqlite3
from datetime import datetime
import json
import requests


def create_db():
    conn = sqlite3.connect('football_matches.db')
    cursor = conn.cursor()

    # Create a table for matches
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS matches (
            id INTEGER PRIMARY KEY,
            league TEXT,
            home_team TEXT,
            away_team TEXT,
            match_date TEXT
        )
    ''')

    # Create a table for team stats
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS team_stats (
            team_name TEXT PRIMARY KEY,
            wins INTEGER,
            losses INTEGER,
            draws INTEGER,
            points INTEGER
        )
    ''')
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='matches'")
    table_exists = cursor.fetchone()

    if table_exists:
        print("✅ Table 'matches' exists!")
    else:
        print("❌ Table 'matches' does NOT exist!")
    conn.commit()
    conn.close()


# Function to add the correct suffix to the day
def add_suffix(day):
    if 11 <= day <= 13:
        return "th"
    return {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")


# Function to calculate points from the form
def calculate_points(form):
    points = 0
    for result in form:
        if result == 'W':
            points += 3
        elif result == 'D':
            points += 1
        # Loss (L) contributes 0 points, so we skip it
    return points


def get_stats(league_name):
    conn = sqlite3.connect('football_matches.db')
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


if __name__ == "__main__":
    create_db()
    print("Database created successfully!")
    leagues = ('PL', 'ELC')
    for league in leagues:
        get_stats(league)

