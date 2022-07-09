import numpy as np
import pandas as pd
from curve_and_ray import curve, ray, obj
from math import *


# read the curve data from file
def read_curve_data():
    df = pd.read_csv(r'data/curve.csv', index_col=0, keep_default_na=False)
    curve_list = []
    index = df.index.values
    item_list = [item for item in index if item != ""]
    # print(f"item_list: {item_list}")
    for item in item_list:
        num = int(float(item))
        d = float(df.at[item, '到下一面的距离'])
        r = float(df.at[item, '曲率半径'])
        material = int(float(df.at[item, '材料']))
        D = float(df.at[item, '口径'])

        curve_temp = curve(num, d, r, material, D)
        curve_list.append(curve_temp)

    return curve_list


# read the ray data from file
def read_ray_data():
    df = pd.read_csv(r'data/ray.csv', index_col=0, keep_default_na=False)
    ray_list = []
    index = df.index.values
    item_list = [item for item in index if item != ""]
    for item in item_list:
        num = int(float(item))    # 编号
        l_obj = float(df.at[item, '物距'])
        if l_obj == np.inf:
            l_obj = -l_obj
        wavelength = float(df.at[item, '波长 (nm)']) * 1.0 / 1000  # 光线波长
        raytype = int(df.at[item, '光线类型'])  # 光线类型
        inf_flag = int(df.at[item, '是否为无穷远'])  # 是否为无穷远光线，True为是，False为否
        if inf_flag == 1:
            inf_flag = True
        else:
            inf_flag = False
        y_max = float(df.at[item, '最大物高'])  # 物最大高度
        h_max = float(df.at[item, '最大入射高度'])  # 光线最大入射高度
        w_max = float(df.at[item, '最大物方视场角']) * 1.0 / 180 * pi  # 光线最大视场角
        K_eta = float(df.at[item, '孔径取点系数'])  # 孔径取点系数
        K_w = float(df.at[item, '视场取点系数'])  # 视场取点系数

        ray_temp = ray(num, l_obj, wavelength, raytype, inf_flag, y_max, h_max, w_max, K_eta, K_w)
        ray_list.append(ray_temp)

    return ray_list


def read_obj_data():
    df = pd.read_csv(r'data/obj.csv', keep_default_na=False)

    l_obj = float(df.at[0, '物距'])
    if l_obj == np.inf:
        l_obj = -l_obj
    wavelength = float(df.at[0, '波长']) * 1.0 / 1000  # 光线波长
    h_max = float(df.at[0, '入瞳半径'])  # 入瞳直径
    y_max = float(df.at[0, '物高'])  # 物最大高度
    w_max = float(df.at[0, '物方视场角']) * 1.0 / 180 * pi  # 光线最大视场角
    K_eta = float(df.at[0, '孔径取点系数'])  # 孔径取点系数
    K_w = float(df.at[0, '视场取点系数'])  # 视场取点系数
    ideal_flag = int(df.at[0, '理想光线追迹'])

    obj_input = obj(l_obj, wavelength, h_max, y_max, w_max, K_eta, K_w, ideal_flag)
    return obj_input


# save the aberration data to file
def save_data(data,cal_flag):
    cal_flag = int(cal_flag)
    header = ['焦距', '像方主面距离', '出瞳距', '像距', '像高', '球差', '位置色差', '子午场曲', '弧矢场曲', '像散', '绝对畸变', '相对畸变', '倍率色差', '子午彗差']
    if cal_flag == 1:
        head_list = header[0:3]
    if cal_flag == 2:
        head_list = [header[3]]
    if cal_flag == 3:
        head_list = [header[4]]
    if cal_flag == 4:
        head_list = [header[5]]
    if cal_flag == 5:
        head_list = [header[6]]
    if cal_flag == 6:
        head_list = header[7:10]
    if cal_flag == 7:
        head_list = header[10:12]
    if cal_flag == 8:
        head_list = [header[12]]
    if cal_flag == 9:
        head_list = [header[13]]
    df = pd.DataFrame(data=data, columns=head_list)
    df.to_csv(r'data/data.csv', encoding="gbk", index=False, mode='a')

def main():
    # read_curve_data()
    # read_ray_data()

    data = [np.array([6.7])]
    save_data(data,3)
    pass

if __name__ == '__main__':
    main()
