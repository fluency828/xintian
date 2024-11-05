import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import os
import matplotlib.dates as mdate

# import io
# import zipfile
# from pathlib import Path
from functions.site_function import Kuntouling_mingyang,kuitonggou_jinfeng,kangzhuang_yunda,RuoQiang_yuanjing,Kuntouling_jinfeng,Guanyun_mingyang_3200,Guanyun_mingyang_4000
from functions.utils import save_data,save_figures

import io
import openpyxl
from functions.gen_docx import gen_document
# import math
# print(math.version)
from matplotlib import rcParams
import matplotlib as mpl
import json
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

phase_name = st.sidebar.selectbox(
    label='请输入您选择的风场',
    options=('昆头岭明阳(大数据平台导出)',
             '昆头岭明阳(风场导出)',
             '康庄运达',
             '魁通沟金风四期',
             '魁通沟金风五六期',
             '若羌三期远景',
             '昆头岭金风',
             '灌云明阳3.2',
             '灌云明阳4.0'),
    help='不同风场可能对应不同的数据格式和测点名称')
st.markdown('# 查看原始数据')
####
site_dictionary = {'昆头岭明阳(大数据平台导出)':Kuntouling_mingyang,
                   '昆头岭明阳(风场导出)':Kuntouling_mingyang,
                   '魁通沟金风四期':kuitonggou_jinfeng,
                   '魁通沟金风五六期':kuitonggou_jinfeng,
                   '康庄运达':kangzhuang_yunda,
                   '若羌三期远景':RuoQiang_yuanjing,
                   '昆头岭金风':Kuntouling_jinfeng,
                   '灌云明阳3.2':Guanyun_mingyang_3200,
                    '灌云明阳4.0':Guanyun_mingyang_4000,
                   }
site_model = site_dictionary[phase_name]

raw_data_path = st.sidebar.file_uploader('上传原始数据')

def load_data(url):
    df = pd.read_csv(url)
    return df
if raw_data_path is not None:
    raw_data = load_data(raw_data_path)
else:
    raw_data = load_data('eg_data/raw_data.csv')

if phase_name=='昆头岭明阳(风场导出)' or phase_name=='昆头岭明阳(大数据平台导出)':
    pw_cur_path = 'pw_theory_cur/昆头岭明阳理论功率曲线.xlsx'
    thr_path = './error_threshold/昆头岭明阳故障阈值.xlsx'
    json_path = 'point_name/昆头岭明阳(大数据平台导出)测点.json' if phase_name=='昆头岭明阳(大数据平台导出)' else 'point_name/昆头岭明阳(风场导出)测点.json'
elif phase_name=='康庄运达':
    pw_cur_path = 'pw_theory_cur/康庄运达理论功率曲线.xlsx'
    thr_path = './error_threshold/康庄运达故障阈值.xlsx'
    json_path = 'point_name/康庄运达测点.json'
elif (phase_name=='魁通沟金风四期') or (phase_name == '魁通沟金风五六期'):
    pw_cur_path = 'pw_theory_cur/魁通沟金风理论功率曲线.xlsx'
    thr_path = './error_threshold/魁通沟金风四期故障阈值.xlsx' if phase_name == '魁通沟金风四期' else './error_threshold/魁通沟金风五六期故障阈值.xlsx'
    json_path = 'point_name/魁通沟金风四期测点.json' if phase_name == '魁通沟金风四期' else 'point_name/魁通沟金风五六期测点.json'

elif phase_name == '若羌三期远景':
    pw_cur_path = 'pw_theory_cur/若羌三期远景理论功率曲线.xlsx'
    thr_path = './error_threshold/若羌三期远景故障阈值.xlsx'
    json_path = 'point_name/若羌三期远景测点.json'

elif phase_name == '昆头岭金风':
    pw_cur_path = 'pw_theory_cur/昆头岭金风理论功率曲线.xlsx'
    thr_path = './error_threshold/昆头岭金风故障阈值.xlsx'
    json_path = 'point_name/昆头岭金风测点.json'

elif phase_name == '灌云明阳3.2':
    pw_cur_path = 'pw_theory_cur/灌云明阳3.2理论功率曲线.xlsx'
    thr_path = './error_threshold/灌云明阳3.2故障阈值.xlsx'
    json_path = 'point_name/灌云明阳3.2测点.json'

