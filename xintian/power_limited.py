import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
# import seaborn as sns
# from matplotlib.pyplot import MultipleLocator
# import statsmodels.api as sm
# import os
# plt.rc('font',family = 'YouYuan')


def limit_power_delete(data,pw_cur,rho_loc,rho_ref,angle_thr,wind_pn = '风速',P_pn='发电机有功功率',blade_angle_pn = '桨叶片角度1',type_pn='风机类型',\
                        pw_thr=100,gap_thr=0.1,multiple_type=False):

    """
    将给定数据中的限功率点剔除。

    Parameters
    ----------
    - data: 需要剔除限电的数据必须包含：风速、发电机有功功率、桨叶片角度三个测点，需要是pandas.DataFrame

    - pw_cur: 理论功率曲线数据，必须包含V_bin（理论风速）P_th_bin（理论功率）两个测点,需要是pandas.DataFrame
    
    - rho_ref:标准空气密度，float
    
    - rho_loc:当地空气密度，float
    
    - angle_thr:限电的桨叶角度阈值，float
    
    - wind_pn:风速的测点名称 point name,str
    
    - P_pn: 发电机有功功率 point name,str
    
    - blade_angle_pn:浆叶角度 point name,str
    
    - type_pn:风机类型 point name,str
    
    - pw_thr: 限电的功率阈值，float
    
    - gap_thr: 实际功率与理论功率差距的阈值，float
    
    - multiple_type:是否包含多个风机类型，boolean

    Returns
    -------
    `pd.DataFrame`    

    """


    for name in ['V_bin','P_th_bin']:
        if name not in list(pw_cur.columns):
            raise Exception(f'传入数据中不包含该字段：{name}')
    for name in [wind_pn,P_pn,blade_angle_pn]:
        if name not in list(data.columns):
            raise Exception(f'传入数据中不包含该字段：{name}')
    if multiple_type & (type_pn not in list(data.columns)):
        raise Exception(f'缺少{type_pn}')

    data['V_n'] = data[wind_pn] * ((rho_loc/rho_ref)**(1/3))
    # 平均风速分bin，调整实际功率为bin功率
    bs = np.arange(-0.25,25.5,0.5)
    ls = np.arange(0,25.5,0.5)
    data['V_bin'] = pd.cut(data['V_n'],bins=bs,right=False,labels=ls).astype('float64')
    data['P_bin'] = np.where(data['V_n']==0,data[P_pn],\
                                ((data['V_bin']/data['V_n'])**3) * data[P_pn])
    # 匹配理论功率
    if multiple_type:
        merge_data =  pd.merge(data,pw_cur,how='left',on= ['V_bin',type_pn])
    else:
        merge_data = pd.merge(data,pw_cur,how='left',on= 'V_bin')
    merge_data['gap'] = (merge_data['P_th_bin'] - merge_data['P_bin'])/merge_data['P_th_bin']
    merge_data.describe()
    # 寻找限功率点
    limit_data = merge_data[(merge_data['gap']>gap_thr) & (merge_data['P_bin']>pw_thr)]
    limit_data = limit_data[(limit_data[blade_angle_pn]>angle_thr)|(limit_data[P_pn]<=0)]# 找限功率点
    print('限功率点:\n',limit_data[['V_n','V_bin',wind_pn,P_pn,'P_bin',blade_angle_pn,'gap']].head(),'\n',limit_data.shape)
    merge_data = merge_data.drop(limit_data.index,axis=0).reset_index(drop=True)

    # 筛选出正常发电点
    # gen_data = merge_data[(merge_data[P_pn]>500)&merge_data[P_pn]<1000].reset_index(drop=True)

    result_df= merge_data[merge_data[P_pn]>0].reset_index(drop=True)
    return result_df


