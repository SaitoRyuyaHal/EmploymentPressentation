from PyQt5.QtWidgets import *
from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib.figure import Figure
from qbstyles import mpl_style
import matplotlib.pyplot as plt
import numpy as np
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from VegetableDatabase import VegetableCsv

class MultiMqlWidget(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.date_base = VegetableCsv()
        self.canvas = FigureCanvas(Figure())
        self.t = np.array([])
        self.y = np.array([])
        self.vertical_layout = QVBoxLayout()
        self.vertical_layout.addWidget(self.canvas)
        self.canvas.axes = self.canvas.figure.add_subplot(111)
        self.canvas.axes.set_ylim(0, 1000)
        self.update_plot()
        self.plot, = self.canvas.axes.plot(self.t, self.y, label="integral_temp")
        self.canvas.axes.legend(loc="center right", bbox_to_anchor=(0.5, 0, 0.5, 1))
        self.setLayout(self.vertical_layout)

    def update_plot(self):
        self.date_update()
        self.canvas_plot()

    def update_plot_date(self, integral_data, time):
        self.date_update()
        if len(self.y) <= 0:
            return
        if self.y[-1] != integral_data:
            self.y = np.append(self.y, integral_data)
            self.t = np.append(self.t, time)
        self.plot.set_xdata(self.t)
        self.plot.set_ydata(self.y)
        self.canvas_plot()
        self.canvas.draw()

    def canvas_plot(self):
        if len(self.t) <= 1:
            return
        self.canvas.axes.set_xlim(min(self.t), max(self.t))
        self.canvas.axes.xaxis.set_major_formatter(
            mdates.DateFormatter("%m-%d"))
        labels = self.canvas.axes.get_xticklabels()
        plt.setp(labels, rotation=0, fontsize=6)

    def date_update(self):
        self.t = np.array([])
        self.y = np.array([])
        integral_temperatures = self.date_base.readIntegralTemperature()
        integral_temperatures = integral_temperatures[1:]
        for i in integral_temperatures:
            self.t = np.append(self.t, 
                datetime.datetime.strptime(i['TIME'],
                                           '%Y-%m-%d %H:%M:%S.%f'))
            self.y = np.append(self.y, float(i['TEMPERATURE']))
