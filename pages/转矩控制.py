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

# st.header('转矩控制')
st.set_page_config(page_title='转矩控制')

if 'phase_name' not in st.session_state:
    st.session_state['phase_name'] = '昆头岭明阳'

site_dictionary = {'昆头岭明阳':Kuntouling_mingyang}
site_model = site_dictionary[st.session_state.phase_name]

for ss in ['raw_data','theory_pw_cur']:
    if ss not in st.session_state:
        st.session_state[ss]=''


if 'instance' not in st.session_state:
    st.session_state['instance'] = site_model(st.session_state.raw_data,st.session_state.theory_pw_cur)


site_instance = st.session_state.instance


####
torque_results_df,torque_fig_ls = st.session_state.instance.torque_speed_warning()
####

st.markdown(f'去除转速大于2000后数据大小为{st.session_state.instance.torque_speed_data.shape}')


saved = st.button('save')

if saved:
    st.session_state.instance = site_instance

# st.session_state.torque_data = site_instance.torque_speed_data
st.session_state.torque_result_df =  torque_results_df
st.session_state.torque_fig_ls = torque_fig_ls

col_ls = st.columns(4)
for i,figs in enumerate(st.session_state.torque_fig_ls):
    with col_ls[i%4]:
        st.pyplot(figs)

st.markdown('转矩控制斜率结果')
st.write(st.session_state.torque_results_df)
st.button('rerun')

