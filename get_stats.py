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

    # Extract the results and build form and results outputs

    for match in results_response.json()["matches"]:
        home_team = str(match['homeTeam']['name']).upper()
        away_team = str(match['awayTeam']['name']).upper()
        match_date = str(match['utcDate'])
        print(f"{home_team} versus {away_team} on {match_date}")

        print(match)
    headers = {'X-Auth-Token': '611a49203eca499a90945814f14d0d8f'}
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

    response = requests.get(match_results, headers=headers)
    for match in response.json()['matches']:

        count = count + 1
        home_team = str(match['homeTeam']['name']).upper()
        away_team = str(match['awayTeam']['name']).upper()

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
        readable_date = dt.strftime(f"%I:%M %p - {day_with_suffix} of %B %Y")
        print(f"{home_team} versus {away_team} on {readable_date}")
        fixtures.append(f"{home_team} versus {away_team} on {readable_date}")

    with open(f'stats/teams_{league_name}.txt', 'w') as f:
        for line in teams:
            f.write(f"{line}\n")

    with open(f'stats/results_{league_name}.txt', 'w') as f:
        for line in results:
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


leagues = ('PL', 'ELC')
for league in leagues:
    get_stats(league)
