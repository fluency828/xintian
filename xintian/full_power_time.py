import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.pyplot import MultipleLocator
import mplcyberpunk
import plotly.express as px




def gen_full_time(dataframe,threshold = 50,full_pw = 4000,Pw_pn='平均电网有功功率',time_pn = 'data_time',full_time_pn = 'full_time'):
    '''
    生成单台风机的满发时间

    Parameters
    -----------
    - dataframe:单台风机的满发数据，需要包含10min维度的功率测点Pw_pn和时间测点data_time
    - threshold:与额定功率相差多少以内算满发，如50，1000
    - full_pw: 额定功率,注意区分不同机型的额定功率不同
    - Pw_pn:功率测点名称 默认平均电网有功功率
    - time_pn:时间测点名称，默认data_time
    
    return:
    -----------
    返回新的dataframe,增加列full_time_pn
    '''
    dataframe['pw_diff'] = full_pw - dataframe[Pw_pn]
    pre_row = None
    for i, row in dataframe.iterrows():
        if i==0:
            pre_row = row
            continue
        elif row['pw_diff']<=threshold:
            # If current power is greater than or equal to rated power,
            # calculate the duration since reaching rated power till now
            sep = ((row[time_pn] - pre_row[time_pn]).total_seconds()) / 60.0 
            if sep > 20:
                pre_row = row
                continue
            duration = pre_row[full_time_pn] + sep          
            # print(pre_row['run_time'],duration)
            dataframe.loc[i,full_time_pn] = duration
            row[full_time_pn] = duration
        pre_row = row
    return dataframe