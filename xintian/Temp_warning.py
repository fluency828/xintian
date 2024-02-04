import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.pyplot import MultipleLocator
# import mplcyberpunk
import sys
import plotly.express as px
import matplotlib.dates as mdate
from matplotlib import rcParams

def plot_scene(full_pw_df,point_name,color_map,ylabel,xlabel,style='default',\
            titlesize=28,labelsize=15,edgecolor='white',glow=False,point_size=50,\
            all_color =None ,point_alpha=1,grid=False,\
            wtg_pn='风机',time_pn='data_time',path=None,title=None,legend_cols = 1,\
            legend_loc = 'lower right',sharpness=200,hlines=[None,None,None,None],\
            annotation_name=['异常值','告警值','故障值','温升异常值'],notation=True,\
            save_fig=True):
    '''
    画出传入风机数据的指定测点的散点图，不同风机用不同颜色标识。
    Parameters
    ----------
    - full_pw_df: 原始数据，一般为筛选满发后的数据
    - point_name: 需要画图的测点名称如 齿轮箱后轴承温度
    - color_map: sns.color_palette参数，如 tab20,rainbow
    - ylabel: y轴标签名
    - xlabel: x轴标签名
    - style: 图片风格，如 default,seaborn,ggplot
    - titlesize: 标题大小
    - labelsize: x，y轴标签大小
    - edgecolor: 散点边缘颜色
    - glow: 当style选赛博朋克时可以使边缘发光
    - point_size: 散点大小 如50
    - all_color: 如果非空则所有风机都用该颜色画图
    - point_alph：散点透明度 0-1
    - grid: 是否要网格
    - time_pn:时间 point name, `str`
    - wtg_pn: 风机号 point name,`str`
    - path: 保存图片的路径
    - title: 图片标题
    - legend_cols：图例的列数（如果有40个风机需要2-4列才能乘下）
    - legend_loc: 图例的位置 如 lower right, lower left, upper right, upper left, lower center,...,best
    - sharpness： 图片清晰度

    return:
    ----------
    返回图片中所用数据 pd.DataFrame
    返回图片对象：matplotlib fig
    '''
    raw_data = full_pw_df[[wtg_pn,time_pn]+[point_name]]
    y_max = full_pw_df[point_name].max()
    y_min = full_pw_df[point_name].min()
    # print(point_name,y_max,y_min,full_pw_df[point_name])
    y_axis_min = min(y_min-5,0)
    # print(raw_data)
    use_data = raw_data.pivot(index = time_pn,columns = wtg_pn)
    wtg_list = np.unique(full_pw_df[wtg_pn])
    #### 画图
    if style is not None:
        plt.style.use(style)
    fig, ax = plt.subplots(figsize=(15,8))
    if grid:
        plt.grid(True,which='both',ls='dashed')
    # plt.rc('font',family = 'YouYuan')
    colors = sns.color_palette(color_map,len(wtg_list))
    # 逐个风机绘制折线图
    all_y = []
    max_x = 0
    for i,wtg in enumerate(wtg_list):
        # 获取当前风机的轴承温度数据
        column_name = wtg
        y = use_data[point_name][column_name].dropna()
        x = np.arange(len(y))
        max_x = max(len(y),max_x)
        # print(wtg,len(y))
        # 绘制折线图，并设置颜色
        if all_color:
            ax.scatter(x, y, color=all_color,edgecolors=edgecolor,s=point_size,alpha=point_alpha)
        else:
            ax.scatter(x, y, label=column_name, color=colors[i],edgecolors=edgecolor,s=point_size,alpha=point_alpha)
        # ax.plot(x, y, label=column_name)
        all_y.append(y.reset_index(drop=True))
    # 设置图形y轴的最大值（如果存在故障值，则最大值为故障值）
    if hlines[-2] is not None:
        max_y = max(y_max,hlines[-2])
    else:
        max_y = y_max
    ax.set_ylim(y_axis_min,(max_y+5)) #最大、最小值前后延长5
    y_sep = (y_max-y_axis_min+5)//20
    y_major_locator = MultipleLocator(y_sep) #设置坐标轴间隔
    ax.yaxis.set_major_locator(y_major_locator)
    # 画出告警值和故障值横线（如果有）
    for i,thre in enumerate(hlines[:-1]):
        if i==0:
            continue
        if thre is not None:
            ax.hlines(y=thre,xmax=max_x,xmin=0,color='#B22222',linestyles='dotted',alpha=0.8)
            ax.text(x=0,y=thre,s=f'{annotation_name[i]}={thre}℃',color='#B22222',ha = 'left',va='bottom')
    if '温升' in point_name:
        abnormal = hlines[-1]
    else:
        abnormal = hlines[0]
    if notation: #是否自动标注图片情况
        print(f'自动标注,数据最大值为：{y_max}，异常阈值：{abnormal}')
        if (abnormal is not None) & (y_max>abnormal):
            print('有异常数据')
            abnormal_data = raw_data[raw_data[point_name]>abnormal].reset_index(drop=True)
            data_max = abnormal_data.groupby(wtg_pn).max()[point_name].sort_values().reset_index()
            text_list = []
            for i,info in data_max.iterrows():
                
                if i%2==0:
                    text_list.append(f'\n{info[0]}风机最高达到{round(info[1],2)}℃')
                else:
                    text_list.append(f'{info[0]}风机最高达到{round(info[1],2)}℃')
                text_verbose = ','.join(text_list)
            abnormal_wtg = ','.join(list(np.unique(abnormal_data[wtg_pn])))
            scene_name = title.split('\n')[0]
            text = f'{abnormal_wtg}风机{scene_name}超过{abnormal}℃；{text_verbose}。'
            # 创建文本框，将文本置于文本框内
            bbox = { "alpha": 0.5,'facecolor':'white','pad':0.5,'edgecolor':'#DCDCDC','boxstyle':'round'}
            # 所有文本使用统一的样式
            # style = {"size": 15, "color": "#CD2626", "bbox": bbox,'fontweight':'bold'}
            style = {"size": 15, "color": '#B22222', "bbox": bbox,'fontweight':'bold'}
            ax.text(x=0,y=y_axis_min+y_sep,s=text,ha = 'left',va='bottom',**style)
        else:
            scene_name = title.split('(')[0]
            text = f'整场风机{scene_name}分布在{round(y_min,2)}到{round(y_max,2)}℃。'
            bbox = { "alpha": 0.5,'facecolor':'white','pad':0.5,'edgecolor':'#DCDCDC','boxstyle':'round'}
            # 所有文本使用统一的样式
            style = {"size": 15, "color":'#4682B4', "bbox": bbox,'fontweight':'bold'}
            ax.text(x=0,y=y_axis_min+y_sep,s=text,ha = 'left',va='bottom',**style)
    # 设置横轴和纵轴标签
    ax.set_xlabel(xlabel,fontdict = {'fontsize':labelsize,'fontweight':'bold'})
    ax.set_ylabel(ylabel,fontdict = {'fontsize':labelsize,'fontweight':'bold'})
    if title:
        ax.set_title(title,fontdict={'fontsize':titlesize,'fontweight':'bold'})

    # 添加图例，设置图例列数和位置
    if all_color is None:
        ax.legend(ncol=legend_cols,loc=legend_loc)

    # 显示图形
    # plt.show()
    if save_fig:
        plt.savefig(path,bbox_inches='tight',facecolor='white',dpi=sharpness)
    plt.close()
    # plot_data = pd.DataFrame(all_y).T
    return fig


