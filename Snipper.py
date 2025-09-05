#!/usr/bin python
# -*- coding: utf-8 -*-
import sys, os
import numpy
assert numpy
import subprocess
from os.path import basename
from PyQt5.QtCore import QPoint, Qt, QRect
from PyQt5.QtWidgets import QAction, QMainWindow, QApplication, QPushButton, QMenu, QFileDialog
from PyQt5.QtGui import *
import tkinter as tk
import numpy as np
import cv2, pyautogui
from PIL import ImageGrab
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import Qt
from pathlib import Path

class SnippingWidget(QtWidgets.QWidget):
    num_snip = 0
    is_snipping = False
    background = True

    def __init__(self, parent=None):
        super(SnippingWidget, self).__init__()
        self.parent = parent
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        root = tk.Tk()
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        self.setGeometry(0, 0, screen_width, screen_height)
        self.begin = QtCore.QPoint()
        self.end = QtCore.QPoint()

    def start(self):
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        SnippingWidget.background = False
        SnippingWidget.is_snipping = True
        self.setWindowOpacity(0.3)
        QtWidgets.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.CrossCursor))
        self.show()

    def paintEvent(self, event):
        if SnippingWidget.is_snipping:
            brush_color = (128, 128, 255, 100)
            lw = 3
            opacity = 0.3
        else:
            self.begin = QtCore.QPoint()
            self.end = QtCore.QPoint()
            brush_color = (0, 0, 0, 0)
            lw = 0
            opacity = 0
        self.setWindowOpacity(opacity)
        qp = QtGui.QPainter(self)
        qp.setPen(QtGui.QPen(QtGui.QColor('black'), lw))
        qp.setBrush(QtGui.QColor(*brush_color))
        rect = QtCore.QRectF(self.begin, self.end)
        qp.drawRect(rect)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Q:
            self.close()
            event.accept()

    def mousePressEvent(self, event):
        self.begin = event.pos()
        self.end = self.begin
        self.update()

    def mouseMoveEvent(self, event):
        self.end = event.pos()
        self.update()

    def mouseReleaseEvent(self, event):
        SnippingWidget.num_snip += 1
        SnippingWidget.is_snipping = False
        QtWidgets.QApplication.restoreOverrideCursor()
        x1 = min(self.begin.x(), self.end.x())
        y1 = min(self.begin.y(), self.end.y())
        x2 = max(self.begin.x(), self.end.x())
        y2 = max(self.begin.y(), self.end.y())
        self.repaint()
        QtWidgets.QApplication.processEvents()
        img = ImageGrab.grab(bbox=(x1, y1, x2, y2))
        QtWidgets.QApplication.processEvents()
        img = cv2.cvtColor(np.array(img), cv2.COLOR_BGR2RGB)
        Menu(img, SnippingWidget.num_snip, (x1, y1, x2, y2))
        SnippingWidget.background = True

