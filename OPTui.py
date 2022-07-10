#!/usr/bin/python3
# -*- coding: utf-8 -*-

# 载入控件和相关的包
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPalette, QColor, QBrush
from PyQt5.QtCore import Qt, QFile, QTextStream, QIODevice, QByteArray
from PyQt5 import QtCore
from pyqtgraph import GraphicsLayoutWidget
import pyqtgraph as pg 
import numpy as np
import pandas as pd
import qdarkstyle
import copy
import os
import sys
from math import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import openpyxl
from scipy.interpolate import make_interp_spline

# self-define scripts
from iostream import *
from cal import *
from cal_abcurve import *

num_line = 0

# Matplotlib Figure Class
class MplWidget(FigureCanvas):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.ax = self.fig.add_subplot(111)

        self.ax.spines['top'].set_visible(False)  # 隐藏上方框线
        self.ax.spines['bottom'].set_visible(False)
        self.ax.spines['right'].set_visible(False)  # 隐藏右侧框线
        self.ax.spines['left'].set_visible(False)
        self.ax.axis('off')

        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    # 色球差计算绘图
    def plot_axial_curve(self):
        cur_list = read_curve_data()

        global num_line
        cal_type = num_line
        cur_list = read_curve_data()
        obj_input = read_obj_data()  # 从文件读入物
        ray_list = obj_input.obj2raylist(cal_type)

        k_eta_item = [0.001, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.707, 0.75, 0.8, 0.85, 0.9, 0.95, 1]
        result = cal_axial_curve(ray_list[0], cur_list, k_eta_item)

        item_new = np.linspace(min(k_eta_item), max(k_eta_item), 300)
        smooth0 = make_interp_spline(k_eta_item, result[0])(item_new)
        smooth1 = make_interp_spline(k_eta_item, result[1])(item_new)
        smooth2 = make_interp_spline(k_eta_item, result[2])(item_new)

        self.ax.plot(smooth0, item_new, label='D ray', color = 'g')
        self.ax.plot(smooth1, item_new, label='F ray', color = 'b')
        self.ax.plot(smooth2, item_new, label='C ray', color = 'r')

        # 坐标轴设置
        self.ax.axis('on')
        self.ax.spines['left'].set_visible(True)
        self.ax.spines['bottom'].set_visible(True)

        y_ticks = np.arange(0.1, 1.1, 0.1)
        self.ax.set_yticks(y_ticks)

        self.ax.spines['top'].set_visible(False)  # 隐藏上方框线
        self.ax.spines['right'].set_visible(False)  # 隐藏右侧框线
        self.ax.xaxis.set_ticks_position('bottom')
        self.ax.spines['bottom'].set_position(('data', 0))
        self.ax.yaxis.set_ticks_position('left')
        self.ax.spines['left'].set_position(('data', 0))
        self.ax.set_xlabel(r"$\delta L'(mm)$",fontsize=12)  # 设置x轴名称 x label
        self.ax.set_title('Longitudinal Aberration Curve')  # 设置图名为Simple Plot
        self.ax.legend(loc='upper center', bbox_to_anchor=(0, 0.90), ncol=1, fancybox=True, shadow=True)  # 自动检测要在图例中显示的元素，并且显示
        self.draw()

    # 场曲和像散
    def plot_filed_curvature_curve(self):
        cur_list = read_curve_data()

        global num_line
        cal_type = num_line
        cur_list = read_curve_data()
        obj_input = read_obj_data()  # 从文件读入物
        ray_list = obj_input.obj2raylist(cal_type)

        k_w_item = [0.001, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.707, 0.75, 0.8, 0.85, 0.9, 0.95, 1]
        result = cal_filed_curvature_curve(ray_list[0], ray_list[1], cur_list, k_w_item)

        item_new = np.linspace(min(k_w_item), max(k_w_item), 300)
        smooth0 = make_interp_spline(k_w_item, result[0])(item_new)
        smooth1 = make_interp_spline(k_w_item, result[1])(item_new)
        smooth2 = make_interp_spline(k_w_item, result[2])(item_new)
        smooth3 = make_interp_spline(k_w_item, result[3])(item_new)
        smooth4 = make_interp_spline(k_w_item, result[4])(item_new)
        smooth5 = make_interp_spline(k_w_item, result[5])(item_new)

        self.ax.plot(smooth0, item_new, label='D ray xt', color = 'g')
        self.ax.plot(smooth1, item_new, label='D ray xs', linestyle = '-.', color = 'g')
        self.ax.plot(smooth2, item_new, label='F ray xt', color = 'b')
        self.ax.plot(smooth3, item_new, label='F ray xs', linestyle = '-.', color = 'b')
        self.ax.plot(smooth4, item_new, label='C ray xt', color = 'r')
        self.ax.plot(smooth5, item_new, label='C ray xs', linestyle = '-.', color = 'r')

        # 坐标轴设置
        self.ax.axis('on')
        self.ax.spines['left'].set_visible(True)
        self.ax.spines['bottom'].set_visible(True)

        y_ticks = np.arange(0.1, 1.1, 0.1)
        self.ax.set_yticks(y_ticks)
        self.ax.spines['top'].set_visible(False)  # 隐藏上方框线
        self.ax.spines['right'].set_visible(False)  # 隐藏右侧框线
        self.ax.xaxis.set_ticks_position('bottom')
        self.ax.spines['bottom'].set_position(('data', 0))
        self.ax.yaxis.set_ticks_position('left')
        self.ax.spines['left'].set_position(('data', 0))
        self.ax.set_xlabel(r"$x'_{t} / x'_{s}(mm)$",fontsize=12)  # 设置x轴名称
        self.ax.set_title('Filed Curvature Curve')  # 设置图名
        self.ax.legend(loc='upper center', bbox_to_anchor=(0, 0.90), ncol=1, fancybox=True, shadow=True)  # 自动检测要在图例中显示的元素，并且显示
        self.draw()

    # 畸变计算绘图
    def plot_cal_distortion_curve(self):
        cur_list = read_curve_data()

        global num_line
        cal_type = num_line
        cur_list = read_curve_data()
        obj_input = read_obj_data()  # 从文件读入物
        ray_list = obj_input.obj2raylist(cal_type)

        k_w_item = [0.001, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.707, 0.75, 0.8, 0.85, 0.9, 0.95, 1]

        result = cal_distortion_curve(ray_list[0], cur_list, k_w_item)

        item_new = np.linspace(min(k_w_item), max(k_w_item), 300)
        smooth0 = make_interp_spline(k_w_item, result[0])(item_new)
        smooth1 = make_interp_spline(k_w_item, result[1])(item_new)
        smooth2 = make_interp_spline(k_w_item, result[2])(item_new)

        self.ax.plot(smooth0, item_new, label='D ray', color = 'g')
        self.ax.plot(smooth1, item_new, label='F ray', color = 'b')
        self.ax.plot(smooth2, item_new, label='C ray', color = 'r')

        # 坐标轴设置
        self.ax.axis('on')
        self.ax.spines['left'].set_visible(True)
        self.ax.spines['bottom'].set_visible(True)
        self.ax.spines['top'].set_visible(False)  # 隐藏上方框线
        self.ax.spines['right'].set_visible(False)  # 隐藏右侧框线
        self.ax.xaxis.set_ticks_position('bottom')
        self.ax.spines['bottom'].set_position(('data', 0))
        self.ax.yaxis.set_ticks_position('left')
        self.ax.spines['left'].set_position(('data', 0))
        y_ticks = np.arange(0.1, 1.1, 0.1)
        self.ax.set_yticks(y_ticks)
        self.ax.set_xlabel(r"$\delta y'(mm)$",fontsize=12)  # 设置x轴名称
        self.ax.set_title('Distortion Curve')  # 设置图标题
        self.ax.legend(loc='upper center', bbox_to_anchor=(0, 0.90), ncol=1, fancybox=True, shadow=True)  # 自动检测要在图例中显示的元素，并且显示
        self.draw()

    # 倍率色差计算绘图
    def plot_lateral_color_curve(self):
        cur_list = read_curve_data()
        global num_line
        cal_type = num_line
        cur_list = read_curve_data()
        obj_input = read_obj_data()  # 从文件读入物
        ray_list = obj_input.obj2raylist(cal_type)
        k_w_item = [0.001, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.707, 0.75, 0.8, 0.85, 0.9, 0.95, 1]

        result = cal_lateral_color_curve(ray_list[0], cur_list, k_w_item)

        result = [1000*item for item in result]

        item_new = np.linspace(min(k_w_item), max(k_w_item), 300)
        smooth0 = make_interp_spline(k_w_item, result)(item_new)

        self.ax.plot(smooth0, item_new)

        # 坐标轴设置
        self.ax.axis('on')
        self.ax.spines['left'].set_visible(True)
        self.ax.spines['bottom'].set_visible(True)

        y_ticks = np.arange(0.1, 1.1, 0.1)
        self.ax.set_yticks(y_ticks)
        self.ax.spines['top'].set_visible(False)  # 隐藏上方框线
        self.ax.spines['right'].set_visible(False)  # 隐藏右侧框线
        self.ax.xaxis.set_ticks_position('bottom')
        self.ax.yaxis.set_ticks_position('left')
        self.ax.spines['bottom'].set_position(('data', 0))
        self.ax.spines['left'].set_position(('data', 0))
        self.ax.set_xlabel(r"$\delta y'_{ch}(\mu m)$",fontsize=12)  # 设置x轴名称
        self.ax.set_title('Lateral Color Curve')
        self.draw()


