import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time
from datetime import datetime, timedelta
import pytz

eastern = pytz.timezone('US/Eastern')
current_date = datetime.now(eastern)

# Sunday Date
sunday = current_date + timedelta((6-current_date.weekday()) % 7)

# Tomorrow Till Sunday
dates = []
next_date = current_date + timedelta(days=1)
while next_date <= sunday:
    dates.append(next_date.strftime('%Y-%m-%d'))
    next_date += timedelta(days=1)

# Initialize Empty DataFrame
all_menus = pd.DataFrame()

# Date Iteration
for date in dates:
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    url_lunch = f"https://api.dineoncampus.com/v1/location/6123ff86a9f13a2a48c2a8ed/periods/64ed0969351d53075fd0c844?platform=0&date={date}"
    url_dinner = f"https://api.dineoncampus.com/v1/location/6123ff86a9f13a2a48c2a8ed/periods/64ed0969351d53075fd0c83e?platform=0&date={date}"
    
    # Lunch and Dinner Menu
    response_lunch = requests.get(url_lunch,headers=headers).json()
    time.sleep(120)

    
    # Grep Menu and Save Data
    series_lunch_kitchen = pd.Series([i['name'] for i in response_lunch['menu']['periods']['categories'][0]['items']], name="Lunch_Kitchen")
    series_lunch_flame = pd.Series([i['name'] for i in response_lunch['menu']['periods']['categories'][1]['items']], name="Lunch_Flame")

    print(f"{date} lunch obtained")

    response_dinner = requests.get(url_dinner,headers=headers).json()
    time.sleep(120)
    series_dinner_kitchen = pd.Series([i['name'] for i in response_dinner['menu']['periods']['categories'][0]['items']], name="Dinner_Kitchen")
    series_dinner_flame = pd.Series([i['name'] for i in response_dinner['menu']['periods']['categories'][1]['items']], name="Dinner_Flame")

    print(f"{date} dinner obtained")
    
    df_daily = pd.concat([series_lunch_kitchen, series_lunch_flame, series_dinner_kitchen, series_dinner_flame], axis=1)
    df_daily['Date'] = date  # Add Date
    
    all_menus = pd.concat([all_menus,df_daily])


# Replace Nan to empty
all_menus = all_menus.replace(np.nan, '', regex=True)

# Create empty subplots
fig, axs = plt.subplots(4, 2, figsize=(30, 20))

# Iterate Dates and Plot on Subplot
for ax, (date, df_date) in zip(axs.flatten(), all_menus.groupby('Date')):
    table = ax.table(cellText=df_date.drop(columns='Date').values,
                     colLabels=df_date.columns.drop('Date'),
                     cellLoc='center', loc='center')
    ax.axis('off')
    table.scale(1, 1.5)
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.auto_set_column_width(col=list(range(len(df_date.columns) - 1)))
    
    # Bold First Row
    for (i, j), cell in table.get_celld().items():
        if i == 0:
            cell.set_fontsize(10)
            cell.set_text_props(weight='bold')
    
    date_obj = datetime.strptime(date, '%Y-%m-%d')

    # Abbreviation for the Day and Add to Date String
    weekday_abbr = date_obj.strftime('%a')
    date_with_weekday = f"{date} ({weekday_abbr})"
    
    ax.set_title(f"Menu for {date_with_weekday}", fontsize=16, fontweight="bold", pad=20)

axs[3,1].axis('off')

# Illustration
fig.text(0.7, 0.2, "Perch Main Menu, by Fengyang Han", ha='center', va='center', fontsize=12, fontweight='bold')

# Width and Heights Between Subplots
plt.subplots_adjust(hspace=0.2, wspace=0.1)
plt.savefig("images/Menu-"+ datetime.now(eastern).strftime('%Y-%m-%d') +".jpg")
plt.show()