elif phase_name == '灌云明阳4.0':
    pw_cur_path = 'pw_theory_cur/灌云明阳4.0理论功率曲线.xlsx'
    thr_path = './error_threshold/灌云明阳4.0故障阈值.xlsx'
    json_path = 'point_name/灌云明阳4.0测点.json'

if not (os.path.exists(pw_cur_path)) :
    pw_cur_path = st.sidebar.file_uploader('上传理论功率数据')

if not (os.path.exists(json_path)) :
    json_path = st.sidebar.file_uploader('上传测点配置JSON文件',type='json')
    pn_dictionary = json.loads(json_path.read())
else:
    f = open(json_path, 'r')
    content = f.read()
    pn_dictionary = json.loads(content)


theory_pw_cur = pd.read_excel(pw_cur_path)
# st.write(raw_data['变流器转矩设定值'])
# print(site_model.print_attribute)
pn_dictionary['raw_data'] = raw_data
pn_dictionary['theory_pw_cur'] = theory_pw_cur
####
site_instance = site_model(**pn_dictionary)
####

del raw_data,theory_pw_cur,pn_dictionary

col_ls = st.columns(2)
with col_ls[0]:
    st.write('原始数据')
    st.write(site_instance.raw_data)
with col_ls[1]:
    st.markdown('原始数据概况：')
    st.write(site_instance.raw_data.describe())

st.markdown(f'原始数据大小为{site_instance.raw_data.shape}')

col_ls = st.columns(2)
with col_ls[0]:
    st.markdown('wtg list')
    st.write(site_instance.wtg_list)
with col_ls[1]:
    st.markdown('各风机原始数据概况')
    st.write(site_instance.raw_data.groupby(site_instance.wtg_pn).describe())

st.markdown('## 风速-功率其基本情况查看')
pw_wind_fig_ls = site_instance.gen_pw_wind()
col_ls = st.columns(4)
for i,figs in enumerate(pw_wind_fig_ls):
    with col_ls[i%4]:
        st.pyplot(figs)

del pw_wind_fig_ls

st.markdown('# 处理限功率点')

st.write('理论功率')
st.write(site_instance.theory_pw_cur)

####
fig_limit_power,size_changing = site_instance.limit_power()
####

st.markdown(f'原始数据、剔除限电后、剔除功率小于等于0后的数据大小分别为{size_changing}')
st.pyplot(fig_limit_power)

col_ls = st.columns(2)
with col_ls[0]:
    st.markdown('标记限电后的数据')
    st.write(site_instance.raw_data_1)
with col_ls[1]:
    st.markdown('各风机去除限电后数据情况')
    st.write(site_instance.gen_data.groupby(site_instance.wtg_pn).describe())


def to_excel(df):
    output = io.BytesIO()
    df.to_csv(output, index=False)
    processed_data = output.getvalue()
    output.close()
    return processed_data
df_csv = to_excel(site_instance.raw_data_1)
st.download_button(label='📥 下载标记限电后的数据',
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
yaw_result_df,yaw_angle_hist,yaw_angle_power_scatter,yaw_result_list = site_instance.yaw_warning()
####

# st.pyplot(yaw_angle_power_scatter)

st.markdown(f'剔除限功率点后数据形状{site_instance.gen_data.shape}')

st.markdown(f'仅保留15°夹角以内数据后的数据大小{site_instance.yaw_data.shape}')

st.write(yaw_result_df)

del site_instance.yaw_data

st.markdown('# 桨叶角度对零')
if_compare = st.selectbox('是否与同型号所有风机比较',options=[True,False,])
col_ls = st.columns(2)
with col_ls[0]:
    blade_lo = st.slider('选择桨叶角度图的最小值',-10,5,-2,1)
with col_ls[1]:
    blade_up = st.slider('选择桨叶角度的最大值',5,20,10,1)

####
blade_result_df,fig_ls_blade,fig_ls_blade_time,fig_ls_blade_type = site_instance.blade_warning(compare=if_compare)
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
# st.write(f'thr_path{thr_path}')

site_instance.set_error_threshold(path = thr_path)
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
st.markdown(f'有 {len(Large_components_fig_single )} 台风机温度异常')
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
            #  yaw_result_df,
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


