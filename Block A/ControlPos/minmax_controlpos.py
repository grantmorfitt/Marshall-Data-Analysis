# -*- coding: utf-8 -*-
"""
Created on Fri Sep 26 15:47:27 2025

@author: esoti
"""

import pandas as pd
import glob
import os

def global_min_max():
    mins=[]
    maxs=[]
    # Find all CSV files in current folder
    csv_files = glob.glob(os.path.join(os.getcwd(), "*.csv"))
    if not csv_files:
        print("No CSV files found.")
        return None, None
    
    for f in csv_files:
        df=pd.read_csv(f)
        local_min = df.min(numeric_only=True)
        local_max = df.max(numeric_only=True)
        mins.append(local_min)
        maxs.append(local_max)
        print("\n=== Min/Max per Column ===")
        print(f)
        for col in local_min.index:
            print(f"{col}: min = {local_min[col]}, max = {local_max[col]}")
        

    # Read and concatenate all CSVs
    df_all = pd.concat((pd.read_csv(f) for f in csv_files), ignore_index=True)

    # Compute column-wise min and max (only numeric columns)
    global_min = df_all.min(numeric_only=True)
    global_max = df_all.max(numeric_only=True)
    
    df_min=pd.DataFrame(mins, columns=["Pitch", "Roll", "Collective","Pedal"])
    df_min.to_csv("minmax/local_mins.csv", index=False)
    
    df_max=pd.DataFrame(maxs, columns=["Pitch", "Roll", "Collective","Pedal"])
    df_max.to_csv("minmax/local_maxs.csv", index=False)

    return global_min, global_max


if __name__ == "__main__":
    gmin, gmax = global_min_max()
    if gmin is not None:
        print("\n=== Global Min/Max per Column ===")
        for col in gmin.index:
            print(f"{col}: min = {gmin[col]}, max = {gmax[col]}")
            
global_min_max()