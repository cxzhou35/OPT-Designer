from curve_and_ray import *
from iostream import *
import copy


def angle2rad(angle):
    """角度转化为弧度"""
    return angle / 180 * pi


def rad2angle(rad):
    """弧度化为角度"""
    return rad / pi * 180


def cal_l(ray, opt_sys):
    """计算像距 \n
        ray 已经初始化后的光线 \n
        opt_sys 调整后的光学系统"""
    cur_list = opt_sys.curve_list  # 取出曲面列表

    for i in range(1, len(cur_list) - 1):  # 从物面之后的面遍历到像面之前的面
        cur_last = cur_list[i - 1]  # 上一个面
        cur_this = cur_list[i]  # 当前面
        ray.get_n(cur_last.material, cur_this.material)  # 获取折射率
        flagarray = ray.IsValid(cur_this)  # 进行校验
        if flagarray[0] is False:
            print(f"ERROR!! type:{flagarray[1]}")
            break
        ray.cal_reflection(cur_this)  # 折射面上计算
        ray.get_next_lu(cur_this)  # 迭代至下一个面

    return ray.l_img


def cal_f(ray, opt_sys):
    """计算焦距 \n
        ray 初始化后的无穷远第一近轴光线 \n
        opt_sys 调整过的光学系统"""
    # ray1 = ray(0, -INF, 0.5893, first_near_axis_ray, True, 0, 10) 用这条光线计算
    cal_l(ray, opt_sys)
    f = ray.h_max / ray.u_img  # 遍历结束后，计算焦距
    return f


def cal_lh(l_imag, f):
    """计算主面位置 \n
        l_img 无穷远第一近轴光的像距 \n
        f 焦距"""

    return l_imag - f


def cal_lp(ray, opt_sys):
    """计算出瞳距 \n
        ray 无穷远第二近轴光线 \n
        opt_sys 光学系统"""
    cal_l(ray, opt_sys)
    return ray.l_img


def cal_y(ray_input, opt_sys):
    """计算像高 \n
        ray 光线 \n
        opt_sys 光学系统"""
    if ray_input.raytype == real_ray:  # 实际像高
        cal_l(ray_input, opt_sys)
        y = ray_input.cal_imghigh()
    else:  # 理想像高
        if ray_input.inf_flag is True:  # 无穷远
            opt_sys.inner_ray_wl = ray_input.wavelength
            opt_sys.get_f()
            y = abs(opt_sys.f * tan(ray_input.w_obj))
        else:
            # opt_sys.n1 = ray_input.n_obj
            # opt_sys.u1 = ray_input.u_obj  # 把第一面的入射角赋值给光线系统
            ray0 = ray(-1, -opt_sys.curve_list[0].d, ray_input.wavelength, first_near_axis_ray, False, 0, 10, 0, 1, 0)
            ray0.get_umax_wmax(opt_sys.curve_list[1])
            ray0.initialize(opt_sys)
            opt_sys.n1 = ray0.n_obj
            opt_sys.u1 = ray0.u_obj
            cal_l(ray0, opt_sys)
            opt_sys.get_beta(ray0)
            y = abs(ray_input.y * opt_sys.beta)

    return y


def cal_sp(l_real, l_near):
    """计算两条光线球差 \n
        l_real 实际像距 \n
        l_near 理想像距"""
    return l_real - l_near


def cal_chro_l(l_f, l_c):
    """计算两条光线位置色差 \n
        l_f f光像距 \n
        l_c c光像距"""
    return l_f - l_c


def cal_chro_y(y_f, y_c):
    """计算两条光线倍率色差 \n
        y_f f光像高 \n
        y_c c光像高"""
    return y_f - y_c


def cal_abe(y_real, y_ideal):
    """计算绝对畸变与相对畸变 \n
        y_real 实际像高 \n
        y_ideal 理想像高"""
    abe_absolute = y_real - y_ideal  # 绝对畸变
    abe_relatively = abe_absolute / y_ideal * 100  # 相对畸变 已经化为百分数
    return [abe_absolute, abe_relatively]


def cal_coma(y_up, y_down, y_main):
    """计算慧差 \n
        y_up 上光线像高 \n
        y_down 下光线像高 \n
        y_main 主光线像高"""
    return 0.5 * (y_up + y_down) - y_main


