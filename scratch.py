# Variable to define how many recent results to consider
form_history = 5
# Sample dictionary
teams_form = {
    "TeamA": "WDLWWDL",
    "TeamB": "WDWLLWD",
    "TeamC": "LLLLDDD",
    "TeamD": "WWWWWLW"
}

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


# Function to process and sort the dictionary
def process_teams(teams_form, form_history):
    # Slice the form to only include the last `form_history` results
    processed_teams = {
        team: form[-form_history:] for team, form in teams_form.items()
    }

    # Sort the dictionary by points based on the sliced form
    sorted_teams = dict(sorted(
        processed_teams.items(),
        key=lambda x: calculate_points(x[1]),
        reverse=True
    ))

    return sorted_teams


# Sort the dictionary based on the calculated points
sorted_teams = dict(sorted(teams_form.items(), key=lambda x: calculate_points(x[1]), reverse=True))


# Display the sorted dictionary
print(sorted_teams)