def limit_power_delete_loc(data,pw_cur,angle_thr,wind_pn = '风速',P_pn='发电机有功功率',blade_angle_pn = '桨叶片角度1',type_pn='风机类型',\
                        pw_thr=100,gap_thr=0.1,multiple_type=False):

    """
    将给定数据中的限功率点剔除。给出的理论功率曲线为当地空气密度下的理论功率曲线

    Parameters
    ----------
    - data: 需要剔除限电的数据必须包含：风速、发电机有功功率、桨叶片角度三个测点，需要是pandas.DataFrame

    - pw_cur: 理论功率曲线数据，必须包含V_bin（理论风速）P_bin（理论功率）两个测点,需要是pandas.DataFrame
    
    - rho_ref:标准空气密度，float
    
    - rho_loc:当地空气密度，float
    
    - angle_thr:限电的桨叶角度阈值，float
    
    - wind_pn:风速的测点名称 point name,str
    
    - P_pn: 发电机有功功率 point name,str
    
    - blade_angle_pn:浆叶角度 point name,str
    
    - type_pn:风机类型 point name,str
    
    - pw_thr: 限电的功率阈值，float
    
    - gap_thr: 实际功率与理论功率差距的阈值，float
    
    - multiple_type:是否包含多个风机类型，boolean

    Returns
    -------
    `pd.DataFrame`    

    """


    for name in ['V_bin','P_th_bin']:
        if name not in list(pw_cur.columns):
            raise Exception(f'传入数据中不包含该字段：{name}')
    for name in [wind_pn,P_pn,blade_angle_pn]:
        if name not in list(data.columns):
            raise Exception(f'传入数据中不包含该字段：{name}')
    if multiple_type & (type_pn not in list(data.columns)):
        raise Exception(f'缺少{type_pn}')

    # 平均风速分bin，调整实际功率为bin功率
    bs = np.arange(-0.25,25.5,0.5)
    ls = np.arange(0,25.5,0.5)
    data['V_bin'] = pd.cut(data[wind_pn],bins=bs,right=False,labels=ls).astype('float64')
    data['P_bin'] = np.where(data[wind_pn]==0,data[P_pn],\
                                ((data['V_bin']/data[wind_pn])**3) * data[P_pn])
    # 匹配理论功率
    if multiple_type:
        merge_data =  pd.merge(data,pw_cur,how='left',on= ['V_bin',type_pn])
    else:
        merge_data = pd.merge(data,pw_cur,how='left',on= 'V_bin')
    merge_data['gap'] = (merge_data['P_th_bin'] - merge_data['P_bin'])/merge_data['P_th_bin']
    merge_data.describe()
    # 寻找限功率点
    limit_data = merge_data[(merge_data['gap']>gap_thr) & (merge_data['P_bin']>pw_thr)]
    limit_data = limit_data[(limit_data[blade_angle_pn]>angle_thr)|(limit_data[P_pn]<=0)]# 找限功率点
    print('限功率点:\n',limit_data[[wind_pn,'V_bin',P_pn,'P_bin',blade_angle_pn,'gap']].head(),'\n',limit_data.shape)
    merge_data = merge_data.drop(limit_data.index,axis=0).reset_index(drop=True)

    # 筛选出正常发电点
    # gen_data = merge_data[(merge_data[P_pn]>500)&merge_data[P_pn]<1000].reset_index(drop=True)

    result_df= merge_data[merge_data[P_pn]>0].reset_index(drop=True)
    return result_df


