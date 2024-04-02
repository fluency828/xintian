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
from site_function import Kuntouling_mingyang,kuitonggou_jinfeng,kangzhuang_yunda
from utils import save_data,save_figures
import matplotlib as mpl
import io
import openpyxl
from xintian.gen_docx import gen_document
# import math
# print(math.version)

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
    options=('昆头岭明阳',
             '康庄运达',
             '魁通沟金风四期',
             '魁通沟金风五六期'),
    help='不同风场可能对应不同的数据格式和测点名称')

####
site_dictionary = {'昆头岭明阳':Kuntouling_mingyang,
                   '魁通沟金风四期':kuitonggou_jinfeng,
                   '魁通沟金风五六期':kuitonggou_jinfeng,
                   '康庄运达':kangzhuang_yunda,
                   }
site_model = site_dictionary[phase_name]
####

if phase_name=='昆头岭明阳':
    # pn_dictionary = {
    #     'phase_name':phase_name,
    #     'wtg_pn':'风机',
    #     'time_pn':'时间',
    #     'type_pn':'风机类型',
    #     'P_pn':'平均电网有功功率',
    #     'w_pn':'平均风速',
    #     'angle_pn':'平均桨叶角度1a',
    #     'cabin_north_angle':'平均机舱对北角度',
    #     'wind_north_angle':'平均风向对北角度',
    #     'generator_speed_pn':'平均发电机转速1',
    #     'cabin_temp_pn':'平均机舱温度',
    #     'Large_components_temp' : ['平均齿轮箱前轴承温度','平均齿轮箱后轴承温度','平均发电机前轴承温度','平均发电机后轴承温度',
    #                 '平均齿轮箱主轴承温度','平均齿轮箱油温',],
    #     'generator_temp' : ['平均发电机绕组温度1','平均发电机绕组温度2','平均发电机绕组温度3','平均发电机绕组温度4','平均发电机绕组温度5','平均发电机绕组温度6'],
    #     'pitch_motor_temp' : ['平均桨叶电机1温度','平均桨叶电机2温度','平均桨叶电机3温度']
    # }
    pn_dictionary = {
        'phase_name':phase_name,
        'wtg_pn':'device_name',
        'time_pn':'data_time',
        'type_pn':'风机类型',
        'P_pn':'发电机有功功率',
        'w_pn':'风速',
        'angle_pn':'桨叶角度1B',
        'cabin_north_angle':'机舱对北角度',
        'wind_north_angle':'风向对北角度',
        'generator_speed_pn':'发电机转速',
        'cabin_temp_pn':'舱内温度',
        'Large_components_temp' : ['齿轮箱前轴承温度','齿轮箱后轴承温度','发电机驱动端轴承温度','发电机非驱动端轴承温度',
                     '齿轮箱主轴承温度', '齿轮箱油池温度',],
        'generator_temp' : ['发电机绕组温度1', '发电机绕组温度2', '发电机绕组温度3', '发电机绕组温度4', '发电机绕组温度5', '发电机绕组温度6'],
        'pitch_motor_temp' : ['1号桨电机温度', '2号桨电机温度', '3号桨电机温度']
    }  
elif phase_name=='魁通沟金风四期':
    pn_dictionary = {
        'phase_name':phase_name,
        'wtg_pn':'device_id',
        'time_pn':'data_time',
        'type_pn':'风机类型',
        'P_pn':'发电机有功功率',
        'w_pn':'风速',
        'angle_pn':'桨叶片角度1',
        'inter_angle_pn':'机舱与风向夹角',
        'generator_speed_pn':'发电机转速瞬时值',
        'blade_dif_pn':'blade_dif',
        'cabin_temp_pn':'舱内温度',
        'Large_components_temp' : ['发电机驱动端轴承温度', '发电机非驱动端轴承温度',],
        'generator_temp' : ['发电机绕组温度1','发电机绕组温度2', '发电机绕组温度3', '发电机绕组温度4',
        '发电机绕组温度5', '发电机绕组温度6', '发电机绕组温度7', '发电机绕组温度8', '发电机绕组温度9','发电机绕组温度10',
        '发电机绕组温度11', '发电机绕组温度12'],
        'pitch_motor_temp' : ['1号变桨电机温度', '2号变桨电机温度','3号变桨电机温度']
    }
