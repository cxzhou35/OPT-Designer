from math import *
from cal_glass_ref import calculate_glass_ref
# from cal_items import cal_l, cal_f
import numpy as np

# 定义三种光线编号
first_near_axis_ray = 1
second_near_axis_ray = 2
real_ray = 3

# 定义空气及两种玻璃编号
air = 0
H_K9L = 1
H_ZF2 = 2

# 三种波长光
dray = 0.587562  # d光
fray = 0.486133  # f光
cray = 0.656273  # c光

# 定义无穷大
# INF = 1E18
INF = np.inf

# 调试模式
debug = False


def cal_L(ray, opt_sys):
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


def cal_F(ray, opt_sys):
    """计算焦距 \n
        ray 初始化后的无穷远第一近轴光线 \n
        opt_sys 调整过的光学系统"""
    # ray1 = ray(0, -INF, 0.5893, first_near_axis_ray, True, 0, 10) 用这条光线计算
    cal_L(ray, opt_sys)
    f = ray.h_max / ray.u_img  # 遍历结束后，计算焦距
    return f


class optsys():
    """定义光学系统"""
    f = 0  # 焦距
    lp = 0  # 入瞳距
    beta = 1  # 整体的放大率
    n1 = 1  # 第一面的物方放大率
    u1 = 0  # 第一面的像方放大率
    inner_ray_wl = dray  # 内置光线波长

    def __init__(self, curve_list):
        self.curve_list = curve_list

    def adjust_curve_obj(self, ray):
        """根据输入光线调整物面 光线初始化后调用 \n
            ray 输入光线"""
        self.curve_list[0].d = ray.l_obj * (-1)
        self.curve_list[0].r = INF
        self.curve_list[0].material = air
        self.curve_list[0].D = ray.y_max

    def adjust_curve_img(self, ray_input):
        """根据输入光线调整像面位置 光线初始化后调用 \n
            ray_input 输入光线"""
        ray0 = ray(-1, ray_input.l_obj, ray_input.wavelength, first_near_axis_ray, ray_input.inf_flag, 0, 2, 0, 1, 0)
        # 定义高斯光线
        ray0.get_umax_wmax(self.curve_list[1])
        ray0.initialize(self)
        l_img = cal_L(ray0, self)  # 计算像距
        self.curve_list[-2].d = l_img  # 改变最后一个折射球面到像面距离

    def get_f(self):
        """计算光学系统自身的焦距"""
        ray0 = ray(0, -INF, 0.587562, first_near_axis_ray, True, 0, 10, 0, 1, 0)
        ray0.wavelength = self.inner_ray_wl
        # self.adjust_curve_obj(ray0)
        # self.adjust_curve_img(ray0)
        ray0.get_umax_wmax(self.curve_list[1])
        ray0.initialize(self)

        self.f = cal_F(ray0, self)

    def get_beta(self, ray):
        """计算光学系统的折射率 \n
            ray 有限远的第二近轴光线"""
        self.beta = self.n1 * self.u1 / ray.n_img / ray.u_img


class curve():
    """定义曲面"""
    def __init__(self, num, d, r, material, D):
        self.num = num  # 曲面编号
        self.d = d  # 此面到下一面距离
        self.r = r  # 曲率半径
        self.material = material  # 此面到下一个曲面之间的材料 1：H-K9L 2：H-ZF2
        self.D = D  # 口径大小


