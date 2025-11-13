# -*- coding: utf-8 -*-
"""
Created on Thu Nov  6 10:30:58 2025

@author: gmorfitt
"""
import pd
import numpy as np

df = pd.read_csv(r'C:/Users/gmorfitt/Documents/Marshall Data Analysis/Steep Turn Right_1_A-L06_Pilot 1_09.49.13.693.csv')

lon_cyclic = df['LonCyclic(percent)']
lat_cyclic = df['LatCyclic(percent)']

lat_cyclic_rad = ((0.34958+0.34497)/ 100) * lat_cyclic - 0.34497

lat_cyclic_deg = np.rad2deg(lat_cyclic_rad)
#.array((np.array(latcyclic)+0.34497)*100/(0.34958+0.34497))
