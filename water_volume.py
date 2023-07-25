# -*- coding: utf-8 -*-
"""
Created on Mon Jul 25 13:48:44 2022

@author: Erick Ball

This script plots a visualization of the specific volume of water as a function of pressure and temperature,
illustrating the effect of temperature on phase change, the meaning of the critical point, and the behavior
of the supercritical fluid. Notably on these plots it becomes clear that the critical point is not 
a sharp boundary, it just continues the trend of the phase change having less effect as pressure/temp increases.
The data is a bit choppy so the boundaries are not smooth, but the overall trends are shown well enough.
The first figure shown uses color to indicate density. 
The second figure uses interactive 3D plotting to show the specific volume, so the height of the vertical 
portion at a given point on the saturation line corresponds to the increase in volume due to a phase change.
Note that specific volume is on a log scale to improve visual clarity.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FormatStrFormatter
from mpl_toolkits.mplot3d import Axes3D

from scipy.interpolate import griddata


#filename = "compressed_liquid_and_superheated_steam_V1.3.csv"
fileurl = "http://learncheme.com/wp-content/uploads/2022/04/compressed_liquid_and_superheated_steam_V1.3.csv"
#download the CSV file
import requests
import io
try:
    response = requests.get(fileurl)
    # If the response was successful, no Exception will be raised
    response.raise_for_status()
except HTTPError as http_err:
    print(f'HTTP error occurred: {http_err}') 
except Exception as err:
    print(f'Other error occurred: {err}')  
else:
    print('Success!')

# assuming the data is encoded in UTF-8, if not, replace 'utf-8' with the correct encoding
data = pd.read_csv(io.StringIO(response.text), encoding='utf-8', skiprows=6)


#data = pd.read_csv(filename)
columns = data.columns[0:3]
df = data[columns]
#df = data[["Pressure (MPa)", " Temperature (Â°C)", " Specific Volume (m^3/kg)"]]

#fig = plt.figure()
#ax = fig.gca(projection='3d')

index = df.index
columns = df.columns
#x, y = np.meshgrid(np.arange(len(columns)), np.arange(len(index)))
p = df["Pressure (MPa)"]
t = df[columns[1]] #df[" Temperature (Â°C)"], except there's some kind of encoding issue with typing it in

v = df[" Specific Volume (m^3/kg)"]

x = np.array(sorted(list(set(p))))
y = np.array(sorted(list(set(t))))
X, Y = np.meshgrid(x, y)

from scipy.interpolate import interp1d
t_v_by_p = {pres: interp1d(t[np.where(p==pres)[0]], v[np.where(p==pres)[0]], bounds_error=False, fill_value="extrapolate") for pres in x}

def getv(pres, temp):
  voft = t_v_by_p[pres]
  #print(pres, temp)
  return voft(temp)


grid_p, grid_t = np.mgrid[0.1:0.4:100j, 0:2000:200j]
points = np.vstack((p,t)).transpose()
grid_z1 = griddata(points, v, (grid_p, grid_t), method='linear')

# Choose a random sample of the points and see if that works better
import random
random.seed(0)
indices = random.sample(range(9527), 9527)
#points2 = np.array([points[i] for i in indices])
# Convert pressure to kPa
points2 = np.array([(points[i][0]*1000, points[i][1]) for i in indices])
#points2 = points
v2 = np.array([np.log(v[i]) for i in indices])
#v2 = np.log(v)
grid_p2, grid_t2 = np.mgrid[100:30000:10000j, 0:600:2000j]
grid_z2 = griddata(points2, v2, (grid_p2, grid_t2), method='nearest')

plt.imshow(grid_z2.T, extent=(100,30000,0,600), origin='lower', aspect='auto')
#plt.title('Linear')
plt.xlabel('Pressure (MPa')
plt.ylabel('Temp (°C)')
plt.show()


#z = np.array([[getv(x1,x2) for x1 in x] for x2 in y])

#p, t, v, xticks, yticks = plottable_3d_info(df)

#plt.axes(projection='3d')
axes = plt.figure().gca(projection='3d')
axes.plot_surface(grid_p2, grid_t2, grid_z2)

axes.set_xlabel("Pressure (kPa)")
axes.set_ylabel("Temp (°C)")
axes.set_zlabel("Log of specific volume (m^3/kg)")

plt.show()

