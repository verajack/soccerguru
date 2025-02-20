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
    save_folder = "images/form"
    os.makedirs(save_folder, exist_ok=True)

    # Optional: Clear old images before saving the new one
    clear_folder(save_folder)

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


# Example function call
plot_team_form("Sheffield United", "WWWDDLLLWWDLLL", "HOME")
