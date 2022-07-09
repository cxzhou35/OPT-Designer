from cal_items import *

# 本部分将所有计算根据计算过程归结为9类
# 1：焦距、主面位置、出瞳距 2：像距 3：像高 4：球差 5：位置色差
# 6：场曲、像散 7：畸变 8：倍率色差 9：彗差


def cal_type1(ray0, optical_system):
    """计算焦距、主面位置、出瞳距 \n
        ray0 无穷远的第一近轴光 \n
        optical_system 光学系统 \n
        返回值：[焦距, lh']"""
    # ray0 示例，调试时可以取消注释
    # ray0 = ray(0, -INF, dray, first_near_axis_ray, True, 0, 10, 0, 1, 0)  # 类型1 焦距、主面位置
    optical_system.inner_ray_wl = ray0.wavelength
    optical_system.adjust_curve_obj(ray0)  # 调整物面
    optical_system.adjust_curve_img(ray0)  # 调整像面
    optical_system.get_f()  # 获得焦距
    ray0.get_umax_wmax(optical_system.curve_list[1])  # 获得入射光最大孔径、视场
    ray0.initialize(optical_system)  # 初始化光线
    l = cal_l(ray0, optical_system)  # 获得像距
    lh = cal_lh(l, optical_system.f)  # 像距-焦距=lh'
    ray1 = ray(0, -INF, ray0.wavelength, second_near_axis_ray, True, 0, 0, angle2rad(3), 0, 1)  # 出瞳距
    lp = cal_type2(ray1, optical_system)
    lp = lp[0]
    return [optical_system.f, lh, lp]


def cal_type2(ray1, optical_system):
    """计算像距 \n
            ray1 任意光线 \n
            optical_system 光学系统 \n
            返回值：[像距]"""
    # ray1 示例，调试时可以取消注释
    # ray1 = ray(0, -500, 0.587562, real_ray, False, 26, 10, 0, 0.7, 0)  # 类型2 像距 出瞳距
    # ray1 = ray(0, -INF, 0.587562, second_near_axis_ray, True, 0, 0, angle2rad(3), 0, 1)  # 出瞳距
    optical_system.adjust_curve_obj(ray1)  # 调整物面
    optical_system.adjust_curve_img(ray1)  # 调整像面
    ray1.get_umax_wmax(optical_system.curve_list[1])  # 获得最大视场和孔径
    ray1.initialize(optical_system)  # 初始化
    l = cal_l(ray1, optical_system)  # 计算像距
    return [l]


def cal_type3(ray1, optical_system):
    """计算像高 \n
        ray1 任意光线 \n
        optical_system 光学系统 \n
        返回值：[像高]"""
    # ray1 示例，调试时可以取消ray1前的注释
    # ray0 = ray(0, -500, 0.587562, real_ray, False, 26, 10, 0, 0, 1)  # 实际光线像高  类型3 像高
    # ray1 = ray(0, -INF, dray, second_near_axis_ray, True, 0, 0, angle2rad(3), 0, 1)  # 理想像高
    # ray1 = ray(0, -500, fray, real_ray, False, 26, 10, 0, 0, 1)
    ray0 = ray(-1, ray1.l_obj, dray, ray1.raytype, ray1.inf_flag, ray1.y_max, ray1.h_max, ray1.w_max, ray1.K_eta,
               ray1.K_w)  # 实例化一条和ray1其他参数一致的d光调整像面！！
    optical_system.adjust_curve_obj(ray0)  # 用d光调整物面
    optical_system.adjust_curve_img(ray0)  # 用d光调整像面
    ray1.get_umax_wmax(optical_system.curve_list[1])  # 获得ray1最大视场、孔径
    ray1.initialize(optical_system)  # 初始化ray1
    y = cal_y(ray1, optical_system)  # 计算像高
    return [y]


