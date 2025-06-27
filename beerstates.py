#!/usr/bin/env python3

import sys
import json
import os
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
try:
    import cartopy.crs as ccrs
    import cartopy.io.shapereader as shpreader
except ImportError:
    print("Error: cartopy is required but not installed.")
    print("Install it with: pip install cartopy")
    sys.exit(1)


COLORS = {
    'not_had': '#ff4444',
    'had': '#44aa44',
    'border': 'black'
}

MAP_CONFIG = {
    'projection': ccrs.LambertConformal(),
    'extent': [-125, -66.5, 20, 50],
    'title': 'Beer Consumption Progress by State',
    'figsize': (12, 8)
}

DATA_FILE = 'states_data.json'

def load_states_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                data = json.load(f)
                return data['states'], data['not_had']
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error reading {DATA_FILE}: {e}")
            print("Using default data...")
    
    states = [
        "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DC", "DE", "FL", "GA",
        "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
        "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
        "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
        "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"
    ]
    not_had = ["AL", "AK", "KS", "MS", "NE", "SD"]
    return states, not_had


def save_states_data(states, not_had):
    data = {
        'states': states,
        'not_had': not_had
    }
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"Data saved to {DATA_FILE}")
    except Exception as e:
        print(f"Error saving data: {e}")


def validate_states(states, not_had):
    invalid_states = [state for state in not_had if state not in states]
    if invalid_states:
        print(f"Warning: Invalid states in not_had list: {invalid_states}")
        return False
    return True


def create_map():
    try:
        fig = plt.figure(figsize=MAP_CONFIG['figsize'])
        ax = fig.add_axes([0, 0, 1, 1], projection=MAP_CONFIG['projection'])
        ax.set_extent(MAP_CONFIG['extent'], ccrs.Geodetic())
        ax.set_title(MAP_CONFIG['title'], fontsize=16, pad=20)
        
        return fig, ax
    except Exception as e:
        print(f"Error creating map: {e}")
        sys.exit(1)


def load_geographic_data():
    try:
        shapename = 'admin_1_states_provinces_lakes_shp'
        states_shp = shpreader.natural_earth(
            resolution='110m',
            category='cultural', 
            name=shapename
        )
        return states_shp
    except Exception as e:
        print(f"Error loading geographic data: {e}")
        sys.exit(1)


def plot_states(ax, states_shp, not_had):
    for state in shpreader.Reader(states_shp).records():
        state_code = state.attributes.get('postal')
        
        if state_code in not_had:
            facecolor = COLORS['not_had']
        else:
            facecolor = COLORS['had']
        
        ax.add_geometries(
            [state.geometry], 
            ccrs.PlateCarree(),
            facecolor=facecolor, 
            edgecolor=COLORS['border'],
            linewidth=0.5
        )


def add_legend(ax, states, not_had):
    legend_elements = [
        Patch(facecolor=COLORS['had'], label=f'Had Beer ({len(states) - len(not_had)} states)'),
        Patch(facecolor=COLORS['not_had'], label=f'Not Had ({len(not_had)} states)')
    ]
    ax.legend(handles=legend_elements, loc='lower left', bbox_to_anchor=(0.02, 0.02))


def add_statistics(ax, states, not_had):
    total_states = len(states)
    completed = total_states - len(not_had)
    percentage = (completed / total_states) * 100
    
    stats_text = f"Progress: {completed}/{total_states} states ({percentage:.1f}%)"
    ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, 
            fontsize=12, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))


def mark_state_completed(state_code):
    states, not_had = load_states_data()
    if state_code in not_had:
        not_had.remove(state_code)
        save_states_data(states, not_had)
        print(f"Marked {state_code} as completed!")
    else:
        print(f"{state_code} was already marked as completed.")


def main():
    states, not_had = load_states_data()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == '--complete' and len(sys.argv) > 2:
            mark_state_completed(sys.argv[2].upper())
            return
        elif sys.argv[1] == '--help':
            print("Usage:")
            print("  python beerstates.py              # Show map")
            print("  python beerstates.py --complete STATE  # Mark state as completed")
            print("  python beerstates.py --help       # Show this help")
            return
    
    if not validate_states(states, not_had):
        sys.exit(1)
    
    fig, ax = create_map()
    states_shp = load_geographic_data()
    
    plot_states(ax, states_shp, not_had)
    add_legend(ax, states, not_had)
    add_statistics(ax, states, not_had)
    
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
