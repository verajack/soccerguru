import sqlite3
from datetime import datetime
import json
import requests
import os
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import make_interp_spline
import glob


def clear_folder(folder_path):
    """Deletes all .jpeg files inside a given folder but keeps the folder itself."""
    files = glob.glob(os.path.join(folder_path, "*.jpeg"))
    for f in files:
        try:
            os.remove(f)
        except Exception as e:
            print(f"Error deleting {f}: {e}")


def plot_team_form(team_name, form_string, form_type):
    """
    Generates a smooth form graph from a given string of results (W, D, L).
    Saves it as a JPEG in 'images/form/'.

    Args:
        team_name (str): The name of the team.
        form_string (str): The results string, e.g., "WWDDLLLWWD".
        form_type (str): The type of form (e.g., "HOME", "AWAY", "OVERALL").
    """

    # Define folder path and ensure it exists
    save_folder = "static/images/form"
    os.makedirs(save_folder, exist_ok=True)

    # Optional: Clear old images before saving the new one
    # clear_folder(save_folder)

    # Convert the form string into numerical values
    y_values = [0]  # Start from 0
    for result in form_string:
        if result == "W":
            y_values.append(y_values[-1] + 1)  # Win increases by 1
        elif result == "L":
            y_values.append(y_values[-1] - 1)  # Loss decreases by 1
        else:  # Draw, stays the same
            y_values.append(y_values[-1])

    x_values = np.array(range(1, len(y_values) + 1))  # Start x-values from 1

    # Create a smooth curve using spline interpolation
    if len(x_values) > 3:  # Only interpolate if enough data points exist
        x_smooth = np.linspace(x_values.min(), x_values.max(), 300)  # More points for smoothness
        spline = make_interp_spline(x_values, y_values, k=3)  # k=3 for cubic spline
        y_smooth = spline(x_smooth)
    else:
        x_smooth, y_smooth = x_values, y_values  # Not enough points, use original

    # Plotting the smooth form
    plt.figure(figsize=(8, 5))
    plt.plot(x_smooth, y_smooth, linestyle="-", color="blue", linewidth=2, label="Form Trend")
    plt.scatter(x_values, y_values, color="red", marker="o", label="Actual Results")  # Mark actual data points

    # Labels and title
    plt.xlabel("Matches Played")
    plt.ylabel("Form Score")
    plt.title(f"{team_name} - {form_type.capitalize()} Form")
    plt.axhline(y=0, color="black", linestyle="--", linewidth=0.8)  # Reference line at 0
    plt.xticks(x_values)  # Ensure x-axis shows 1,2,3...
    plt.legend()

    # Save the image
    filename = f"{team_name} - {form_type.capitalize()} Form.jpeg"
    filepath = os.path.join(save_folder, filename)
    plt.savefig(filepath, format="jpeg", dpi=300)
    plt.close()

    print(f"Graph saved: {filepath}")


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