elif phase_name == '魁通沟金风五六期':
    pn_dictionary = {
        'phase_name':phase_name,
        'wtg_pn':'device_id',
        'time_pn':'data_time',
        'type_pn':'风机类型',
        'P_pn':'发电机有功功率',
        'w_pn':'风速',
        'angle_pn':'桨叶片角度1',
        'inter_angle_pn':'机舱与风向夹角',
        'generator_speed_pn':'发电机转速瞬时值',
        'blade_dif_pn':'blade_dif',
        'cabin_temp_pn':'舱内温度',
        'Large_components_temp' : ['发电机前轴承外圈温度','发电机后轴承外圈温度', '发电机前轴承内圈温度', '发电机后轴承内圈温度'],
        'generator_temp' : ['发电机绕组温度最大值',],
        'pitch_motor_temp' : ['1号变桨电机温度', '2号变桨电机温度','3号变桨电机温度']
    }
elif phase_name == '康庄运达':
    pn_dictionary = {
        'phase_name':phase_name,
        'wtg_pn':'device_name',
        'time_pn':'data_time',
        'type_pn':'风机类型',
        'P_pn':'发电机有功功率',
        'generator_speed_pn':'发电机转速',
        'generator_torque_pn':'变流器转矩反馈',
        'w_pn':'风速',
        'angle_pn':'桨叶片角度1',
        'inter_angle_pn':'对风误差',
        'cabin_temp_pn':'舱内温度',
        'Large_components_temp' : ['主轴承温度','齿轮箱油池温度','齿轮箱高速轴驱动端轴承温度','齿轮箱高速轴非驱动端轴承温度','发电机驱动端轴承温度', '发电机非驱动端轴承温度', ],
        'generator_temp' : ['发电机定子U相线圈温度', '发电机定子V相线圈温度','发电机定子W相线圈温度'],
        'pitch_motor_temp' : ['1号变桨电机温度', '2号变桨电机温度','3号变桨电机温度']        
    }

# ROOT_PATH = st.sidebar.text_input('文件路径')
# raw_data_path = ROOT_PATH + st.sidebar.selectbox(label='选择原始数据文件',
#                            options=os.listdir(ROOT_PATH))
# pw_cur_path = 'pw_theory_cur/'+st.sidebar.selectbox(label='选择理论功率数据文件',
#                            options=os.listdir('pw_theory_cur/'))

raw_data_path = st.sidebar.file_uploader('上传原始数据')
# pw_cur_path = st.sidebar.file_uploader('上传理论功率数据')

# @st.cache_data
def load_data(url):
    df = pd.read_csv(url)
    return df
if raw_data_path is not None:
    raw_data = load_data(raw_data_path)
else:
    raw_data = load_data('eg_data/raw_data.csv')

if phase_name=='昆头岭明阳':
    pw_cur_path = 'pw_theory_cur/昆头岭明阳理论功率曲线.xlsx'
elif phase_name=='康庄运达':
    pw_cur_path = 'pw_theory_cur/康庄运达理论功率曲线.xlsx'
elif (phase_name=='魁通沟金风四期') or (phase_name == '魁通沟金风五六期'):
    pw_cur_path = 'pw_theory_cur/魁通沟金风理论功率曲线.xlsx'
else:
    pw_cur_path = st.sidebar.file_uploader('上传理论功率数据')

theory_pw_cur = pd.read_excel(pw_cur_path if pw_cur_path else 'pw_theory_cur/昆头岭明阳理论功率曲线.xlsx')

# print(site_model.print_attribute)
pn_dictionary['raw_data'] = raw_data
pn_dictionary['theory_pw_cur'] = theory_pw_cur
####
site_instance = site_model(**pn_dictionary)
####

