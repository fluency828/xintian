# import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as figure

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
# from xintian.useful_tools import figs2zip
from xintian.yaw import yaw_result_generate
from xintian.angle_wind import plot_angle_power

class Kuntouling_mingyang():
    def __init__(self,raw_data,theory_pw_cur,
    wtg_pn = '风机',
    time_pn ='时间',
    type_pn = '风机类型',
    P_pn = '平均电网有功功率',
    w_pn = '平均风速',
    angle_pn='平均桨叶角度1a',
    cabin_north_angle = '平均机舱对北角度',
    wind_north_angle = '平均风向对北角度',
    generator_speed_pn = '平均发电机转速1',
    cabin_temp_pn = '平均机舱温度',
    Large_components_temp = ['平均齿轮箱前轴承温度','平均齿轮箱后轴承温度','平均发电机前轴承温度','平均发电机后轴承温度',
                      '平均齿轮箱主轴承温度','平均齿轮箱油温',],
    generator_temp = ['平均发电机绕组温度1','平均发电机绕组温度2','平均发电机绕组温度3','平均发电机绕组温度4','平均发电机绕组温度5','平均发电机绕组温度6'],
    pitch_motor_temp =  ['平均桨叶电机1温度','平均桨叶电机2温度','平均桨叶电机3温度']) -> None:
        self.wtg_pn = wtg_pn
        self.time_pn = time_pn
        self.type_pn = type_pn
        self.P_pn = P_pn
        self.w_pn = w_pn
        self.angle_pn = angle_pn
        self.cabin_north_angle = cabin_north_angle
        self.wind_north_angle = wind_north_angle
        self.generator_speed_pn = generator_speed_pn
        self.generator_speed_square = '平均发电机转速平方'
        self.generator_speed_square_standard = '发电机转速平方(去量纲)'
        self.generator_torque_pn = '平均发电机转矩'
        self.inter_angle = '机舱与风向夹角'
        self.inter_angle_bin = '机舱与风向夹角_bin'
        
        ## 整理原始数据
        self.raw_data = raw_data
        if 'Unnamed: 235' in  self.raw_data.columns:
            self.raw_data = self.raw_data.drop('Unnamed: 235',axis=1)
        self.raw_data[self.time_pn] = pd.to_datetime(self.raw_data[self.time_pn])
        self.wtg_list =self.raw_data[[self.wtg_pn,self.type_pn]].drop_duplicates().reset_index(drop=True)

        ## 理论功率数据
        self.theory_pw_cur = theory_pw_cur


    def gen_full_time(self):
        pass

    def limit_power(self,angle_threshold=3,
                    gap_threshold=0.1,
                    pw_threshold=0,
                    wtg_multi_type=True):
        
        self.gen_data, self.raw_data_1,unlimit_data_size = limit_power_detect_loc(self.raw_data,
                                                     self.theory_pw_cur,
                                                     wtg_pn = self.wtg_pn,
                                                     time_pn = self.time_pn,
                                                     wind_pn = self.w_pn,
                                                     P_pn = self.P_pn,
                                                     blade_angle_pn = self.angle_pn,
                                                     angle_thr = angle_threshold,
                                                     gap_thr = gap_threshold,
                                                     pw_thr = pw_threshold,
                                                     multiple_type = wtg_multi_type)
        
        figure_limit_power = plot_limit_power(self.raw_data_1,
                                              self.gen_data,
                                              self.theory_pw_cur,
                                              x_pn=self.w_pn,
                                              y_pn=self.P_pn)
        size_change = (self.raw_data.shape[0],unlimit_data_size,self.gen_data.shape[0])
        return figure_limit_power,size_change
    

    def torque_speed_warning(self,
                             ticks_x_n = 10,
                             u_bound = [5e4,1e6],
                             l_bound=[5810,1.2e5],
                             r_speed=[240,1056],
                             r_torque=[22,3.9],
                             thre=[0.5,0.2]):
        
        self.torque_speed_data = self.gen_data[abs(self.gen_data[self.generator_speed_pn])<2000].reset_index(drop=True)
        self.torque_speed_data[self.generator_torque_pn] = self.torque_speed_data[self.P_pn] / self.torque_speed_data[self.generator_speed_pn]
        self.torque_speed_data[self.generator_speed_square] = self.torque_speed_data[self.generator_speed_pn]**2
        self.torque_speed_data[self.generator_speed_square_standard] = self.torque_speed_data[self.generator_speed_square]/1e4

        results = []
        torque_fig_ls = []
        for _,wtg_info in self.wtg_list.iterrows():
            wtg_id,types = wtg_info
            wtg_data = self.torque_speed_data[self.torque_speed_data[self.wtg_pn]==wtg_id].reset_index(drop=True)
            t2 = f'{wtg_id}最小二乘拟合,型号{types}'
            if types=='MySE5.0MW':
                k,figure1 = rated_speed_torque(wtg_data,
                                               self.generator_speed_square_standard,
                                               self.generator_torque_pn,
                                               limit_pn=self.generator_speed_square,
                                               title=t2,
                                               path=None,
                                               x_ticks_n=ticks_x_n,
                                               upper=u_bound[0],
                                               lower=l_bound[0],
                                               rated_speed=r_speed[0],
                                               rated_torque=r_torque[0],
                                               outlier_thre=thre[0],
                                               save_figure=False)
            elif types=='MySE4.0MW':
                k,figure1 = rated_speed_torque(wtg_data,
                                               self.generator_speed_square_standard,
                                               self.generator_torque_pn,
                                               limit_pn=self.generator_speed_square,
                                               title=t2,
                                               path=None,
                                               x_ticks_n=ticks_x_n,
                                               upper=u_bound[1],
                                               lower=l_bound[1],
                                               rated_speed=r_speed[1],
                                               rated_torque=r_torque[1],
                                               outlier_thre=thre[1],
                                               save_figure=False)
            results.append([wtg_id,types,k])
            torque_fig_ls.append(figure1)

        torque_results_df = pd.DataFrame(results)
        torque_results_df.columns=['风机号','风机型号','斜率']
        return torque_results_df,torque_fig_ls

    def yaw_warning(self):
        self.yaw_data = self.gen_data
        self.yaw_data['dif'] = self.gen_data[self.wind_north_angle]-self.gen_data[self.cabin_north_angle]
        self.yaw_data[self.inter_angle] = np.where(self.yaw_data['dif']>180,360-self.yaw_data['dif'],self.yaw_data['dif'])
        self.yaw_data[self.inter_angle] = np.where(self.yaw_data[self.inter_angle]<-180,-360-self.yaw_data[self.inter_angle],self.yaw_data[self.inter_angle])
        self.yaw_data = self.yaw_data[(self.yaw_data[self.inter_angle]>=-15.25)&(self.yaw_data[self.inter_angle]<=15.25)].reset_index(drop=True)
        bs2 = np.arange(-15.5,16,1)
        ls2 = np.arange(-15,16,1)
        self.yaw_data[self.inter_angle_bin] = pd.cut(self.yaw_data[self.inter_angle],bins=bs2,right=False,labels=ls2).astype('float64')
        figure_yaw_angle_hist = plot_yaw_angle(self.yaw_data,self.inter_angle_bin)
        self.yaw_data['P_th'] = self.yaw_data['P_th_bin']/((self.yaw_data['V_bin']/self.yaw_data[self.w_pn])**3)
        yaw_result_df,wtg_result_list = yaw_result_generate(self.wtg_list,
                                                            self.yaw_data,
                                                            self.inter_angle_bin,
                                                            self.angle_pn,
                                                            wtg_pn=self.wtg_pn,
                                                            P_pn=self.P_pn)
        
        return yaw_result_df,figure_yaw_angle_hist,wtg_result_list

    def blade_warning(self,point_s=10,point_c='r'):
        self.blade_data = self.raw_data[(self.raw_data[self.angle_pn]>-7)&(self.raw_data[self.angle_pn]<100)].reset_index(drop=True)
        fig_ls_blade_type = []
        for wtg_type in np.unique(self.wtg_list[self.type_pn]):
            use_data = self.blade_data[self.blade_data[self.type_pn]==wtg_type].reset_index(drop=True)
            figure = plot_blade_power_all(use_data,
                                          blade_pn=self.angle_pn,
                                          Pw_pn=self.P_pn,
                                          title=f'{wtg_type}功率-桨叶角度散点图')
            fig_ls_blade_type.append(figure)

        fig_ls_blade = []
        fig_ls_blade_time = []
        result_list=[]
        for _,wtg_info in self.wtg_list.iterrows():
            wtg_id,wtg_type = wtg_info
            wtg_data = self.blade_data[self.blade_data[self.wtg_pn]==wtg_id].reset_index(drop=True)
            # save_path = ROOT_PATH +f'桨叶角度/{title1}.jpg'
            min_angle = wtg_data[self.angle_pn].min()
            title1 = f'{wtg_id}风机有功功率-桨叶角度散点图，型号{wtg_type},桨叶角最小值{min_angle}'.replace('/','_')
            figure1 = plot_angle_power(dataframe=wtg_data[wtg_data[self.angle_pn]<5].reset_index(drop=True),
                                       wtg=wtg_id,
                                       wtg_point_name=self.wtg_pn,
                                       y_point_name=self.P_pn,
                                       x_point_name=self.angle_pn,
                                       time_point_name=self.time_pn,
                                       point_size=point_s,
                                       style=None,
                                       path=None,
                                       title=title1,
                                       legend_cols=2,
                                       color=point_c,
                                       comparison=False,
                                       save_figure=False)
            title2 = f'{wtg_id}风机桨叶角度-时间散点图，型号{wtg_type},桨叶角最小值{min_angle}'.replace('/','_')
            figure2 = plot_angle_power(dataframe=wtg_data[wtg_data[self.angle_pn]<5].reset_index(drop=True),
                                       wtg=wtg_id,
                                       wtg_point_name=self.wtg_pn,
                                       y_point_name=self.angle_pn,
                                       x_point_name=self.time_pn,
                                       time_point_name=self.time_pn,
                                       point_size=point_s,
                                       style=None,
                                       path=None,
                                       title=title2,
                                       legend_cols=2,
                                       color=point_c,
                                       comparison=False,
                                       save_figure=False)
            fig_ls_blade.append(figure1)
            fig_ls_blade_time.append(figure2)
            result_list.append([wtg_id,wtg_type,min_angle])
        blade_result_df = pd.DataFrame(result_list)
        blade_result_df.columns = ['风机号','风机型号','桨叶角度最小值']
        return blade_result_df,fig_ls_blade,fig_ls_blade_time,fig_ls_blade_type

    def save_figures(self,path,figure,filename):
        if not os.path.exists(path):
            os.makedirs(path)
        save_path = os.path.join(path,filename)
        figure.savefig(save_path,bbox_inches='tight',dpi=500,facecolor='white')
    def save_data(self,path,data,filename):
        if not os.path.exists(path):
            os.makedirs(path)
        save_path = os.path.join(path,filename)
        data.to_excel(save_path,index=False)



####################### test #####################
# ROOT_PATH = 'D:/1 新天\数字运营部 任务\昆头岭手动分析/12月/'
# raw_data_path = ROOT_PATH+'raw_data.csv'
# raw_df = pd.read_csv(raw_data_path)
# theory_cur_df = pd.read_excel('D:/1 新天/数字运营部 任务/昆头岭手动分析/理论功率曲线.xlsx')
# raw_df_11 = pd.read_csv('D:/1 新天\数字运营部 任务\昆头岭手动分析/11月/raw_data.csv')



# kuitonggou_instance = kuitonggou_jinfeng(raw_df_11,theory_cur_df)
# fig_limit_power,size_changing = kuitonggou_instance.limit_power()
# torque_results_df,torque_fig_ls = kuitonggou_instance.torque_speed_warning()
# yaw_result_df,yaw_angle_hist,yaw_result_list = kuitonggou_instance.yaw_warning()
# blade_result_df,fig_ls_blade,fig_ls_blade_time,fig_ls_blade_type = kuitonggou_instance.blade_warning()