def get_stats(league_name):
    with sqlite3.connect('/Users/jason/PycharmProjects/soccer/templates/football_matches.db') as conn:
        cursor = conn.cursor()

    print(f"League is {league_name}")
    match_results = f'https://api.football-data.org/v4/competitions/{league_name}/matches?status=FINISHED'
    headers = {'X-Auth-Token': '611a49203eca499a90945814f14d0d8f'}

    results_response = requests.get(match_results, headers=headers)
    current_month_text = datetime.now().strftime('%B')
    current_day = datetime.now().strftime('%d')
    current_year_full = datetime.now().strftime('%Y')

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

    response = requests.get(match_results, headers=headers)
    for match in response.json()['matches']:

        count = count + 1
        home_team = str(match['homeTeam']['name']).upper()
        away_team = str(match['awayTeam']['name']).upper()
        home_score = str(match['score']['fullTime']['home'])
        away_score = str(match['score']['fullTime']['away'])

        cursor.execute('''
                    INSERT OR REPLACE INTO detailed_results (league, home_team, home_score, away_team, away_score) VALUES (?, ?, ?, ? ,?)
                ''', (league_name, home_team, home_score, away_team, away_score))

        results.append(
            f"{match['homeTeam']['name']} {match['score']['fullTime']['home']} : {match['score']['fullTime']['away']} {match['awayTeam']['name']}")

        if (match['score']['fullTime']['home']) > (match['score']['fullTime']['away']):

            if home_team not in form.keys():
                form[home_team] = "W"
                points[home_team] = 3

            else:
                form[home_team] += "W"
                points[home_team] += 3

            if home_team not in home_form.keys():
                home_goals = match['score']['fullTime']['home']
                away_goals = match['score']['fullTime']['away']
                home_form[home_team] = "W"
                home_points[home_team] = 3

            else:
                home_form[home_team] += "W"
                home_points[home_team] += 3

            if away_team not in form.keys():
                form[away_team] = "L"
                points[away_team] = 0
            else:
                form[away_team] += "L"

            if away_team not in away_form.keys():
                away_form[away_team] = "L"
                away_points[away_team] = 0
            else:
                away_form[away_team] += "L"

        elif (match['score']['fullTime']['home']) < (match['score']['fullTime']['away']):

            if home_team not in form.keys():
                form[home_team] = "L"
                points[home_team] = 0
            else:
                form[home_team] += "L"

            if home_team not in home_form.keys():
                home_form[home_team] = "L"
                home_points[home_team] = 0
            else:
                home_form[home_team] += "L"

            if away_team not in form.keys():
                form[away_team] = "W"
                points[away_team] = 3
            else:
                form[away_team] += "W"
                points[away_team] += 3

            if away_team not in away_form.keys():
                away_form[away_team] = "W"
                away_points[away_team] = 3
            else:
                away_form[away_team] += "W"
                away_points[away_team] += 3

        elif (match['score']['fullTime']['home']) == (match['score']['fullTime']['away']):

            if home_team not in form.keys():
                form[home_team] = "D"
                points[home_team] = 1
            else:
                form[home_team] += "D"
                points[home_team] += 1

            if home_team not in home_form.keys():
                home_form[home_team] = "D"
                home_points[home_team] = 1
            else:
                home_form[home_team] += "D"
                home_points[home_team] += 1

            if away_team not in away_form.keys():
                form[away_team] = "D"
                points[away_team] = 1
            else:
                form[away_team] += "D"
                points[away_team] += 1

            if away_team not in away_form.keys():
                away_form[away_team] = "D"
                away_points[away_team] = 1
            else:
                away_form[away_team] += "D"
                away_points[away_team] += 1

        if match['awayTeam']['name'] not in teams:
            teams.append(f"{match['awayTeam']['name']}")
        # home_form[home_team] += ":" + str(points[home_team])

    teams.sort()
    sorted_points = sorted(points.items(), key=lambda x: x[1])
    sorted_form = dict(sorted(form.items(), key=lambda x: calculate_points(x[1]), reverse=True))
    sorted_home_form = dict(sorted(home_form.items(), key=lambda x: calculate_points(x[1]), reverse=True))
    sorted_away_form = dict(sorted(away_form.items(), key=lambda x: calculate_points(x[1]), reverse=True))

    for team in sorted_form.keys():
        cursor.execute('''
                        INSERT OR REPLACE INTO form (league, team, form) VALUES (?, ?, ?)
                    ''', (league, team, sorted_form[team]))

        plot_team_form(team, sorted_form[team], "ALL")

    for team in sorted_home_form.keys():
        cursor.execute('''
                        INSERT OR REPLACE INTO home_form (league, team, form) VALUES (?, ?, ?)
                    ''', (league, team, sorted_home_form[team]))
        plot_team_form(team, sorted_home_form[team], "HOME")

    for team in sorted_away_form.keys():
        cursor.execute('''
                        INSERT OR REPLACE  INTO away_form (league, team, form) VALUES (?, ?, ?)
                    ''', (league, team, sorted_away_form[team]))
        plot_team_form(team, sorted_away_form[team], "AWAY")

    with open(f'stats/teams_{league_name}.txt', 'w') as f:
        for line in teams:
            print(f"Writing {line}")
            cursor.execute('''
                        INSERT OR REPLACE INTO teams (league, team) VALUES (?, ?)
                    ''', (league_name, line))
            f.write(f"{line}\n")

    with open(f'stats/results_{league_name}.txt', 'w') as f:
        for line in results:
            cursor.execute('''
                        INSERT OR REPLACE INTO results (league, result) VALUES (?, ?)
                    ''', (league_name, line))
            f.write(f"{line}\n")

    with open(f'stats/team_form_{league_name}.json', 'w') as fp:
        json.dump(sorted_form, fp, indent=4)

    with open(f'stats/home_form_{league_name}.json', 'w') as fp:
        json.dump(sorted_home_form, fp, indent=4)

    with open(f'stats/away_form_{league_name}.json', 'w') as fp:
        json.dump(sorted_away_form, fp, indent=4)

    with open(f'stats/points_{league_name}.json', 'w') as fp:
        json.dump(sorted_points, fp, indent=4)

    with open(f'stats/home_points_{league_name}.json', 'w') as fp:
        json.dump(home_points, fp, indent=4)

    with open(f'stats/away_points_{league_name}.json', 'w') as fp:
        json.dump(away_points, fp, indent=4)

    with open(f'stats/fixtures_{league_name}.txt', 'w') as f:
        for line in fixtures:
            f.write(f"{line}\n")

    conn.commit()


leagues = ('PL', 'ELC')
for league in leagues:
    get_stats(league)
