# import_all_csvs.py
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.io as pio
from plotly.subplots import make_subplots
import plotly.graph_objects as go
pio.renderers.default='browser'
import re
import datetime
import random

def import_csvs(folder_path):

    csv_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]
    if not csv_files:
        print("No CSV files found in the folder.")
        return {}

    dataframes = {}
    for file in csv_files:
        full_path = os.path.join(folder_path, file)
        try:
            df = pd.read_csv(full_path)
            key_name = os.path.splitext(file)[0]  # remove .csv extension
            dataframes[key_name] = df
            print(f"Loaded: {file} ({len(df)} rows, {len(df.columns)} columns)")
        except Exception as e:
            print(f"Error loading {file}: {e}")

    return dataframes


def get_active_maneuvers(df, column="Maneuver/Comments"):
    """
    Returns only maneuver rows (START/STOP) with Time and Active_Maneuver columns.
    Example: START_Straight Level, STOP_Normal Climb
    """
    # Clean up text
    df[column] = df[column].str.strip().str.strip('"')

    # Keep only maneuver rows
    df = df[df[column].str.startswith("MANEUVER_")].copy()

    # Extract type and maneuver name
    df["Active_Maneuver"] = df[column].str.extract(r"MANEUVER_(START|STOP)_(.*)")[0] + "_" + df[column].str.extract(r"MANEUVER_(START|STOP)_(.*)")[1]

    # Keep only needed columns
    return df[["Time", "Active_Maneuver"]].reset_index(drop=True)


def extract_time(series):
    if isinstance(series, str):
    # Single string: slice characters 11-19
        return series[11:19]
    else:
        # Series or list-like: use vectorized slice
        series = pd.Series(series)
        return series.str.slice(11, 19)

def extract_pilot_id(filename):
    """
    Extracts and normalizes pilot identifier from filename, e.g. 'Pilot 5', 'Pilot_05', etc.
    """
    match = re.search(r'pilot[_\s-]*(\d+)|pilot\s*instructor', filename, re.IGNORECASE)
    if match:
        # handle both numbered pilots and "Instructor"
        if match.group(1):
            return f"pilot {int(match.group(1))}"
        else:
            return "pilot instructor"
    return ""

def link_flight_data_by_pilot(maneuver_dfs, state_dfs, control_dfs, return_combined=False):
    """
    Links maneuver, state, and control DataFrames by pilot ID (based on filename content).
    
    Returns a dict of matched DataFrames per pilot if return_combined=True.
    """
    
    # Build lookups using pilot ID from filenames
    state_by_pilot = {extract_pilot_id(fname): df for fname, df in state_dfs.items()}
    control_by_pilot = {extract_pilot_id(fname): df for fname, df in control_dfs.items()}

    combined_data = {} if return_combined else None

    for manu_fname, manu_df in maneuver_dfs.items():
        pilot_id = extract_pilot_id(manu_fname)

        state_df = state_by_pilot.get(pilot_id)
        control_df = control_by_pilot.get(pilot_id)

        print(f"\nPilot: {pilot_id}")
        print(f"  Maneuver file: {manu_fname}")

        if state_df is not None:
            print(f"State file found")
        else:
            print("No matching state file found")

        if control_df is not None:
            print(f"Control file found")
        else:
            print("No matching control file found")

        if return_combined:
            combined_data[pilot_id] = {
                "maneuver": manu_df,
                "state": state_df,
                "control": control_df
            }

    return combined_data

def random_rgb():
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    return f'rgb({r},{g},{b})'

