#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd

from rossmo_et_ridgway import Rossmo, RossmoPlot


# In[2]:


body_locations_path = '../resources/Ridgway/body_locations.csv'
ridgway_locations_path = '../resources/Ridgway/ridgway_locations.csv'
disappearances_path = '../resources/Ridgway/disappearances.csv'

df_victims = pd.read_csv(body_locations_path)
df_ridgway = pd.read_csv(ridgway_locations_path)
df_disappearances = pd.read_csv(disappearances_path)


# In[3]:


R = Rossmo.from_dataframe([df_victims, df_disappearances])


# In[4]:


P = RossmoPlot(R, [df_victims, df_ridgway, df_disappearances], aliases=['body locations', 'ridgway', 'disappearances'])


# In[17]:


P.create_plot()


# In[18]:


P.show_plot()

