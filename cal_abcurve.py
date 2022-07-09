from cal import *


def cal_axial_curve(ray0, curve_list, K_eta_list):
    """根据输入的光线计算色球差曲线数据 \n
        ray0 光线 \n
        curve_list 曲面列表 \n
        K_eta_list 孔径取点系数列表 \n
        返回值 [[d光球差数据],[f光球差数据],[c光球差数据]]"""
    wl_list = [dray, fray, cray]  # 三种波长列表，计算色球差用
    # K_eta_list = [0.001, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65,  0.707, 0.75, 0.8,
    #              0.85, 0.9, 0.95, 1]  # 孔径取点系数
    result = []  # 三种颜色球差的列表构成的列表
    res = []  # 储存一种颜色球差列表

    for wl in wl_list:  # 对不同的波长循环
        res = []
        for item in K_eta_list:  # 循环计算不同孔径下的球差
            K_eta = item * ray0.K_eta  # 新孔径系数 = 取点系数 * 原孔径系数
            # ray0 = ray(0, -INF, dray, first_near_axis_ray, True, 0, 10, 0, item, 0)
            ray0.wavelength = wl  # 分别代入d、f、c光
            ray1 = ray(1, ray0.l_obj, dray, first_near_axis_ray, ray0.inf_flag, ray0.y_max, ray0.h_max, ray0.w_max,
                       K_eta, ray0.K_w)  # 实例化理想光线
            ray2 = ray(2, ray0.l_obj, wl, real_ray, ray0.inf_flag, ray0.y_max, ray0.h_max, ray0.w_max, K_eta,
                       ray0.K_w)  # 实例化无穷远光线
            ray_list = [ray1, ray2]
            opt_sys = optsys(curve_list)  # 实例化光学系统
            data = cal_main(4, ray_list, opt_sys)  # 计算一种波长、一个取点系数下球差
            res.append(data[0][0])

        result.append(res)

    return result


def cal_lateral_color_curve(ray0, curve_list, K_w_list):
    """根据输入的光线计算倍率色差曲线数据 \n
         ray0 光线 \n
         curve_list 曲面列表 \n
         K_w_list 视场去点系数列表 \n
         返回值 [倍率色差数据]"""
    # K_w_list = [0.001, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65,  0.707, 0.75, 0.8,
    #             0.85, 0.9, 0.95, 1]
    result = []  # 储存位置色差数据的列表

    for item in K_w_list:  # 循环计算各个视场下的倍率色差
        K_w = item * ray0.K_w  # 新视场系数 = 取点系数 * 原视场取点系数
        ray1 = ray(1, ray0.l_obj, fray, real_ray, ray0.inf_flag, ray0.y_max, ray0.h_max, ray0.w_max,
                   ray0.K_eta, K_w)  # 实例化f光实际光线
        ray2 = ray(2, ray0.l_obj, cray, real_ray, ray0.inf_flag, ray0.y_max, ray0.h_max, ray0.w_max,
                   ray0.K_eta, K_w)  # 实例化c光实际光线
        ray_list = [ray1, ray2]  # 构造光线列表
        opt_sys = optsys(curve_list)  # 实例化光学系统
        data = cal_main(8, ray_list, opt_sys)  # 计算一个视场下的倍率色差
        result.append(data[0][0])  # 将结果添加至列表

    return result


def cal_filed_curvature_curve(ray1, ray2, curve_list, K_w_list):
    """根据输入的光线计算场曲曲线数据 \n
         ray0 光线 \n
         curve_list 曲面列表 \n
         K_w_list 视场去点系数列表 \n
         返回值 [[d光子午场曲数据],[d光弧矢场曲数据],[f光子午场曲数据],[f光弧矢场曲数据]，[c光子午场曲数据],[c光弧矢场曲数据]]"""
    wl_list = [dray, fray, cray]
    # K_w_list = [0.001, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.707, 0.75,
    #             0.8, 0.85, 0.9, 0.95, 1]
    result = []  # 储存各个波长的场曲数据列表的列表
    res_t = []  # 每次循环中储存一种颜色的子午场曲数据
    res_s = []  # 每次循环中储存一种颜色的弧矢场曲数据

    for wl in wl_list:  # 对不同波长循环
        res_t = []
        res_s = []
        for item in K_w_list:  # 循环计算不同视场下场曲
            K_w = item * ray2.K_w  # 新视场系数 = 取点系数 * 原视场取点系数
            ray3 = ray(1, ray1.l_obj, wl, first_near_axis_ray, ray1.inf_flag, ray1.y_max, ray1.h_max, ray1.w_max,
                       ray1.K_eta, K_w)  # 实例化第一近轴光
            ray4 = ray(2, ray2.l_obj, wl, second_near_axis_ray, ray2.inf_flag, ray2.y_max, ray2.h_max, ray2.w_max,
                       ray2.K_eta, K_w)  # 实例化第二近轴光
            ray_list = [ray3, ray4]  # 构造光线列表
            opt_sys = optsys(curve_list)  # 实例化光学系统
            data = cal_main(6, ray_list, opt_sys)  # 计算一个视场下的场曲
            res_t.append(data[0][0])  # 将弧矢场曲添加至res_t
            res_s.append(data[0][1])  # 将子午场曲添加至res_s

        result.append(res_t)
        result.append(res_s)

    return result


def cal_distortion_curve(ray0, curve_list, K_w_list):
    """根据输入的光线计算不同颜色相对畸变曲线数据 \n
         ray0 光线 \n
         curve_list 曲面列表 \n
         K_w_list 视场取点系数列表 \n
         返回值 [[d光相对畸变曲线数据],[f光相对畸变曲线数据],[c光相对畸变曲线数据]]"""
    wl_list = [dray, fray, cray]
    # K_w_list = [0.001, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.707, 0.75,
    #             0.8, 0.85, 0.9, 0.95, 1]
    result = []  # 储存三种颜色光畸变数据的列表的列表
    res = []  # 每次循环中储存一种颜色的畸变数据

    for wl in wl_list:  # 对不同波长循环
        res = []
        for item in K_w_list:  # 循环计算不同视场的相对畸变数据
            K_w = item * ray0.K_w  # 新视场系数 = 取点系数 * 原视场取点系数
            ray1 = ray(1, ray0.l_obj, wl, second_near_axis_ray, ray0.inf_flag, ray0.y_max, ray0.h_max, ray0.w_max,
                       ray0.K_eta, K_w)  # 实例化第二近轴光
            ray2 = ray(2, ray0.l_obj, wl, real_ray, ray0.inf_flag, ray0.y_max, ray0.h_max, ray0.w_max,
                       ray0.K_eta, K_w)  # 实例化实际光线
            ray_list = [ray1, ray2]  # 构造光线列表
            opt_sys = optsys(curve_list)  # 实例化光学系统
            data = cal_main(7, ray_list, opt_sys)  # 计算畸变
            res.append(data[0][1])  # 将相对畸变加入res

        result.append(res)

    return result


def cal_abcurve(ray_list, opt_sys, cal_type):
    pass
