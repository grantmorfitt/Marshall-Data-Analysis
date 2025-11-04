# -*- coding: utf-8 -*-
"""
Created on Tue Oct 26 13:37:09 2025

@author: gmorfitt
"""


import pandas as pd
import numpy as np
import plotly.io as pio
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import random
import math

pio.renderers.default='browser'


def read_csv(filename):
    """Reads data from a specified CSV file and prints each row."""

    print(f"--- Reading '{filename}' ---")
    try:
        df_csv = pd.read_csv(filename)
    
        print("--- DataFrame imported from CSV ---")
        print(df_csv.head())
        return df_csv
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        
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

def convert_data(col) -> pd.series:
    """
    Parameters
    ----------
    col : series
        series to convert with control data

    Returns
    -------
    converted series

    """
    cyclic_x = 160 #distance from fulcrum to approximate location on cyclic
    
    name = col.name
    try: 
        if name == "Pitch" or name == "Roll":
            y0 = voltage_to_distance(col[1]) #246mm

            col = col.apply(voltage_to_distance)
            
            col = col.apply(lambda y: math.tan((y-y0)/cyclic_x) )

            col = col.apply(math.degrees)
            print(f"Max: {col.max()}")
            
            return col
        else:
        
            return col
    
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if "__main__":
    
    path = r'ControlPos_2025-10-13_15-40-21_P02 Block C.csv'
    data = read_csv(path)
    
    fig = make_subplots(rows=4, cols=1, shared_xaxes=True,)
    

    '''
    y_savgol = sp.savgol_filter(data["Pitch"], 50, 5)
    sav_signal = go.Scatter(x=data["Pitch"].index,name = "savitzky-golay filter", y=y_savgol, line = dict(color='green'))
    fig.add_trace(sav_signal, row = 1,col = 1)
    
    y_movavg = data["Pitch"].rolling(window=3).mean()
    avg_signal = go.Scatter(x=data["Pitch"].index,name = "moving average filter", y=y_movavg, line = dict(color='orange'))
    fig.add_trace(avg_signal,row = 2, col = 1)
    fig.add_trace(org_signal, row = 2, col = 1)
    '''
    
    for i,v in enumerate(data.columns, start = 0):

        if v == 'Time':
            continue;
        
        #random colors for lines
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)
        
        converted_col = convert_data(data[v])
        min_y = converted_col.min()
        max_y = converted_col.max()
        
        
        signal = go.Scatter(x=data["Time"].index,y=converted_col,name = str(v), line = dict(color=f'rgba({r},{g},{b},1)'))
        
        fig.add_trace(signal, row = i,col = 1)
        fig.add_hline(y=min_y, line_dash="dash", line_color="red", annotation_text=f"Min: {min_y}",row = i,col = 1)
        fig.add_hline(y=max_y, line_dash="dash", line_color="green", annotation_text=f"Max: {max_y}",row = i,col = 1)
        
        #Plot Limits of control inputs
        if v == "Pitch":
            fig.add_hline(y=-15, line_dash="dash", line_color="gray", annotation_text="-15\(\degree \)",row = i,col = 1)
            fig.add_hline(y=15, line_dash="dash", line_color="gray", annotation_text="+15\(\degree \)",row = i,col = 1)

        if v == "Roll":
            fig.add_hline(y=-15, line_dash="dash", line_color="gray", annotation_text="-15\(\degree \)",row = i,col = 1)
            fig.add_hline(y=15, line_dash="dash", line_color="gray", annotation_text="+15\(\degree \)",row = i,col = 1)
        if v == "Collective":
            fig.add_hline(y=0, line_dash="dash", line_color="gray", annotation_text="0\(\degree \)",row = i,col = 1)
            fig.add_hline(y=30, line_dash="dash", line_color="gray", annotation_text="+30\(\degree \)",row = i,col = 1)
        if v == "Pedal":
            fig.add_hline(y=-20, line_dash="dash", line_color="gray", annotation_text="-20\(\degree \)",row = i,col = 1)
            fig.add_hline(y=15, line_dash="dash", line_color="gray", annotation_text="+15\(\degree \)",row = i,col = 1)
    
        
    
    fig.update_layout(title_text=f"{path}")
    fig.update_xaxes(title_text = "Sample(n)")
    fig.update_yaxes(title_text = "Degrees")
    fig.show()
    
    
    
    