def cal_type4(ray0, ray1, optical_system):
    """计算两条光线球差 \n
        ray0 第一近轴光线 \n
        ray1 实际光线 \n
        optical_system 光学系统 \n
        返回值：[球差]"""
    # ray0 ray1 示例，调试时可以取消一组ray0和ray1前的注释
    # ray0 = ray(0, -INF, dray, first_near_axis_ray, True, 0, 10, 0, 1, 0)  #  类型4 球差
    # ray1 = ray(1, -INF, dray, real_ray, True, 0, 10, 0, 1, 0)  # 无穷远
    # ray0 = ray(0, -500, dray, first_near_axis_ray, False, 26, 10, 0, 1, 0)
    # ray1 = ray(0, -500, dray, real_ray, False, 26, 10, 0, 1, 0)  # 有限远物
    optical_system.adjust_curve_obj(ray0)  # 调整物面
    optical_system.adjust_curve_img(ray0)  # 调整像面
    ray0.get_umax_wmax(optical_system.curve_list[1])  # 获得最大视场、孔径
    ray0.initialize(optical_system)  # 初始化光线
    ray1.get_umax_wmax(optical_system.curve_list[1])  # 获得最大视场、孔径
    ray1.initialize(optical_system)  # 初始化光线

    ray0.wavelength = dray
    l0 = cal_l(ray0, optical_system)  # 计算理想像距
    l1 = cal_l(ray1, optical_system)  # 计算实际像距
    sp = cal_sp(l1, l0)  # 计算球差
    return [sp]


def cal_type5(ray0, ray1, optical_system):
    """计算两条光线位置色差 \n
        ray0 实际光线，且为f光 \n
        ray1 实际光线，且为c光 \n
        optical_system 光学系统 \n
        返回值：[位置色差]"""
    # ray0 ray1 示例，调试时可以取消一组ray0和ray1前的注释
    # ray0 = ray(0, -INF, fray, real_ray, True, 0, 10, 0, 1, 0)  # 类型5 位置色差
    # ray1 = ray(1, -INF, cray, real_ray, True, 0, 10, 0, 1, 0)  # 无穷远
    # ray0 = ray(0, -500, fray, real_ray, False, 26, 10, 0, 1, 0)
    # ray1 = ray(0, -500, cray, real_ray, False, 26, 10, 0, 1, 0)  # 有限远物
    optical_system.adjust_curve_obj(ray0)  # 调整物面
    optical_system.adjust_curve_img(ray0)  # 调整像面
    ray0.get_umax_wmax(optical_system.curve_list[1])  # 获得光线最大孔径、视场
    ray0.initialize(optical_system)  # 初始化光线
    ray1.get_umax_wmax(optical_system.curve_list[1])  # 获得光线最大孔径、视场
    ray1.initialize(optical_system)  # 初始化光线

    l0 = cal_l(ray0, optical_system)  # 计算f光像距
    l1 = cal_l(ray1, optical_system)  # 计算c光像距
    chro = cal_chro_l(l0, l1)  # 计算位置色差
    return [chro]


def cal_type6(ray1, ray2, optical_system):
    """计算两条光线场曲、像散 \n
        ray1 第一近轴光线 \n
        ray2 第二近轴光线 \n
        optical_system 光学系统 \n
        返回值：[子午场曲 弧矢场曲 像散]"""
    # ray1 ray2 示例，调试时可以取消一组ray1和ray2前的注释
    # ray1 = ray(0, -INF, 0.58756, first_near_axis_ray, True, 0, 10, 0, 1, 0)  # 类型6 像散，场曲
    # ray2 = ray(1, -INF, 0.58756, second_near_axis_ray, True, 0, 0, angle2rad(3), 0, 1)  # 物无穷远
    # ray1 = ray(0, -500, 0.58756, first_near_axis_ray, False, 0, 10, 0, 1, 0)
    # ray2 = ray(0, -500, 0.58756, second_near_axis_ray, False, 26, 10, 0, 0, 1)  # 物有限远
    ray0 = ray(-1, ray1.l_obj, dray, first_near_axis_ray, ray1.inf_flag, ray1.y_max, ray1.h_max, ray1.w_max,
               ray1.K_eta, ray1.K_w)  # 实例化用于调整像面的d光
    optical_system.adjust_curve_obj(ray0)  # 用第一近轴光调整物面
    optical_system.adjust_curve_img(ray0)  # 用第一近轴光调整像面
    ray1.get_umax_wmax(optical_system.curve_list[1])  # 获得最大孔径、视场
    ray1.initialize(optical_system)  # 初始化光线
    ray2.get_umax_wmax(optical_system.curve_list[1])  # 获得最大孔径、视场
    ray2.initialize(optical_system)  # 初始化光线
    ray3 = copy.deepcopy(ray1)  # 深拷贝第一近轴光
    ray4 = copy.deepcopy(ray2)  # 深拷贝第二近轴光
    xt = cal_cur_t(ray1, ray2, optical_system)  # 计算子午场曲
    xs = cal_cur_s(ray3, ray4, optical_system)  # 计算弧矢场曲
    delta_ts = cal_ast(xt, xs)  # 计算像散
    return [xt, xs, delta_ts]