class MainUi(QMainWindow):
    def __init__(self):
        super().__init__()

        pg.setConfigOption('background', '#19232D')
        pg.setConfigOption('foreground', 'd')
        pg.setConfigOptions(antialias=True)
        
        # 窗口居中显示
        self.center()

        self.init_ui()
        
        # return request json file
        self.rep = ""

        # 创建绘图面板
        self.plt = []
        # 读入的文件名称
        self.filename = ""

        # 输入标志
        self.input_flag = 0

        # 计算标志
        self.cal_flag = 0

        self.cal_list = []

        self.cal1 = 0
        self.cal2 = 0
        self.cal3 = 0
        self.cal4 = 0


        # 默认的状态栏
        self.status = self.statusBar()
        self.status.showMessage("Main Menu")
        
        # 标题栏
        self.setWindowTitle("光学系统计算软件")

        self.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())


    def init_ui(self):

        # 不固定窗口大小
        # self.setFixedSize(1080,700)
        
        # 创建窗口主部件
        self.main_widget = QWidget()  
        # 创建主部件的网格布局
        self.main_layout = QGridLayout()  
        # 设置窗口主部件布局为网格布局
        self.main_widget.setLayout(self.main_layout)  

        # 创建左侧部件
        self.left_widget = QWidget()  
        self.left_widget.setObjectName('left_widget')
        # 创建左侧部件的网格布局层
        self.left_layout = QGridLayout()  
        # 设置左侧部件布局为网格
        self.left_widget.setLayout(self.left_layout) 

        # 创建右侧部件
        self.right_widget = QWidget() 
        self.right_widget.setObjectName('right_widget')
        self.right_layout = QGridLayout()
        self.right_widget.setLayout(self.right_layout) 

        # 左侧部件
        self.main_layout.addWidget(self.left_widget, 0, 0, 12, 5)
        # 右侧部件
        self.main_layout.addWidget(self.right_widget, 0, 6, 12, 8)
        # 设置窗口主部件
        self.setCentralWidget(self.main_widget)

        # lineEdit to input a id
        self.id_line = QLineEdit()
        self.id_line.setPlaceholderText("输入管理员帐号登录")
        self.id_line.returnPressed.connect(self.match_id)
        self.left_layout.addWidget(self.id_line, 0, 0, 1, 5)

        # function button
        self.import_sys_button = QPushButton("输入光学系统参数")
        self.left_layout.addWidget(self.import_sys_button, 1, 0, 1, 5)
        self.import_sys_button.clicked.connect(self.import_data)
        self.import_sys_button.setEnabled(False)

        self.import_ray_button = QPushButton("输入实物参数")
        self.left_layout.addWidget(self.import_ray_button, 2, 0, 1, 5)
        self.import_ray_button.clicked.connect(self.import_data)
        self.import_ray_button.setEnabled(False)

        self.sys_cal_button = QPushButton("综合计算")
        self.left_layout.addWidget(self.sys_cal_button, 3, 0, 1, 5)
        self.sys_cal_button.clicked.connect(self.cal_data)
        self.sys_cal_button.setEnabled(False)

        self.sys_draw_button = QPushButton("绘制像差曲线")
        self.left_layout.addWidget(self.sys_draw_button, 4, 0, 1, 5)
        self.sys_draw_button.clicked.connect(self.draw_fig)
        self.sys_draw_button.setEnabled(False)

        # save figure and quit window
        self.save_fig_button = QPushButton("保存像差曲线图")
        self.left_layout.addWidget(self.save_fig_button, 5, 0, 1, 5)
        self.save_fig_button.clicked.connect(self.fig_save)
        self.save_fig_button.setEnabled(False)

        self.quit_button = QPushButton("退出")
        self.left_layout.addWidget(self.quit_button, 6, 0, 1, 5)
        self.quit_button.clicked.connect(self.quit_act)

        self.clear_button = QPushButton("清空")
        self.left_layout.addWidget(self.clear_button, 7, 0, 1, 1)
        self.clear_button.clicked.connect(self.clear_act)
        self.clear_button.setEnabled(False)

        self.import_button = QPushButton("导入")
        self.left_layout.addWidget(self.import_button, 7, 2, 1, 1)
        self.import_button.clicked.connect(self.import_act)
        self.import_button.setEnabled(False)

        self.output_button = QPushButton("导出")
        self.left_layout.addWidget(self.output_button, 7, 4, 1, 1)
        self.output_button.clicked.connect(self.save_act)
        self.output_button.setEnabled(False)

        self.num_line = QLineEdit()
        self.num_line.setPlaceholderText("输入计算序号")
        self.num_line.returnPressed.connect(self.match_cal_num)
        self.left_layout.addWidget(self.num_line, 8, 0, 1, 5)
        self.num_line.setEnabled(False)

        # tablewidgt to view data
        self.data_table = QTableWidget()
        self.left_layout.addWidget(self.data_table, 9, 0, 5, 5)

        self.fig_label = QLabel("像差曲线图展示区域")
        self.right_layout.addWidget(self.fig_label, 0, 3, 1, 5)

        # Fig 1
        self.plot_qiucha = MplWidget(self, width=5, height=4)
        self.right_layout.addWidget(self.plot_qiucha, 1, 0, 5, 4)

        # Fig 2
        self.plot_jibian =  MplWidget(self, width=5, height=4)
        self.right_layout.addWidget(self.plot_jibian, 6, 0, 5, 4)

        # Fig 3
        self.plot_changqu =  MplWidget(self, width=5, height=4)
        self.right_layout.addWidget(self.plot_changqu, 1, 4, 5, 4)

        # Fig 4
        self.plot_secha = MplWidget(self, width=5, height=4)
        self.right_layout.addWidget(self.plot_secha, 6, 4, 5, 4)

        # window config
        self.setWindowOpacity(1.0) # 设置窗口透明度
        self.main_layout.setSpacing(0)

    # 输入数据
    def import_data(self):
        sender = self.sender()
        if sender.text() == "输入光学系统参数":
            self.input_flag = 1
            self.input_sys_table(10, 5, '编号', '到下一面的距离', '曲率半径', '材料', '口径')
        if sender.text() == "输入实物参数":
            self.input_flag = 2
            self.input_ray_table(10, 10, '编号', '物距', '波长 (nm)', '光线类型', '是否为无穷远', '最大物高', '最大入射高度', '最大物方视场角', '孔径取点系数', '视场取点系数')


    # 读取 id 判断是否是管理员
    def match_id(self):
        list_id = ['123456']
        line_id = self.id_line.text()
        # 与输入的学号比较
        if line_id in list_id:
            # 输入正确的学号后才能开始操作
            self.import_sys_button.setEnabled(True)
            self.import_ray_button.setEnabled(True)
            self.clear_button.setEnabled(True)
            self.import_button.setEnabled(True)
            self.output_button.setEnabled(True)
            self.num_line.setEnabled(True)

            self.id_line.setEnabled(False)
            Qreply = QMessageBox.information(self, "Message", "登录成功，欢迎使用本软件！", QMessageBox.Ok)
        else:
            Qreply = QMessageBox.critical(self, "Message", "登录失败，请输入正确的管理员帐号!", QMessageBox.Retry | QMessageBox.Cancel, QMessageBox.Retry)

    def match_cal_num(self):
        self.sys_cal_button.setEnabled(True)
        self.sys_draw_button.setEnabled(True)
        cal_type = int(self.num_line.text())
        global num_line
        num_line = cal_type

        if  1 <= cal_type <= 9:
            self.cal_flag = cal_type
            if cal_type == 1:
                Qreply = QMessageBox.information(self, "Message", "开始计算焦距、像方主面位置、出瞳距", QMessageBox.Ok)
            elif cal_type == 2:
                Qreply = QMessageBox.information(self, "Message", "开始计算像距", QMessageBox.Ok)
            elif cal_type == 3:
                Qreply = QMessageBox.information(self, "Message", "开始计算像高", QMessageBox.Ok)
            elif cal_type == 4:
                Qreply = QMessageBox.information(self, "Message", "开始计算球差", QMessageBox.Ok)
            elif cal_type == 5:
                Qreply = QMessageBox.information(self, "Message", "开始计算位置色差", QMessageBox.Ok)
            elif cal_type == 6:
                Qreply = QMessageBox.information(self, "Message", "开始计算场曲、像散", QMessageBox.Ok)
            elif cal_type == 7:
                Qreply = QMessageBox.information(self, "Message", "开始计算畸变", QMessageBox.Ok)
            elif cal_type == 8:
                Qreply = QMessageBox.information(self, "Message", "开始计算倍率色差", QMessageBox.Ok)
            elif cal_type == 9:
                Qreply = QMessageBox.information(self, "Message", "开始计算子午彗差", QMessageBox.Ok)
            self.cal_list.append(cal_type)

            obj_input = read_obj_data()  # 从文件读入物
            ray_list = obj_input.obj2raylist(cal_type)

            # 读入数据
            for i in range(len(ray_list)):
                item = QTableWidgetItem(str(i))
                item.setForeground(QBrush(QColor(144, 182, 240)))
                item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.data_table.setItem(i, 0, item)

                item = QTableWidgetItem(str(ray_list[i].l_obj))
                item.setForeground(QBrush(QColor(144, 182, 240)))
                item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.data_table.setItem(i, 1, item)

                item = QTableWidgetItem(str(ray_list[i].wavelength*1000))
                item.setForeground(QBrush(QColor(144, 182, 240)))
                item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.data_table.setItem(i, 2, item)

                item = QTableWidgetItem(str(ray_list[i].raytype))
                item.setForeground(QBrush(QColor(144, 182, 240)))
                item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.data_table.setItem(i, 3, item)

                item = QTableWidgetItem(str(ray_list[i].inf_flag))
                item.setForeground(QBrush(QColor(144, 182, 240)))
                item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.data_table.setItem(i, 4, item)

                item = QTableWidgetItem(str(ray_list[i].y_max))
                item.setForeground(QBrush(QColor(144, 182, 240)))
                item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.data_table.setItem(i, 5, item)

                item = QTableWidgetItem(str(ray_list[i].h_max))
                item.setForeground(QBrush(QColor(144, 182, 240)))
                item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.data_table.setItem(i, 6, item)

                item = QTableWidgetItem(str(rad2angle(ray_list[i].w_max)))
                item.setForeground(QBrush(QColor(144, 182, 240)))
                item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.data_table.setItem(i, 7, item)

                item = QTableWidgetItem(str(ray_list[i].K_eta))
                item.setForeground(QBrush(QColor(144, 182, 240)))
                item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.data_table.setItem(i, 8, item)

                item = QTableWidgetItem(str(ray_list[i].K_w))
                item.setForeground(QBrush(QColor(144, 182, 240)))
                item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.data_table.setItem(i, 9, item)

        else:
            Qreply = QMessageBox.critical(self, "Message", "请输入正确的计算序号!", QMessageBox.Retry | QMessageBox.Cancel, QMessageBox.Retry)

    # 输入光学系统参数
    def input_sys_table(self, row_num, col_num, *args):
        # 设置行列
        self.data_table.setRowCount(row_num)
        self.data_table.setColumnCount(col_num)

        # 设置表头信息
        header_list = [item for item in args]
        self.data_table.setHorizontalHeaderLabels(header_list)
        self.data_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.data_table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.data_table.verticalHeader().setVisible(False)
        self.data_table.horizontalHeader().setVisible(True)

        for i in range(row_num):
            for j in range(col_num):
                item = QTableWidgetItem("")
                item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                item.setForeground(QBrush(QColor(144, 182, 240)))
                self.data_table.setItem(i, j, item)


    # 输入光线参数
    def input_ray_table(self, row_num, col_num, *args):
        # 设置行列
        self.data_table.setRowCount(row_num)
        self.data_table.setColumnCount(col_num)

        # 设置表头信息
        header_list = [item for item in args]
        self.data_table.setHorizontalHeaderLabels(header_list)
        self.data_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.data_table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.data_table.verticalHeader().setVisible(False)
        self.data_table.horizontalHeader().setVisible(True)

        for i in range(row_num):
            for j in range(col_num):
                item = QTableWidgetItem("")
                item.setForeground(QBrush(QColor(144, 182, 240)))
                item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.data_table.setItem(i, j, item)

    # 计算光学系统的参数
    def cal_data(self):
        cal_type = int(self.cal_flag)
        cur_list = read_curve_data()  # 从文件读入曲面列表
        obj_input = read_obj_data()  # 从文件读入光线列表
        ray_list = obj_input.obj2raylist(cal_type)
        opt_sys = optsys(cur_list)  # 实例化光学系统

        data = cal_main(cal_type, ray_list, opt_sys)  # 计算数据
        save_data(data, cal_type)  # 将计算结果写入文件
        Qreply = QMessageBox.information(self, "Message", "计算成功，请在对应文件中查看计算结果！", QMessageBox.Ok)

    # 绘制像差曲线
    def draw_fig(self):
        caling = 0
        quicha_flag = 4
        weizhisecha_flag = 5
        changqu_flag = 6
        jibian_flag = 7
        beilvsecha_flag = 8

        if (quicha_flag in self.cal_list) and (weizhisecha_flag in self.cal_list):
            if self.cal1 == 0:
                self.cal1 = 1
                caling = 1
                self.plot_qiucha.plot_axial_curve()
                self.cal_list.remove(quicha_flag)
                self.cal_list.remove(weizhisecha_flag)
                Qreply = QMessageBox.information(self, "Message", "成功绘制色球差曲线!")
            elif self.cal1 == 1:
                Qreply = QMessageBox.critical(self, "Message", "色球差曲线已绘制，请勿重复绘图！", QMessageBox.Ok)

        if jibian_flag in self.cal_list:
            if self.cal2 == 0:
                self.cal2 = 1
                caling = 1
                self.plot_jibian.plot_cal_distortion_curve()
                self.cal_list.remove(jibian_flag)
                Qreply = QMessageBox.information(self, "Message", "成功绘制畸变曲线!")
            elif self.cal2 == 1:
                Qreply = QMessageBox.critical(self, "Message", "畸变曲线已绘制，请勿重复绘图！", QMessageBox.Ok)

        if beilvsecha_flag in self.cal_list:
            if self.cal3 == 0:
                self.cal3 = 1
                caling = 1
                self.plot_secha.plot_lateral_color_curve()
                self.cal_list.remove(beilvsecha_flag)
                Qreply = QMessageBox.information(self, "Message", "成功绘制倍率色差曲线!")
            elif self.cal3 == 1:
                Qreply = QMessageBox.critical(self, "Message", "倍率色差曲线已绘制，请勿重复绘图！", QMessageBox.Ok)

        if changqu_flag in self.cal_list:
            if self.cal4 == 0:
                self.cal4 = 1
                caling = 1
                self.plot_changqu.plot_filed_curvature_curve()
                self.cal_list.remove(changqu_flag)
                Qreply = QMessageBox.information(self, "Message", "成功绘制像散曲线!")
            elif self.cal4 == 1:
                Qreply = QMessageBox.critical(self, "Message", "像散曲线已绘制，请勿重复绘图！", QMessageBox.Ok)


        if caling == 1:
            self.save_fig_button.setEnabled(True)
        else:
            Qreply = QMessageBox.critical(self, "Message", "参数不足，无法正确计算像差！", QMessageBox.Ok)

    # 保存图片成功时的提醒
    def pic_messagebox(self):
        Qreply = QMessageBox.information(self, "Message", "图片保存成功，请到对应目录下查看!")

    # 保存图片的设置
    def fig_save(self):
        save_flag = 0

        pdir = './fig'
        if not os.path.exists(pdir):
            os.mkdir(pdir)

        if self.cal1 == 1:
            filename = r"fig/axial_curve.png"
            self.plot_qiucha.figure.savefig(filename)
            save_flag = 1

        if self.cal2 == 1:
            filename = r"fig/distortion_curve.png"
            self.plot_jibian.figure.savefig(filename)
            save_flag = 1

        if self.cal3 == 1:
            filename = r"fig/lateral_color_curve.png"
            self.plot_secha.figure.savefig(filename)
            save_flag = 1

        if self.cal4 == 1:
            filename = r"fig/filed_curvature_curve.png"
            self.plot_changqu.figure.savefig(filename)
            save_flag = 1

        if save_flag == 1:
            self.pic_messagebox()
        else:
            Qreply = QMessageBox.critical(self, "Message", "图片保存失败！", QMessageBox.Ok)


    # 退出按钮
    def quit_act(self):
        # sender 是发送信号的对象
        sender = self.sender()
        print(sender.text() + '键被按下')
        qApp = QApplication.instance()
        qApp.quit()

    # 清空按钮
    def clear_act(self):
        self.data_table.clearContents()

    # 导入按钮
    def import_act(self):

        self.filename, ftype = QFileDialog.getOpenFileName(self, "选择导入文件", "data", "All Files(*);; Excel(*.csv);; Txt(*.txt)")
        if len(self.filename) > 0:  # 判断路径非空
            Qreply = QMessageBox.information(self, "Message", "导入文件成功!", QMessageBox.Ok)
            if 'curve.csv' in self.filename:
                # 读入数据
                input_table = pd.read_csv(self.filename, keep_default_na=False)
                input_table_rows = input_table.shape[0]
                input_table_colunms = input_table.shape[1]

                for i in range(input_table_rows):
                    input_table_rows_values = input_table.iloc[[i]]
                    input_table_rows_values_array = np.array(input_table_rows_values)
                    input_table_rows_values_list = input_table_rows_values_array.tolist()[0]
                    for j in range(input_table_colunms):
                        input_table_items_list = input_table_rows_values_list[j]
                        input_table_items = str(input_table_items_list)

                        item = QTableWidgetItem(input_table_items)
                        item.setForeground(QBrush(QColor(144, 182, 240)))
                        item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                        self.data_table.setItem(i, j, item)

        else:
            Qreply = QMessageBox.critical(self, "Message", "请导入正确的文件!", QMessageBox.Retry | QMessageBox.Cancel)

    # 导出按钮
    def save_act(self):
        col_num = self.data_table.columnCount()
        row_num = self.data_table.rowCount()
        wb = openpyxl.Workbook()

        # create header list
        Headers = []
        savefile = QFileDialog.getSaveFileName(self, '选择保存路径', 'data', 'Excel files(*.csv)')
        fpath = savefile[0]

        for i in range(col_num):
            Headers.append(self.data_table.horizontalHeaderItem(i).text())
        # 创建表
        df = pd.DataFrame(columns=Headers)
        for row in range(row_num):
            for col in range(col_num):
                item = self.data_table.item(row, col)
                df.at[row, Headers[col]] = item.text() if item is not None else ""
        df.to_csv(fpath, index=False)
        Qreply = QMessageBox.information(self, "Message", "导出成功，请在对应目录下查看文件!", QMessageBox.Ok)


    def center(self):
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move(int((screen.width() - size.width()) / 2), int((screen.height() - size.height()) / 2))
