# -*- coding: utf-8 -*-
"""
Created on Wed Nov 12 08:52:53 2025

@author: gmorfitt
"""

# import_all_csvs.py
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.io as pio
from plotly.subplots import make_subplots
import plotly.graph_objects as go
#pio.renderers.default='browser'

import re
import datetime
import random
import math

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
        
def voltage_to_distance(volts):
    """
    

    Parameters
    ----------
    volts : FLOAT
        voltage from DI-2008

    Returns
    -------
    x : FLOAT
        converted voltage from string pot to distance in mm

    """
    
    x = 1270 * (volts/15)
    
    return x

def convert_data(col):
    """
    Parameters
    ----------
    col : series
        series to convert with control data

    Returns
    -------
    converted series

    """
    cyclic_x = (183+60) #distance from fulcrum to approximate location on cyclic
    name = col.name
    #try: 
    
    if name == "Pitch" or name == "Roll":
        if len(col) > 1: #in some rare instances there is only one index, and iloc[1] will return an error
            y0 = voltage_to_distance(col.iloc[1]) 
        else:
            y0 = voltage_to_distance(col)
        col = col.apply(voltage_to_distance)
        
        col = col.apply(lambda y: math.tan((y-y0)/cyclic_x) )

        col = col.apply(math.degrees)
       # print(f"Max: {col.max()}")
        
        return col
    else:
    
        return col
    
    #except Exception as e:
      #  print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    
    stateFilePath = r"C:\Users\gmorfitt\Documents\Marshall Data Analysis\Block A\States"
    stateFile_dfs = import_csvs(stateFilePath)
    manuFilePath = r"C:\Users\gmorfitt\Documents\Marshall Data Analysis\Block A\ManeuverLog"
    manuFile_dfs = import_csvs(manuFilePath)
    controlFilePath = r"C:\Users\gmorfitt\Documents\Marshall Data Analysis\Block A\ControlPos"
    controlPos_dfs = import_csvs(controlFilePath)
    
    """
    STATE FILE VARS
    FOG TIME SAMPLE - 200Hz
    CONTROL - 50 hz
    """

    
    linked_data = link_flight_data_by_pilot(
    manuFile_dfs,
    stateFile_dfs,
    controlPos_dfs,
    return_combined=True
    )
    
    for pilot_id, pilot_data in linked_data.items():
        #if pilot_id == "pilot 3":
        print(f"\n- {str.upper(pilot_id)} -")
        #if pilot_id == "pilot 9": #I'm doing these one at a time
        
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
        vs.name = "Vertical speed down (ft/min)"
        alt = (df_state['Height (m)'] * 3.281)
        alt.name = "Height (ft)"
        
        print("Converting timestamps")
        FOG_timestamp = df_state['Human Timestamp'].apply(extract_time) #gets
        print("Timestamps converted")
        heading = df_state['Heading (degrees)'] 
        latitudes = df_state['Latitude (degrees)']
        longitudes = df_state['Longitude (degrees)']
        roll_state = df_state['Roll (degrees)']
        v_e = df_state['Velocity East (m/s)']
        v_n = df_state['Velocity North (m/s)']
        speed = np.sqrt( np.pow(v_e, 2) + np.pow(v_n,2) )
        
        control_timestamp = df_control["Time"].str.split('.').str[0]
        pitch = convert_data(df_control["Pitch"])
        roll = convert_data(df_control["Roll"])
        collective = df_control["Collective"]
        pedal = df_control["Pedal"]
        
   
         
        newTable = get_active_maneuvers(df_maneuver) #get manuevers to plot on graphs
        
        df_control = df_control.apply(convert_data) #Convert data before slicing based on manuevers
        
        for i,v in newTable.iterrows():
            if i <= len(newTable):
                currentTime = v["Time"]
                startorstop = v["Active_Maneuver"].split("_")[0]
                currentManeuver = v["Active_Maneuver"].split("_")[1]
                
               
                if str.lower(startorstop) == 'start':
                    #print(f"Found start for {currentManeuver}")
                    dfcontrol_times = df_control['Time'].str.slice(0,8) #timestamp is different in this col so need to convert it
                    
                    currentTime = currentTime.zfill(8) #adds leading zeros if not long enough
                    startManueverIndex = dfcontrol_times[dfcontrol_times == currentTime].index[0]  #grab manuever start time
                    
                    
                    nextrow = newTable.iloc[i+1]
                    nextTime = nextrow["Time"]
                    nextTime = nextTime.zfill(8) #fill the leading zero for times < 12
                    nextstartorstop = nextrow["Active_Maneuver"].split("_")[0]
                    nextManeuver = nextrow["Active_Maneuver"].split("_")[1]
                    
                    if nextManeuver == currentManeuver:
                        nextManeuverIndex = dfcontrol_times[dfcontrol_times == nextTime].index[0]
                        #print(f"Found stop for {currentManeuver}")
                        controlSegmentSection = df_control.loc[startManueverIndex:nextManeuverIndex]
                        
                        filePath = r"C:\Users\gmorfitt\Documents\Marshall Data Analysis\Reports"
                        fileName = f"BlockA_{pilot_id}_{currentManeuver}_controlpos.csv"
                        
                        
                        controlSegmentSection.to_csv(os.path.join(filePath,fileName), index = False)
                        
                        
                        
                    #if str.lower(start_stop) == 'stop':
                        
                
                
                
                
            
            # dataToPlot = [vs, alt, heading, pitch, roll, roll_state, collective, pedal]
             
            # fig = make_subplots(rows=len(dataToPlot),
            # cols=1, 
            # shared_xaxes=True)
            
            # for i, v in enumerate(dataToPlot, start = 1):
            #     print(f"Plotting {v.name}")
            #     if v.name == "Pitch" or v.name == "Roll" or v.name == "Collective" or v.name == "Pedal":
            #          color = random_rgb()
            #          signal = go.Scatter(x=control_timestamp,y=v,name = str(v.name), line = dict(color='red'))
            #          fig.add_trace(signal, row = i,col = 1)
                     
                         
            #     else:
            #          color = random_rgb()
            #          signal = go.Scatter(x=FOG_timestamp,y=v,name = str(v.name), line = dict(color='blue'))
            #          fig.add_trace(signal, row = i,col = 1)
                     
            #     for currentTime, currentMan in zip(newTable["Time"], newTable["Active_Maneuver"]):
            #         fig.add_vline(x=currentTime, line_dash="dash", line_color="gray", row=i, col=1)
            #         fig.add_annotation(
            #             x=currentTime,
            #             y=0,
            #             text=currentMan,
            #             row=i,
            #             col=1
            #         )
            # fig.update_layout(height = 1500)
            # print(f"Generating {pilot_id} report")
            # filepath = r"C:\Users\gmorfitt\Documents\Marshall Data Analysis\Reports"
            # filename = os.path.join(filepath, f'{pilot_id.replace(" ", "_")}_report.html')
            # fig.write_html(filename, auto_open=False)
        
    
           

