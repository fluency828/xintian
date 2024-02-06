import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import os
import matplotlib.dates as mdate
from matplotlib import rcParams
# import io
# import zipfile
# from pathlib import Path
from site_function import Kuntouling_mingyang
from utils import save_data,save_figures
import matplotlib as mpl
import io

mpl.font_manager.fontManager.addfont('字体/SIMSUN.ttf')
config = {
    "font.family":'serif',
    # "font.size": 20,
    "mathtext.fontset":'stix',
    "font.serif": ['SIMSUN'],
}
rcParams.update(config)
plt.rcParams['axes.unicode_minus'] = False



########################## 正式开始网页！###################
st.title('风场数据分析报告')
st.markdown('# 查看原始数据')
phase_name = st.sidebar.selectbox(
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


# ROOT_PATH = st.sidebar.text_input('文件路径')
# raw_data_path = ROOT_PATH + st.sidebar.selectbox(label='选择原始数据文件',
#                            options=os.listdir(ROOT_PATH))
# pw_cur_path = 'pw_theory_cur/'+st.sidebar.selectbox(label='选择理论功率数据文件',
#                            options=os.listdir('pw_theory_cur/'))

raw_data_path = st.sidebar.file_uploader('上传原始数据')
pw_cur_path = st.sidebar.file_uploader('上传理论功率数据')

# @st.cache_data
def load_data(url):
    df = pd.read_csv(url)
    return df
if raw_data_path is not None:
    raw_data = load_data(raw_data_path)
else:
    raw_data = load_data('D:/1 新天\数字运营部 任务\昆头岭手动分析/24年1月/raw_data.csv')
theory_pw_cur = pd.read_excel(pw_cur_path if pw_cur_path else 'pw_theory_cur\昆头岭明阳理论功率曲线.xlsx')


####
site_instance = site_model(raw_data,theory_pw_cur)
####

del raw_data,theory_pw_cur

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

st.markdown('# 转矩控制')

####
torque_results_df,torque_fig_ls = site_instance.torque_speed_warning()
####


st.markdown(f'去除转速大于2000后数据大小为{site_instance.torque_speed_data.shape}')
st.write(site_instance.torque_speed_data[[type_pn,
                                          site_instance.generator_torque_pn,
                                          generator_speed_pn,
                                          site_instance.generator_speed_square,]].groupby(type_pn).describe().T)

col_ls = st.columns(4)
for i,figs in enumerate(torque_fig_ls):
    with col_ls[i%4]:
        st.pyplot(figs)

st.markdown('转矩控制斜率结果')
st.write(torque_results_df)

st.markdown('# 偏航对风')

####
yaw_result_df,yaw_angle_hist,yaw_result_list = site_instance.yaw_warning()
####

st.markdown(f'剔除限功率点后数据形状{site_instance.gen_data.shape}')

st.markdown(f'仅保留15°夹角以内数据后的数据大小{site_instance.yaw_data.shape}')

st.write(yaw_result_df)

st.markdown('# 桨叶角度对零')

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

#####
site_instance.full_time()
all_data = site_instance.get_all_data()
site_instance.set_error_threshold()
################################
st.markdown('# 满发后大部件温度预警')
st.markdown('all data')
st.write(site_instance.all_data.describe())



st.markdown('error threshold')
st.write(site_instance.scene_df)

if_n = st.selectbox('是否带文字标注',options=[True,False])

generate = st.button('生成图片')
st.markdown('full power data')
# st.write(site_instance.full_pw)

Large_components_fig = site_instance.gen_Large_components_temp(if_notation=if_n)
col_ls = st.columns(2)
for i,figs in enumerate(Large_components_fig):
    with col_ls[i%2]:
        st.pyplot(figs)

#################################
st.markdown('# 满发后发电机绕组温度预警')
# st.write(site_instance.full_pw)

generator_temp_fig = site_instance.gen_generator_Temp()
st.markdown(f'有 {len(generator_temp_fig)} 台风机发电机绕组温度对比异常')
col_ls = st.columns(4)
for i,figs in enumerate(generator_temp_fig):
    with col_ls[i%4]:
        st.pyplot(figs)

#################################
st.markdown('# 变桨电机温度预警')
# st.write(site_instance.full_pw)

pitch_motor_temp_fig = site_instance.gen_pitch_motor_Temp()
st.markdown(f'有 {len(pitch_motor_temp_fig)} 台风机变桨电机温度对比异常')
col_ls = st.columns(4)
for i,figs in enumerate(pitch_motor_temp_fig):
    with col_ls[i%4]:
        st.pyplot(figs)

from xintian.gen_docx import gen_document


st.markdown('# 最后生成word文档')
Doc = gen_document(site_instance,
             Large_components_fig,
             generator_temp_fig,
             pitch_motor_temp_fig,
             torque_fig_ls,
             yaw_result_df,
             fig_ls_blade,
             fig_ls_blade_time
             )
word = Doc.document
st.markdown('文档生成成功了！')

bio = io.BytesIO()
word.save(bio)
if word:
    st.download_button(
        label = '点击下载word文件',
        data = bio.getvalue(),
        file_name = f'{phase_name}.docx',
        mime = 'docx'
    )




# save = st.button('save_all_results')
# if save:
#     save_figures(ROOT_PATH+'limit_power/',fig_limit_power,'limit_power.png')
#     save_data(ROOT_PATH+'转矩控制/',torque_results_df,'斜率结果.xlsx')
#     for i,fig in enumerate(torque_fig_ls):
#         save_figures(ROOT_PATH+'转矩控制/',fig,f'{i}.jpg')
#     save_data(ROOT_PATH+'偏航对风/',yaw_result_df,'预警结果.xlsx')
#     save_data(ROOT_PATH+'桨叶角度/',blade_result_df,'桨叶角度最小值.xlsx')
#     for i,fig in enumerate(fig_ls_blade):
#         save_figures(ROOT_PATH+f'桨叶角度/',fig,f'功率-桨叶角度{i}.jpg')
#         save_figures(ROOT_PATH+'桨叶角度/',fig_ls_blade_time[i],f'桨叶角度-时间{i}.jpg')


