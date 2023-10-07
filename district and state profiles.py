# -*- coding: utf-8 -*-
"""
Created on Mon Aug 28 10:44:01 2023

@author: Sattva Vasavada
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter
import numpy as np
import geopandas as gpd
import seaborn as sns
import matplotlib.style as style 

from functools import reduce

#%%

#define function to convert list to string
def listToString(s):
 
    str1 = ""
 
    for ele in s:
        str1 = str1 + " " + ele
 
    # return string
    return str1.strip()


#%% Read block shapefiles

os.chdir("D:/Users/savas/Documents/Ashoka/Economics/NITI Aayog/Aspirational Blocks Program/Block Analysis/data/Block GIS Files")
blockmap = gpd.read_file("Block_boundary.shp")
blockmap.columns = blockmap.columns.str.lower() #column names to lowercase.

#%% General Code for creating maps at district level 

def distmaps_var(pathtodata, filename, sheetname, filesuffix,
                 lgdcodecolname, distcodecolname, varname, positive_negative, graphtitle, 
                 savename, saveplotspath):
    os.chdir(pathtodata)
    
    df = pd.read_excel(filename, sheet_name = sheetname)
    
    df.rename(columns = {lgdcodecolname: 'blockcode_' + filesuffix, 
                         distcodecolname: 'distcode_' + filesuffix, 
                         varname: varname.lower()}, inplace = True)
    
    df['aspirational_block'] = 1
         
    merged = pd.merge(df, blockmap, left_on = ['blockcode_' + filesuffix], 
                      right_on = ['block_lgd'], how = 'outer')
    
    merged = gpd.GeoDataFrame(merged)
    
    os.chdir(saveplotspath)
    
    loopnames = merged[merged.aspirational_block == 1].drop_duplicates(subset = ['district', 'state'])

    for district, state in zip(loopnames.district, loopnames.state):
        
        if str(district) == 'nan' or str(state) == 'nan':
            continue 
                
        distavg = np.round(np.mean(merged[(merged.district == district) & 
                         (merged.state == state)][varname]), 1)
        stateavg = np.round(np.mean(merged[(merged.state == state)][varname]), 1)
        
        if positive_negative == "positive":
            cmap_color = "RdYlGn"
        elif positive_negative == "negative":
            cmap_color = "RdYlGn_r"
        
        ax = merged[(merged.state == state) &
               (merged.district == district)].plot(column = varname, 
                    cmap = cmap_color, legend = True, missing_kwds = dict(color = "lightgrey"),
                    vmin = 0, vmax = 100)
                                                   
        merged[(merged.state == state) &
               (merged.district == district)].plot(ax = ax, facecolor='none', edgecolor='black', linewidth = 1, alpha = 1)
                                                 
        for blockname, geometry in zip(merged[(merged.state== state) &
                                                 (merged.district == district) &
                                                 (merged.aspirational_block == 1)]['block_name'], 
                                         merged[(merged.state== state) & 
                                                 (merged.district == district) & 
                                                 (merged.aspirational_block == 1)]['geometry']):
            
            if str(blockname) == 'nan':
                continue
            
            ax.text(geometry.centroid.x, geometry.centroid.y, str(blockname.title()), fontsize = 5, 
                    bbox={"facecolor":"orange", "alpha":0.5, "pad":0.5})
            
        plt.axis('off')
        plt.title('State: ' + state.title() + ", \n District: " + district.title() + ",\n" + graphtitle)
        plt.figtext(0.5, 0.05, state.title() + ' AB avg: ' + str(stateavg) + "\n" + district.title() + ' AB avg:' + str(distavg),
                    ha="center",
                    fontsize=12, bbox={"facecolor":"orange", "alpha":0.5, "pad":5})
        
        state = state.strip()
        district = district.strip()
        plt.savefig(state.title() + "_" + district.title() + "_" + savename + ".png", dpi = 300,
                    bbox_inches='tight')
        plt.close()
        print(district, state)              
     
#%% JJM

distmaps_var("D:/Users/savas/Documents/Ashoka/Economics/NITI Aayog/Aspirational Blocks Program/Block Analysis/data/Latest Data Files",
             'ABP Data_JJM.xlsx', 
             'Aspitational_Block_data',
             'jjm', 
             'LGDBlockCode', 
             'LGDDistrictCode',
             '% of households with tap connection',
             'positive', 
             '% HH with Tap Water Connection: JJM',
             'percentHH_tapwater_JJM', 
             'D:/Users/savas/Documents/Ashoka/Economics/NITI Aayog/Aspirational Blocks Program/Block Analysis/output files/State and District Profiles/JJM')

#%% PMK

distmaps_var("D:/Users/savas/Documents/Ashoka/Economics/NITI Aayog/Aspirational Blocks Program/Block Analysis/data/Latest Data Files",
             'ABP Data_Agri.xlsx', 
             'LGD CODES',
             'agri', 
             'BLOCK LGD', 
             'DISTRICT LGD',
             '%',
             'positive', 
             '% PM-KISAN Coverage',
             'percent_PMK', 
             'D:/Users/savas/Documents/Ashoka/Economics/NITI Aayog/Aspirational Blocks Program/Block Analysis/output files/State and District Profiles/PMK')
