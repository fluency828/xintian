import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.pyplot import MultipleLocator
import statsmodels.api as sm
import os
# plt.rc('font',family = 'YouYuan')
import sys
sys.path.append('D:/OneDrive - CUHK-Shenzhen/utils/')
from xintian.power_limited import limit_power_delete
import streamlit as st


def plot_scatter(data,r,T,r_square,title,path,x_ticks_n=20,sharpness=500,if_plot_square=True):
    '''
    转矩-转速&转速的平方 散点图,纵轴为转矩,横轴为转速和转速平方,包含图例。
    -- parameter --
    - data: 输入的原始数据（单台风机），列名需要包含 r,T
    - r:转速测点名
    - T:转矩测点名
    - r_square: 转矩的平方测点名
    - title:标题
    - path: 图片存储路径
    - x_ticks_n:x轴间隔，默认为20
    - sharpness: 保存图片的清晰度
    - if_plot_square:是否画出转速的平方，如不画出则图中仅有转矩-转速的散点图
    -- return --
    None
    '''
    _, ax = plt.subplots(figsize=(15,8))
    plt.grid(True,which='both',ls='dashed')
    ax.scatter(data[r],data[T],label=f'{T}-{r}',color='blue')
    if if_plot_square:
        ax.scatter(data[r_square],data[T],label=f'{T}-{r_square}',color='red')
    ax.legend()
    # ax.set_title(f'[{bin-0.25}°,{bin+0.25}°)区间的功率曲线',fontdict={'fontsize':20,'fontweight':'bold'})
    # ax.set_title(f'{wtg_id}功率曲线',fontdict={'fontsize':20,'fontweight':'bold'})
    y_max = max(data[T])
    if if_plot_square:
        x_max = max(data[r_square])
    else:
        x_max=max(data[r])
    # print(x_max)
    y_major_locator = MultipleLocator((y_max)/20)
    x_major_locator = MultipleLocator((x_max)/x_ticks_n)
    # y_major_locator = MultipleLocator(2)
    ax.yaxis.set_major_locator(y_major_locator)
    ax.xaxis.set_major_locator(x_major_locator)
    ax.set_xlabel(r)
    ax.set_ylabel(T)
    ax.set_title(f'{title}',fontdict={'fontsize':20,'fontweight':'bold'})
    plt.savefig(path,bbox_inches='tight',dpi=sharpness)



# @st.cache_resource(ttl=10800)
def rated_speed_torque(dataframe,X_point_name,y_point_name,title,path,limit_pn,x_ticks_n=20,lower=1.2e5,upper=1e6,rated_lines=True,\
                       rated_speed=240,rated_torque=3.9,standardize_times=1e4,legend_loc='best',outlier_thre=None,save_figure=True):
    '''
    检测 detect_data 中的 y 与 X之间的线性关系,查看斜率是否正常，检测转速和转矩是否达到额定值。
    检测方法为使用OLS进行回归拟合斜率。
    
    -- parameter --
    - detect_data: 输入的数据，pd.DataFrame
    - X_point_name: 自变量特征名称，str，需要被包含在detect_data中
    - y_point_name: 因变量特征名称，str，需要被包含在detect_data中
    - limit_pn: 做回归的阈值条件依据测点，如转速评方
    - title: 图片标题
    - path: 图片保存路径
    - lower: 做回归的阈值条件中的lower bound
    - upper: 做回归的阈值条件中的upper bound
    - rated_speed: 额定转速
    - rated_torque: 额定转矩
    -- return --
    返回OLS计算出的斜率。
    '''
    dataframe['ols_flag']= (dataframe[limit_pn]>lower)&(dataframe[limit_pn]<upper) +1-1
    y_max = max(dataframe[y_point_name])
    y_min = min(dataframe[y_point_name])
    x_max = max(dataframe[X_point_name])
    x_min = min(dataframe[X_point_name])
    detect_data = dataframe[dataframe['ols_flag']==1].reset_index(drop=True)
    # print(detect_data)
    # rest_data = dataframe[dataframe['ols_flag']!=1].reset_index(drop=True)
    y_train = detect_data[y_point_name]
    X_train =  detect_data[X_point_name]
    res_ols = sm.OLS(y_train,X_train).fit()
    k1 = res_ols.params[0]
    detect_data['resid']=res_ols.resid
    sigma=np.std(res_ols.resid)
    # print('sigma',sigma)
    # detect_data['weight'] = w
    fig, ax = plt.subplots(figsize=(15,8))
    plt.grid(True,which='both',ls='dashed')
    ax.scatter(dataframe[X_point_name],dataframe[y_point_name],label='转矩-转速平方',color='blue')
    # ax.plot(detect_data[X_point_name],k2*detect_data[X_point_name],color='red')
    if outlier_thre is not None:
        threshold = 3*sigma if outlier_thre=='sigma' else outlier_thre
        outlier_label = (abs(detect_data['resid']) >threshold) +1 -1
        detect_data['outlier'] = outlier_label
        outlier_data =  detect_data[detect_data['outlier']==1].reset_index(drop=True)
        ax.scatter(outlier_data[X_point_name],outlier_data[y_point_name],label=f'异常值(残差>{round(threshold,2)})',color='#FFA500')
    ax.plot(detect_data[X_point_name],k1*detect_data[X_point_name],label='最小二乘拟合回归线',color='lightgreen',linewidth=3)
    if rated_lines:
        ax.vlines(x=rated_speed**2/standardize_times,ymin=y_min,ymax=y_max,color='red',linestyles='dotted',label=f'额定转速={rated_speed}',linewidth=5)
        rated_torque_display = int(rated_torque*9549.5) if y_point_name not in ('变流器转矩反馈','实际扭矩') else rated_torque
        ax.hlines(y=rated_torque,xmin = x_min,xmax=x_max,color='red',linestyles='dotted',label=f'额定转矩={rated_torque_display}',linewidth=5)
    ax.legend(loc=legend_loc)
    # ax.set_title(f'[{bin-0.25}°,{bin+0.25}°)区间的功率曲线',fontdict={'fontsize':20,'fontweight':'bold'})
    # ax.set_title(f'{wtg_id}功率曲线',fontdict={'fontsize':20,'fontweight':'bold'})
    y_sep = (y_max)/20
    y_major_locator = MultipleLocator(y_sep)
    x_sep = x_max/x_ticks_n
    x_major_locator = MultipleLocator(x_sep)
    ax.set_xlim(min(x_min-x_sep,0),max(x_max+x_sep,rated_speed**2/standardize_times+x_sep))
    ax.set_ylim(min(y_min-y_sep,0),max(y_max+y_sep,rated_torque+y_sep))
    # y_major_locator = MultipleLocator(2)
    ax.yaxis.set_major_locator(y_major_locator)
    
    ax.xaxis.set_major_locator(x_major_locator)
    ax.set_xlabel(X_point_name)
    ax.set_ylabel(y_point_name)
    ax.set_title(f'{title},k={round(k1,4)}',fontdict={'fontsize':20,'fontweight':'bold'})
    # print(detect_data.groupby('outlier').mean('weight'))
    if save_figure:
        plt.savefig(path,bbox_inches='tight',facecolor='white',dpi=500)
    plt.close()
    return k1,fig