@st.cache_resource(ttl=10800)
def limit_power_detect_loc(data,pw_cur,angle_thr=3,wind_pn = '风速',P_pn='发电机有功功率',blade_angle_pn = '桨叶片角度1',type_pn='风机类型',\
                        pw_thr=100,gap_thr=0.1,multiple_type=False,time_pn='data_time',wtg_pn='device_name'):
    """
    监测给定数据中的限功率点，并返回剔除限功率点后的数据，以及加入限功率点标识的原始数据。给出的理论功率曲线为当地空气密度下的理论功率曲线。
    具体做法：1.所有小于理论功率 10% 且有功功率大于 100 且桨叶角度大于 3 的点都是限功率点
            2.前后均为限功率点的中间某个点也应该是限功率点
    Parameters
    ----------
    - data: 需要剔除限电的数据必须包含：风速、发电机有功功率、桨叶片角度三个测点，类型是`pandas.DataFrame`

    - pw_cur: 理论功率曲线数据，必须包含V_bin（理论风速）P_bin（理论功率）两个测点,类型是`pandas.DataFrame`
    
    - angle_thr:限电的桨叶角度阈值，`float`
    
    - wind_pn:风速的测点名称 point name,`str`
    
    - P_pn: 发电机有功功率 point name,`str`
    
    - blade_angle_pn:浆叶角度 point name,`str`
    
    - type_pn:风机类型 point name,`str`
    
    - pw_thr: 限电的功率阈值，`float`
    
    - gap_thr: 实际功率与理论功率差距的阈值，`float`
    
    - multiple_type:是否包含多个风机类型，`boolean`

    - time_pn:时间 point name, `str`

    - wtg_pn: 风机号 point name,`str`

    Returns
    -------
    `pd.DataFrame`,`pd.DataFrame`
    """

    #检查输入的原始数据和理论功率曲线数据测点是否完全，测点名是否输入正确。
    for name in ['V_bin','P_th_bin']:
        if name not in list(pw_cur.columns):
            raise Exception(f'传入数据中不包含该字段：{name}')
    for name in [wind_pn,P_pn,blade_angle_pn]:
        if name not in list(data.columns):
            raise Exception(f'传入数据中不包含该字段：{name}')
    if multiple_type & (type_pn not in list(data.columns)):
        raise Exception(f'缺少{type_pn}')
    print(f'原始数据{data.shape}')

    # 风速分bin，调整实际功率为bin功率（因为风速调整为bin值后需要相应的调整功率来弥补这一变动）
    bs = np.arange(-0.25,25.5,0.5)
    ls = np.arange(0,25.5,0.5)
    data['V_bin'] = pd.cut(data[wind_pn],bins=bs,right=False,labels=ls).astype('float64')
    data['P_bin'] = np.where(data[wind_pn]==0,data[P_pn],\
                                ((data['V_bin']/data[wind_pn])**3) * data[P_pn])
    # 匹配理论功率，如存在多种类型的风机则需要增加“风机类型”匹配条件
    if multiple_type:
        merge_data =  pd.merge(data,pw_cur,how='inner',on= ['V_bin',type_pn])
    else:
        merge_data = pd.merge(data,pw_cur,how='inner',on= 'V_bin')
    #计算与理论功率的差距（该值代表比理论功率小百分之多少，如为负数代表大于理论功率）
    merge_data['gap'] = (merge_data['P_th_bin'] - merge_data['P_bin'])/merge_data['P_th_bin'] 
    # 寻找限功率点
    wtg_list = np.unique(merge_data[wtg_pn])
    all_data = []
    for wtg_id in wtg_list: #遍历风机号
        wtg_data = merge_data[merge_data[wtg_pn]==wtg_id].reset_index(drop=True).sort_values(time_pn).reset_index(drop=True) #提取某个风机的数据
        flag = (wtg_data['gap']>gap_thr) & (wtg_data[P_pn]>pw_thr) & (wtg_data[blade_angle_pn]>angle_thr) #比理论功率小{gap_thr}%且功率大于{pw_thr}且桨叶角度大于{angle_thr}的标识
        wtg_data['flag'] = flag +1 -1 #将True/False标识换为1/0
        #如果某风机某时刻前后均为限功率点，而该时刻不满足限功率阈值条件，则也划为限功率点
        wtg_data['flag_after'] = np.array(list(flag[1:])+[np.nan]) #后一个点是否为限功率点
        wtg_data['flag_before'] = np.array([np.nan]+list(flag[:-1])) #前一个点是否为限功率点
        wtg_data['limit_flag']= (wtg_data['flag']==1)|((wtg_data['flag_after']==1)&(wtg_data['flag_before']==1)) #最终的限功率标识
        all_data.append(wtg_data)
    all_data_df = pd.concat(all_data,axis=0).reset_index(drop=True)
    limit_data_all = all_data_df[all_data_df['limit_flag']==1].reset_index(drop=True) #所有的限功率点
    # print(f'限功率点:{limit_data_all.shape}\n',limit_data_all[[wtg_pn,time_pn,wind_pn,'V_bin',P_pn,'P_bin',blade_angle_pn,'gap']].head())
    unlimited_data = all_data_df[all_data_df['limit_flag']==0].reset_index(drop=True) #剔除后的非限功率数据
    print(f'非限功率点：{unlimited_data.shape}')
    # 筛选出正常发电点
    # gen_data = merge_data[(merge_data[P_pn]>500)&merge_data[P_pn]<1000].reset_index(drop=True)
    print(f'功率小于0点:{unlimited_data[unlimited_data[P_pn]<=0].shape}') #查看功率小于0的数据有多少
    # print(np.unique(unlimited_data[P_pn]))
    result_df= unlimited_data[unlimited_data[P_pn]>0].reset_index(drop=True) #最终的剔除了限功率点且功率大于0的所有数据
    print(f'正常发电点:{result_df.shape}')
    return result_df,all_data_df,unlimited_data.shape[0]