def cal_type7(ray1, ray2, optical_system):
    """计算两条光线绝对畸变、相对畸变 \n
        ray1 第二近轴光线 用于通过y'=beta*y 或 y'=f'tanW 计算理想像高 \n
        ray2 实际光线 用于计算实际像高\n
        optical_system 光学系统 \n
        返回值：[绝对畸变 相对畸变]"""
    # ray1 ray2 示例，调试时可以取消一组ray1和ray2前的注释
    # ray1 = ray(0, -INF, dray, second_near_axis_ray, True, 0, 0, angle2rad(3), 0, 1)  # 类型7 畸变
    # ray2 = ray(0, -INF, dray, real_ray, True, 0, 0, angle2rad(3), 0, 1)  # 无穷远
    # ray1 = ray(0, -500, dray, second_near_axis_ray, False, 26, 10, 0, 0, 1)
    # ray2 = ray(0, -500, dray, real_ray, False, 26, 10, 0, 0, 1)  # 有限远
    ray0 = ray(-1, ray1.l_obj, ray1.wavelength, ray1.raytype, ray1.inf_flag, ray1.y_max, ray1.h_max, ray1.w_max,
               ray1.K_eta,
               ray1.K_w)  # 实例化一条第一近轴光计算像面
    optical_system.adjust_curve_obj(ray0)  # 用第一近轴光调整物面
    optical_system.adjust_curve_img(ray0)  # 用第一近轴光调整像面
    ray1.get_umax_wmax(optical_system.curve_list[1])  # 获得最大孔径、视场
    ray1.initialize(optical_system)  # 初始化光线
    ray2.get_umax_wmax(optical_system.curve_list[1])  # 获得最大孔径、视场
    ray2.initialize(optical_system)  # 初始化光线
    y_ideal = cal_y(ray1, optical_system)  # 计算理想像高
    y_real = cal_y(ray2, optical_system)  # 计算实际像高
    res = cal_abe(y_real, y_ideal)  # 计算绝对畸变、相对畸变
    return res


def cal_type8(ray1, ray2, optical_system):
    """计算两条光线倍率色差 \n
        ray1 实际光线，且为f光\n
        ray2 实际光线，且为c光\n
        optical_system 光学系统 \n
        返回值：[倍率色差]"""
    # ray1 ray2 示例，调试时可以取消一组ray1和ray2前的注释
    # ray1 = ray(0, -500, fray, real_ray, False, 26, 10, 0, 0, 1)   # 类型8 倍率色差
    # ray2 = ray(1, -500, cray, real_ray, False, 26, 10, 0, 0, 1)  # 有限远
    # ray1 = ray(0, -INF, fray, real_ray, True, 0, 0, angle2rad(3), 0, 1)
    # ray2 = ray(0, -INF, cray, real_ray, True, 0, 0, angle2rad(3), 0, 1) # 无穷远
    ray0 = ray(-1, ray1.l_obj, dray, ray1.raytype, ray1.inf_flag, ray1.y_max, ray1.h_max, ray1.w_max,
               ray1.K_eta, ray1.K_w)  # 实例化一条和ray1其他属性一致的d光，用于计算像面位置
    optical_system.adjust_curve_obj(ray0)  # 用d光调整物面
    optical_system.adjust_curve_img(ray0)  # 用d光调整像面
    ray1.get_umax_wmax(optical_system.curve_list[1])  # 获得最大孔径、视场
    ray1.initialize(optical_system)  # 初始化光线
    ray2.get_umax_wmax(optical_system.curve_list[1])  # 获得最大孔径、视场
    ray2.initialize(optical_system)  # 初始化光线
    y_f = cal_y(ray1, optical_system)  # 计算f光实际像高
    y_c = cal_y(ray2, optical_system)  # 计算c光实际像高
    delta_fc = cal_chro_y(y_f, y_c)  # 计算倍率色差
    return [delta_fc]


