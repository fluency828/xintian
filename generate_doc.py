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
from matplotlib import rcParams
# import io
# import zipfile
# from pathlib import Path
from site_function import Kuntouling_mingyang


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

####
site_dictionary = {'昆头岭明阳':Kuntouling_mingyang}
site_model = site_dictionary[phase_name]
####

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
    theory_pw_cur = pd.read_excel('D:/1 新天/数字运营部 任务/昆头岭手动分析/理论功率曲线.xlsx')


ROOT_PATH = st.sidebar.text_input('文件路径')


# st.file_uploader("file path")
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


####
site_instance = site_model(raw_data,theory_pw_cur)
####

st.write('原始数据')
st.write(site_instance.raw_data)
st.markdown('原始数据概况：')
st.write(site_instance.raw_data.describe())
st.markdown(f'原始数据大小为{site_instance.raw_data.shape}')


st.markdown('# 处理限功率点')

st.write('理论功率')
st.write(site_instance.theory_pw_cur)

####
fig_limit_power,size_changing = site_instance.limit_power()
####

st.markdown(f'原始数据、剔除限电后、剔除功率小于等于0后的数据大小分别为{size_changing}')
st.pyplot(fig_limit_power)

st.markdown('## 转矩控制')

####
torque_results_df,torque_fig_ls = site_instance.torque_speed_warning()
####


st.markdown(f'去除转速大于2000后数据大小为{site_instance.torque_speed_data.shape}')
st.write(site_instance.torque_speed_data[[type_pn,site_instance.generator_torque_pn,generator_speed_pn,site_instance.generator_speed_square,]].groupby(type_pn).describe().T)

col_ls = st.columns(4)
for i,figs in enumerate(torque_fig_ls):
    with col_ls[i%4]:
        st.pyplot(figs)

st.markdown('转矩控制斜率结果')
st.write(torque_results_df)

st.markdown('## 偏航对风')

####
yaw_result_df,yaw_angle_hist,yaw_result_list = site_instance.yaw_warning()
####

st.markdown(f'剔除限功率点后数据形状{site_instance.gen_data.shape}')

st.markdown(f'仅保留15°夹角以内数据后的数据大小{site_instance.yaw_data.shape}')

st.write(yaw_result_df)

st.markdown('## 桨叶角度对零')

####
blade_result_df,fig_ls_blade,fig_ls_blade_time,fig_ls_blade_type = site_instance.blade_warning()
####

st.markdown(f'原始数据形状{site_instance.raw_data.shape}')
st.markdown(f'仅保留桨叶角度正常值（剔除缺失值和小于-7，大于100的异常值）的数据大小{site_instance.blade_data.shape}')

col_ls = st.columns(len(fig_ls_blade_type))
for i,figs in enumerate(fig_ls_blade_type):
    with col_ls[i]:
        st.pyplot(figs)

st.write(blade_result_df)
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



# from docx import Document
# import math
# from docx.shared import Inches

# document = Document()
# document.add_heading('3.1 大部件温度', level=2)

# document.add_heading('3.2 控制特性', level=2)


# # 图片地址

# # 向上取整 
# ceil = math.ceil(len(torque_fig_ls)/4)
# # 生成一个ceil行2列的表格,保证表格数量 > 图片数量
# table = document.add_table(rows=ceil, cols=2)

# # 对表格进行枚举
# for i,cell in enumerate(table._cells):
# 	# 这个地方尤其注意 必须先拿到 paragraph 对象 才能run
#     run = cell.add_paragraph().add_run()
#     run.add_picture(torque_fig_ls[i], width=Inches(2.25))

