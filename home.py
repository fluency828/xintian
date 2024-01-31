import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import sys
# sys.path.append('D:/OneDrive - CUHK-Shenzhen/utils/')
# from xintian.full_power_time import gen_full_time
# from xintian.Temp_warning import plot_scene,plotly_scene,plot_comparison_divide
import plotly.express as px
import os
import matplotlib.dates as mdate
import sys
# sys.path.append('D:/OneDrive - CUHK-Shenzhen/utils/')
from xintian.power_limited import limit_power_detect_loc
from xintian.plotly_functions import plot_limit_power,plot_yaw_angle,plot_blade_power_all
from matplotlib import rcParams
from xintian.Speed_Torque import rated_speed_torque
from xintian.useful_tools import figs2zip
from xintian.yaw import yaw_result_generate
from xintian.angle_wind import plot_angle_power
import io
import zipfile



config = {
    "font.family":'serif',
    # "font.size": 20,
    "mathtext.fontset":'stix',
    "font.serif": ['SimSun'],
}
rcParams.update(config)
plt.rcParams['axes.unicode_minus'] = False



########################## 正式开始网页！###################
st.title('风场数据分析报告')
st.markdown('# 查看原始数据')
phase_name = st.selectbox(
    label='请输入您选择的风场',
    options=('昆头岭明阳','康庄运达','魁通沟金风'),
    help='不同风场可能对应不同的数据格式和测点名称')


if phase_name=='昆头岭明阳':
    wtg_pn = '风机'
    time_pn ='时间'
    type_pn = '风机类型'

    P_pn = '平均电网有功功率'
    w_pn = '平均风速'
    angle_pn='平均桨叶角度1a'
    cabin_north_angle = '平均机舱对北角度'
    wind_north_angle = '平均风向对北角度'
    generator_speed_pn = '平均发电机转速1'
    # inter_angle = '机舱与风向夹角'
    # inter_angle_bin = '机舱与风向夹角_bin'
    # generator_speed = '平均发电机转速1'
    # lambda_ = '叶尖速比'
from pathlib import Path

ROOT_PATH = st.file_uploader("file path")
if ROOT_PATH is not None:
    raw_data_path = ROOT_PATH
else:
    ROOT_PATH = 'D:/1 新天\数字运营部 任务\昆头岭手动分析/12月/'
    raw_data_path = ROOT_PATH+'raw_data.csv'

@st.cache_data
def load_data(url):
    df = pd.read_csv(url)
    return df

raw_data = load_data(raw_data_path)
raw_data[time_pn] = pd.to_datetime(raw_data[time_pn])
if 'Unnamed:235' in  raw_data.columns:
    raw_data = raw_data.drop('Unamed:235',axis=1)
st.write('原始数据')
st.write(raw_data)
st.markdown(f'原始数据时间起止:  \n 开始时间：  {raw_data[time_pn].min()},  \n 结束时间： {raw_data[time_pn].max()}')
st.write(raw_data.describe())
st.markdown(f'当前数据大小为{raw_data.shape}')
wtg_list =raw_data[[wtg_pn,type_pn]].drop_duplicates().reset_index(drop=True)


st.markdown('# 处理限功率点')

if phase_name=='昆头岭明阳':
    theory_pw_cur = pd.read_excel('D:/1 新天/数字运营部 任务/昆头岭手动分析/理论功率曲线.xlsx')
    st.write('理论功率')
    st.write(theory_pw_cur)
    gen_data,raw_data_1 = limit_power_detect_loc(raw_data,theory_pw_cur,wtg_pn=wtg_pn,time_pn=time_pn,wind_pn=w_pn,P_pn=P_pn,blade_angle_pn=angle_pn,angle_thr=3,gap_thr=0.1,pw_thr=0,multiple_type=True)
    st.markdown(f'剔除限功率点和非正常发电点后数据大小为{gen_data.shape}')
figure = plot_limit_power(raw_data_1,gen_data,theory_pw_cur,x_pn=w_pn,y_pn=P_pn)
st.pyplot(figure)
plt.close()