def cal_type9(ray0, ray1, ray2, optical_system):
    """用三条光线计算彗差 \n
        ray0 实际光线，且为主光线 K_eta = 0 \n
        ray1 实际光线，上光线 K_eta = K_eta_max \n
        ray2 实际光线，下光线 K_eta = -K_eta_max \n
        optical_system 光学系统 \n
        返回值：[慧差]"""
    # ra0 ray1 ray2 示例，调试时可以取消一组ray0、ray1和ray2前的注释
    # ray0 = ray(0, -INF, 0.58762, real_ray, True, 0, 10, angle2rad(3), 0, 1)  # 类型9 彗差，无穷远物
    # ray1 = ray(0, -INF, 0.58762, real_ray, True, 0, 10, angle2rad(3), 0.7, 1)
    # ray2 = ray(0, -INF, 0.58762, real_ray, True, 0, 10, angle2rad(3), -0.7, 1)
    # ray0 = ray(0, -500, 0.58762, real_ray, False, 26, 10, 0, 0, 0.7)  # 有限远物
    # ray1 = ray(0, -500, 0.58762, real_ray, False, 26, 10, 0, 0.7, 0.7)
    # ray2 = ray(0, -500, 0.58762, real_ray, False, 26, 10, 0, -0.7, 0.7)
    optical_system.adjust_curve_obj(ray0)  # 用主光线调整物面
    optical_system.adjust_curve_img(ray0)  # 用主光线调整像面
    ray0.get_umax_wmax(optical_system.curve_list[1])  # 获得最大孔径、视场
    ray0.initialize(optical_system)  # 初始化光线
    ray1.get_umax_wmax(optical_system.curve_list[1])  # 获得最大孔径、视场
    ray1.initialize(optical_system)  # 初始化光线
    ray2.get_umax_wmax(optical_system.curve_list[1])  # 获得最大孔径、视场
    ray2.initialize(optical_system)  # 初始化光线

    y_main = cal_y(ray0, optical_system)  # 计算主光线像高
    y_up = cal_y(ray1, optical_system)  # 计算上光线像高
    y_down = cal_y(ray2, optical_system)  # 计算下光线像高

    Kt = cal_coma(y_up, y_down, y_main)  # 计算彗差
    return [Kt]


def cal_main(cal_type, ray_list, opt_sys):
    """九种计算的接口，统一九种计算\n
        cal_type 计算的类型，1-9有效 \n
        1：焦距、主面位置 2：像距或出瞳距 3：像高 \n
        4：球差 5：位置色差 6：场曲、像散 \n
        7：畸变 8：倍率色差 9：彗差 \n
        ray_list 输入的光线列表 \n
        opt_sys 光线系统 \n
        返回值：计算结果构成的矩阵的列表 如计算畸变，返回[[绝对畸变 相对畸变]] 内层为np.array 外层为list"""
    if cal_type == 1:
        return [np.array(cal_type1(ray_list[0], opt_sys))]
    if cal_type == 2:
        return [np.array(cal_type2(ray_list[0], opt_sys))]
    if cal_type == 3:
        return [np.array(cal_type3(ray_list[0], opt_sys))]
    if cal_type == 4:
        return [np.array(cal_type4(ray_list[0], ray_list[1], opt_sys))]
    if cal_type == 5:
        return [np.array(cal_type5(ray_list[0], ray_list[1], opt_sys))]
    if cal_type == 6:
        return [np.array(cal_type6(ray_list[0], ray_list[1], opt_sys))]
    if cal_type == 7:
        return [np.array(cal_type7(ray_list[0], ray_list[1], opt_sys))]
    if cal_type == 8:
        return [np.array(cal_type8(ray_list[0], ray_list[1], opt_sys))]
    if cal_type == 9:
        return [np.array(cal_type9(ray_list[0], ray_list[1], ray_list[2], opt_sys))]