def cal_cur_t(ray1, ray2, opt_sys):
    """计算子午场曲 \n
        ray1 第一近轴光线 \n
        ray2 第二近轴光线 \n
        opt_sys 光学系统"""
    cur_list = opt_sys.curve_list
    ray1.wavelength = dray
    l0 = cal_l(ray1, opt_sys)

    for i in range(1, len(cur_list) - 1):  # 从物面之后的面遍历到像面之前的面
        cur_last = cur_list[i - 1]  # 上一个面
        cur_this = cur_list[i]  # 当前面
        cur_next = cur_list[i + 1]  # 下一个面
        ray2.get_n(cur_last.material, cur_this.material)  # 获取折射率
        flagarray = ray2.IsValid(cur_this)  # 进行校验
        if flagarray[0] is False:
            print(f"ERROR!! type:{flagarray[1]}")
            break
        ray2.cal_reflection(cur_this)  # 折射面上计算

        # 初始化x和t
        if i == 1:
            if cur_this.r >= 0:
                x1 = cur_this.r - sqrt(cur_this.r ** 2 - ray2.h ** 2)
            else:
                x1 = cur_this.r + sqrt(cur_this.r ** 2 - ray2.h ** 2)
            if ray2.inf_flag is True:
                t1 = -1E15
            else:
                t1 = (-cur_list[0].d - x1) / cos(ray2.u_obj)

        # I1 = (ray2.l_obj - cur_this.r) / cur_this.r * ray2.u_obj  # 计算I
        I1 = asin((ray2.l_obj - cur_this.r) / cur_this.r * sin(ray2.u_obj))  # 计算I
        # I2 = ray2.n_obj / ray2.n_img * I1
        I2 = asin(ray2.n_obj / ray2.n_img * sin(I1))  # 计算I'
        t2 = t1*cur_this.r*ray2.n_img*(cos(I2)**2)/(cur_this.r*ray2.n_obj*(cos(I1)**2)+t1*(ray2.n_img*cos(
            I2)-ray2.n_obj*cos(I1)))

        ray2.get_next_lu(cur_this)  # 迭代至下一个面
        if cur_next.r >= 0:
            x2 = cur_next.r - sqrt(cur_next.r**2 - (ray2.l_obj*ray2.u_obj)**2)
        else:
            x2 = cur_next.r + sqrt(cur_next.r ** 2 - (ray2.l_obj * ray2.u_obj) ** 2)
        D = (cur_this.d - x1 + x2) / cos(ray2.u_obj)
        if i!= len(cur_list) - 2:
            x1 = x2
        t1 = t2 - D

    l_t = t2 * cos(ray2.u_img) + x1
    x_t = l_t - l0

    return x_t


def cal_cur_s(ray1, ray2, opt_sys):
    """计算弧矢场曲 \n
        ray1 第一近轴光线 \n
        ray2 第二近轴光线
        opt_sys 光学系统"""
    cur_list = opt_sys.curve_list
    ray1.wavelength = dray
    l0 = cal_l(ray1, opt_sys)

    for i in range(1, len(cur_list) - 1):  # 从物面之后的面遍历到像面之前的面
        cur_last = cur_list[i - 1]  # 上一个面
        cur_this = cur_list[i]  # 当前面
        cur_next = cur_list[i + 1]  # 下一个面
        ray2.get_n(cur_last.material, cur_this.material)  # 获取折射率
        flagarray = ray2.IsValid(cur_this)  # 进行校验
        if flagarray[0] is False:
            print(f"ERROR!! type:{flagarray[1]}")
            break
        ray2.cal_reflection(cur_this)  # 折射面上计算

        # 初始化x和s
        if i == 1:
            if cur_this.r >= 0:
                x1 = cur_this.r - sqrt(cur_this.r ** 2 - ray2.h ** 2)
            else:
                x1 = cur_this.r + sqrt(cur_this.r ** 2 - ray2.h ** 2)
            if ray2.inf_flag is True:
                s1 = -1E15
            else:
                s1 = (-cur_list[0].d - x1) / cos(ray2.u_obj)

        # I1 = (ray2.l_obj - cur_this.r) / cur_this.r * ray2.u_obj  # 计算I
        I1 = asin((ray2.l_obj - cur_this.r) / cur_this.r * sin(ray2.u_obj))  # 计算I
        # I2 = ray2.n_obj / ray2.n_img * I1
        I2 = asin(ray2.n_obj / ray2.n_img * sin(I1))  # 计算I'
        s2 = s1*cur_this.r*ray2.n_img/(cur_this.r*ray2.n_obj+s1*(ray2.n_img*cos(I2)-ray2.n_obj*cos(I1)))

        ray2.get_next_lu(cur_this)  # 迭代至下一个面
        if cur_next.r >= 0:
            x2 = cur_next.r - sqrt(cur_next.r ** 2 - (ray2.l_obj * ray2.u_obj) ** 2)
        else:
            x2 = cur_next.r + sqrt(cur_next.r ** 2 - (ray2.l_obj * ray2.u_obj) ** 2)
        D = (cur_this.d - x1 + x2) / cos(ray2.u_obj)
        if i != len(cur_list) - 2:
            x1 = x2
        s1 = s2 - D

    l_s = s2 * cos(ray2.u_img) + x1
    x_s = l_s - l0

    return x_s