del raw_data,theory_pw_cur,pn_dictionary

st.write('原始数据')
st.write(site_instance.raw_data)
st.markdown('原始数据概况：')
st.write(site_instance.raw_data.describe())
st.markdown(f'原始数据大小为{site_instance.raw_data.shape}')
st.markdown('wtg list')
st.write(site_instance.wtg_list)

st.markdown('# 处理限功率点')

st.write('理论功率')
st.write(site_instance.theory_pw_cur)

####
fig_limit_power,size_changing = site_instance.limit_power()
####

st.markdown(f'原始数据、剔除限电后、剔除功率小于等于0后的数据大小分别为{size_changing}')
st.pyplot(fig_limit_power)

st.markdown('剔除限电后的数据')
st.write(site_instance.raw_data_1)

def to_excel(df):
    output = io.BytesIO()
    df.to_csv(output, index=False)
    processed_data = output.getvalue()
    output.close()
    return processed_data
df_csv = to_excel(site_instance.raw_data_1)
st.download_button(label='📥 Download Current Result',
                                data=df_csv,
                                file_name= 'raw_data_1.csv')



st.markdown('# 转矩控制')

####
torque_results_df,torque_fig_ls = site_instance.torque_speed_warning()
####


st.markdown(f'去除转速大于2000后数据大小为{site_instance.torque_speed_data.shape}')
st.write(site_instance.torque_speed_data[[site_instance.type_pn,
                                          site_instance.generator_torque_pn,
                                          site_instance.generator_speed_pn,
                                          site_instance.generator_speed_square,]].groupby(site_instance.type_pn).describe().T)

col_ls = st.columns(4)
for i,figs in enumerate(torque_fig_ls):
    with col_ls[i%4]:
        st.pyplot(figs)

st.markdown('转矩控制斜率结果')
st.write(torque_results_df)

del size_changing,site_instance.torque_speed_data

st.markdown('# 偏航对风')

####
yaw_result_df,yaw_angle_hist,yaw_result_list = site_instance.yaw_warning()
####

st.markdown(f'剔除限功率点后数据形状{site_instance.gen_data.shape}')

st.markdown(f'仅保留15°夹角以内数据后的数据大小{site_instance.yaw_data.shape}')

st.write(yaw_result_df)

del site_instance.yaw_data

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
del site_instance.blade_data

#####
site_instance.full_time()
all_data = site_instance.get_all_data()
site_instance.set_error_threshold()
################################
st.markdown('# 满发后大部件温度预警')
st.markdown('all data')
st.write(site_instance.all_data)

def to_excel(df):
    output = io.BytesIO()
    df.to_csv(output, index=False)
    processed_data = output.getvalue()
    output.close()
    return processed_data
df_csv = to_excel(site_instance.all_data)
st.download_button(label='📥 Download Current Result',
                                data=df_csv,
                                file_name= 'all_data.csv')


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

##################################

st.markdown('# 大部件文件预警（非满发）')
# st.write(site_instance.full_pw)
if_verbose = st.selectbox('是否标明详细情况',options=[False,True,])
Large_components_fig_single = site_instance.gen_Large_components_temp_single(if_notation=if_verbose)
st.markdown(f'有 {len(Large_components_fig_single )} 台风机发电机绕组温度对比异常')
col_ls = st.columns(4)
for i,figs in enumerate(Large_components_fig_single ):
    with col_ls[i%4]:
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



del yaw_result_list,site_instance.raw_data,site_instance.gen_data,site_instance.all_data,df_csv
st.markdown('# 最后生成word文档')
Doc = gen_document(site_instance,
             Large_components_fig,
             Large_components_fig_single,
             generator_temp_fig,
             pitch_motor_temp_fig,
             torque_fig_ls,
             yaw_result_df,
             fig_ls_blade,
             fig_ls_blade_time
             )
del site_instance,Large_components_fig,Large_components_fig_single,generator_temp_fig,pitch_motor_temp_fig,torque_fig_ls,yaw_result_df,fig_ls_blade,fig_ls_blade_time
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


