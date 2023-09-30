import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time
from datetime import datetime, timedelta

# 获取当前日期
current_date = datetime.now()

# 获取周日的日期
sunday = current_date + timedelta((6-current_date.weekday()) % 7)

# 从明天开始到周日为止
dates = []
next_date = current_date + timedelta(days=1)
while next_date <= sunday:
    dates.append(next_date.strftime('%Y-%m-%d'))
    next_date += timedelta(days=1)


# 初始化一个空的DataFrame来存储所有菜单
all_menus = pd.DataFrame()

# 循环遍历每一天的日期
for date in dates:
    url_lunch = f"https://api.dineoncampus.com/v1/location/6123ff86a9f13a2a48c2a8ed/periods/64ed0969351d53075fd0c844?platform=0&date={date}"
    url_dinner = f"https://api.dineoncampus.com/v1/location/6123ff86a9f13a2a48c2a8ed/periods/64ed0969351d53075fd0c83e?platform=0&date={date}"
    
    # 获取午餐和晚餐的菜单
    response_lunch = requests.get(url_lunch).json()
    time.sleep(5)
    response_dinner = requests.get(url_dinner).json()
    time.sleep(5)
    

    
    # 提取并存储菜单
    series_lunch_kitchen = pd.Series([i['name'] for i in response_lunch['menu']['periods']['categories'][0]['items']], name="Lunch_Kitchen")
    series_lunch_flame = pd.Series([i['name'] for i in response_lunch['menu']['periods']['categories'][1]['items']], name="Lunch_Flame")
    series_dinner_kitchen = pd.Series([i['name'] for i in response_dinner['menu']['periods']['categories'][0]['items']], name="Dinner_Kitchen")
    series_dinner_flame = pd.Series([i['name'] for i in response_dinner['menu']['periods']['categories'][1]['items']], name="Dinner_Flame")
    
    df_daily = pd.concat([series_lunch_kitchen, series_lunch_flame, series_dinner_kitchen, series_dinner_flame], axis=1)
    df_daily['Date'] = date  # 添加日期列
    
    all_menus = pd.concat([all_menus,df_daily])

# 将NaN替换为空字符串
all_menus = all_menus.replace(np.nan, '', regex=True)

# 创建 4*2 的子图阵列
fig, axs = plt.subplots(4, 2, figsize=(30, 20))

# 遍历每个日期并在子图上绘制表格
for ax, (date, df_date) in zip(axs.flatten(), all_menus.groupby('Date')):
    table = ax.table(cellText=df_date.drop(columns='Date').values,
                     colLabels=df_date.columns.drop('Date'),
                     cellLoc='center', loc='center')
    ax.axis('off')
    table.scale(1, 1.5)
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.auto_set_column_width(col=list(range(len(df_date.columns) - 1)))
    
    # 加粗第一行字体
    for (i, j), cell in table.get_celld().items():
        if i == 0:
            cell.set_fontsize(10)
            cell.set_text_props(weight='bold')
    
    date_obj = datetime.strptime(date, '%Y-%m-%d')

    # 获取星期几的缩写
    weekday_abbr = date_obj.strftime('%a')

    # 将星期几的缩写添加到日期字符串中
    date_with_weekday = f"{date} ({weekday_abbr})"
    
    ax.set_title(f"Menu for {date_with_weekday}", fontsize=16, fontweight="bold", pad=20)

axs[3,1].axis('off')
# 在底部中央加一行文本
fig.text(0.7, 0.2, "Perch Main Menu, by Fengyang Han", ha='center', va='center', fontsize=12, fontweight='bold')

# 调整子图间的间距
plt.subplots_adjust(hspace=0.2, wspace=0.1)
plt.savefig("images/Menu-"+ datetime.now().strftime('%Y-%m-%d') +".jpg")
plt.show()