def plotly_scene(full_pw_df,point_name,ylabel,xlabel,title,\
            # full_pw_pn ='full_time',\
            wtg_pn='风机',time_pn='data_time',mg=10,w=1000,h=600,):
    '''
    可互动plotly库的动态网页散点图
    画出传入风机数据的指定测点的散点图，不同风机用不同颜色标识。

    Parameters
    ----------
    - full_pw_df: 原始数据，一般为筛选满发后的数据
    - point_name: 需要画图的测点名称如 齿轮箱后轴承温度
    - ylabel: y轴标签名
    - xlabel: x轴标签名
    - title: 图片标题
    - time_pn:时间 point name, `str`
    - wtg_pn: 风机号 point name,`str`
    - mg: margin, 图片上下左右预留多大距离
    - w: width
    - h: height

    return:
    ----------
    返回图片对象：plotly.express fig
    '''
    # full_pw_df = dataframe[dataframe[full_pw_pn]>full_time_thre].reset_index(drop=True).sort_values(by=[wtg_pn,time_pn])
    use_data = full_pw_df[[wtg_pn,time_pn]+[point_name]]
    y_max = full_pw_df[point_name].max()
    y_min = full_pw_df[point_name].min()
    use_data = use_data.pivot(index=time_pn,columns=wtg_pn)
    wtg_list = np.unique(full_pw_df[wtg_pn])
    if y_max == np.NaN:
        print('all data NaN')
        return None
    all_y = []
    for i,wtg in enumerate(wtg_list):
        # 获取当前风机的轴承温度数据
        column_name = wtg
        y = use_data[point_name][column_name].dropna()
        all_y.append(y.reset_index(drop=True))
    plot_df = pd.DataFrame(all_y).T    
    plotly_df =  pd.melt(plot_df.reset_index(),id_vars='index').dropna().reset_index(drop=True)
    plotly_df.columns = [xlabel,'风机',ylabel]
    fig = px.scatter(plotly_df,x=xlabel,y=ylabel,
                     color='风机')
    fig.update_yaxes(range=[y_min-y_max//20,y_max+y_max//20])
    fig.update_layout(
        title = {'text':title,
                #  'y':0.95,
                 'x':0.5,
                 },
        legend_title_text = '图例',
        width = w,
        height = h,
        margin = dict(l=mg,r=mg,t=40,b=mg)
    )
    return fig
# all_data = all_data[all_data['时间']>='2023-09-23']

# import chart_studio
# chart_studio.tools.set_credentials_file(username='221041004',api_key='wbZMxMecylzhXahyRIam')

# import chart_studio.plotly as py

# # py.sign_in('221041004','wbZMxMecylzhXahyRIam')
# # figure = figure.encode('utf-8')

def plot_comparison_divide(dataframe,wtg_id,point_names,ylabel,xlabel,style=None,titlesize=28,labelsize=15,point_size =20 ,edgecolor='white',point_alpha=1,grid=False,\
                    wtg_pn='风机',time_pn='data_time',path=None,title=None,legend_cols=1,legend_loc='lower right',color_map='tab20',sharpness=500,\
                    divide_thre=1.13,diff_thre=-1,if_hlines=True,notation=True,loc = 'upper right',unit='℃',day_sep=5,save_fig=True):
    '''
    一个风机不同测点互相对比, 异常的风机画出散点图，不同测点用不同颜色标识。
    对比方法：
    计算同风机每个测点的平均值（消除时刻维度）
    如果没有满足条件的聚合结果，且测点平均值中最大值/最小值 小于`{divide_thre}`则该风机无异常。
    反之认为该风机有异常，画出三相温度的对比图。

    Parameters
    ----------
    - dataframe: 原始数据，一般为可以为满发后的数据，也可以是每个风机都连续的数据
    - wtg_id: 需要指定风机号
    - point_names: 需要画图的测点名称列表如 [变桨电机温度1，xxxxxx2，xxxxxx3]
    - color_map: sns.color_palette参数，如 tab20,rainbow
    - ylabel: y轴标签名
    - xlabel: x轴标签名
    - style: 图片风格，如 default,seaborn,ggplot
    - titlesize: 标题大小
    - labelsize: x，y轴标签大小
    - edgecolor: 散点边缘颜色
    - glow: 当style选赛博朋克时可以使边缘发光
    - point_size: 散点大小 如50
    - all_color: 如果非空则所有风机都用该颜色画图
    - point_alph：散点透明度 0-1
    - grid: 是否要网格
    - time_pn:时间 point name, `str`
    - wtg_pn: 风机号 point name,`str`
    - path: 保存图片的路径
    - title: 图片标题
    - legend_cols：图例的列数（如果有40个风机需要2-4列才能乘下）
    - legend_loc: 图例的位置 如 lower right, lower left, upper right, upper left, lower center,...,best
    - sharpness： 图片清晰度
    ----------
    - abnormal_thre: 判断每一时刻该风机所有测点的最大值是否大于最小值的倍数阈值
    - diff_trhe: 判断每一时刻所有测点最大值是否大于最小值的距离阈值
    - continue_num: 满足abnormal_thre,diff_thre两个条件的异常情况的连续时刻阈值
    - mean_diff_thre: 满足以上三个条件，且每次异常的平均差值（对时刻维度做平均）达到该阈值
    - vlines: 是否对异常情况画图,用红色区域标出异常区域
    - divided_thre: 所有时刻的各测点平均值排序，最大值/最小值的倍数阈值

    return:
    ----------
    返回异常的原始数据 pd.DataFrame
    返回聚合后的异常原始数据： pd.DataFrame
    '''    
    data_df = dataframe[dataframe[wtg_pn]==wtg_id].sort_values(by=[wtg_pn,time_pn]).reset_index(drop=True)
    temp_mean=data_df[point_names].mean(axis=0,)
    divide = temp_mean.max()/temp_mean.min()
    diff = temp_mean.max()-temp_mean.min()
    max_point = temp_mean.idxmax()
    min_point = temp_mean.idxmin()
    if data_df.shape[0] == 0:
        return
    elif  (divide<divide_thre)or(diff<diff_thre):
        print(f'congrats! {wtg_id}风机对比无异常')
        return
    else:
        print(f'{wtg_id}风机对比异常')
        print(f'{wtg_id}风机{max_point}/{min_point}={divide},{max_point}-{min_point} = {diff}')
    if style is not None:
        plt.style.use(style)
        config = {
            "font.family":'serif',
            # "font.size": 20,
            "mathtext.fontset":'stix',
            "font.serif": ['SimSun'],
        }
        rcParams.update(config)
    figure,ax = plt.subplots(figsize=(15,8))
    if grid:
            plt.grid(True,which='both',ls='dashed')
    colors = sns.color_palette(color_map,len(point_names))
    y_max = data_df[point_names].max().max()
    y_min=data_df[point_names].min().min()
    y_axis_min = min(y_min-5,0)
    max_x = 0 if xlabel=='次数' else data_df[time_pn][0]
    min_x = 0 if xlabel=='次数' else data_df[time_pn][0]
    for i,pn in enumerate(point_names):
            y = data_df[pn]
            if xlabel=='次数':
                x = np.arange(len(y))
                max_x = max(len(y),max_x)
            elif xlabel=='时间':
                x=data_df[time_pn]
                max_x = max(max(x),max_x)
            ax.scatter(x, y, label=pn, color=colors[i],edgecolors=edgecolor,s=point_size,alpha=point_alpha)
    # y_major_locator = MultipleLocator((y_max+5)//20)
    y_sep = (y_max-y_axis_min+5)//20
    y_major_locator = MultipleLocator(y_sep)
    ax.yaxis.set_major_locator(y_major_locator)
    ax.set_ylim(min(y_axis_min,0),(y_max+y_sep))
    if xlabel=='时间':
        x_major_locator = mdate.DayLocator(interval=day_sep)
    elif xlabel=='次数':
        x_major_locator = MultipleLocator(max_x//20)
    ax.xaxis.set_major_locator(x_major_locator)
    # print(max_x,min_x)
    if if_hlines:
        bbox0 = { "alpha": 0.5,'facecolor':'white','pad':0.01,'edgecolor':'#DCDCDC','boxstyle':'round'}
        ax.hlines(y=temp_mean.max(),xmax=max_x,xmin=min_x,linestyles='dotted',alpha=0.8,color='red')
        ax.text(x=min_x,y=temp_mean.max(),s=f'{max_point}平均值 = {round(temp_mean.max(),2)}{unit}',color='#CD0000',ha = 'left',va='bottom',size=10,fontweight='bold',bbox = bbox0)
        ax.hlines(y=temp_mean.min(),xmax=max_x,xmin=min_x,linestyles='dotted',alpha=0.8,color='red')
        ax.text(x=min_x,y=temp_mean.min(),s=f'{min_point}平均值 = {round(temp_mean.min(),2)}{unit}',color='#CD0000',ha = 'left',va='bottom',size=10,fontweight='bold',bbox = bbox0)    
    if notation:
        # text = f'{max_point}平均比{min_point}高{round(diff,2)}{unit},高出{round((divide-1)*100,2)}%。'
        text = f'{max_point}平均比{min_point}高{round((divide-1)*100,2)}%({round(diff,2)}℃)。'
        # 创建文本框，将文本置于文本框内
        bbox = { "alpha": 0.5,'facecolor':'white','pad':0.5,'edgecolor':'#DCDCDC','boxstyle':'round'}
        # 所有文本使用统一的样式
        # style = {"size": 15, "color": "#CD2626", "bbox": bbox,'fontweight':'bold'}
        style = {"size": 20, "color": '#CD0000', "bbox": bbox,'fontweight':'bold'}
        if loc=='upper right':
            ax.text(x=max_x,y=y_max-y_sep,s=text,ha = 'right',va='top',**style)
        elif loc=='lower left':
            ax.text(x=min_x,y=min(y_min-5,0)+y_sep,s=text,ha = 'left',va='bottom',**style)
    # 设置横轴和纵轴标签
    ax.set_xlabel(xlabel,fontdict = {'fontsize':labelsize,'fontweight':'bold'})
    ax.set_ylabel(ylabel,fontdict = {'fontsize':labelsize,'fontweight':'bold'})
    if title:
        ax.set_title(title,fontdict={'fontsize':titlesize,'fontweight':'bold'})
    # ax.set_title(f'与额定功率差值小于{1000}'+f'{full_time_thre}'+'min后'+point_name)

    ax.legend(ncol=legend_cols,loc=legend_loc)
    # 显示图形
    # plt.show()
    if save_fig:
        plt.savefig(path,bbox_inches='tight',dpi=sharpness,facecolor='white')
    return figure