def limit_power_detect_loc_Goldwind(data,pw_cur,angle_thr=3,wind_pn = '风速',P_pn='发电机有功功率',blade_angle_pn = '桨叶片角度1',blade_angle_dif_pn = 'blade_dif_pn',type_pn='风机类型',\
                        pw_thr=100,gap_thr=0.1,multiple_type=False,time_pn='data_time',wtg_pn='device_name'):
    """
    监测给定数据中的限功率点，并返回剔除限功率点后的数据，以及加入限功率点标识的原始数据。给出的理论功率曲线为当地空气密度下的理论功率曲线。
    具体做法：1.所有实际功率小于理论功率 10% （桨叶角度大于1 或 桨叶角度10min最大值-10min最小值大于1）
            2.前后均为限功率点的中间某个点也应该是限功率点
    Parameters
    ----------
    - data: 需要剔除限电的数据必须包含：风速、发电机有功功率、桨叶片角度三个测点，类型是`pandas.DataFrame`

    - pw_cur: 理论功率曲线数据，必须包含V_bin（理论风速）P_bin（理论功率）两个测点,类型是`pandas.DataFrame`
    
    - angle_thr:限电的桨叶角度阈值，`float`
    
    - wind_pn:风速的测点名称 point name,`str`
    
    - P_pn: 发电机有功功率 point name,`str`
    
    - blade_angle_pn:浆叶角度 point name,`str`

    - blade_angle_dif_pn: 桨叶角度最大值-最小值的 point name,`str`
    
    - type_pn:风机类型 point name,`str`
    
    - pw_thr: 限电的功率阈值，`float`
    
    - gap_thr: 实际功率与理论功率差距的阈值，`float`
    
    - multiple_type:是否包含多个风机类型，`boolean`

    - time_pn:时间 point name, `str`

    - wtg_pn: 风机号 point name,`str`

    Returns
    -------
    `pd.DataFrame`,`pd.DataFrame`
    """

    #检查输入的原始数据和理论功率曲线数据测点是否完全，测点名是否输入正确。
    for name in ['V_bin','P_th_bin']:
        if name not in list(pw_cur.columns):
            raise Exception(f'传入数据中不包含该字段：{name}')
    for name in [wind_pn,P_pn,blade_angle_pn]:
        if name not in list(data.columns):
            raise Exception(f'传入数据中不包含该字段：{name}')
    if multiple_type & (type_pn not in list(data.columns)):
        raise Exception(f'缺少{type_pn}')
    print(f'原始数据{data.shape}')

    # 风速分bin，调整实际功率为bin功率（因为风速调整为bin值后需要相应的调整功率来弥补这一变动）
    bs = np.arange(-0.25,25.5,0.5)
    ls = np.arange(0,25.5,0.5)
    data['V_bin'] = pd.cut(data[wind_pn],bins=bs,right=False,labels=ls).astype('float64')
    data['P_bin'] = np.where(data[wind_pn]==0,data[P_pn],\
                                ((data['V_bin']/data[wind_pn])**3) * data[P_pn])
    # 匹配理论功率，如存在多种类型的风机则需要增加“风机类型”匹配条件
    if multiple_type:
        merge_data =  pd.merge(data,pw_cur,how='inner',on= ['V_bin',type_pn])
    else:
        merge_data = pd.merge(data,pw_cur,how='inner',on= 'V_bin')
    print(f'有效风速段数据{merge_data.shape}')
    #计算与理论功率的差距（该值代表比理论功率小百分之多少，如为负数代表大于理论功率）
    merge_data['gap'] = (merge_data['P_th_bin'] - merge_data['P_bin'])/merge_data['P_th_bin'] 
    # 寻找限功率点
    wtg_list = np.unique(merge_data[wtg_pn])
    all_data = []
    for wtg_id in wtg_list: #遍历风机号
        wtg_data = merge_data[merge_data[wtg_pn]==wtg_id].reset_index(drop=True).sort_values(time_pn).reset_index(drop=True) #提取某个风机的数据
        flag = (wtg_data['gap']>gap_thr) & (wtg_data[P_pn]>pw_thr) & ((wtg_data[blade_angle_dif_pn]>1) | (wtg_data[blade_angle_pn]>angle_thr)) #比理论功率小{gap_thr}%且功率大于{pw_thr}且桨叶角度大于{angle_thr}的标识
        wtg_data['flag'] = flag +1 -1 #将True/False标识换为1/0
        #如果某风机某时刻前后均为限功率点，而该时刻不满足限功率阈值条件，则也划为限功率点
        wtg_data['flag_after'] = np.array(list(flag[1:])+[np.nan]) #后一个点是否为限功率点
        wtg_data['flag_before'] = np.array([np.nan]+list(flag[:-1])) #前一个点是否为限功率点
        wtg_data['limit_flag']= (wtg_data['flag']==1)|((wtg_data['flag_after']==1)&(wtg_data['flag_before']==1)) #最终的限功率标识
        all_data.append(wtg_data)
    all_data_df = pd.concat(all_data,axis=0).reset_index(drop=True)
    limit_data_all = all_data_df[all_data_df['limit_flag']==1].reset_index(drop=True) #所有的限功率点
    print(f'限功率点:{limit_data_all.shape}\n',limit_data_all[[wtg_pn,time_pn,wind_pn,'V_bin',P_pn,'P_bin',blade_angle_pn,'gap',blade_angle_dif_pn]].head())
    unlimited_data = all_data_df[all_data_df['limit_flag']==0].reset_index(drop=True) #剔除后的非限功率数据
    print(f'非限功率点：{unlimited_data.shape}')
    # 筛选出正常发电点
    # gen_data = merge_data[(merge_data[P_pn]>500)&merge_data[P_pn]<1000].reset_index(drop=True)
    print(f'功率小于0点:{unlimited_data[unlimited_data[P_pn]<=0].shape}') #查看功率小于0的数据有多少
    # print(np.unique(unlimited_data[P_pn]))
    result_df= unlimited_data[unlimited_data[P_pn]>0].reset_index(drop=True) #最终的剔除了限功率点且功率大于0的所有数据
    print(f'正常发电点:{result_df.shape}')
    return result_df,all_data_df