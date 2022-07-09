#!/usr/bin/python3
# -*- coding: utf-8 -*-

from OPTui import *


def main():
    app = QApplication(sys.argv)
    gui = MainUi()
    gui.show()
    Qreply = QMessageBox.information(gui, "Message", "请输入管理员帐号登录！", QMessageBox.Ok)
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