class Menu(QMainWindow):
    COLORS = ['Red', 'Black', 'Blue', 'Green', 'Yellow']
    SIZES = [1, 3, 5, 7, 9, 11]
    default_title = "Snip And Sketch"

    def __init__(self, numpy_image=None, snip_number=None, start_position=(300, 300, 350, 250)):
        super().__init__()
        self._is_exiting = False
        self.drawing = False
        self.brushSize = 3
        self.brushColor = Qt.red
        self.lastPoint = QPoint()
        self.total_snips = 0
        self.title = Menu.default_title
        new_snip_action = QAction('New', self)
        new_snip_action.setShortcut('Ctrl+N')
        new_snip_action.setStatusTip('Snip!')
        new_snip_action.triggered.connect(self.new_image_window)
        brush_color_button = QPushButton("Brush Color")
        colorMenu = QMenu()
        for color in Menu.COLORS:
            colorMenu.addAction(color)
        brush_color_button.setMenu(colorMenu)
        colorMenu.triggered.connect(lambda action: self.change_brush_color(action.text()))
        brush_size_button = QPushButton("Brush Size")
        sizeMenu = QMenu()
        for size in Menu.SIZES:
            sizeMenu.addAction("{0}px".format(str(size)))
        brush_size_button.setMenu(sizeMenu)
        sizeMenu.triggered.connect(lambda action: self.change_brush_size(action.text()))
        save_action = QAction('Save', self)
        save_action.setShortcut('Ctrl+S')
        save_action.setStatusTip('Save')
        save_action.triggered.connect(self.save_file)
        exit_window = QAction('Exit', self)
        exit_window.setShortcut('Esc')
        exit_window.setStatusTip('Exit application')
        exit_window.triggered.connect(self.exit_app)
        self.toolbar = self.addToolBar('Exit')
        self.toolbar.addAction(new_snip_action)
        self.toolbar.addAction(save_action)
        self.toolbar.addWidget(brush_color_button)
        self.toolbar.addWidget(brush_size_button)
        self.toolbar.addAction(exit_window)
        self.snippingTool = SnippingWidget()
        self.setGeometry(*start_position)
        if numpy_image is not None and snip_number is not None:
            self.image = self.convert_numpy_img_to_qpixmap(numpy_image)
            self.change_and_set_title("Snip #{0}".format(snip_number))
        else:
            if os.path.exists("background.PNG"):
                self.image = QPixmap("background.PNG")
            else:
                self.image = QPixmap(800, 600)
                self.image.fill(QColor('white'))
            self.change_and_set_title(Menu.default_title)
        self.resize(self.image.width(), self.image.height() + self.toolbar.height())
        self.show()

    def change_brush_color(self, new_color):
        try:
            self.brushColor = getattr(Qt, new_color.lower())
        except Exception:
            self.brushColor = Qt.red

    def change_brush_size(self, new_size):
        try:
            self.brushSize = int(''.join(filter(lambda x: x.isdigit(), new_size)))
        except Exception:
            self.brushSize = 3

    def new_image_window(self):
        if self.snippingTool.background:
            self._is_exiting = False
            self.close()
            QtWidgets.QApplication.processEvents()
            self.total_snips += 1
            self.snippingTool.start()

    def save_file(self):
        pictures_folder = str(Path.home() / "Pictures/temp")
        try:
            os.makedirs(pictures_folder, exist_ok=True)
        except Exception:
            pass
        file_path, name = QFileDialog.getSaveFileName(self, "Save file",
                                                    pictures_folder,
                                                    "PNG Image file (*.png)")
        if file_path:
            self.image.save(file_path)
            self.change_and_set_title(basename(file_path))
            print(self.title, 'Saved')

    def change_and_set_title(self, new_title):
        self.title = new_title
        self.setWindowTitle(self.title)

    def paintEvent(self, event):
        painter = QPainter(self)
        rect = QRect(0,  self.toolbar.height(), self.image.width(), self.image.height())
        painter.drawPixmap(rect, self.image)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drawing = True
            self.lastPoint = event.pos() - QPoint(0, self.toolbar.height())

    def mouseMoveEvent(self, event):
        if (event.buttons() & Qt.LeftButton) and self.drawing:
            painter = QPainter(self.image)
            painter.setPen(QPen(self.brushColor, self.brushSize, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            painter.drawLine(self.lastPoint, event.pos() - QPoint(0, self.toolbar.height()))
            self.lastPoint = event.pos() - QPoint(0, self.toolbar.height())
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drawing = False

    def exit_app(self):
        self._is_exiting = True
        self.close()

    def closeEvent(self, event):
        if getattr(self, "_is_exiting", False):
            QtWidgets.QApplication.quit()
        else:
            event.accept()

    @staticmethod
    def convert_numpy_img_to_qpixmap(np_img):
        height, width, channel = np_img.shape
        bytesPerLine = 3 * width
        return QPixmap(QImage(np_img.data, width, height, bytesPerLine, QImage.Format_RGB888).rgbSwapped())

class MyWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        root = tk.Tk()
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        self.setGeometry(0, 0, screen_width, screen_height)
        self.setWindowTitle(' ')
        self.begin = QtCore.QPoint()
        self.end = QtCore.QPoint()
        self.setWindowOpacity(0.3)
        QtWidgets.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.CrossCursor))
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.show()

    def paintEvent(self, event):
        qp = QtGui.QPainter(self)
        qp.setPen(QtGui.QPen(QtGui.QColor('black'), 3))
        qp.setBrush(QtGui.QColor(128, 128, 255, 128))
        qp.drawRect(QtCore.QRect(self.begin, self.end))

    def mousePressEvent(self, event):
        self.begin = event.pos()
        self.end = self.begin
        self.update()

    def mouseMoveEvent(self, event):
        self.end = event.pos()
        self.update()

    def mouseReleaseEvent(self, event):
        self.close()
        x1 = min(self.begin.x(), self.end.x())
        y1 = min(self.begin.y(), self.end.y())
        x2 = max(self.begin.x(), self.end.x())
        y2 = max(self.begin.y(), self.end.y())
        img = ImageGrab.grab(bbox=(x1, y1, x2, y2))
        temp_capture = 'capture.png'
        try:
            img.save(temp_capture)
            img = cv2.cvtColor(np.array(img), cv2.COLOR_BGR2RGB)
        finally:
            try:
                if os.path.exists(temp_capture):
                    os.remove(temp_capture)
            except Exception:
                pass

    def save_file(self):
        file_path, name = QFileDialog.getSaveFileName(self, "Save file", self.title, "PNG Image file (*.png)")
        if file_path:
            self.image.save(file_path)
            self.change_and_set_title(basename(file_path))
            print(self.title, 'Saved') 

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.showFullScreen()

stylesheet = """
    MainWindow {
        background-image: url("./temp.png");
    }
"""

class Snip:
    def __init__(self):
        pass

    @staticmethod
    def Snip_Brush():
        app = QApplication(sys.argv)
        app.setQuitOnLastWindowClosed(False)
        mainMenu = Menu()
        sys.exit(app.exec_())

    def killprocess(self):
        def check_pid(pid):        
            try:
                print("-------YOU MAY IGNORE THE BELOW ERROR/WARNING GIVEN-------")
                os.kill(pid, 0)
            except OSError:
                return True
        os.system('cmd /c tasklist /v /fo csv | findstr /i "hellofromwin64py" > pidchecker.txt')
        file = open("pidchecker.txt")
        pidfile = file.read()
        pid = int(pidfile[14] + pidfile[15] + pidfile[16] + pidfile[17])
        check_pid(pid)

    @staticmethod
    def Snip_only():  
        app = QApplication(sys.argv) 
        app.setQuitOnLastWindowClosed(False)
        app.setStyleSheet(stylesheet)
        window2hello = MainWindow()
        window2hello.setWindowTitle('hellofromwin64py')
        window2hello.showFullScreen()
        window = MyWidget()
        window.show()
        app.exec_()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    mainMenu = Menu()
    sys.exit(app.exec_())
