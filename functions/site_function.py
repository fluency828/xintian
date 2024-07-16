# import streamlit as st
import numpy as np
import pandas as pd
# import matplotlib.pyplot as figure

import sys
# sys.path.append('D:/OneDrive - CUHK-Shenzhen/utils/')
# from functions.full_power_time import gen_full_time
# from functions.Temp_warning import plot_scene,plotly_scene,plot_comparison_divide
# import plotly.express as px
import os
import matplotlib.dates as mdate
import sys
# sys.path.append('D:/OneDrive - CUHK-Shenzhen/utils/')
from functions.power_limited import limit_power_detect_loc,limit_power_detect_loc_Goldwind
from functions.plotly_functions import plot_limit_power,plot_yaw_angle,plot_blade_power_all,plot_yaw_scatter
from matplotlib import rcParams
from functions.Speed_Torque import rated_speed_torque
# from functions.useful_tools import figs2zip
from functions.yaw import yaw_result_generate
from functions.angle_wind import plot_angle_power
from functions.Temp_warning import plot_scene,plot_comparison_divide,plot_single_scene
from functions.full_power_time import gen_full_time

class Kuntouling_mingyang():
    def __init__(self,raw_data,theory_pw_cur,
    phase_name = '昆头岭明阳',
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
        self.cabin_temp_pn = cabin_temp_pn
        self.Large_components_temp_ls = Large_components_temp
        self.generator_temp_ls = generator_temp
        self.pitch_motor_temp_ls = pitch_motor_temp

        self.generator_speed_pn = generator_speed_pn
        self.generator_speed_square = '平均发电机转速平方'
        self.generator_speed_square_standard = '发电机转速平方(去量纲)'
        self.generator_torque_pn = '平均发电机转矩'
        self.inter_angle_pn = '机舱与风向夹角'
        self.inter_angle_bin = '机舱与风向夹角_bin'
        self.full_time_pn = 'full_time'
        self.wind_pn_bin = '风速_bin'


        ## 整理原始数据
        self.raw_data = raw_data[[self.wtg_pn,
                                  self.time_pn,
                                  self.type_pn,
                                  self.P_pn,
                                  self.w_pn,
                                  self.angle_pn,
                                  self.cabin_north_angle,
                                  self.wind_north_angle,
                                  self.generator_speed_pn,
                                  self.cabin_temp_pn,
                                    ]+self.Large_components_temp_ls+
                                    self.generator_temp_ls+
                                    self.pitch_motor_temp_ls]
        if 'Unnamed: 235' in  self.raw_data.columns:
            self.raw_data = self.raw_data.drop('Unnamed: 235',axis=1)
        self.raw_data[self.time_pn] = pd.to_datetime(self.raw_data[self.time_pn])
        self.wtg_list =self.raw_data[[self.wtg_pn,self.type_pn]].drop_duplicates().reset_index(drop=True)

        ## 理论功率数据
        self.theory_pw_cur = theory_pw_cur


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
    
    def full_time(self,
                  pw_diff_threshold=[1000,1000],
                  type_ls = ['MySE4.0MW','MySE5.0MW'], 
                  rated_pw_ls = [4000,5000,]):
        all_wtg = []
        for _,wtg_info in self.wtg_list.iterrows():
            # print(wtg_info)
            wtg,type = wtg_info
            wtg_dataframe = self.raw_data[self.raw_data[self.wtg_pn]==wtg].reset_index(drop=True).sort_values(by=self.time_pn)
            for j in range(len(type_ls)):
                if type_ls[j] == type:
                    df_ft = gen_full_time(wtg_dataframe,
                                          threshold = pw_diff_threshold[j],
                                          full_pw=rated_pw_ls[j],
                                          time_pn = self.time_pn,
                                          Pw_pn = self.P_pn,
                                          full_time_pn=self.full_time_pn)
                    all_wtg.append(df_ft)

        self.all_data = pd.concat(all_wtg,axis=0)


    def get_all_data(self,):
        scene_list = self.Large_components_temp_ls + self.generator_temp_ls
        for scene in scene_list:
            self.all_data[f'{scene}温升({scene}-舱内温度)'.replace('温度温升','温升')] = self.all_data[scene] - self.all_data[self.cabin_temp_pn]
            self.full_pw = self.all_data[self.all_data[self.full_time_pn]>60].sort_values(by=[self.wtg_pn,self.time_pn]).reset_index(drop=True)

    

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
            if wtg_data.shape[0]==0:
                continue
            t2 = f'{wtg_id}最小二乘拟合,型号{types}'
            if types=='MySE5.0MW':
                k,figure1 = rated_speed_torque(wtg_data,
                                               X_point_name=self.generator_speed_square_standard,
                                               y_point_name=self.generator_torque_pn,
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
                                               X_point_name=self.generator_speed_square_standard,
                                               y_point_name=self.generator_torque_pn,
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
        self.yaw_data[self.inter_angle_pn] = np.where(self.yaw_data['dif']>180,360-self.yaw_data['dif'],self.yaw_data['dif'])
        self.yaw_data[self.inter_angle_pn] = np.where(self.yaw_data[self.inter_angle_pn]<-180,-360-self.yaw_data[self.inter_angle_pn],self.yaw_data[self.inter_angle_pn])
        self.yaw_data = self.yaw_data[(self.yaw_data[self.inter_angle_pn]>=-30.25)&(self.yaw_data[self.inter_angle_pn]<=30.25)].reset_index(drop=True)
        # 夹角分仓
        bs2 = np.arange(-30.5,31,1)
        ls2 = np.arange(-30,31,1)
        self.yaw_data[self.inter_angle_bin] = pd.cut(self.yaw_data[self.inter_angle_pn],bins=bs2,right=False,labels=ls2).astype('float64')

        #风速分仓
        bs1 = np.arange(4,8,0.5)
        ls1 = np.arange(4.5,8,0.5)
        self.yaw_data[self.wind_pn_bin] = pd.cut(self.yaw_data[self.w_pn],bins=bs1,right=False,labels=ls1).astype(float)

        figure_yaw_angle_hist = plot_yaw_angle(self.yaw_data,self.inter_angle_bin)
        figure_yaw_angle_power_scatter = plot_yaw_scatter(data = self.yaw_data,
                                                          yaw_angle_pn=self.inter_angle_pn,
                                                          w_pn_bin=self.wind_pn_bin,
                                                          wtg_pn=self.wtg_pn,
                                                          wtg_list = self.wtg_list,
                                                          P_pn=self.P_pn,
                                                          label_size=ls1)
        self.yaw_data['P_th'] = self.yaw_data['P_th_bin']/((self.yaw_data['V_bin']/self.yaw_data[self.w_pn])**3)
        yaw_result_df,wtg_result_list = yaw_result_generate(self.wtg_list,
                                                            self.yaw_data,
                                                            self.inter_angle_bin,
                                                            self.angle_pn,
                                                            wtg_pn=self.wtg_pn,
                                                            P_pn=self.P_pn)
        
        return yaw_result_df,figure_yaw_angle_hist,figure_yaw_angle_power_scatter,wtg_result_list

    def blade_warning(self,
                      point_s=10,
                      point_c='r',
                      compare = False):
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
            wtg_data = self.blade_data[self.blade_data[self.wtg_pn]==wtg_id].reset_index(drop=True)  if not compare else self.blade_data[self.blade_data[self.type_pn]==wtg_type].reset_index(drop=True)
            # save_path = ROOT_PATH +f'桨叶角度/{title1}.jpg'
            if (wtg_data.shape[0] ==0) or (wtg_data[wtg_data[self.angle_pn]<5].shape[0] ==0):
                continue
            min_data = self.blade_data[self.blade_data[self.wtg_pn]==wtg_id].reset_index(drop=True)
            min_angle = wtg_data[self.angle_pn].min() if not compare else min_data[self.angle_pn].min()
            title1 = f'{wtg_id}风机有功功率-桨叶角度散点图，型号{wtg_type},桨叶角最小值{min_angle}'.replace('/','_')
            # print(wtg_id)
            # print(np.unique(wtg_data[self.wtg_pn]))
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
                                       comparison=compare,
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

    def set_error_threshold(self,
                            path = None):
        # print(path)
        if os.path.exists(path):
            self.scene_df = pd.read_excel(path)
        else:
            scene_list = self.Large_components_temp_ls + self.generator_temp_ls
            warning_thre = [None]*12
            error_thre = [80,80,95,95,70,70] + [150]*6
            abnormal_thre = [70,70,85,85,60,60] + [140]*6
            abnormal_thre2 = [65,65,80,80,55,60] + [130]*6
            self.scene_df = pd.DataFrame({'scene_name':scene_list,'abnormal_thre':abnormal_thre,'warning_thre':warning_thre,'error_thre':error_thre,'abnormal_thre_k':abnormal_thre2})

    def gen_Large_components_temp(self,
                                  if_notation=True):
        figure_list = []
        for _,scene_info in self.scene_df.iterrows():
            scene,abnormal,warning,error,abnormal_k = scene_info
            # print(scene)
            title1 = f'满发60分钟后{scene}'
            title2 = f'满发60分钟后{scene}温升'.replace('温度温升','温升')
            title2 = f'满发60分钟后{scene}温升\n({scene}-舱内温度)'.replace('温度温升','温升')
            # save_path = 'D:\OneDrive - CUHK-Shenzhen/1 新天\数字运营部 任务\昆头岭手动分析/6、7月/'+ scene+'.png'
            fig1 = plot_scene(self.full_pw,
                              scene,
                              'tab20',
                              '温度（℃）',
                              '次数',
                              style=None,
                              edgecolor='face',
                              point_size=20,
                              point_alpha = 1,
                              title=title1,
                              time_pn=self.time_pn,
                              wtg_pn = self.wtg_pn,
                              legend_cols=2,
                              hlines=[abnormal,warning,error,abnormal_k],
                              notation=if_notation,
                              save_fig=False)

            fig2 = plot_scene(self.full_pw,
                              f'{scene}温升({scene}-舱内温度)'.replace('温度温升','温升'),
                              'tab20',
                              '温度（℃）',
                              '次数',
                              style=None,
                              edgecolor='face',
                              point_size=20,
                              point_alpha = 1,
                              title=title2,
                              time_pn=self.time_pn,
                              wtg_pn =  self.wtg_pn,
                              legend_cols=2,
                              hlines=[None,None,None,abnormal_k],
                              notation=if_notation,
                              save_fig=False)
            figure_list.append(fig1)
            figure_list.append(fig2)        
        return figure_list

    def gen_Large_components_temp_single(self,
                                         if_notation=True):
        figure_list = []
        for _,scene_info in self.scene_df.iterrows():
            scene,abnormal,warning,error,abnormal_k = scene_info
            # print(scene)
            for _,wtg_info in self.wtg_list.iterrows():
                wtg_id,_ = wtg_info
                title1 = f'{wtg_id}风机{scene}'
                wtg_data = self.all_data[self.all_data[self.wtg_pn]==wtg_id].reset_index(drop=True)
                fig1 = plot_single_scene(wtg_data,
                                scene,
                                '温度（℃）',
                                '时间',
                                style=None,
                                edgecolor='face',
                                point_size=15,
                                point_alpha = 1,
                                title=title1,
                                time_pn=self.time_pn,
                                wtg_pn = self.wtg_pn,
                                wtg_id = wtg_id,
                                hlines=[abnormal,warning,error,abnormal_k],
                                notation=if_notation,
                                save_fig=False)
                if fig1 is not None:
                    figure_list.append(fig1)      
        return figure_list        
    
    def gen_generator_Temp(self,
                           if_h=True,):
        scene_comparison = self.generator_temp_ls
        fig_ls = []
        for _,wtg_info in self.wtg_list.iterrows():
            wtg_id,_ = wtg_info
            title =  f'{wtg_id}风机满发后发电机绕组温度预警'
            fig = plot_comparison_divide(dataframe=self.full_pw,
                                         wtg_id=wtg_id,
                                         point_names=scene_comparison,
                                         ylabel='温度(℃)',
                                         xlabel='次数',
                                         wtg_pn = self.wtg_pn,
                                         time_pn=self.time_pn,
                                         title= title,
                                         point_size=15,
                                         edgecolor='face',
                                         divide_thre = 1.2,
                                         diff_thre = 6,
                                         loc='lower left',
                                         if_hlines=if_h,
                                         save_fig=False)
            if fig is not None:
                fig_ls.append(fig)
        return fig_ls


    def gen_pitch_motor_Temp(self,
                           if_h=True,):
        scene_comparison2 = self.pitch_motor_temp_ls
        fig_ls = []
        for i,wtg_info in self.wtg_list.iterrows():
            wtg_id,_ = wtg_info
            title =  f'{wtg_id}变桨电机温度预警'
            fig =  plot_comparison_divide(dataframe = self.all_data,
                                          wtg_id=wtg_id,
                                          point_names=scene_comparison2,
                                          ylabel='温度(℃)',
                                          xlabel='时间',
                                          wtg_pn = self.wtg_pn,
                                          time_pn=self.time_pn,
                                          title=title,
                                          point_size=6,
                                          edgecolor='face',
                                          color_map='nipy_spectral',
                                          divide_thre=1.2,
                                          diff_thre = 6,
                                          sharpness=500,
                                          loc='lower left',
                                          unit='℃',
                                          if_hlines=if_h,
                                          notation=True,
                                          save_fig=False)
            if fig is not None:
                fig_ls.append(fig)
        return fig_ls


class kuitonggou_jinfeng():
    def __init__(self,raw_data,theory_pw_cur,
    phase_name = '魁通沟金风四期',
    wtg_pn='device_id',
    time_pn = 'data_time',
    type_pn = '风机类型',
    P_pn = '发电机有功功率',
    w_pn = '风速',
    angle_pn = '桨叶片角度1',
    inter_angle_pn = '机舱与风向夹角',
    generator_speed_pn = '发电机转速瞬时值',
    blade_dif_pn = 'blade_dif',
    
    cabin_temp_pn = '舱内温度',
    Large_components_temp = ['发电机驱动端轴承温度', '发电机非驱动端轴承温度',],
    generator_temp = ['发电机绕组温度1','发电机绕组温度2', '发电机绕组温度3', '发电机绕组温度4',
       '发电机绕组温度5', '发电机绕组温度6', '发电机绕组温度7', '发电机绕组温度8', '发电机绕组温度9','发电机绕组温度10',
       '发电机绕组温度11', '发电机绕组温度12'],
    pitch_motor_temp =  ['1号变桨电机温度', '2号变桨电机温度','3号变桨电机温度']) -> None:
        self.phase_name = phase_name
        self.wtg_pn = wtg_pn
        self.time_pn = time_pn
        self.type_pn = type_pn
        self.P_pn = P_pn
        self.w_pn = w_pn
        self.angle_pn = angle_pn
        self.inter_angle_pn = inter_angle_pn
        self.cabin_temp_pn = cabin_temp_pn
        self.blade_dif_pn = blade_dif_pn
        self.generator_speed_pn = generator_speed_pn
        self.generator_speed_square = '平均发电机转速平方'
        self.generator_speed_square_standard = '发电机转速平方(去量纲)'
        self.generator_torque_pn = '平均发电机转矩'
        self.inter_angle_bin = '机舱与风向夹角_bin'
        self.full_time_pn = 'full_time'
        self.wind_pn_bin = '风速_bin'
        self.Large_components_temp_ls = Large_components_temp
        self.generator_temp_ls = generator_temp
        self.pitch_motor_temp_ls = pitch_motor_temp

        ## 整理原始数据
        self.raw_data = raw_data[[self.wtg_pn,
                                  self.time_pn,
                                  self.type_pn,
                                  self.P_pn,
                                  self.w_pn,
                                  self.angle_pn,
                                  self.inter_angle_pn,
                                  self.blade_dif_pn,
                                  self.generator_speed_pn,
                                  self.cabin_temp_pn,
                                    ]+self.Large_components_temp_ls+
                                    self.generator_temp_ls+
                                    self.pitch_motor_temp_ls]
        if self.phase_name == '魁通沟金风四期':
            self.raw_data = self.raw_data[self.raw_data[self.type_pn]=='GW121_2500'].reset_index(drop=True)
        elif self.phase_name == '魁通沟金风五六期':
            self.raw_data = self.raw_data[self.raw_data[self.type_pn]=='GW140_3400'].reset_index(drop=True)
        if 'Unnamed: 235' in  self.raw_data.columns:
            self.raw_data = self.raw_data.drop('Unnamed: 235',axis=1)
        self.raw_data[self.time_pn] = pd.to_datetime(self.raw_data[self.time_pn])
        self.wtg_list =self.raw_data[[self.wtg_pn,self.type_pn]].drop_duplicates().reset_index(drop=True)

        ## 理论功率数据
        self.theory_pw_cur = theory_pw_cur
        if self.phase_name == '魁通沟金风四期':
            self.theory_pw_cur = self.theory_pw_cur[self.theory_pw_cur[self.type_pn]=='GW121_2500'].reset_index(drop=True)
        elif self.phase_name == '魁通沟金风五六期':
            self.theory_pw_cur = self.theory_pw_cur[self.theory_pw_cur[self.type_pn]=='GW140_3400'].reset_index(drop=True)


    def limit_power(self,angle_threshold=1,
                    gap_threshold=0.1,
                    pw_threshold=0,
                    wtg_multi_type=True):
        
        self.gen_data, self.raw_data_1,unlimit_data_size = limit_power_detect_loc_Goldwind(self.raw_data,
                                                                                           self.theory_pw_cur,
                                                                                           wtg_pn=self.wtg_pn,
                                                                                           time_pn=self.time_pn,
                                                                                           wind_pn=self.w_pn,
                                                                                           P_pn=self.P_pn,
                                                                                           blade_angle_pn=self.angle_pn,
                                                                                           angle_thr=angle_threshold,
                                                                                           blade_angle_dif_pn = self.blade_dif_pn,
                                                                                           gap_thr=gap_threshold,
                                                                                           pw_thr=pw_threshold,
                                                                                           multiple_type=wtg_multi_type)
        
        figure_limit_power = plot_limit_power(self.raw_data_1,
                                              self.gen_data,
                                              self.theory_pw_cur,
                                              x_pn=self.w_pn,
                                              y_pn=self.P_pn)
        size_change = (self.raw_data.shape[0],unlimit_data_size,self.gen_data.shape[0])
        return figure_limit_power,size_change
    
    def full_time(self,
                  pw_diff_threshold=[1000,1000],
                  type_ls = ['GW121_2500','GW140_3400'],
                  rated_pw_ls = [2500,3400,]):
        all_wtg = []
        for _,wtg_info in self.wtg_list.iterrows():
            # print(wtg_info)
            wtg,type = wtg_info
            wtg_dataframe = self.raw_data[self.raw_data[self.wtg_pn]==wtg].reset_index(drop=True).sort_values(by=self.time_pn)
            for j in range(len(type_ls)):
                if type_ls[j] == type:
                    df_ft = gen_full_time(wtg_dataframe,
                                          threshold = pw_diff_threshold[j],
                                          full_pw=rated_pw_ls[j],
                                          time_pn = self.time_pn,
                                          Pw_pn = self.P_pn,
                                          full_time_pn=self.full_time_pn)
                    all_wtg.append(df_ft)

        self.all_data = pd.concat(all_wtg,axis=0)


    def get_all_data(self,):
        scene_list = self.Large_components_temp_ls + self.generator_temp_ls
        for scene in scene_list:
            self.all_data[f'{scene}温升({scene}-舱内温度)'.replace('温度温升','温升')] = self.all_data[scene] - self.all_data[self.cabin_temp_pn]
            self.full_pw = self.all_data[self.all_data[self.full_time_pn]>60].sort_values(by=[self.wtg_pn,self.time_pn]).reset_index(drop=True)

    

    def torque_speed_warning(self,
                             ticks_x_n = 10,
                             u_bound = [13,11.5],
                             l_bound=[8.3,7],
                             r_speed=[13.6,12.1],
                             r_torque=[188.5,290],
                             thre=[15,15]):
        
        self.torque_speed_data = self.gen_data[abs(self.gen_data[self.generator_speed_pn])<2000].reset_index(drop=True)
        self.torque_speed_data[self.generator_torque_pn] = np.where(self.torque_speed_data[self.generator_speed_pn]>1,self.torque_speed_data[self.P_pn]/self.torque_speed_data[self.generator_speed_pn],np.NaN)
        # self.torque_speed_data[self.P_pn] / self.torque_speed_data[self.generator_speed_pn]
        self.torque_speed_data[self.generator_speed_square] = self.torque_speed_data[self.generator_speed_pn]**2
        self.torque_speed_data[self.generator_speed_square_standard] = self.torque_speed_data[self.generator_speed_square]/10

        results = []
        torque_fig_ls = []
        for _,wtg_info in self.wtg_list.iterrows():
            wtg_id,types = wtg_info
            wtg_data = self.torque_speed_data[self.torque_speed_data[self.wtg_pn]==wtg_id].reset_index(drop=True)
            t2 = f'{wtg_id}最小二乘拟合,型号{types}'
            if types=='GW121_2500':
                k,figure1 = rated_speed_torque(wtg_data,
                                               self.generator_speed_square_standard,
                                               self.generator_torque_pn,
                                               limit_pn=self.generator_speed_pn,
                                               title=t2,
                                               path=None,
                                               x_ticks_n=ticks_x_n,
                                               upper=u_bound[0],
                                               lower=l_bound[0],
                                               rated_speed=r_speed[0],
                                               rated_torque=r_torque[0],
                                               standardize_times=10,
                                               outlier_thre=thre[0],
                                               save_figure=False,
                                               legend_loc='lower right')
            elif types=='GW140_3400':
                k,figure1 = rated_speed_torque(wtg_data,
                                               self.generator_speed_square_standard,
                                               self.generator_torque_pn,
                                               limit_pn=self.generator_speed_pn,
                                               title=t2,
                                               path=None,
                                               x_ticks_n=ticks_x_n,
                                               upper=u_bound[1],
                                               lower=l_bound[1],
                                               rated_speed=r_speed[1],
                                               rated_torque=r_torque[1],
                                               outlier_thre=thre[1],
                                               standardize_times=10,
                                               save_figure=False,
                                               legend_loc='lower right')
            results.append([wtg_id,types,k])
            torque_fig_ls.append(figure1)

        torque_results_df = pd.DataFrame(results)
        torque_results_df.columns=['风机号','风机型号','斜率']
        return torque_results_df,torque_fig_ls

    def yaw_warning(self):
        self.yaw_data = self.gen_data
        self.yaw_data[self.inter_angle_pn] = np.where(self.yaw_data[self.inter_angle_pn]>180,self.yaw_data[self.inter_angle_pn]-360,self.yaw_data[self.inter_angle_pn])
        self.yaw_data = self.yaw_data[(self.yaw_data[self.inter_angle_pn]>=-15.25)&(self.yaw_data[self.inter_angle_pn]<=15.25)].reset_index(drop=True)
        bs2 = np.arange(-15.5,16,1)
        ls2 = np.arange(-15,16,1)

                #风速分仓
        bs1 = np.arange(4,8,0.5)
        ls1 = np.arange(4.5,8,0.5)
        self.yaw_data[self.wind_pn_bin] = pd.cut(self.yaw_data[self.w_pn],bins=bs1,right=False,labels=ls1).astype(float)

        self.yaw_data[self.inter_angle_bin] = pd.cut(self.yaw_data[self.inter_angle_pn],bins=bs2,right=False,labels=ls2).astype('float64')
        figure_yaw_angle_hist = plot_yaw_angle(self.yaw_data,self.inter_angle_bin)
        figure_yaw_angle_power_scatter = plot_yaw_scatter(data = self.yaw_data,
                                                          yaw_angle_pn=self.inter_angle_pn,
                                                          w_pn_bin=self.wind_pn_bin,
                                                          wtg_pn=self.wtg_pn,
                                                          wtg_list = self.wtg_list,
                                                          P_pn=self.P_pn,
                                                          label_size=ls1)
        self.yaw_data['P_th'] = self.yaw_data['P_th_bin']/((self.yaw_data['V_bin']/self.yaw_data[self.w_pn])**3)
        yaw_result_df,wtg_result_list = yaw_result_generate(self.wtg_list,
                                                            self.yaw_data,
                                                            self.inter_angle_bin,
                                                            self.angle_pn,
                                                            wtg_pn=self.wtg_pn,
                                                            P_pn=self.P_pn)
        
        return yaw_result_df,figure_yaw_angle_hist,figure_yaw_angle_power_scatter,wtg_result_list

    def blade_warning(self,
                      point_s=10,
                      point_c='r',
                      compare = False):
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
            wtg_data = self.blade_data[self.blade_data[self.wtg_pn]==wtg_id].reset_index(drop=True)  if not compare else self.blade_data
            # save_path = ROOT_PATH +f'桨叶角度/{title1}.jpg'
            min_data = self.blade_data[self.blade_data[self.wtg_pn]==wtg_id].reset_index(drop=True)
            min_angle = wtg_data[self.angle_pn].min() if not compare else min_data[self.angle_pn].min()
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
                                       comparison=compare,
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
                                       save_figure=False,
                                       day_interval=10)
            fig_ls_blade.append(figure1)
            fig_ls_blade_time.append(figure2)
            result_list.append([wtg_id,wtg_type,min_angle])
        blade_result_df = pd.DataFrame(result_list)
        blade_result_df.columns = ['风机号','风机型号','桨叶角度最小值']
        return blade_result_df,fig_ls_blade,fig_ls_blade_time,fig_ls_blade_type

    def set_error_threshold(self,
                            path = None):
        if os.path.exists(path):
            self.scene_df = pd.read_excel(path)
        else:
            scene_list =  self.Large_components_temp_ls + self.generator_temp_ls
            if self.phase_name == '魁通沟金风四期':
                warning_thre = [75]*2 + [None]*12
                error_thre = [80]*2 + [140]*12
                abnormal_thre = [70]*2 + [130]*12 
                abnormal_thre2 = [60]*2 + [120]*12 
            elif self.phase_name == '魁通沟金风五六期':
                warning_thre = [None,None,None,None,None]
                error_thre = [80,80,90,90,150,]
                abnormal_thre = [70,70,80,80,140,]
                abnormal_thre2 = [100,100,100,100,110,]
            self.scene_df = pd.DataFrame({'scene_name':scene_list,'abnormal_thre':abnormal_thre,'warning_thre':warning_thre,'error_thre':error_thre,'abnormal_thre_k':abnormal_thre2})

    def gen_Large_components_temp(self,
                                  if_notation=True):
        figure_list = []
        for _,scene_info in self.scene_df.iterrows():
            scene,abnormal,warning,error,abnormal_k = scene_info
            # print(scene)
            title1 = f'满发60分钟后{scene}'
            title2 = f'满发60分钟后{scene}温升'.replace('温度温升','温升')
            title2 = f'满发60分钟后{scene}温升\n({scene}-舱内温度)'.replace('温度温升','温升')
            # save_path = 'D:\OneDrive - CUHK-Shenzhen/1 新天\数字运营部 任务\昆头岭手动分析/6、7月/'+ scene+'.png'
            fig1 = plot_scene(self.full_pw,
                              scene,
                              'tab20',
                              '温度（℃）',
                              '次数',
                              style=None,
                              edgecolor='face',
                              point_size=20,
                              point_alpha = 1,
                              title=title1,
                              time_pn=self.time_pn,
                              wtg_pn = self.wtg_pn,
                              legend_cols=2,
                              hlines=[abnormal,warning,error,abnormal_k],
                              notation=if_notation,
                              save_fig=False)

            fig2 = plot_scene(self.full_pw,
                              f'{scene}温升({scene}-舱内温度)'.replace('温度温升','温升'),
                              'tab20',
                              '温度（℃）',
                              '次数',
                              style=None,
                              edgecolor='face',
                              point_size=20,
                              point_alpha = 1,
                              title=title2,
                              time_pn=self.time_pn,
                              wtg_pn =  self.wtg_pn,
                              legend_cols=2,
                              hlines=[None,None,None,abnormal_k],
                              notation=if_notation,
                              save_fig=False)
            figure_list.append(fig1)
            figure_list.append(fig2)        
        return figure_list
    def gen_Large_components_temp_single(self,
                                         if_notation=True):
        figure_list = []
        for _,scene_info in self.scene_df.iterrows():
            scene,abnormal,warning,error,abnormal_k = scene_info
            # print(scene)
            for _,wtg_info in self.wtg_list.iterrows():
                wtg_id,_ = wtg_info
                title1 = f'{wtg_id}风机{scene}'
                wtg_data = self.all_data[self.all_data[self.wtg_pn]==wtg_id].reset_index(drop=True)
                fig1 = plot_single_scene(wtg_data,
                                scene,
                                '温度（℃）',
                                '时间',
                                style=None,
                                edgecolor='face',
                                point_size=15,
                                point_alpha = 1,
                                title=title1,
                                time_pn=self.time_pn,
                                wtg_pn = self.wtg_pn,
                                wtg_id = wtg_id,
                                hlines=[abnormal,warning,error,abnormal_k],
                                notation=if_notation,
                                save_fig=False,
                                day_sep=10)
                if fig1 is not None:
                    figure_list.append(fig1)      
        return figure_list  
    def gen_generator_Temp(self,
                           if_h=True,):
        scene_comparison = self.generator_temp_ls
        fig_ls = []
        for _,wtg_info in self.wtg_list.iterrows():
            wtg_id,_ = wtg_info
            title =  f'{wtg_id}风机满发后发电机绕组温度预警'
            fig = plot_comparison_divide(dataframe=self.full_pw,
                                         wtg_id=wtg_id,
                                         point_names=scene_comparison,
                                         ylabel='温度(℃)',
                                         xlabel='次数',
                                         wtg_pn = self.wtg_pn,
                                         time_pn=self.time_pn,
                                         title= title,
                                         point_size=15,
                                         edgecolor='face',
                                         divide_thre = 1.2,
                                         diff_thre = 6,
                                         loc='lower left',
                                         if_hlines=if_h,
                                         day_sep=10,
                                         save_fig=False)
            if fig is not None:
                fig_ls.append(fig)
        return fig_ls


    def gen_pitch_motor_Temp(self,
                           if_h=True,):
        scene_comparison2 = self.pitch_motor_temp_ls
        fig_ls = []
        for i,wtg_info in self.wtg_list.iterrows():
            wtg_id,_ = wtg_info
            title =  f'{wtg_id}变桨电机温度预警'
            fig =  plot_comparison_divide(dataframe = self.all_data,
                                          wtg_id=wtg_id,
                                          point_names=scene_comparison2,
                                          ylabel='温度(℃)',
                                          xlabel='时间',
                                          wtg_pn = self.wtg_pn,
                                          time_pn=self.time_pn,
                                          title=title,
                                          point_size=6,
                                          edgecolor='face',
                                          color_map='nipy_spectral',
                                          divide_thre=1.2,
                                          diff_thre = 6,
                                          sharpness=500,
                                          loc='lower left',
                                          unit='℃',
                                          if_hlines=if_h,
                                          notation=True,
                                          day_sep=10,
                                          save_fig=False)
            if fig is not None:
                fig_ls.append(fig)
        return fig_ls



class kangzhuang_yunda():
    def __init__(self,raw_data,theory_pw_cur,
    phase_name = '康庄运达',
    wtg_pn = '风机',
    time_pn ='时间',
    type_pn = '风机类型',
    P_pn = '平均电网有功功率',
    w_pn = '平均风速',
    angle_pn='平均桨叶角度1a',
    inter_angle_pn = '机舱与风向夹角',
    generator_speed_pn = '平均发电机转速1',
    cabin_temp_pn = '平均机舱温度',
    generator_torque_pn = '变流器转矩反馈',
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
        self.inter_angle_pn = inter_angle_pn
        self.cabin_temp_pn = cabin_temp_pn
        self.Large_components_temp_ls = Large_components_temp
        self.generator_temp_ls = generator_temp
        self.pitch_motor_temp_ls = pitch_motor_temp
        self.generator_torque_pn = generator_torque_pn
        self.generator_speed_pn = generator_speed_pn
        self.generator_speed_square = '发电机转速平方'
        self.generator_speed_square_standard = '发电机转速平方(去量纲)'
        # self.generator_torque_pn = '发电机转矩'
        # self.inter_angle_pn = '机舱与风向夹角'
        self.inter_angle_bin = '机舱与风向夹角_bin'
        self.full_time_pn = 'full_time'
        self.wind_pn_bin = '风速_bin'

        ## 整理原始数据
        self.raw_data = raw_data[[self.wtg_pn,
                                  self.time_pn,
                                  self.type_pn,
                                  self.P_pn,
                                  self.w_pn,
                                  self.angle_pn,
                                  self.inter_angle_pn,
                                  self.generator_speed_pn,
                                  self.generator_torque_pn,
                                  self.cabin_temp_pn,
                                    ]+self.Large_components_temp_ls+
                                    self.generator_temp_ls+
                                    self.pitch_motor_temp_ls]
        if 'Unnamed: 235' in  self.raw_data.columns:
            self.raw_data = self.raw_data.drop('Unnamed: 235',axis=1)
        self.raw_data[self.time_pn] = pd.to_datetime(self.raw_data[self.time_pn])
        self.wtg_list =self.raw_data[[self.wtg_pn,self.type_pn]].drop_duplicates().reset_index(drop=True)

        ## 理论功率数据
        self.theory_pw_cur = theory_pw_cur


    def limit_power(self,angle_threshold=1,
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
    
    def full_time(self,
                  pw_diff_threshold=[200,200],
                  type_ls = ['WD140-2500','WD147-2500'],
                  rated_pw_ls = [2500,2500]):
        all_wtg = []
        for _,wtg_info in self.wtg_list.iterrows():
            # print(wtg_info)
            wtg,type = wtg_info
            wtg_dataframe = self.raw_data[self.raw_data[self.wtg_pn]==wtg].reset_index(drop=True).sort_values(by=self.time_pn)
            for j in range(len(type_ls)):
                if type_ls[j] == type:
                    df_ft = gen_full_time(wtg_dataframe,
                                          threshold = pw_diff_threshold[j],
                                          full_pw=rated_pw_ls[j],
                                          time_pn = self.time_pn,
                                          Pw_pn = self.P_pn,
                                          full_time_pn=self.full_time_pn)
                    all_wtg.append(df_ft)

        self.all_data = pd.concat(all_wtg,axis=0)


    def get_all_data(self,):
        scene_list = self.Large_components_temp_ls + self.generator_temp_ls
        for scene in scene_list:
            self.all_data[f'{scene}温升({scene}-舱内温度)'.replace('温度温升','温升')] = self.all_data[scene] - self.all_data[self.cabin_temp_pn]
            self.full_pw = self.all_data[self.all_data[self.full_time_pn]>60].sort_values(by=[self.wtg_pn,self.time_pn]).reset_index(drop=True)

    

    def torque_speed_warning(self,
                             ticks_x_n = 10,
                             u_bound = [1.7111e3,1.7111e3],
                             l_bound=[1.1777e3,1.1777e3],
                             r_speed=[1.755e3,1.755e3],
                             r_torque=[14000,14000],
                             thre=[1000,1000]):
        
        self.torque_speed_data = self.gen_data[abs(self.gen_data[self.generator_speed_pn])<2000].reset_index(drop=True)
        # self.torque_speed_data[self.generator_torque_pn] = self.torque_speed_data[self.P_pn] / self.torque_speed_data[self.generator_speed_pn]
        self.torque_speed_data[self.generator_speed_square] = self.torque_speed_data[self.generator_speed_pn]**2
        self.torque_speed_data[self.generator_speed_square_standard] = self.torque_speed_data[self.generator_speed_square]/1e4

        results = []
        torque_fig_ls = []
        for _,wtg_info in self.wtg_list.iterrows():
            wtg_id,types = wtg_info
            wtg_data = self.torque_speed_data[self.torque_speed_data[self.wtg_pn]==wtg_id].reset_index(drop=True)
            # print(wtg_data.shape)
            t2 = f'{wtg_id}最小二乘拟合,型号{types}'
            if types=='WD140-2500':
                k,figure1 = rated_speed_torque(wtg_data,
                                               self.generator_speed_square_standard,
                                               self.generator_torque_pn,
                                               limit_pn=self.generator_speed_pn,
                                               title=t2,
                                               path=None,
                                               x_ticks_n=ticks_x_n,
                                               upper=u_bound[0],
                                               lower=l_bound[0],
                                               rated_speed=r_speed[0],
                                               rated_torque=r_torque[0],
                                               outlier_thre=thre[0],
                                               save_figure=False)
            elif types=='WD147-2500':
                k,figure1 = rated_speed_torque(wtg_data,
                                               self.generator_speed_square_standard,
                                               self.generator_torque_pn,
                                               limit_pn=self.generator_speed_pn,
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
        self.yaw_data = self.yaw_data[(self.yaw_data[self.inter_angle_pn]>=-15.25)&(self.yaw_data[self.inter_angle_pn]<=15.25)].reset_index(drop=True)

        bs2 = np.arange(-15.5,16,1)
        ls2 = np.arange(-15,16,1)

                #风速分仓
        bs1 = np.arange(4,8,0.5)
        ls1 = np.arange(4.5,8,0.5)
        self.yaw_data[self.wind_pn_bin] = pd.cut(self.yaw_data[self.w_pn],bins=bs1,right=False,labels=ls1).astype(float)

        self.yaw_data[self.inter_angle_bin] = pd.cut(self.yaw_data[self.inter_angle_pn],bins=bs2,right=False,labels=ls2).astype('float64')
        figure_yaw_angle_hist = plot_yaw_angle(self.yaw_data,self.inter_angle_bin)
        figure_yaw_angle_power_scatter = plot_yaw_scatter(data = self.yaw_data,
                                                          yaw_angle_pn=self.inter_angle_pn,
                                                          w_pn_bin=self.wind_pn_bin,
                                                          wtg_pn=self.wtg_pn,
                                                          wtg_list = self.wtg_list,
                                                          P_pn=self.P_pn,
                                                          label_size=ls1)
        self.yaw_data['P_th'] = self.yaw_data['P_th_bin']/((self.yaw_data['V_bin']/self.yaw_data[self.w_pn])**3)
        yaw_result_df,wtg_result_list = yaw_result_generate(self.wtg_list,
                                                            self.yaw_data,
                                                            self.inter_angle_bin,
                                                            self.angle_pn,
                                                            wtg_pn=self.wtg_pn,
                                                            P_pn=self.P_pn)
        
        return yaw_result_df,figure_yaw_angle_hist,figure_yaw_angle_power_scatter,wtg_result_list

    def blade_warning(self,
                      point_s=10,
                      point_c='r',
                      compare = False):
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
            wtg_data = self.blade_data[self.blade_data[self.wtg_pn]==wtg_id].reset_index(drop=True)  if not compare else self.blade_data[self.blade_data[self.type_pn]==wtg_type].reset_index(drop=True)
            # save_path = ROOT_PATH +f'桨叶角度/{title1}.jpg'
            min_data = self.blade_data[self.blade_data[self.wtg_pn]==wtg_id].reset_index(drop=True)
            min_angle = wtg_data[self.angle_pn].min() if not compare else min_data[self.angle_pn].min()
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
                                       comparison=compare,
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

    def set_error_threshold(self,
                            path = None):
        if os.path.exists(path):
            self.scene_df = pd.read_excel(path)
        else:
            scene_list = self.Large_components_temp_ls + self.generator_temp_ls
            warning_thre =[None,None,None,None,90,90,150,150,150]
            error_thre = [65,75,90,90,95,95,155,155,155]
            abnormal_thre = [55,65,80,80,85,85,145,145,145]
            abnormal_thre2 = [1000]*9
            self.scene_df = pd.DataFrame({'scene_name':scene_list,'abnormal_thre':abnormal_thre,'warning_thre':warning_thre,'error_thre':error_thre,'abnormal_thre_k':abnormal_thre2})

    def gen_Large_components_temp(self,
                                  if_notation=True):
        figure_list = []
        for _,scene_info in self.scene_df.iterrows():
            scene,abnormal,warning,error,abnormal_k = scene_info
            # print(scene)
            title1 = f'满发60分钟后{scene}'
            title2 = f'满发60分钟后{scene}温升'.replace('温度温升','温升')
            title2 = f'满发60分钟后{scene}温升\n({scene}-舱内温度)'.replace('温度温升','温升')
            # save_path = 'D:\OneDrive - CUHK-Shenzhen/1 新天\数字运营部 任务\昆头岭手动分析/6、7月/'+ scene+'.png'
            fig1 = plot_scene(self.full_pw,
                              scene,
                              'tab20',
                              '温度（℃）',
                              '次数',
                              style=None,
                              edgecolor='face',
                              point_size=20,
                              point_alpha = 1,
                              title=title1,
                              time_pn=self.time_pn,
                              wtg_pn = self.wtg_pn,
                              legend_cols=2,
                              hlines=[abnormal,warning,error,abnormal_k],
                              notation=if_notation,
                              save_fig=False)

            fig2 = plot_scene(self.full_pw,
                              f'{scene}温升({scene}-舱内温度)'.replace('温度温升','温升'),
                              'tab20',
                              '温度（℃）',
                              '次数',
                              style=None,
                              edgecolor='face',
                              point_size=20,
                              point_alpha = 1,
                              title=title2,
                              time_pn=self.time_pn,
                              wtg_pn =  self.wtg_pn,
                              legend_cols=2,
                              hlines=[None,None,None,abnormal_k],
                              notation=if_notation,
                              save_fig=False)
            figure_list.append(fig1)
            figure_list.append(fig2)        
        return figure_list
    def gen_Large_components_temp_single(self,
                                         if_notation=True):
        figure_list = []
        for _,scene_info in self.scene_df.iterrows():
            scene,abnormal,warning,error,abnormal_k = scene_info
            # print(scene)
            for _,wtg_info in self.wtg_list.iterrows():
                wtg_id,_ = wtg_info
                title1 = f'{wtg_id}风机{scene}'
                wtg_data = self.all_data[self.all_data[self.wtg_pn]==wtg_id].reset_index(drop=True)
                fig1 = plot_single_scene(wtg_data,
                                scene,
                                '温度（℃）',
                                '时间',
                                style=None,
                                edgecolor='face',
                                point_size=15,
                                point_alpha = 1,
                                title=title1,
                                time_pn=self.time_pn,
                                wtg_pn = self.wtg_pn,
                                wtg_id = wtg_id,
                                hlines=[abnormal,warning,error,abnormal_k],
                                notation=if_notation,
                                save_fig=False)
                if fig1 is not None:
                    figure_list.append(fig1)      
        return figure_list  
    
    def gen_generator_Temp(self,
                           if_h=True,):
        scene_comparison = self.generator_temp_ls
        fig_ls = []
        for _,wtg_info in self.wtg_list.iterrows():
            wtg_id,_ = wtg_info
            title =  f'{wtg_id}风机满发后发电机绕组温度预警'
            fig = plot_comparison_divide(dataframe=self.full_pw,
                                         wtg_id=wtg_id,
                                         point_names=scene_comparison,
                                         ylabel='温度(℃)',
                                         xlabel='次数',
                                         wtg_pn = self.wtg_pn,
                                         time_pn=self.time_pn,
                                         title= title,
                                         point_size=15,
                                         edgecolor='face',
                                         divide_thre = 1.2,
                                         diff_thre = 6,
                                         loc='lower left',
                                         if_hlines=if_h,
                                         save_fig=False)
            if fig is not None:
                fig_ls.append(fig)
        return fig_ls


    def gen_pitch_motor_Temp(self,
                           if_h=True,):
        scene_comparison2 = self.pitch_motor_temp_ls
        fig_ls = []
        for i,wtg_info in self.wtg_list.iterrows():
            wtg_id,_ = wtg_info
            title =  f'{wtg_id}变桨电机温度预警'
            fig =  plot_comparison_divide(dataframe = self.all_data,
                                          wtg_id=wtg_id,
                                          point_names=scene_comparison2,
                                          ylabel='温度(℃)',
                                          xlabel='时间',
                                          wtg_pn = self.wtg_pn,
                                          time_pn=self.time_pn,
                                          title=title,
                                          point_size=6,
                                          edgecolor='face',
                                          color_map='nipy_spectral',
                                          divide_thre=1.2,
                                          diff_thre = 6,
                                          sharpness=500,
                                          loc='lower left',
                                          unit='℃',
                                          if_hlines=if_h,
                                          notation=True,
                                          save_fig=False)
            if fig is not None:
                fig_ls.append(fig)
        return fig_ls

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

class RuoQiang_yuanjing():
    def __init__(self,raw_data,theory_pw_cur,
    phase_name = '若羌三期远景',
    wtg_pn = '风机',
    time_pn ='时间',
    type_pn = '风机类型',
    P_pn = '平均电网有功功率',
    w_pn = '平均风速',
    torque_pn = '实际扭矩',
    angle_pn1='桨叶片角度1',
    angle_pn2='桨叶片角度2',
    angle_pn3='桨叶片角度3',
    inter_angle_pn = '瞬时机舱中轴线与风向夹角',
    generator_speed_pn = '发电机转速',
    vibrate_x_pn = '机舱横向振动值',
    vibrate_y_pn = '机舱侧向振动值',
    cabin_temp_pn = '舱内温度',
    Large_components_temp = ['主变绕组温度',
                             '主轴承内圈温度', 
                             '主轴承外圈温度', 
                             '主轴承温度', 
                             '齿轮箱中速轴非驱动端轴承温度', 
                             '齿轮箱中速轴驱动端轴承温度',
                             '齿轮箱油池温度', 
                             '齿轮箱高速轴非驱动端轴承温度', 
                             '齿轮箱高速轴驱动端轴承温度',
                             '发电机非驱动端轴承温度',
                             '发电机驱动端轴承温度',
                             '发电机出风口温度', 
                             '塔底柜温度',
                             ],
    generator_temp = ['发电机定子U相线圈温度', 
                      '发电机定子V相线圈温度',
                      '发电机定子W相线圈温度',],
    pitch_motor_temp =  ['1号桨电机温度',
                         '2号桨电机温度',
                         '3号桨电机温度'],
) -> None:
        self.wtg_pn = wtg_pn
        self.time_pn = time_pn
        self.type_pn = type_pn
        self.P_pn = P_pn
        self.w_pn = w_pn
        self.angle_pn1 = angle_pn1
        self.angle_pn2 = angle_pn2
        self.angle_pn3 = angle_pn3
        self.vibrate_x_pn = vibrate_x_pn
        self.vibrate_y_pn = vibrate_y_pn
        self.inter_angle_pn = inter_angle_pn
        self.cabin_temp_pn = cabin_temp_pn
        self.Large_components_temp_ls = Large_components_temp
        self.generator_temp_ls = generator_temp
        self.pitch_motor_temp_ls = pitch_motor_temp
        self.generator_speed_pn = generator_speed_pn
        self.generator_torque_pn = torque_pn
        self.generator_speed_square = '发电机转速平方'
        self.generator_speed_square_standard = '发电机转速平方(去量纲)'
        self.generator_torque_pn = torque_pn 
        self.inter_angle_bin = '机舱与风向夹角_bin'
        self.full_time_pn = 'full_time'
        self.wind_pn_bin = '风速_bin'

        ## 整理原始数据
        self.raw_data = raw_data[[self.wtg_pn,
                                  self.time_pn,
                                  self.type_pn,
                                  self.P_pn,
                                  self.w_pn,
                                  self.angle_pn1,
                                  self.angle_pn2,
                                  self.angle_pn3,
                                  self.cabin_temp_pn,
                                  self.generator_speed_pn,
                                  self.generator_torque_pn,
                                  self.vibrate_x_pn,
                                  self.vibrate_y_pn,
                                  self.inter_angle_pn,
                                   ]+self.Large_components_temp_ls+
                                   self.generator_temp_ls+
                                   self.pitch_motor_temp_ls]

        if 'Unnamed: 235' in  self.raw_data.columns:
            self.raw_data = self.raw_data.drop('Unnamed: 235',axis=1)
        self.raw_data[self.time_pn] = pd.to_datetime(self.raw_data[self.time_pn])
        self.wtg_list =self.raw_data[[self.wtg_pn,self.type_pn]].drop_duplicates().reset_index(drop=True)

        ## 理论功率数据
        self.theory_pw_cur = theory_pw_cur


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
                                                     blade_angle_pn = self.angle_pn1,
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
                             ticks_x_n = 15,
                             u_bound = [2.9e6],
                             l_bound=[1.4e6],
                             r_speed=[1752],
                             r_torque=[34434],
                             thre=[2900],
                             root_path = 'none',
                             save_figure=False):
        self.torque_speed_data =  self.gen_data[abs( self.gen_data[ self.generator_speed_pn])<2000].reset_index(drop=True)
        # self.torque_speed_data[ self.generator_torque_pn] =  self.torque_speed_data[ self.P_pn] /  self.torque_speed_data[ self.generator_speed_pn]
        self.torque_speed_data[ self.generator_speed_square] =  self.torque_speed_data[ self.generator_speed_pn]**2
        self.torque_speed_data[ self.generator_speed_square_standard] =  self.torque_speed_data[ self.generator_speed_square]/1e4

        results = []
        torque_fig_ls = []
        for _,wtg_info in  self.wtg_list.iterrows():
            wtg_id,types = wtg_info
            wtg_data =  self.torque_speed_data[ self.torque_speed_data[ self.wtg_pn]==wtg_id].reset_index(drop=True)
            t2 = f'{wtg_id}最小二乘拟合,型号{types}'
            if types=='EN-192-6.25':
                k,figure1 = rated_speed_torque(wtg_data,
                                                    self.generator_speed_square_standard,
                                                    self.generator_torque_pn,
                                                limit_pn= self.generator_speed_square,
                                                title=t2,
                                                x_ticks_n=ticks_x_n,
                                                upper=u_bound[0],
                                                lower=l_bound[0],
                                                rated_speed=r_speed[0],
                                                rated_torque=r_torque[0],
                                                outlier_thre=thre[0],
                                                # path=None,
                                                path = root_path+f'转速转矩/{t2}.jpg',
                                                save_figure=save_figure)

            results.append([wtg_id,types,k])
            torque_fig_ls.append(figure1)

        torque_results_df = pd.DataFrame(results)
        torque_results_df.columns=['风机号','风机型号','斜率']

        return torque_results_df,torque_fig_ls

    def blade_warning(self,
                      point_s=10,
                      point_c='r',
                      root_path ='None',
                      save_figure=False,
                      blade_pn = '桨叶片角度1',
                      compare = False):
        
        self.blade_data = self.raw_data[(self.raw_data[self.angle_pn1]>-7)&(self.raw_data[self.angle_pn1]<100)].reset_index(drop=True)
        fig_ls_blade_type = []
        for wtg_type in np.unique(self.wtg_list[self.type_pn]):
            use_data = self.blade_data[self.blade_data[self.type_pn]==wtg_type].reset_index(drop=True)
            figure = plot_blade_power_all(use_data,
                                          blade_pn=self.angle_pn1,
                                          Pw_pn=self.P_pn,
                                          title=f'{wtg_type}功率-桨叶角度散点图')
            fig_ls_blade_type.append(figure)

        fig_ls_blade = []
        fig_ls_blade_time = []
        result_list=[]
        for _,wtg_info in self.wtg_list.iterrows():
            wtg_id,wtg_type = wtg_info
            wtg_data = self.blade_data[self.blade_data[self.wtg_pn]==wtg_id].reset_index(drop=True) if not compare else self.blade_data
            # save_path = ROOT_PATH +f'桨叶角度/{title1}.jpg'
            min_data = self.blade_data[self.blade_data[self.wtg_pn]==wtg_id].reset_index(drop=True)
            min_angle = wtg_data[blade_pn].min() if not compare else min_data[blade_pn].min()
            title1 = f'{wtg_id}风机有功功率-桨叶角度散点图，型号{wtg_type},桨叶角最小值{min_angle}'.replace('/','_')
            figure1 = plot_angle_power(dataframe=wtg_data[wtg_data[blade_pn]<5].reset_index(drop=True),
                                       wtg=wtg_id,
                                       wtg_point_name=self.wtg_pn,
                                       y_point_name=self.P_pn,
                                       x_point_name=blade_pn,
                                       time_point_name=self.time_pn,
                                       point_size=point_s,
                                       style=None,
                                    #    path=None,
                                       title=title1,
                                       legend_cols=2,
                                       color=point_c,
                                       comparison=compare,
                                       save_figure=save_figure,
                                       path = root_path+f'桨叶角度对零/{title1}.jpg')
            title2 = f'{wtg_id}风机桨叶角度-时间散点图，型号{wtg_type},桨叶角最小值{min_angle}'.replace('/','_')
            figure2 = plot_angle_power(dataframe=wtg_data[wtg_data[blade_pn]<5].reset_index(drop=True),
                                       wtg=wtg_id,
                                       wtg_point_name=self.wtg_pn,
                                       y_point_name=blade_pn,
                                       x_point_name=self.time_pn,
                                       time_point_name=self.time_pn,
                                       point_size=point_s,
                                       style=None,
                                    #    path=None,
                                       title=title2,
                                       legend_cols=2,
                                       color=point_c,
                                       comparison=False,
                                       save_figure=save_figure,
                                       path = root_path+f'桨叶角度对零/{title2}.jpg')

            fig_ls_blade.append(figure1)
            fig_ls_blade_time.append(figure2)
            result_list.append([wtg_id,wtg_type,min_angle])
        blade_result_df = pd.DataFrame(result_list)
        blade_result_df.columns = ['风机号','风机型号','桨叶角度最小值']
        return blade_result_df,fig_ls_blade,fig_ls_blade_time,fig_ls_blade_type

    def full_time(self,
                  pw_diff_threshold=[1000],
                  type_ls = ['EN-192-6.25'],
                  rated_pw_ls = [6250]):
        all_wtg = []
        for _,wtg_info in self.wtg_list.iterrows():
            # print(wtg_info)
            wtg,type = wtg_info
            wtg_dataframe = self.raw_data[self.raw_data[self.wtg_pn]==wtg].reset_index(drop=True).sort_values(by=self.time_pn)
            for j in range(len(type_ls)):
                if type_ls[j] == type:
                    df_ft = gen_full_time(wtg_dataframe,
                                          threshold = pw_diff_threshold[j],
                                          full_pw=rated_pw_ls[j],
                                          time_pn = self.time_pn,
                                          Pw_pn = self.P_pn,
                                          full_time_pn=self.full_time_pn)
                    all_wtg.append(df_ft)
            del wtg_dataframe,df_ft
        self.all_data = pd.concat(all_wtg,axis=0)

    def get_all_data(self,):
        scene_list = self.Large_components_temp_ls + self.generator_temp_ls
        for scene in scene_list:
            self.all_data[f'{scene}温升({scene}-舱内温度)'.replace('温度温升','温升')] = self.all_data[scene] - self.all_data[self.cabin_temp_pn]
            self.full_pw = self.all_data[self.all_data[self.full_time_pn]>60].sort_values(by=[self.wtg_pn,self.time_pn]).reset_index(drop=True)


    def yaw_warning(self):
        self.yaw_data = self.gen_data
        # self.yaw_data['dif'] = self.gen_data[self.wind_north_angle]-self.gen_data[self.cabin_north_angle]
        # self.yaw_data[self.inter_angle_pn] = np.where(self.yaw_data['dif']>180,360-self.yaw_data['dif'],self.yaw_data['dif'])
        # self.yaw_data[self.inter_angle_pn] = np.where(self.yaw_data[self.inter_angle_pn]<-180,-360-self.yaw_data[self.inter_angle_pn],self.yaw_data[self.inter_angle_pn])
        self.yaw_data = self.yaw_data[(self.yaw_data[self.inter_angle_pn]>=-30.25)&(self.yaw_data[self.inter_angle_pn]<=30.25)].reset_index(drop=True)
        # 夹角分仓
        bs2 = np.arange(-30.5,31,1)
        ls2 = np.arange(-30,31,1)
        self.yaw_data[self.inter_angle_bin] = pd.cut(self.yaw_data[self.inter_angle_pn],bins=bs2,right=False,labels=ls2).astype('float64')

        #风速分仓
        bs1 = np.arange(4,8,0.5)
        ls1 = np.arange(4.5,8,0.5)
        self.yaw_data[self.wind_pn_bin] = pd.cut(self.yaw_data[self.w_pn],bins=bs1,right=False,labels=ls1).astype(float)

        figure_yaw_angle_hist = plot_yaw_angle(self.yaw_data,self.inter_angle_bin)
        figure_yaw_angle_power_scatter = plot_yaw_scatter(data = self.yaw_data,
                                                          yaw_angle_pn=self.inter_angle_pn,
                                                          w_pn_bin=self.wind_pn_bin,
                                                          wtg_pn=self.wtg_pn,
                                                          wtg_list = self.wtg_list,
                                                          P_pn=self.P_pn,
                                                          label_size=ls1)
        self.yaw_data['P_th'] = self.yaw_data['P_th_bin']/((self.yaw_data['V_bin']/self.yaw_data[self.w_pn])**3)
        yaw_result_df,wtg_result_list = yaw_result_generate(self.wtg_list,
                                                            self.yaw_data,
                                                            self.inter_angle_bin,
                                                            self.angle_pn1,
                                                            wtg_pn=self.wtg_pn,
                                                            P_pn=self.P_pn)
        
        return yaw_result_df,figure_yaw_angle_hist,figure_yaw_angle_power_scatter,wtg_result_list



    def set_error_threshold(self,
                            path = None):
        if os.path.exists(path):
            self.scene_df = pd.read_excel(path)
        else:
            scene_list = self.Large_components_temp_ls + self.generator_temp_ls
            warning_thre = [65,65,65,90,90,75,90,90,95,95,None,145,145,145]
            error_thre = [70,70,70,95,95,80,95,95,100,100,58,155,155,155]
            abnormal_thre = [60,60,60,80,80,70,80,80,90,90,50,140,140,140]
            abnormal_thre2 = [55,55,55,75,75,65,75,75,85,85,45,135,135,135]
            self.scene_df = pd.DataFrame({'scene_name':scene_list,'abnormal_thre':abnormal_thre,'warning_thre':warning_thre,'error_thre':error_thre,'abnormal_thre_k':abnormal_thre2})


    def gen_Large_components_temp(self,
                                  if_notation=True):
        figure_list = []
        for _,scene_info in self.scene_df.iterrows():
            scene,abnormal,warning,error,abnormal_k = scene_info
            # print(scene)
            title1 = f'满发60分钟后{scene}'
            title2 = f'满发60分钟后{scene}温升'.replace('温度温升','温升')
            title2 = f'满发60分钟后{scene}温升\n({scene}-舱内温度)'.replace('温度温升','温升')
            # save_path = 'D:\OneDrive - CUHK-Shenzhen/1 新天\数字运营部 任务\昆头岭手动分析/6、7月/'+ scene+'.png'
            fig1 = plot_scene(self.full_pw,
                              scene,
                              'tab20',
                              '温度（℃）',
                              '次数',
                              style=None,
                              edgecolor='face',
                              point_size=20,
                              point_alpha = 1,
                              title=title1,
                              time_pn=self.time_pn,
                              wtg_pn = self.wtg_pn,
                              legend_cols=2,
                              hlines=[abnormal,warning,error,abnormal_k],
                              notation=if_notation,
                              save_fig=False)

            fig2 = plot_scene(self.full_pw,
                              f'{scene}温升({scene}-舱内温度)'.replace('温度温升','温升'),
                              'tab20',
                              '温度（℃）',
                              '次数',
                              style=None,
                              edgecolor='face',
                              point_size=20,
                              point_alpha = 1,
                              title=title2,
                              time_pn=self.time_pn,
                              wtg_pn =  self.wtg_pn,
                              legend_cols=2,
                              hlines=[None,None,None,abnormal_k],
                              notation=if_notation,
                              save_fig=False)
            figure_list.append(fig1)
            figure_list.append(fig2)        
        return figure_list


    def gen_Large_components_temp_single(self,
                                         if_notation=True):
        figure_list = []
        for _,scene_info in self.scene_df.iterrows():
            scene,abnormal,warning,error,abnormal_k = scene_info
            # print(scene)
            for _,wtg_info in self.wtg_list.iterrows():
                wtg_id,_ = wtg_info
                title1 = f'{wtg_id}风机{scene}'
                wtg_data = self.all_data[self.all_data[self.wtg_pn]==wtg_id].reset_index(drop=True)
                fig1 = plot_single_scene(wtg_data,
                                scene,
                                '温度（℃）',
                                '时间',
                                style=None,
                                edgecolor='face',
                                point_size=15,
                                point_alpha = 1,
                                title=title1,
                                time_pn=self.time_pn,
                                wtg_pn = self.wtg_pn,
                                wtg_id = wtg_id,
                                hlines=[abnormal,warning,error,abnormal_k],
                                notation=if_notation,
                                save_fig=False)
                if fig1 is not None:
                    figure_list.append(fig1)      
        return figure_list        

    
    def gen_generator_Temp(self,
                           if_h=True,):
        scene_comparison = self.generator_temp_ls
        fig_ls = []
        for _,wtg_info in self.wtg_list.iterrows():
            wtg_id,_ = wtg_info
            title =  f'{wtg_id}风机满发后发电机绕组温度预警'
            fig = plot_comparison_divide(dataframe=self.full_pw,
                                         wtg_id=wtg_id,
                                         point_names=scene_comparison,
                                         ylabel='温度(℃)',
                                         xlabel='次数',
                                         wtg_pn = self.wtg_pn,
                                         time_pn=self.time_pn,
                                         title= title,
                                         point_size=15,
                                         edgecolor='face',
                                         divide_thre = 1.2,
                                         diff_thre = 6,
                                         loc='lower left',
                                         if_hlines=if_h,
                                         save_fig=False)
            if fig is not None:
                fig_ls.append(fig)
        return fig_ls


    def gen_pitch_motor_Temp(self,
                           if_h=True,):
        scene_comparison2 = self.pitch_motor_temp_ls
        fig_ls = []
        for i,wtg_info in self.wtg_list.iterrows():
            wtg_id,_ = wtg_info
            title =  f'{wtg_id}变桨电机温度预警'
            fig =  plot_comparison_divide(dataframe = self.all_data,
                                          wtg_id=wtg_id,
                                          point_names=scene_comparison2,
                                          ylabel='温度(℃)',
                                          xlabel='时间',
                                          wtg_pn = self.wtg_pn,
                                          time_pn=self.time_pn,
                                          title=title,
                                          point_size=6,
                                          edgecolor='face',
                                          color_map='nipy_spectral',
                                          divide_thre=1.2,
                                          diff_thre = 6,
                                          sharpness=500,
                                          loc='lower left',
                                          unit='℃',
                                          if_hlines=if_h,
                                          notation=True,
                                          save_fig=False)
            if fig is not None:
                fig_ls.append(fig)
        return fig_ls

class Kuntouling_jinfeng():
    def __init__(self,raw_data,theory_pw_cur,
    phase_name = '魁通沟金风四期',
    wtg_pn='device_id',
    time_pn = 'data_time',
    type_pn = '风机类型',
    P_pn = '发电机有功功率',
    w_pn = '风速',
    angle_pn = '桨叶片角度1',
    inter_angle_pn = '机舱与风向夹角',
    generator_speed_pn = '发电机转速',
    blade_dif_pn = 'blade_dif',
    cabin_temp_pn = '舱内温度',
    Large_components_temp = ['发电机轴承温度1', '发电机轴承温度2',],
    generator_temp = ['发电机绕组温度1','发电机绕组温度2', '发电机绕组温度3', '发电机绕组温度4',
       '发电机绕组温度5', '发电机绕组温度6', '发电机绕组温度7', '发电机绕组温度8', '发电机绕组温度9','发电机绕组温度10',
       '发电机绕组温度11', '发电机绕组温度12'],
    pitch_motor_temp =  ['1号变桨电机温度', '2号变桨电机温度','3号变桨电机温度']) -> None:
        self.phase_name = phase_name
        self.wtg_pn = wtg_pn
        self.time_pn = time_pn
        self.type_pn = type_pn
        self.P_pn = P_pn
        self.w_pn = w_pn
        self.angle_pn = angle_pn
        self.inter_angle_pn = inter_angle_pn
        self.cabin_temp_pn = cabin_temp_pn
        self.blade_dif_pn = blade_dif_pn
        self.generator_speed_pn = generator_speed_pn
        self.generator_speed_square = '平均发电机转速平方'
        self.generator_speed_square_standard = '发电机转速平方(去量纲)'
        self.generator_torque_pn = '平均发电机转矩'
        self.inter_angle_bin = '机舱与风向夹角_bin'
        self.full_time_pn = 'full_time'
        self.wind_pn_bin = '风速_bin'
        self.Large_components_temp_ls = Large_components_temp
        self.generator_temp_ls = generator_temp
        self.pitch_motor_temp_ls = pitch_motor_temp

        ## 整理原始数据
        self.raw_data = raw_data[[self.wtg_pn,
                                  self.time_pn,
                                  self.type_pn,
                                  self.P_pn,
                                  self.w_pn,
                                  self.angle_pn,
                                  self.inter_angle_pn,
                                  self.blade_dif_pn,
                                  self.generator_speed_pn,
                                  self.cabin_temp_pn,
                                    ]+self.Large_components_temp_ls+
                                    self.generator_temp_ls+
                                    self.pitch_motor_temp_ls]
        if 'Unnamed: 235' in  self.raw_data.columns:
            self.raw_data = self.raw_data.drop('Unnamed: 235',axis=1)
        self.raw_data[self.time_pn] = pd.to_datetime(self.raw_data[self.time_pn])
        self.wtg_list =self.raw_data[[self.wtg_pn,self.type_pn]].drop_duplicates().reset_index(drop=True)

        ## 理论功率数据
        self.theory_pw_cur = theory_pw_cur



    def limit_power(self,angle_threshold=1,
                    gap_threshold=0.1,
                    pw_threshold=0,
                    wtg_multi_type=True):
        
        self.gen_data, self.raw_data_1,unlimit_data_size = limit_power_detect_loc_Goldwind(self.raw_data,
                                                                                           self.theory_pw_cur,
                                                                                           wtg_pn=self.wtg_pn,
                                                                                           time_pn=self.time_pn,
                                                                                           wind_pn=self.w_pn,
                                                                                           P_pn=self.P_pn,
                                                                                           blade_angle_pn=self.angle_pn,
                                                                                           angle_thr=angle_threshold,
                                                                                           blade_angle_dif_pn = self.blade_dif_pn,
                                                                                           gap_thr=gap_threshold,
                                                                                           pw_thr=pw_threshold,
                                                                                           multiple_type=wtg_multi_type)
        
        figure_limit_power = plot_limit_power(self.raw_data_1,
                                              self.gen_data,
                                              self.theory_pw_cur,
                                              x_pn=self.w_pn,
                                              y_pn=self.P_pn)
        size_change = (self.raw_data.shape[0],unlimit_data_size,self.gen_data.shape[0])
        return figure_limit_power,size_change
    
    def full_time(self,
                  pw_diff_threshold=[1000,1000],
                  type_ls = ['GW121_2500','GW140_3400'],
                  rated_pw_ls = [2500,3400,]):
        all_wtg = []
        for _,wtg_info in self.wtg_list.iterrows():
            # print(wtg_info)
            wtg,type = wtg_info
            wtg_dataframe = self.raw_data[self.raw_data[self.wtg_pn]==wtg].reset_index(drop=True).sort_values(by=self.time_pn)
            for j in range(len(type_ls)):
                if type_ls[j] == type:
                    df_ft = gen_full_time(wtg_dataframe,
                                          threshold = pw_diff_threshold[j],
                                          full_pw=rated_pw_ls[j],
                                          time_pn = self.time_pn,
                                          Pw_pn = self.P_pn,
                                          full_time_pn=self.full_time_pn)
                    all_wtg.append(df_ft)

        self.all_data = pd.concat(all_wtg,axis=0)


    def get_all_data(self,):
        scene_list = self.Large_components_temp_ls + self.generator_temp_ls
        for scene in scene_list:
            self.all_data[f'{scene}温升({scene}-舱内温度)'.replace('温度温升','温升')] = self.all_data[scene] - self.all_data[self.cabin_temp_pn]
            self.full_pw = self.all_data[self.all_data[self.full_time_pn]>60].sort_values(by=[self.wtg_pn,self.time_pn]).reset_index(drop=True)

    

    def torque_speed_warning(self,
                             ticks_x_n = 10,
                             u_bound = [13,11.5],
                             l_bound=[8.3,7],
                             r_speed=[13.6,12.1],
                             r_torque=[188.5,290],
                             thre=[15,15]):
        
        self.torque_speed_data = self.gen_data[abs(self.gen_data[self.generator_speed_pn])<2000].reset_index(drop=True)
        self.torque_speed_data[self.generator_torque_pn] = np.where(self.torque_speed_data[self.generator_speed_pn]>1,self.torque_speed_data[self.P_pn]/self.torque_speed_data[self.generator_speed_pn],np.NaN)
        # self.torque_speed_data[self.P_pn] / self.torque_speed_data[self.generator_speed_pn]
        self.torque_speed_data[self.generator_speed_square] = self.torque_speed_data[self.generator_speed_pn]**2
        self.torque_speed_data[self.generator_speed_square_standard] = self.torque_speed_data[self.generator_speed_square]/10

        results = []
        torque_fig_ls = []
        for _,wtg_info in self.wtg_list.iterrows():
            wtg_id,types = wtg_info
            wtg_data = self.torque_speed_data[self.torque_speed_data[self.wtg_pn]==wtg_id].reset_index(drop=True)
            t2 = f'{wtg_id}最小二乘拟合,型号{types}'
            if types=='GW121_2500':
                k,figure1 = rated_speed_torque(wtg_data,
                                               self.generator_speed_square_standard,
                                               self.generator_torque_pn,
                                               limit_pn=self.generator_speed_pn,
                                               title=t2,
                                               path=None,
                                               x_ticks_n=ticks_x_n,
                                               upper=u_bound[0],
                                               lower=l_bound[0],
                                               rated_speed=r_speed[0],
                                               rated_torque=r_torque[0],
                                               standardize_times=10,
                                               outlier_thre=thre[0],
                                               save_figure=False,
                                               legend_loc='lower right')
            elif types=='GW140_3400':
                k,figure1 = rated_speed_torque(wtg_data,
                                               self.generator_speed_square_standard,
                                               self.generator_torque_pn,
                                               limit_pn=self.generator_speed_pn,
                                               title=t2,
                                               path=None,
                                               x_ticks_n=ticks_x_n,
                                               upper=u_bound[1],
                                               lower=l_bound[1],
                                               rated_speed=r_speed[1],
                                               rated_torque=r_torque[1],
                                               outlier_thre=thre[1],
                                               standardize_times=10,
                                               save_figure=False,
                                               legend_loc='lower right')
            results.append([wtg_id,types,k])
            torque_fig_ls.append(figure1)

        torque_results_df = pd.DataFrame(results)
        torque_results_df.columns=['风机号','风机型号','斜率']
        return torque_results_df,torque_fig_ls

    def yaw_warning(self):
        self.yaw_data = self.gen_data
        self.yaw_data[self.inter_angle_pn] = np.where(self.yaw_data[self.inter_angle_pn]>180,self.yaw_data[self.inter_angle_pn]-360,self.yaw_data[self.inter_angle_pn])
        self.yaw_data = self.yaw_data[(self.yaw_data[self.inter_angle_pn]>=-15.25)&(self.yaw_data[self.inter_angle_pn]<=15.25)].reset_index(drop=True)
        bs2 = np.arange(-15.5,16,1)
        ls2 = np.arange(-15,16,1)

                #风速分仓
        bs1 = np.arange(4,8,0.5)
        ls1 = np.arange(4.5,8,0.5)
        self.yaw_data[self.wind_pn_bin] = pd.cut(self.yaw_data[self.w_pn],bins=bs1,right=False,labels=ls1).astype(float)

        self.yaw_data[self.inter_angle_bin] = pd.cut(self.yaw_data[self.inter_angle_pn],bins=bs2,right=False,labels=ls2).astype('float64')
        figure_yaw_angle_hist = plot_yaw_angle(self.yaw_data,self.inter_angle_bin)
        figure_yaw_angle_power_scatter = plot_yaw_scatter(data = self.yaw_data,
                                                          yaw_angle_pn=self.inter_angle_pn,
                                                          w_pn_bin=self.wind_pn_bin,
                                                          wtg_pn=self.wtg_pn,
                                                          wtg_list = self.wtg_list,
                                                          P_pn=self.P_pn,
                                                          label_size=ls1)
        self.yaw_data['P_th'] = self.yaw_data['P_th_bin']/((self.yaw_data['V_bin']/self.yaw_data[self.w_pn])**3)
        yaw_result_df,wtg_result_list = yaw_result_generate(self.wtg_list,
                                                            self.yaw_data,
                                                            self.inter_angle_bin,
                                                            self.angle_pn,
                                                            wtg_pn=self.wtg_pn,
                                                            P_pn=self.P_pn)
        
        return yaw_result_df,figure_yaw_angle_hist,figure_yaw_angle_power_scatter,wtg_result_list

    def blade_warning(self,
                      point_s=10,
                      point_c='r',
                      compare = False):
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
            wtg_data = self.blade_data[self.blade_data[self.wtg_pn]==wtg_id].reset_index(drop=True) if not compare else self.blade_data
            # save_path = ROOT_PATH +f'桨叶角度/{title1}.jpg'
            min_data = self.blade_data[self.blade_data[self.wtg_pn]==wtg_id].reset_index(drop=True)
            min_angle = wtg_data[self.angle_pn].min() if not compare else min_data[self.angle_pn].min()
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
                                       comparison=compare,
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
                                       save_figure=False,
                                       day_interval=10)
            fig_ls_blade.append(figure1)
            fig_ls_blade_time.append(figure2)
            result_list.append([wtg_id,wtg_type,min_angle])
        blade_result_df = pd.DataFrame(result_list)
        blade_result_df.columns = ['风机号','风机型号','桨叶角度最小值']
        return blade_result_df,fig_ls_blade,fig_ls_blade_time,fig_ls_blade_type

    def set_error_threshold(self,
                            path = None):
        if os.path.exists(path):
            self.scene_df = pd.read_excel(path)
        else:
            scene_list =  self.Large_components_temp_ls + self.generator_temp_ls
            warning_thre = [75]*2 + [None]*12
            error_thre = [80]*2 + [140]*12
            abnormal_thre =[70]*2 + [130]*12 
            abnormal_thre2 = [60]*2 + [120]*12 
            self.scene_df = pd.DataFrame({'scene_name':scene_list,'abnormal_thre':abnormal_thre,'warning_thre':warning_thre,'error_thre':error_thre,'abnormal_thre_k':abnormal_thre2})

    def gen_Large_components_temp(self,
                                  if_notation=True):
        figure_list = []
        for _,scene_info in self.scene_df.iterrows():
            scene,abnormal,warning,error,abnormal_k = scene_info
            # print(scene)
            title1 = f'满发60分钟后{scene}'
            title2 = f'满发60分钟后{scene}温升'.replace('温度温升','温升')
            title2 = f'满发60分钟后{scene}温升\n({scene}-舱内温度)'.replace('温度温升','温升')
            # save_path = 'D:\OneDrive - CUHK-Shenzhen/1 新天\数字运营部 任务\昆头岭手动分析/6、7月/'+ scene+'.png'
            fig1 = plot_scene(self.full_pw,
                              scene,
                              'tab20',
                              '温度（℃）',
                              '次数',
                              style=None,
                              edgecolor='face',
                              point_size=20,
                              point_alpha = 1,
                              title=title1,
                              time_pn=self.time_pn,
                              wtg_pn = self.wtg_pn,
                              legend_cols=2,
                              hlines=[abnormal,warning,error,abnormal_k],
                              notation=if_notation,
                              save_fig=False)

            fig2 = plot_scene(self.full_pw,
                              f'{scene}温升({scene}-舱内温度)'.replace('温度温升','温升'),
                              'tab20',
                              '温度（℃）',
                              '次数',
                              style=None,
                              edgecolor='face',
                              point_size=20,
                              point_alpha = 1,
                              title=title2,
                              time_pn=self.time_pn,
                              wtg_pn =  self.wtg_pn,
                              legend_cols=2,
                              hlines=[None,None,None,abnormal_k],
                              notation=if_notation,
                              save_fig=False)
            figure_list.append(fig1)
            figure_list.append(fig2)        
        return figure_list
    def gen_Large_components_temp_single(self,
                                         if_notation=True):
        figure_list = []
        for _,scene_info in self.scene_df.iterrows():
            scene,abnormal,warning,error,abnormal_k = scene_info
            # print(scene)
            for _,wtg_info in self.wtg_list.iterrows():
                wtg_id,_ = wtg_info
                title1 = f'{wtg_id}风机{scene}'
                wtg_data = self.all_data[self.all_data[self.wtg_pn]==wtg_id].reset_index(drop=True)
                fig1 = plot_single_scene(wtg_data,
                                scene,
                                '温度（℃）',
                                '时间',
                                style=None,
                                edgecolor='face',
                                point_size=15,
                                point_alpha = 1,
                                title=title1,
                                time_pn=self.time_pn,
                                wtg_pn = self.wtg_pn,
                                wtg_id = wtg_id,
                                hlines=[abnormal,warning,error,abnormal_k],
                                notation=if_notation,
                                save_fig=False,
                                day_sep=10)
                if fig1 is not None:
                    figure_list.append(fig1)      
        return figure_list  
    def gen_generator_Temp(self,
                           if_h=True,):
        scene_comparison = self.generator_temp_ls
        fig_ls = []
        for _,wtg_info in self.wtg_list.iterrows():
            wtg_id,_ = wtg_info
            title =  f'{wtg_id}风机满发后发电机绕组温度预警'
            fig = plot_comparison_divide(dataframe=self.full_pw,
                                         wtg_id=wtg_id,
                                         point_names=scene_comparison,
                                         ylabel='温度(℃)',
                                         xlabel='次数',
                                         wtg_pn = self.wtg_pn,
                                         time_pn=self.time_pn,
                                         title= title,
                                         point_size=15,
                                         edgecolor='face',
                                         divide_thre = 1.2,
                                         diff_thre = 6,
                                         loc='lower left',
                                         if_hlines=if_h,
                                         day_sep=10,
                                         save_fig=False)
            if fig is not None:
                fig_ls.append(fig)
        return fig_ls


    def gen_pitch_motor_Temp(self,
                           if_h=True,):
        scene_comparison2 = self.pitch_motor_temp_ls
        fig_ls = []
        for i,wtg_info in self.wtg_list.iterrows():
            wtg_id,_ = wtg_info
            title =  f'{wtg_id}变桨电机温度预警'
            fig =  plot_comparison_divide(dataframe = self.all_data,
                                          wtg_id=wtg_id,
                                          point_names=scene_comparison2,
                                          ylabel='温度(℃)',
                                          xlabel='时间',
                                          wtg_pn = self.wtg_pn,
                                          time_pn=self.time_pn,
                                          title=title,
                                          point_size=6,
                                          edgecolor='face',
                                          color_map='nipy_spectral',
                                          divide_thre=1.2,
                                          diff_thre = 6,
                                          sharpness=500,
                                          loc='lower left',
                                          unit='℃',
                                          if_hlines=if_h,
                                          notation=True,
                                          day_sep=10,
                                          save_fig=False)
            if fig is not None:
                fig_ls.append(fig)
        return fig_ls
