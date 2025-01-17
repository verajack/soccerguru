def get_stats(league_name):
    print(f"League is {league_name}")
    from datetime import datetime
    import json
    import requests


    uri = f'https://api.football-data.org/v4/competitions/{league_name}/matches?status=FINISHED'
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

    response = requests.get(uri, headers=headers)
    for match in response.json()['matches']:

        count = count + 1
        home_team = str(match['homeTeam']['name']).upper()
        away_team = str(match['awayTeam']['name']).upper()

        results.append(
            f"{match['homeTeam']['name']} {match['score']['fullTime']['home']} : {match['score']['fullTime']['away']} {match['awayTeam']['name']}")

        if (match['score']['fullTime']['home']) > (match['score']['fullTime']['away']):

            if home_team not in home_form.keys():
                home_goals = match['score']['fullTime']['home']
                away_goals = match['score']['fullTime']['away']
                home_form[home_team] = "W"
                form[home_team] = "W"
                home_points[home_team] = 3
                points[home_team] = 3

            else:
                home_form[home_team] += "W"
                form[home_team] += "W"
                home_points[home_team] += 3
                points[home_team] += 3

            if away_team not in away_form.keys():
                away_form[away_team] = "L"
                form[away_team] = "L"
                away_points[away_team] = 0
                points[away_team] = 0
            else:
                away_form[away_team] += "L"
                form[away_team] += "L"

        elif (match['score']['fullTime']['home']) < (match['score']['fullTime']['away']):

            if home_team not in home_form.keys():
                home_form[home_team] = "L"
                form[home_team] = "L"
                home_points[home_team] = 0
                points[home_team] = 0
            else:
                home_form[home_team] += "L"
                form[home_team] += "L"

            if away_team not in away_form.keys():
                away_form[away_team] = "W"
                form[away_team] = "W"
                away_points[away_team] = 3
                points[away_team] = 3
            else:
                away_form[away_team] += "W"
                form[away_team] += "W"
                away_points[away_team] += 3
                points[away_team] += 3

        elif (match['score']['fullTime']['home']) == (match['score']['fullTime']['away']):

            if home_team not in home_form.keys():
                home_form[home_team] = "D"
                form[home_team] = "D"
                home_points[home_team] = 1
                points[home_team] = 1
            else:
                home_form[home_team] += "D"
                form[home_team] += "D"
                home_points[home_team] += 1
                points[home_team] += 1

            if away_team not in away_form.keys():
                away_form[away_team] = "D"
                form[away_team] = "D"
                away_points[away_team] = 1
                points[away_team] = 1
            else:
                away_form[away_team] += "D"
                form[away_team] += "D"
                away_points[away_team] += 1
                points[away_team] += 1

        if match['awayTeam']['name'] not in teams:
            teams.append(f"{match['awayTeam']['name']}")


    teams.sort()
    sorted_points = sorted(points.items(), key=lambda x: x[1])

    with open(f'stats/teams_{league_name}.txt', 'w') as f:
        for line in teams:
            f.write(f"{line}\n")

    with open(f'stats/results_{league_name}.txt', 'w') as f:
        for line in results:
            f.write(f"{line}\n")

    with open(f'stats/team_form_{league_name}.json', 'w') as fp:
        json.dump(form, fp, indent=4)

    with open(f'stats/home_form_{league_name}.json', 'w') as fp:
        json.dump(home_form, fp, indent=4)

    with open(f'stats/away_form_{league_name}.json', 'w') as fp:
        json.dump(away_form, fp, indent=4)

    with open(f'stats/points_{league_name}.json', 'w') as fp:
        json.dump(sorted_points, fp, indent=4)

    with open(f'stats/home_points_{league_name}.json', 'w') as fp:
        json.dump(home_points, fp, indent=4)

    with open(f'stats/away_points_{league_name}.json', 'w') as fp:
        json.dump(away_points, fp, indent=4)


leagues = ('PL', 'ELC')
for league in leagues:
    get_stats(league)