class obj():
    """定义物"""
    def __init__(self, l_obj, wavelength, h_max=0, y_max=0, w_max=0, K_eta=1, K_w=1, ideal_flag=0):
        self.l_obj = l_obj
        self.wavelength = wavelength
        self.h_max = h_max
        self.y_max = y_max
        self.w_max = w_max
        self.K_eta = K_eta
        self.K_w = K_w
        self.ideal_flag = ideal_flag  # 是否为理想物，0为实际物，1为理想物

    def IsInf(self):
        if self.l_obj == -np.inf:
            return True
        else:
            return False

    def obj2raylist(self, cal_type):
        """将物根据计算类型转换为计算需要的光线列表"""
        ray_list = []

        if cal_type == 1:
            ray0 = ray(0, -INF, self.wavelength, first_near_axis_ray, True, 0, self.h_max, 0, self.K_eta, 0)
            ray_list.append(ray0)
        if cal_type == 2:
            if self.ideal_flag == 0:  # 实际物
                if self.l_obj == -np.inf:
                    ray0 = ray(0, self.l_obj, self.wavelength, real_ray, True, 0, self.h_max, 0,
                               self.K_eta, 0)
                else:
                    ray0 = ray(0, self.l_obj, self.wavelength, real_ray, False, self.y_max, self.h_max, 0,
                               self.K_eta, 0)
            else:  # 理想物
                if self.l_obj == -np.inf:
                    ray0 = ray(0, self.l_obj, self.wavelength, first_near_axis_ray, True, 0, self.h_max, 0,
                               self.K_eta, 0)
                else:
                    ray0 = ray(0, self.l_obj, self.wavelength, first_near_axis_ray, False, self.y_max, self.h_max, 0,
                               self.K_eta, 0)
            ray_list.append(ray0)
        if cal_type == 3:
            if self.ideal_flag == 0:  # 实际物
                if self.l_obj == -np.inf:
                    ray0 = ray(0, self.l_obj, self.wavelength, real_ray, True, 0, 0, self.w_max,
                               0, self.K_w)
                else:
                    ray0 = ray(0, self.l_obj, self.wavelength, real_ray, False, self.y_max, self.h_max, 0,
                               0, self.K_w)
            else:
                if self.l_obj == -np.inf:
                    ray0 = ray(0, self.l_obj, self.wavelength, second_near_axis_ray, True, 0, 0, self.w_max,
                               0, self.K_w)
                else:
                    ray0 = ray(0, self.l_obj, self.wavelength, second_near_axis_ray, False, self.y_max, self.h_max, 0,
                               0, self.K_w)
            ray_list.append(ray0)
        if cal_type == 4:
            inf_flag = self.IsInf()
            ray0 = ray(0, self.l_obj, self.wavelength, first_near_axis_ray, inf_flag, self.y_max, self.h_max,
                       0, self.K_eta, 0)
            ray1 = ray(1, self.l_obj, self.wavelength, real_ray, inf_flag, self.y_max, self.h_max,
                       0, self.K_eta, 0)
            ray_list.append(ray0)
            ray_list.append(ray1)
        if cal_type == 5:
            inf_flag = self.IsInf()
            ray0 = ray(0, self.l_obj, fray, real_ray, inf_flag, self.y_max, self.h_max,
                       0, self.K_eta, 0)
            ray1 = ray(1, self.l_obj, cray, real_ray, inf_flag, self.y_max, self.h_max,
                       0, self.K_eta, 0)
            if self.K_eta == 0:
                ray0.raytype = ray1.raytype = first_near_axis_ray
                ray0.K_eta = ray1.K_eta = 1
            ray_list.append(ray0)
            ray_list.append(ray1)
        if cal_type == 6:
            inf_flag = self.IsInf()
            ray0 = ray(0, self.l_obj, self.wavelength, first_near_axis_ray, inf_flag, 0, self.h_max, 0, self.K_eta,
                       0)
            ray1 = ray(1, self.l_obj, self.wavelength, second_near_axis_ray, inf_flag, self.y_max, self.h_max,
                       self.w_max, 0, self.K_w)
            ray_list.append(ray0)
            ray_list.append(ray1)
        if cal_type == 7:
            inf_flag = self.IsInf()
            ray0 = ray(0, self.l_obj, self.wavelength, second_near_axis_ray, inf_flag, self.y_max, self.h_max,
                       self.w_max, 0, self.K_w)
            ray1 = ray(1, self.l_obj, self.wavelength, real_ray, inf_flag, self.y_max, self.h_max,
                       self.w_max, 0, self.K_w)
            ray_list.append(ray0)
            ray_list.append(ray1)
        if cal_type == 8:
            inf_flag = self.IsInf()
            ray0 = ray(0, self.l_obj, fray, real_ray, inf_flag, self.y_max, self.h_max,
                       self.w_max, 0, self.K_w)
            ray1 = ray(1, self.l_obj, cray, real_ray, inf_flag, self.y_max, self.h_max,
                       self.w_max, 0, self.K_w)
            ray_list.append(ray0)
            ray_list.append(ray1)
        if cal_type == 9:
            inf_flag = self.IsInf()
            ray0 = ray(0, self.l_obj, self.wavelength, real_ray, inf_flag, self.y_max, self.h_max,
                       self.w_max, 0, self.K_w)
            ray1 = ray(1, self.l_obj, self.wavelength, real_ray, inf_flag, self.y_max, self.h_max,
                       self.w_max, self.K_eta, self.K_w)
            ray2 = ray(2, self.l_obj, self.wavelength, real_ray, inf_flag, self.y_max, self.h_max,
                       self.w_max, -self.K_eta, self.K_w)
            ray_list.append(ray0)
            ray_list.append(ray1)
            ray_list.append(ray2)

        return ray_list


