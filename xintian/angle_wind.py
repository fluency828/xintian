import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.pyplot import MultipleLocator
import statsmodels.api as sm
import os
plt.rc('font',family = 'YouYuan')
plt.rcParams['axes.unicode_minus'] = False
import matplotlib.dates as mdate

def plot_angle_wind(dataframe,wtg=None,wtg_point_name = '风机',angle_point_name = '平均桨叶角度1a',\
                wind_speed_point_name = '平均风速',color_map='tab20',\
                time_point_name = '时间',\
                point_size=50,edgecolor='face',point_alpha=0.9,color='y',\
                labelsize = 15,titlesize=28,style='default',grid=False,path=None,title=None,\
                legend_cols = 1,legend_loc='best',sharpness=500
            ):
    '''
    画出传入风机数据的桨叶角度-风速散点图，不同风机用不同颜色标识。

    Parameters
    ----------
    - dataframe: 原始数据，一般为包含多个风机,需要包含下面参数中的测点名从
    - wtg: 如为单台风机号，则从dataframe里筛选出该风机的数据，并只画出这台风机的桨叶角度-风速图。如为'all'或'所有风机'则画出数据中所有风机的散点图，不同风机用不同颜色标识。
    - wtg_point_name: 风机号测点名称，默认为'风机'
    - angle_point_name: 桨叶角度测点名称，默认为'平均桨叶角度1a'
    - wind_speed_point_name: 风速测点名称
    - time_point_name:时间测点名称
    - color_map: sns.color_palette参数，如 tab20,rainbow
    - color: 当只画出单个风机的散点图时散点图的颜色
    - style: 图片风格，如 default,seaborn,ggplot
    - titlesize: 标题大小
    - labelsize: x，y轴标签大小
    - edgecolor: 散点边缘颜色
    - point_size: 散点大小 如50
    - point_alph：散点透明度 0-1
    - grid: 是否要网格
    - path: 保存图片的路径
    - title: 图片标题
    - legend_cols：图例的列数（如果有40个风机需要2-4列才能乘下）
    - legend_loc: 图例的位置 如 lower right, lower left, upper right, upper left, lower center,...,best
    - sharpness： 图片清晰度

    return:
    ----------
    None
    '''
    point_max = np.max(dataframe[angle_point_name])
    point_min = np.min(dataframe[angle_point_name])
    # print(wtg_list)
    #### 画图
    # plt.style.use('fivethirtyeight')
    plt.style.use(style)
    plt.rc('font',family = 'YouYuan')
    plt.rcParams['axes.unicode_minus'] = False
    _, ax = plt.subplots(figsize=(15,8))
    if grid:
        plt.grid(True,which='both',ls='dashed')
    # 定义颜色列表

    # 单个风机绘制折线图
    if wtg!='all' and wtg!='所有风机':
        assert(wtg in np.unique(dataframe[wtg_point_name]))
        wtg_data =  dataframe[dataframe[wtg_point_name ]==wtg].sort_values(by = time_point_name).reset_index(drop=True)
        y =wtg_data[angle_point_name]
        x =wtg_data[wind_speed_point_name]
        # print(wtg,len(y))
        # 绘制散点图，并设置颜色
        ax.scatter(x, y, label=wtg, color=color,\
                edgecolors=edgecolor,s=point_size,alpha=point_alpha)
        y_major_locator = MultipleLocator(max((point_max-point_min)//20,1))
        ax.set_ylabel(angle_point_name,fontdict = {'fontsize':labelsize,'fontweight':'bold'})
        ax.set_xlabel(wind_speed_point_name,fontdict = {'fontsize':labelsize,'fontweight':'bold'})
        ax.set_title(title,fontdict = {'fontsize':titlesize,'fontweight':'bold'})
    #所有风机
    elif wtg =='all' or wtg == '所有风机':
        wtg_list = np.unique(dataframe[wtg_point_name])
        colors = sns.color_palette(color_map,len(wtg_list))
        for i,wtg in enumerate(wtg_list):
           # 获取当前风机的数据
            print(i,wtg)
            wtg_data =  dataframe[dataframe[wtg_point_name]==wtg].sort_values(by =time_point_name).reset_index(drop=True)
            y =wtg_data[angle_point_name]
            x =wtg_data[wind_speed_point_name]
            ax.scatter(x, y, label=wtg, color=colors[i],\
                    edgecolors=edgecolor,s=point_size,alpha=point_alpha)
            
        y_major_locator = MultipleLocator(max((point_max-point_min)//20,1))
        ax.yaxis.set_major_locator(y_major_locator)

        # 设置横轴和纵轴标签
        # ax.set_xlabel('time')
        ax.set_ylabel(angle_point_name,fontdict = {'fontsize':labelsize,'fontweight':'bold'})
        ax.set_xlabel(wind_speed_point_name,fontdict = {'fontsize':labelsize,'fontweight':'bold'})
        ax.set_title(title,fontdict = {'fontsize':titlesize,'fontweight':'bold'})

    # 添加图例
    ax.legend(ncol=legend_cols,loc=legend_loc)

    # 显示图形
    # plt.show()
    plt.savefig(path,bbox_inches='tight',dpi=sharpness)



def plot_angle_power(dataframe,wtg=None,wtg_point_name = '风机',y_point_name = '平均桨叶角度1a',\
                x_point_name = '平均风速',color_map='tab20',\
                time_point_name = '时间',\
                point_size=50,edgecolor='face',point_alpha=0.9,color='y',\
                labelsize = 15,titlesize=28,style='default',grid=False,path=None,title=None,\
                legend_cols = 1,legend_loc='best',sharpness=500,comparison=True,x_margin=0.5,\
                save_figure=True
            ):
    '''
    画出传入风机数据的桨叶角度-风速散点图，不同风机用不同颜色标识。

    Parameters
    ----------
    - dataframe: 原始数据，一般为包含多个风机,需要包含下面参数中的测点名从
    - wtg: 如为单台风机号，则从dataframe里筛选出该风机的数据，并只画出这台风机的桨叶角度-风速图。如为'all'或'所有风机'则画出数据中所有风机的散点图，不同风机用不同颜色标识。
    - wtg_point_name: 风机号测点名称，默认为'风机'
    - y_point_name: 桨叶角度测点名称，默认为'平均桨叶角度1a'
    - x_point_name: 风速测点名称
    - time_point_name:时间测点名称
    - color_map: sns.color_palette参数，如 tab20,rainbow
    - color: 当只画出单个风机的散点图时散点图的颜色
    - style: 图片风格，如 default,seaborn,ggplot
    - titlesize: 标题大小
    - labelsize: x，y轴标签大小
    - edgecolor: 散点边缘颜色
    - point_size: 散点大小 如50
    - point_alph：散点透明度 0-1
    - grid: 是否要网格
    - path: 保存图片的路径
    - title: 图片标题
    - legend_cols：图例的列数（如果有40个风机需要2-4列才能乘下）
    - legend_loc: 图例的位置 如 lower right, lower left, upper right, upper left, lower center,...,best
    - sharpness： 图片清晰度

    return:
    ----------
    None
    '''
    y_point_max = np.max(dataframe[y_point_name])
    y_point_min = np.min(dataframe[y_point_name])
    x_point_max = np.max(dataframe[x_point_name])
    x_point_min = np.min(dataframe[x_point_name])
    # print(wtg_list)
    #### 画图
    # plt.style.use('fivethirtyeight')
    if style is not None:
        plt.style.use(style)
    figure, ax = plt.subplots(figsize=(15,8))
    if grid:
        plt.grid(True,which='both',ls='dashed')
    # 定义颜色列表

    # 单个风机绘制折线图
    if wtg!='all' and wtg!='所有风机':
        assert(wtg in np.unique(dataframe[wtg_point_name]))
        wtg_data =  dataframe[dataframe[wtg_point_name]==wtg].sort_values(by = time_point_name).reset_index(drop=True)
        y =wtg_data[y_point_name]
        x =wtg_data[x_point_name]
        # print(wtg,len(y))
        # 绘制散点图，并设置颜色
        if comparison:
            ax.scatter(dataframe[x_point_name],dataframe[y_point_name],\
                    label='其余同型号风机',color='#CDC9C9',edgecolors=edgecolor,s=point_size,alpha=1)
        ax.scatter(x, y, label=wtg, color=color,\
                edgecolors=edgecolor,s=point_size,alpha=point_alpha)
        y_major_locator = MultipleLocator(max((y_point_max-y_point_min)//20,1))
        # x_major_locator = MultipleLocator(max((x_point_max-x_point_min)//20,1))
        ax.set_ylabel(y_point_name,fontdict = {'fontsize':labelsize,'fontweight':'bold'})
        ax.set_xlabel(x_point_name,fontdict = {'fontsize':labelsize,'fontweight':'bold'})
        ax.set_title(title,fontdict = {'fontsize':titlesize,'fontweight':'bold'})
    #所有风机
    elif wtg =='all' or wtg == '所有风机':
        wtg_list = np.unique(dataframe[wtg_point_name])
        colors = sns.color_palette(color_map,len(wtg_list))
        for i,wtg in enumerate(wtg_list):
           # 获取当前风机的数据
            print(i,wtg)
            wtg_data =  dataframe[dataframe[wtg_point_name]==wtg].sort_values(by =time_point_name).reset_index(drop=True)
            y =wtg_data[y_point_name]
            x =wtg_data[x_point_name]
            ax.scatter(x, y, label=wtg, color=colors[i],\
                    edgecolors=edgecolor,s=point_size,alpha=point_alpha)

        y_major_locator = MultipleLocator(max((y_point_max-y_point_min)//20,1))
        # x_major_locator = MultipleLocator(max((x_point_max-x_point_min)//20,1))
        # ax.xaxis.set_major_locator(x_major_locator)

        # 设置横轴和纵轴标签
        # ax.set_xlabel('time')
        ax.set_ylabel(y_point_name,fontdict = {'fontsize':labelsize,'fontweight':'bold'})
        ax.set_xlabel(x_point_name,fontdict = {'fontsize':labelsize,'fontweight':'bold'})
        ax.set_title(title,fontdict = {'fontsize':titlesize,'fontweight':'bold'})

    if x_point_name==time_point_name:
        x_major_locator = mdate.DayLocator(interval=5)
    else:
        x_major_locator = MultipleLocator(max((x_point_max-x_point_min)/50,x_margin))
    # print(x_point_max,x_point_min)
    # print(max((x_point_max-x_point_min)//20,1))
    ax.yaxis.set_major_locator(y_major_locator)
    ax.xaxis.set_major_locator(x_major_locator)
    # 添加图例
    ax.legend(ncol=legend_cols,loc=legend_loc)
    # 显示图形
    # plt.show()
    if save_figure:
        plt.savefig(path,bbox_inches='tight',dpi=sharpness)
    plt.close()
    return figure