st.markdown('## 转矩控制')
generator_speed_square = '平均发电机转速平方'
generator_speed_square_standard = '发电机转速平方(去量纲)'
generator_torque_pn = '平均发电机转矩'
torque_speed_data = gen_data[abs(gen_data[generator_speed_pn])<2000].reset_index(drop=True)
torque_speed_data[generator_torque_pn] = torque_speed_data[P_pn] / torque_speed_data[generator_speed_pn]
torque_speed_data[generator_speed_square] = torque_speed_data[generator_speed_pn]**2
torque_speed_data[generator_speed_square_standard] = torque_speed_data[generator_speed_square]/1e4
st.markdown(f'去除转速大于2000后数据大小为{torque_speed_data.shape}')
st.write(torque_speed_data[[type_pn,generator_torque_pn,generator_speed_pn,generator_speed_square,]].groupby(type_pn).describe().T)

results = []
# warning_results = []

fig_ls = []
for i,wtg_info in wtg_list.iterrows():
    wtg_id,types = wtg_info
    # wtg_data = gen_data[gen_data[wtg_pn]==wtg_id].reset_index(drop=True)
    wtg_data = torque_speed_data[torque_speed_data[wtg_pn]==wtg_id].reset_index(drop=True)
    t1 = f'{wtg_id}转矩-转速散点图,型号{types}'
    t2 = f'{wtg_id}最小二乘拟合,型号{types}'
    # t3 = f'{wtg_id}转矩-转速平方散点图，型号{types}'
    # plot_scatter(wtg_data,r=generator_speed_pn,T=generator_torque_pn,r_square=generator_speed_square,title=t1,path=f'{ROOT_PATH}转矩控制/{t1}.png',if_plot_square=False,x_ticks_n=20)
    # plot_scatter(wtg_data,r=generator_speed_pn,T=generator_torque_pn,r_square=generator_speed_square,title=t1,path=f'{ROOT_PATH}转矩控制/{t3}.png',x_ticks_n=20)

    if types=='MySE5.0MW':
        # print(5000,wtg_id)
        use_data = wtg_data[(wtg_data[generator_speed_square]>5810)&(wtg_data[generator_speed_square]<5e4)].reset_index(drop=True)
        # print(wtg_id,use_data.shape)
        k,figure1 = rated_speed_torque(wtg_data,generator_speed_square_standard,generator_torque_pn,limit_pn=generator_speed_square,\
                                                    title=t2,path=None,x_ticks_n=10,\
                                                    upper=5e4,lower=5810,rated_speed=240,rated_torque=22,outlier_thre=0.5,save_figure=False)
    elif types=='MySE4.0MW':
        # print(4000,wtg_id)
        use_data = wtg_data[(wtg_data[generator_speed_square]>1.2e5)&(wtg_data[generator_speed_square]<1e6)].reset_index(drop=True)
        # print(wtg_id,use_data.shape)
        k,figure1 = rated_speed_torque(wtg_data,generator_speed_square_standard,generator_torque_pn,limit_pn=generator_speed_square,\
                                                    title=t2,path=None,x_ticks_n=10,\
                                                    upper=1e6,lower=1.2e5,rated_speed=1056,rated_torque=3.9,outlier_thre=0.2,save_figure=False)

    results.append([wtg_id,types,k])
    fig_ls.append(figure1)
    plt.close()

col_ls = st.columns(4)
for i,figs in enumerate(fig_ls):
    with col_ls[i%4]:
        st.pyplot(figs)

results_df = pd.DataFrame(results)
results_df.columns=['风机号','风机型号','斜率']
st.markdown('转矩控制斜率结果')
st.write(results_df)


st.button("Rerun")

st.markdown('## 偏航对风')
inter_angle = '机舱与风向夹角'
inter_angle_bin = '机舱与风向夹角_bin'

yaw_data = gen_data
st.markdown(f'当前数据形状{yaw_data.shape}')
yaw_data['dif'] = gen_data[wind_north_angle]-gen_data[cabin_north_angle]
yaw_data[inter_angle] = np.where(yaw_data['dif']>180,360-yaw_data['dif'],yaw_data['dif'])
yaw_data[inter_angle] = np.where(yaw_data[inter_angle]<-180,-360-yaw_data[inter_angle],yaw_data[inter_angle])