class ray():
    """定义光线"""
    u_max = 0
    w_max = 0
    u_obj = 0  # 物方孔径角
    w_obj = 0  # 物方视场角
    l_img = 0  # 像距
    u_img = 0  # 像方孔径角
    n_obj = 1  # 此光线在物方折射率
    n_img = 1  # 此光线在像方折射率
    y = 0  # 物高
    h = 0  # 像高

    def __init__(self, num, l_obj, wavelength, raytype, inf_flag, y_max=0, h_max=0, w_max=0, K_eta=1.0, K_w=1.0):
        self.num = num
        self.l_obj = l_obj  # 物距
        self.wavelength = wavelength  # 光线波长
        self.raytype = raytype  # 光线类型 0：主光线 1：第一近轴光 2：第二近轴光 3：实际光线
        self.inf_flag = inf_flag  # 是否为无穷远光线，True为是，False为否
        self.y_max = y_max  # 物最大高度
        self.h_max = h_max  # 光线最大入射高度
        self.w_max = w_max  # 光线最大物方视场角
        # self.u_max = u_max  # 光线最大物方孔径角
        self.K_eta = K_eta  # 孔径取点系数
        self.K_w = K_w  # 视场取点系数

    def get_umax_wmax(self, curve):
        """计算光线的最大物方孔径角和物方视场角 \n
            curve：第一个曲面，即光阑
            实例化类后必须调用"""
        d = curve.r - sqrt(curve.r ** 2 - (curve.D / 2) ** 2)
        self.u_max = atan(curve.D / 2 / (-self.l_obj))
        # self.u_max = atan(curve.D / 2 / (d - self.l_obj))
        if self.inf_flag is False:  # 有限远物
            self.w_max = atan(self.y_max / self.l_obj)

    # 以下皆为第一近轴光的计算

    def initialize(self, optsys):
        """光线初始化函数，根据光线的类型确定物距和物方孔径角 \n
            optsys：整个光学系统"""
        if self.raytype is first_near_axis_ray:  # 第一近轴光
            if self.inf_flag is True:  # 无穷远
                self.l_obj = -INF  # 计算物距
                self.u_obj = 0  # 计算物方孔径角
                self.h = self.K_eta * self.h_max  # 计算入射高度
            else:  # 有限距离
                self.l_obj = self.l_obj  # 计算物距
                self.u_obj = self.K_eta * self.u_max  # 计算物方孔径角

        if self.raytype is second_near_axis_ray:  # 第二近轴光
            if self.inf_flag is True:  # 无穷远
                self.w_obj = self.K_w * self.w_max  # 计算物方视场角
                self.l_obj = optsys.lp  # 计算物距
                self.u_obj = sin(self.w_obj)  # 计算物方孔径角
            else:  # 有限距离
                self.y = self.y_max * self.K_w  # 计算物高
                self.w_obj = atan(self.y/(optsys.lp-self.l_obj))  # 计算物方视场角
                self.l_obj = optsys.lp  # 计算物距
                self.u_obj = sin(self.w_obj)  # 计算物方视场角

        if self.raytype is real_ray:  # 实际光线
            if self.inf_flag is True:  # 无穷远
                if self.w_max * self.K_w == 0:  # 轴上点
                    self.l_obj = -INF  # 初始化物距
                    self.u_obj = 0  # 初始化物方视场角
                    self.h = self.K_eta * self.h_max  # 计算入射高度
                else:  # 轴外点
                    self.w_obj = self.K_w * self.w_max  # 计算物方视场角
                    self.u_obj = self.w_obj  # 计算物方孔径角
                    self.l_obj = optsys.lp + self.K_eta * self.h_max / tan(self.u_obj)  # 计算物距

            else:  # 有限距离
                if self.w_max * self.K_w == 0:  # 轴上点
                    self.l_obj = self.l_obj  # 初始化物距
                    self.u_obj = asin(self.K_eta * sin(self.u_max))  # 计算物方视场角
                else:  # 轴外点
                    self.u_obj = atan((self.K_w * self.y_max - self.K_eta * self.h_max) / (optsys.lp - self.l_obj))
                    # 计算物方孔径角
                    self.l_obj = optsys.lp + self.K_eta * self.h_max / tan(self.u_obj)  # 计算物方视场角

    def get_n(self, glass_type_last, glass_type_this):
        """计算一条光线的物方、像方折射率 \n
            glass_type_last：上一个曲面后的介质 \n
            glass_type_this：当前曲面后的介质"""
        self.n_obj = calculate_glass_ref(self.wavelength, glass_type_last)  # 计算物方折射率，与上一个面material相关
        self.n_img = calculate_glass_ref(self.wavelength, glass_type_this)  # 计算像方折射率，与当前要入射的面material相关

    def cal_reflection(self, curve_this):
        """光线计算 \n
            curve_this：光线即将入射的曲面"""
        if self.raytype == real_ray:  # 实际光线，不近似
            if self.l_obj == -INF:  # 无穷远轴上点
                I1 = asin(self.h / curve_this.r)
            else:  # 其他情况
                self.h = self.l_obj * self.u_obj  # 计算h
                I1 = asin((self.l_obj - curve_this.r) / curve_this.r * sin(self.u_obj))  # 计算I
                if debug is True:
                    print(f"I:{I1}")

            I2 = asin(self.n_obj / self.n_img * sin(I1))  # 计算I'
            if debug is True:
                print(f"I':{I2}")
            self.u_img = self.u_obj + I1 - I2  # 计算u'
            self.l_img = curve_this.r + curve_this.r * sin(I2) / sin(self.u_img)  # 计算L'

        else:  # 近轴光线
            if self.l_obj == -INF:  # 无穷远轴上点
                I1 = self.h / curve_this.r
            else:  # 其他情况
                self.h = self.l_obj * self.u_obj  # 计算h
                I1 = (self.l_obj - curve_this.r) / curve_this.r * self.u_obj  # 计算I
                if debug is True:
                    print(f"I:{I1}")

            I2 = self.n_obj / self.n_img * I1  # 计算I'
            if debug is True:
                print(f"I':{I2}")
            self.u_img = self.u_obj + I1 - I2  # 计算u'
            self.l_img = curve_this.r + curve_this.r * I2 / self.u_img  # 计算L'

    def get_next_lu(self, curve_this):
        """计算下一次入射的物距、物方视场角 \n
            curve_this：光线即将入射的曲面 \n
            所有光线通用"""
        self.l_obj = self.l_img - curve_this.d  # 计算lk+1
        self.u_obj = self.u_img  # 计算uk+1

    def IsValid(self, curve_this):
        """光线进入入射下一个曲面之前检验数据是否合理 \n
            curve_this：即将入射的曲面"""

        if abs(self.u_obj) > pi/2:  # 物方孔径角是否合理
            return [False, 0]
        if curve_this.r == 0:  # 曲率半径是否合理
            return [False, 1]

        if self.l_obj == -INF:  # 无穷远轴上点
            sinI1 = self.h / curve_this.r
        else:  # 其他情况
            sinI1 = (self.l_obj - curve_this.r) / curve_this.r * sin(self.u_obj) # 计算I

        if abs(sinI1) > 1:  # 入射角是否合理
            return [False, 2]

        sinI2 = self.n_obj / self.n_img * sinI1  # 计算I'

        if abs(sinI2) > 1:
            return [False, 3]  # 出射角是否合理

        return [True, True]

    def cal_imghigh(self):
        """计算并返回像面上像高 \n
            所有光线通用"""
        return abs(self.l_obj*tan(self.u_obj))