def cal_ast(xt, xs):
    """计算像散 \n
        xt 子午场曲 \n
        xs 弧矢场曲 \n"""
    return xt - xs


if __name__ == "__main__":
    # d光 0.587562    f光 0.486133  c光 0.656273
    dray = 0.587562
    fray = 0.486133
    cray = 0.656273

    curve_obj = curve(0, INF, INF, air, INF)
    curve1 = curve(1, 4, 62.5, H_K9L, 20)
    curve2 = curve(2, 2.5, -43.65, H_ZF2, 20)
    curve3 = curve(3, 100, -124.35, air, 20)
    curve_img = curve(4, 0, INF, air, INF)

    curve_list = [curve_obj, curve1, curve2, curve3, curve_img]

    optical_system = optsys(curve_list)

    ray0 = ray(0, -INF, 0.587562, first_near_axis_ray, True, 0, 10, 0, 1, 0)  # 类型1 焦距、主面位置
    optical_system.adjust_curve_obj(ray0)
    optical_system.adjust_curve_img(ray0)
    optical_system.get_f()
    ray0.get_umax_wmax(curve1)
    ray0.initialize(optical_system)
    l = cal_l(ray0, optical_system)
    lh = cal_lh(l, optical_system.f)

    ray1 = ray(0, -500, 0.587562, real_ray, False, 26, 10, 0, 0.7, 0)  # 类型2 像距 出瞳距
    # ray1 = ray(0, -500, 0.5893, second_near_axis_ray, True, 0, 0, angle2rad(3), 0, 1)  # 出瞳距
    optical_system.adjust_curve_obj(ray1)
    optical_system.adjust_curve_img(ray1)
    ray1.get_umax_wmax(curve1)
    ray1.initialize(optical_system)
    l = cal_l(ray1, optical_system)

    # ray0 = ray(0, -500, 0.587562, real_ray, False, 26, 10, 0, 0, 1)  # 实际光线像高  类型3 像高
    # ray1 = ray(0, -INF, dray, second_near_axis_ray, True, 0, 0, angle2rad(3), 0, 1)  # 理想像高
    ray1 = ray(0, -500, fray, real_ray, False, 26, 10, 0, 0, 1)
    ray0 = ray(-1, ray1.l_obj, dray, ray1.raytype, ray1.inf_flag, ray1.y_max, ray1.h_max, ray1.w_max, ray1.K_eta,
               ray1.K_w)
    optical_system.adjust_curve_obj(ray0)
    optical_system.adjust_curve_img(ray0)
    ray1.get_umax_wmax(curve1)
    ray1.initialize(optical_system)
    y = cal_y(ray1, optical_system)

    ray0 = ray(0, -INF, dray, first_near_axis_ray, True, 0, 10, 0, 1, 0)  #  类型4 球差
    ray1 = ray(1, -INF, dray, real_ray, True, 0, 10, 0, 1, 0)  # 无穷远
    ray0 = ray(0, -500, dray, first_near_axis_ray, False, 26, 10, 0, 1, 0)
    ray1 = ray(0, -500, dray, real_ray, False, 26, 10, 0, 1, 0)  # 有限远物
    optical_system.adjust_curve_obj(ray0)
    optical_system.adjust_curve_img(ray0)
    ray0.get_umax_wmax(curve1)
    ray0.initialize(optical_system)
    ray1.get_umax_wmax(curve1)
    ray1.initialize(optical_system)

    l0 = cal_l(ray0, optical_system)
    l1 = cal_l(ray1, optical_system)
    sp = cal_sp(l1, l0)

    ray0 = ray(0, -INF, fray, real_ray, True, 0, 10, 0, 1, 0)  # 类型5 位置色差
    ray1 = ray(1, -INF, cray, real_ray, True, 0, 10, 0, 1, 0)  # 无穷远
    ray0 = ray(0, -500, fray, real_ray, False, 26, 10, 0, 1, 0)
    ray1 = ray(0, -500, cray, real_ray, False, 26, 10, 0, 1, 0)  # 有限远物
    optical_system.adjust_curve_obj(ray0)
    optical_system.adjust_curve_img(ray0)
    ray0.get_umax_wmax(curve1)
    ray0.initialize(optical_system)
    ray1.get_umax_wmax(curve1)
    ray1.initialize(optical_system)

    l0 = cal_l(ray0, optical_system)
    l1 = cal_l(ray1, optical_system)
    chro = cal_chro_l(l0, l1)

    ray1 = ray(0, -INF, 0.58756, first_near_axis_ray, True, 0, 10, 0, 1, 0)  # 类型6 像散，场曲
    ray2 = ray(1, -INF, 0.58756, second_near_axis_ray, True, 0, 0, angle2rad(3), 0, 1)  # 物无穷远
    ray1 = ray(0, -500, 0.58756, first_near_axis_ray, False, 0, 10, 0, 1, 0)
    ray2 = ray(0, -500, 0.58756, second_near_axis_ray, False, 26, 10, 0, 0, 1)  # 物有限远
    optical_system.adjust_curve_obj(ray1)
    optical_system.adjust_curve_img(ray1)
    ray1.get_umax_wmax(curve1)
    ray1.initialize(optical_system)
    ray2.get_umax_wmax(curve1)
    ray2.initialize(optical_system)
    ray3 = copy.deepcopy(ray1)
    ray4 = copy.deepcopy(ray2)
    xt = cal_cur_t(ray1, ray2, optical_system)
    xs = cal_cur_s(ray3, ray4, optical_system)
    delta_ts = cal_ast(xt, xs)

    ray1 = ray(0, -INF, dray, second_near_axis_ray, True, 0, 0, angle2rad(3), 0, 1)  # 类型7 畸变
    ray2 = ray(0, -INF, dray, real_ray, True, 0, 0, angle2rad(3), 0, 1)  # 无穷远
    ray1 = ray(0, -500, dray, second_near_axis_ray, False, 26, 10, 0, 0, 1)
    ray2 = ray(0, -500, dray, real_ray, False, 26, 10, 0, 0, 1)  # 有限远
    ray0 = ray(-1, ray1.l_obj, dray, ray1.raytype, ray1.inf_flag, ray1.y_max, ray1.h_max, ray1.w_max, ray1.K_eta,
               ray1.K_w)
    optical_system.adjust_curve_obj(ray0)
    optical_system.adjust_curve_img(ray0)
    ray1.get_umax_wmax(curve1)
    ray1.initialize(optical_system)
    ray2.get_umax_wmax(curve1)
    ray2.initialize(optical_system)
    y_ideal = cal_y(ray1, optical_system)
    y_real = cal_y(ray2, optical_system)
    res = cal_abe(y_real, y_ideal)

    ray1 = ray(0, -500, fray, real_ray, False, 26, 10, 0, 0, 1)   # 类型8 倍率色差
    ray2 = ray(1, -500, cray, real_ray, False, 26, 10, 0, 0, 1)  # 有限远
    ray1 = ray(0, -INF, fray, real_ray, True, 0, 0, angle2rad(3), 0, 1)
    ray2 = ray(0, -INF, cray, real_ray, True, 0, 0, angle2rad(3), 0, 1) # 无穷远
    ray0 = ray(-1, ray1.l_obj, dray, ray1.raytype, ray1.inf_flag, ray1.y_max, ray1.h_max, ray1.w_max,
               ray1.K_eta, ray1.K_w)
    optical_system.adjust_curve_obj(ray0)
    optical_system.adjust_curve_img(ray0)
    ray1.get_umax_wmax(curve1)
    ray1.initialize(optical_system)
    ray2.get_umax_wmax(curve1)
    ray2.initialize(optical_system)
    y_f = cal_y(ray1, optical_system)
    y_c = cal_y(ray2, optical_system)
    delta_fc = cal_chro_y(y_f, y_c)

    ray0 = ray(0, -INF, 0.58762, real_ray, True, 0, 10, angle2rad(3), 0, 1)  # 类型9 彗差，无穷远物
    ray1 = ray(0, -INF, 0.58762, real_ray, True, 0, 10, angle2rad(3), 0.7, 1)
    ray2 = ray(0, -INF, 0.58762, real_ray, True, 0, 10, angle2rad(3), -0.7, 1)
    ray0 = ray(0, -500, 0.58762, real_ray, False, 26, 10, 0, 0, 0.7)  # 有限远物
    ray1 = ray(0, -500, 0.58762, real_ray, False, 26, 10, 0, 0.7, 0.7)
    ray2 = ray(0, -500, 0.58762, real_ray, False, 26, 10, 0, -0.7, 0.7)
    optical_system.adjust_curve_obj(ray0)
    optical_system.adjust_curve_img(ray0)
    ray0.get_umax_wmax(curve1)
    ray0.initialize(optical_system)
    ray1.get_umax_wmax(curve1)
    ray1.initialize(optical_system)
    ray2.get_umax_wmax(curve1)
    ray2.initialize(optical_system)

    y_main = cal_y(ray0, optical_system)
    y_up = cal_y(ray1, optical_system)
    y_down = cal_y(ray2, optical_system)

    Kt = cal_coma(y_up, y_down, y_main)