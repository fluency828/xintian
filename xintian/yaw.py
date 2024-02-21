import pandas as pd
import numpy as np

def yaw_result_generate(wtg_ls,data_df,yaw_angle_bin_pn='机舱与风向夹角_bin',yaw_angle_pn='机舱与风向夹角',wtg_pn = '风机',P_pn='发电机有功功率'):
    result_wtg_list = []
    topk=[]
    for _,wtg_info in wtg_ls.iterrows():
        wtg_id,wtg_type = wtg_info
        # path = ROOT_PATH + f'偏航对风/{wtg_id}/'
        # if not os.path.exists(path):
        #     os.makedirs(path)
        wtg_data = data_df[data_df[wtg_pn]==wtg_id].reset_index(drop=True)
        gb = wtg_data[['P_th',P_pn,yaw_angle_bin_pn,yaw_angle_pn]].groupby(yaw_angle_bin_pn)
        #各角度计数
        result = pd.DataFrame({'count':gb.count()[yaw_angle_pn]})
        #理论功率之和
        result['P_th']=gb.sum()['P_th']
        result['P_real'] = gb.sum()[P_pn]
        result['K'] = result['P_real']/result['P_th']
        result = result.reset_index()
        result['prob'] = result['count']/result['count'].sum()
        result_wtg_list.append(result)

        result_valid = result[result['count'].rank(ascending=False)<=15]

        target1 = result.iloc[result_valid['K'].idxmin(),:][yaw_angle_bin_pn] #K值最小夹角
        target2 = result.iloc[result_valid['K'].idxmax(),:][yaw_angle_bin_pn] #K值最大夹角
        target3 = result.iloc[result_valid['prob'].idxmax(),:][yaw_angle_bin_pn] #频率最高夹角
        K_0 = result.loc[result[yaw_angle_bin_pn]==0,'K'].values[0] # 0°夹角K值
        K_max= result.iloc[result_valid['K'].idxmax(),:]['K'] # 最高K值
        K_most= result.iloc[result_valid['prob'].idxmax(),:]['K'] # 频率最高夹角对应K值
        K_dif = K_max-K_0 # 最高K值-0°K值
        topk.append([wtg_id,wtg_type,wtg_data.shape[0],target2,target3,abs(target2-target3),round(K_0,4),round(K_max,4),round(K_most,4),round(K_dif,4)])



    warning = pd.DataFrame(topk)
    warning.columns = ['风机号','风机型号','计数','K值最大夹角','频率最高夹角','差值','0°K值','最高K值','频率最高K值','最高K值-0°K值']
    return warning,result_wtg_list 