if __name__ == "__main__":
    stateFilePath = r"C:\Users\gmorfitt\Documents\Marshall Data Analysis\Block A\States"  # <-- change this path
    stateFile_dfs = import_csvs(stateFilePath)
    manuFilePath = r"C:\Users\gmorfitt\Documents\Marshall Data Analysis\Block A\ManeuverLog"
    manuFile_dfs = import_csvs(manuFilePath)
    controlFilePath = r"C:\Users\gmorfitt\Documents\Marshall Data Analysis\Block A\ControlPos"
    controlPos_dfs = import_csvs(controlFilePath)
    
    """
    STATE FILE VARS
    FOG TIME SAMPLE - 200Hz
    CONTROL - 50 hz
    'Human Timestamp', 'Unix Time', 'Microseconds', 'System Failure',
           'Accelerometer Failure', 'Gyroscope Failure', 'Magnetometer Failure',
           'Pressure Failure', 'GNSS Failure', 'Accelerometer Overrange',
           'Gyroscope Overrange', 'Magnetometer Overrange', 'Pressure Overrange',
           'Minimum Temperature', 'Maximum Temperature', 'Low Voltage',
           'High Voltage', 'GNSS Antenna Disconnected', 'Data Overflow',
           'Orientation Ready', 'Navigation Ready', 'Heading Ready', 'Time Ready',
           'GNSS Fix Type', 'Event 1 Flag', 'Event 2 Flag',
           'Internal GNSS Enabled', 'Dual Antenna Heading Active',
           'Velocity Heading Enabled', 'Atmospheric Altitude Enabled',
           'External Position Active', 'External Velocity Active',
           'External Heading Active', 'Latitude (degrees)', 'Longitude (degrees)',
           'Height (m)', 'Velocity North (m/s)', 'Velocity East (m/s)',
           'Velocity Down (m/s)', 'Acceleration X (m/s/s)',
           'Acceleration Y (m/s/s)', 'Acceleration Z (m/s/s)', 'G Force (g)',
           'Roll (degrees)', 'Pitch (degrees)', 'Heading (degrees)',
           'Angular Velocity X (degrees/s)', 'Angular Velocity Y (degrees/s)',
           'Angular Velocity Z (degrees/s)', 'Latitude Error (m)',
           'Longitude Error (m)', 'Height Error (m)'
   """

    
    linked_data = link_flight_data_by_pilot(
    manuFile_dfs,
    stateFile_dfs,
    controlPos_dfs,
    return_combined=True
    )
    for pilot_id, pilot_data in linked_data.items():
        print(f"\n- {str.upper(pilot_id)} -")
        if pilot_id == "pilot 3":
             # Access each DataFrame
             df_maneuver = pilot_data.get("maneuver")
             df_state = pilot_data.get("state")
             df_control = pilot_data.get("control")
             
             
             if df_maneuver is None:
                 print("No maneuver data")
             else:
                 print(f"Maneuver DataFrame shape: {df_maneuver.shape}")
             
             if df_state is None:
                 print("No state data")
             else:
                 print(f"State DataFrame shape: {df_state.shape}")
             
             if df_control is None:
                 print("No control data")
             else:
                 print(f"Control DataFrame shape: {df_control.shape}")
             
             
             
            #GPS Data
             vs = -1 * (df_state['Velocity Down (m/s)'] * 196.85)
             alt = df_state['Height (m)'] * 3.281
             FOG_timestamp = df_state['Human Timestamp'].apply(extract_time)
             heading = df_state['Heading (degrees)'] 
             latitudes = df_state['Latitude (degrees)']
             longitudes = df_state['Longitude (degrees)']
             
             control_timestamp = df_control["Time"].str.split('.').str[0]
             pitch = df_control["Pitch"]
             roll = df_control["Roll"]
             collective = df_control["Collective"]
             pedal = df_control["Pedal"]
             

             dataToPlot = [vs, alt, heading, pitch, roll, collective, pedal]
             
             fig = make_subplots(rows=len(dataToPlot),
             cols=1, 
             shared_xaxes=True)
             
             for i, v in enumerate(dataToPlot, start = 1):
                 #Controls data
                 print(i)
                 
                 if v.name == "Pitch" or v.name == "Roll" or v.name == "Collective" or v.name == "Pedal":
                     color = random_rgb()
                     signal = go.Scatter(x=control_timestamp,y=v,name = str(v.name), line = dict(color=f'{color}'))
                     fig.add_trace(signal, row = i,col = 1)
                 else:
                     color = random_rgb()
                     signal = go.Scatter(x=FOG_timestamp,y=v,name = str(v.name), line = dict(color=f'{color}'))
                     fig.add_trace(signal, row = i,col = 1)
        
             fig.show()
             
             """
             plot mans
             newTable = get_active_maneuvers(df_maneuver)
             for i,v in newTable.iterrows():
                 currentTime = newTable["Time"][i]
                 currentMan = newTable['Active_Maneuver'][i]
                 fig.add_vline(x=currentTime , line_dash="dash", line_color="green", row = 2,col = 1)
                 fig.add_annotation(
                     x=currentTime,
                     y=-10,
                     xref='x2',  # <-- explicitly link to x-axis of row=2
                     yref='y2',  # <-- explicitly link to y-axis of row=2
                     text=currentMan,
                     showarrow=False,
                     arrowhead=2,
                     arrowsize=1,
                     arrowwidth=2,
                     arrowcolor="red"
                 )
             """
             break
    
    
   
    
   
    
           

