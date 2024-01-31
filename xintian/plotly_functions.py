
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import streamlit as st
import seaborn as sns

def plotly_limit_power(data_before_delete,data_after_delete,theory_cur_data,x_pn='平均风速',y_pn = '平均电网有功功率',title='限功率前后对比',left_subplot_text = "去除限功率点前",right_subplot_text="去除限功率点后"):
    fig = make_subplots(rows=1, 
                        cols=2,
                        column_widths=[0.5,0.5],  # 重点：两个子图的宽度占比
                        subplot_titles=[left_subplot_text,right_subplot_text]  # 名字
                    ) 
    fig.add_trace(go.Scatter(x=data_before_delete[x_pn],y=data_before_delete[y_pn],mode='markers'),row=1,col=1)
    fig.add_trace(go.Line(x=theory_cur_data['V_bin'],y=theory_cur_data['P_th_bin'],mode='markers'),row=1,col=1)

    fig.add_trace(go.Scatter(x=data_after_delete[x_pn],y=data_after_delete[y_pn],mode='markers'),row=1,col=2)
    fig.add_trace(go.Line(x=theory_cur_data['V_bin'],y=theory_cur_data['P_th_bin'],mode='markers'),row=1,col=2)
    fig.update_layout(autosize=False,width=1400,height=400,
                    title_text=title,
                    margin=dict(
                                    l=10,
                                    r=10,
                                    b=10,
                                    # t=40,
                                    # pad=9
                                )
                        )
    fig.update_xaxes(title_text=x_pn, row=1, col=1)  # 正常显示
    fig.update_xaxes(title_text=x_pn, row=1, col=2)  # 设置范围range
    fig.update_yaxes(title_text=y_pn, row=1, col=1)
    fig.update_yaxes(title_text=y_pn,  row=1, col=2)
    # fig.show()
    return fig

@st.cache_resource(ttl=10800)
def plot_limit_power(data_before_delete,data_after_delete,theory_cur_data,x_pn='平均风速',y_pn = '平均电网有功功率',left_subplot_text = "去除限功率点前",right_subplot_text="去除限功率点后"):
    fig, ax = plt.subplots(1,2,figsize=(20,6))
    ax[0].scatter(data=data_before_delete,x=x_pn,y=y_pn,s=10)
    ax[0].scatter(data=theory_cur_data,x='V_bin',y='P_th_bin')
    ax[0].set_xlabel(x_pn)
    ax[0].set_ylabel(y_pn)
    ax[1].scatter(data=data_after_delete,x=x_pn,y=y_pn,s=10)
    ax[1].scatter(data=theory_cur_data,x='V_bin',y='P_th_bin')
    ax[1].set_xlabel(x_pn,fontdict = {'fontsize':13,'fontweight':'bold'})
    ax[1].set_ylabel(y_pn,fontdict = {'fontsize':13,'fontweight':'bold'})
    # sns.scatterplot(data=data_after_delete,x='V_bin',y='P_bin') #功率散点
    # sns.scatterplot(data=theory_cur_data,x='V_bin',y='P_th_bin') #
    ax[0].set_title(left_subplot_text ,size=20)
    ax[1].set_title(right_subplot_text ,size=20)
    plt.close()
    return fig

@st.cache_resource(ttl=10800)
def plot_yaw_angle(data,yaw_angle_pn,bn=60,figuresize=(8,6)):
    fig,ax = plt.subplots(figsize=figuresize)
    ax.hist(data[yaw_angle_pn],bins=bn)
    plt.close()
    return fig

@st.cache_resource(ttl=10800)
def plot_blade_power_all(blade_df,blade_pn='桨叶角度1',Pw_pn = '发电机有功功率',title='功率-桨叶角度散点图'):
    fig, ax = plt.subplots(figsize=(15,6))
    ax.scatter(data =blade_df,x=blade_pn,y=Pw_pn,s=25,edgecolors='white')
    ax.set_xlabel(blade_pn,fontdict = {'fontsize':13,'fontweight':'bold'})
    ax.set_ylabel(Pw_pn,fontdict = {'fontsize':13,'fontweight':'bold'})
    ax.set_title(title,size=20)
    plt.close()
    return fig