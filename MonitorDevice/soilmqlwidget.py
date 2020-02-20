from PyQt5.QtWidgets import *
from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib.figure import Figure
from qbstyles import mpl_style
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import datetime 

class SoilMqlWidget(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.buffer_num = 120
        self.t = np.array([])
        self.y = np.array([])
        self.canvas = FigureCanvas(Figure())
        vertical_layout = QVBoxLayout()
        vertical_layout.addWidget(self.canvas)
        self.canvas.axes = self.canvas.figure.add_subplot(111)
        self.canvas.axes.set_ylim(0, 100)
        self.plot, = self.canvas.axes.plot(self.t, self.y, label="soil moisture")
        self.canvas_plot()
        self.canvas.axes.legend(loc="center right", bbox_to_anchor=(0.5, 0, 0.5, 1))
        self.setLayout(vertical_layout)

    def update_plot_date(self, soil_value, time):
        if len(self.t) >= self.buffer_num:
            self.t = np.append(self.t, time)
            self.t = np.delete(self.t, 0)
            self.y = np.append(self.y, soil_value)
            self.y = np.delete(self.y, 0)
        else:
            self.t = np.append(self.t, time)
            self.y = np.append(self.y, soil_value)
        self.plot.set_xdata(self.t)
        self.plot.set_ydata(self.y)
        self.canvas_plot()
        self.canvas.draw()

    def canvas_plot(self):
        if len(self.t) <= 1:
            return
        self.canvas.axes.set_xlim(min(self.t), max(self.t))
        self.canvas.axes.set_xticks([])
