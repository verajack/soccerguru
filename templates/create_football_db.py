import sqlite3

def get_stats(league_name):

    print(f"League is {league_name}")
    from datetime import datetime
    import json
    import requests

    matchday=1

    match_results = f'https://api.football-data.org/v4/competitions/{league_name}/matches?status=FINISHED'

    if league_name == "PL":
        matchday = 24
    elif league_name == "ELC":
        matchday = 24

    match_fixtures = f'https://api.football-data.org/v4/competitions/{league_name}/matches?matchday={matchday}'
    headers = {'X-Auth-Token': '611a49203eca499a90945814f14d0d8f'}

    results_response = requests.get(match_results, headers=headers)
    fixtures_response = requests.get(match_fixtures, headers=headers)

    count = 0
    results = []
    teams = []
    home_form = {}
    away_form = {}
    home_points = {}
    away_points = {}
    points = {}
    form = {}
    fixtures = []

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



    fixtures_response = requests.get(match_fixtures, headers=headers)

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
        cursor.executemany('''
            INSERT OR REPLACE INTO matches (home_team, away_team, match_date) VALUES (?, ?, ?)
        ''', [
            ({home_team}, {away_team}, {match_date}),
        ])

def create_db():
    conn = sqlite3.connect('football_matches.db')
    cursor = conn.cursor()

    # Create a table for matches
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS matches (
            id INTEGER PRIMARY KEY,
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



    cursor.executemany('''
        INSERT OR REPLACE INTO team_stats (team_name, wins, losses, draws, points) VALUES (?, ?, ?, ?, ?)
    ''', [
        ("STOKE CITY FC", 8, 6, 4, 28),
        ("SUNDERLAND AFC", 10, 5, 3, 33),
        ("SWANSEA CITY AFC", 7, 7, 4, 25),
        ("LUTON TOWN FC", 6, 8, 4, 22),
        ("WATFORD FC", 9, 5, 4, 31),
        ("CARDIFF CITY FC", 7, 6, 5, 26),
        ("DERBY COUNTY FC", 8, 7, 3, 27),
        ("LEEDS UNITED FC", 11, 4, 3, 36),
        ("MIDDLESBROUGH FC", 10, 6, 2, 32),
        ("BURNLEY FC", 12, 3, 3, 39),
    ])

    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_db()
    print("Database created successfully!")