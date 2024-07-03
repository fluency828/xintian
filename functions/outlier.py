import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.pyplot import MultipleLocator
import statsmodels.api as sm
import os
plt.rc('font',family = 'YouYuan')
import sys
sys.path.append('D:/OneDrive - CUHK-Shenzhen/utils/')
# from xintian.power_limited import limit_power_delete

def outlier_detection_wls(detect_data,X_point_name,y_point_name,threshold,title,path,x_ticks_n=20):
    '''
    离群值检测
    检测 detect_data 中的 y 与 X之间的线性关系，以及离群点
    检测方法为使用OLS的残差的倒数作为WLS（加权最小二乘法）的权重，进行回归。
    并根据WLS的残差以及输入的阈值判断是否存在离群样本。
    
    -- parameter --
    - detect_data: 输入的数据，pd.DataFrame
    - X_point_name: 自变量特征名称，str，需要被包含在detect_data中
    - y_point_name: 因变量特征名称，str，需要被包含在detect_data中
    - threshold: wls回归后若样本的残差超过该阈值则判定为离群点，否则非离群点，float
    - title: 图片标题
    - path: 图片保存路径
    -- return --
    返回每个点是否为离群点的结果（0否1是），以及WLS计算出的斜率。
    '''
    y_train = detect_data[y_point_name]
    X_train =  detect_data[X_point_name]
    res_ols = sm.OLS(y_train,X_train).fit()
    # print(res_ols.summary())
    # k=res_ols.params[0]
    mod_wls = sm.WLS(y_train,X_train, weights=1.0 / (abs(res_ols.resid)*100))
    res_wls = mod_wls.fit()
    k=res_wls.params[0]
    print('params',res_wls.params)
    detect_data['resid']=res_wls.resid
    # print(detect_data.describe())
    outlier_label = (abs(detect_data['resid']) >threshold) +1 -1
    detect_data['outlier'] = outlier_label
    fig, ax = plt.subplots(figsize=(15,8))
    plt.grid(True,which='both',ls='dashed')
    wtg_data = detect_data[detect_data['outlier']==0].reset_index(drop=True)
    outlier_data = detect_data[detect_data['outlier']==1].reset_index(drop=True)
    ax.scatter(wtg_data[X_point_name],wtg_data[y_point_name],label=f'正常值')
    ax.scatter(outlier_data[X_point_name],outlier_data[y_point_name],label=f'异常值')
    ax.plot(detect_data[X_point_name],k*detect_data[X_point_name],color='red')
    ax.legend()
    # ax.set_title(f'[{bin-0.25}°,{bin+0.25}°)区间的功率曲线',fontdict={'fontsize':20,'fontweight':'bold'})
    # ax.set_title(f'{wtg_id}功率曲线',fontdict={'fontsize':20,'fontweight':'bold'})
    y_max = max(detect_data[y_point_name])
    x_max = max(detect_data[X_point_name])
    y_major_locator = MultipleLocator((y_max)/20)
    x_major_locator = MultipleLocator((x_max)/x_ticks_n)
    # y_major_locator = MultipleLocator(2)
    ax.yaxis.set_major_locator(y_major_locator)
    ax.xaxis.set_major_locator(x_major_locator)

    ax.set_xlabel(X_point_name)
    ax.set_ylabel(y_point_name)
    ax.set_title(f'{title},k={k}',fontdict={'fontsize':20,'fontweight':'bold'})
    plt.savefig(path,bbox_inches='tight',dpi=500)
    return outlier_label,k

def outlier_detection_ols(detect_data,X_point_name,y_point_name,threshold,title,path,x_ticks_n=20,sigma_3=False):
    '''
    离群值检测
    检测 detect_data 中的 y 与 X之间的线性关系，以及离群点
    检测方法为使用OLS的残差的倒数作为WLS（加权最小二乘法）的权重，进行回归。
    并根据WLS的残差以及输入的阈值判断是否存在离群样本。
    
    -- parameter --
    - detect_data: 输入的数据，pd.DataFrame
    - X_point_name: 自变量特征名称，str，需要被包含在detect_data中
    - y_point_name: 因变量特征名称，str，需要被包含在detect_data中
    - threshold: wls回归后若样本的残差超过该阈值则判定为离群点，否则非离群点，float
    - title: 图片标题
    - path: 图片保存路径
    -- return --
    返回每个点是否为离群点的结果（0否1是），以及WLS计算出的斜率。
    '''
    y_train = detect_data[y_point_name]
    X_train =  detect_data[X_point_name]
    res_ols = sm.OLS(y_train,X_train).fit()
    k1 = res_ols.params[0]
    detect_data['resid']=res_ols.resid
    sigma=np.std(res_ols.resid)
    print('sigma',sigma)
    # print(detect_data.describe())
    if sigma_3:
        threshold = 3*sigma
    outlier_label = (abs(detect_data['resid']) >threshold) +1 -1
    detect_data['outlier'] = outlier_label
    # detect_data['weight'] = w
    fig, ax = plt.subplots(figsize=(15,8))
    plt.grid(True,which='both',ls='dashed')
    wtg_data = detect_data[detect_data['outlier']==0].reset_index(drop=True)
    outlier_data = detect_data[detect_data['outlier']==1].reset_index(drop=True)
    ax.scatter(wtg_data[X_point_name],wtg_data[y_point_name],label=f'正常值')
    ax.scatter(outlier_data[X_point_name],outlier_data[y_point_name],label=f'异常值(残差>{round(threshold,2)})')
    # ax.plot(detect_data[X_point_name],k2*detect_data[X_point_name],color='red')
    ax.plot(detect_data[X_point_name],k1*detect_data[X_point_name],color='yellow')
    ax.legend()
    # ax.set_title(f'[{bin-0.25}°,{bin+0.25}°)区间的功率曲线',fontdict={'fontsize':20,'fontweight':'bold'})
    # ax.set_title(f'{wtg_id}功率曲线',fontdict={'fontsize':20,'fontweight':'bold'})
    y_max = max(detect_data[y_point_name])
    x_max = max(detect_data[X_point_name])
    y_major_locator = MultipleLocator((y_max)/20)
    x_major_locator = MultipleLocator((x_max)/x_ticks_n)
    # y_major_locator = MultipleLocator(2)
    ax.yaxis.set_major_locator(y_major_locator)
    ax.xaxis.set_major_locator(x_major_locator)

    ax.set_xlabel(X_point_name)
    ax.set_ylabel(y_point_name)
    ax.set_title(f'{title},k={round(k1,4)}',fontdict={'fontsize':20,'fontweight':'bold'})
    # print(detect_data.groupby('outlier').mean('weight'))
    plt.savefig(path,bbox_inches='tight',dpi=500)
    return outlier_label,k1