use_data = yaw_data[(yaw_data[inter_angle]>=-15.25)&(yaw_data[inter_angle]<=15.25)].reset_index(drop=True)
st.markdown(f'仅保留15°夹角以内数据后的数据大小{use_data.shape}')

bs2 = np.arange(-15.5,16,1);
ls2 = np.arange(-15,16,1);
use_data[inter_angle_bin] = pd.cut(use_data[inter_angle],bins=bs2,right=False,labels=ls2).astype('float64')
figure = plot_yaw_angle(use_data,inter_angle_bin)
st.pyplot(figure)
plt.close()
use_data['P_th'] = use_data['P_th_bin']/((use_data['V_bin']/use_data[w_pn])**3)

yaw_warning,wtg_result_list = yaw_result_generate(wtg_list,use_data,inter_angle_bin,angle_pn,wtg_pn=wtg_pn,P_pn=P_pn)

st.write(yaw_warning)


st.markdown('## 桨叶角度对零')
st.markdown(f'当前数据形状{raw_data.shape}')
blade_data = raw_data[(raw_data[angle_pn]>-7)&(raw_data[angle_pn]<100)].reset_index(drop=True)
st.markdown(f'仅保留桨叶角度正常值（剔除缺失值和小于-7，大于100的异常值）的数据大小{blade_data.shape}')

fig_ls_blade_type = []
for wtg_type in np.unique(wtg_list[type_pn]):
    use_data = blade_data[blade_data[type_pn]==wtg_type].reset_index(drop=True)
    figure = plot_blade_power_all(use_data,blade_pn=angle_pn,Pw_pn=P_pn,title=f'{type}功率-桨叶角度散点图')
    fig_ls_blade_type.append(figure)
    plt.close()

col_ls = st.columns(len(fig_ls_blade_type))
for i,figs in enumerate(fig_ls_blade_type):
    with col_ls[i]:
        st.pyplot(figs)

fig_ls_blade = []
fig_ls_blade_time = []
result_list=[]
for _,wtg_info in wtg_list.iterrows():
    wtg_id,wtg_type = wtg_info
    wtg_data = blade_data[blade_data[wtg_pn]==wtg_id].reset_index(drop=True)
    # save_path = ROOT_PATH +f'桨叶角度/{title1}.jpg'
    min_angle = wtg_data[angle_pn].min()
    title1 = f'{wtg_id}风机有功功率-桨叶角度散点图，型号{wtg_type},桨叶角最小值{min_angle}'.replace('/','_')
    figure1 = plot_angle_power(dataframe=wtg_data[wtg_data[angle_pn]<5].reset_index(drop=True),wtg=wtg_id,wtg_point_name=wtg_pn,y_point_name=P_pn,x_point_name=angle_pn,\
                    time_point_name=time_pn,point_size=10,style=None,path=None,title=title1,legend_cols=2,color='r',comparison=False,save_figure=False)
    plt.close()
    title2 = f'{wtg_id}风机桨叶角度-时间散点图，型号{wtg_type},桨叶角最小值{min_angle}'.replace('/','_')
    figure2 = plot_angle_power(dataframe=wtg_data[wtg_data[angle_pn]<5].reset_index(drop=True),wtg=wtg_id,wtg_point_name=wtg_pn,y_point_name=angle_pn,x_point_name=time_pn,\
                    time_point_name=time_pn,point_size=10,style=None,path=None,title=title2,legend_cols=2,color='r',comparison=False,save_figure=False)
    plt.close()
    fig_ls_blade.append(figure1)
    fig_ls_blade_time.append(figure2)
    result_list.append([wtg_id,wtg_type,min_angle])
result_df = pd.DataFrame(result_list)
result_df.columns = ['风机号','风机型号','桨叶角度最小值']
st.write(result_df)
st.markdown('功率-桨叶角度散点图')
col_ls = st.columns(4)
for i,figs in enumerate(fig_ls_blade):
    with col_ls[i%4]:
        st.pyplot(figs)

st.markdown('桨叶角度-时间散点图')
col_ls = st.columns(4)
for i,figs in enumerate(fig_ls_blade_time):
    with col_ls[i%4]:
        st.pyplot(figs)

