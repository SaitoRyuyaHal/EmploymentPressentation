from PyQt5.QtWidgets import *
from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib.figure import Figure
from qbstyles import mpl_style
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import datetime 
from VegetableDatabase import VegetableCsv

class WaterPumpMqlWidget(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.date_base = VegetableCsv()
        self.buffer_num = 120
        self.t = np.array([])
        self.y = np.array([])
        self.canvas = FigureCanvas(Figure())
        vertical_layout = QVBoxLayout()
        vertical_layout.addWidget(self.canvas)
        self.canvas.axes = self.canvas.figure.add_subplot(111)
        self.canvas.axes.set_ylim(0, 100)
        self.time = datetime.datetime.now()
        self.date_update()
        self.plot, = self.canvas.axes.plot(self.t, self.y, label="Water Pump Speed")
        self.canvas.axes.legend(loc="center right", bbox_to_anchor=(0.5, 0, 0.5, 1))
        self.canvas_plot()
        self.setLayout(vertical_layout)

    def date_update(self):
        waterpump_data = self.date_base.read_day_waterpump_speed(self.time)
        for i in waterpump_data:
            self.t = np.append(self.t, 
                datetime.datetime.strptime(i['TIME'],
                                           '%Y-%m-%d %H:%M:%S.%f'))
            self.y = np.append(self.y, float(i['SOIL']))

    def canvas_plot(self):
        if len(self.t) <= 1:
            return
        self.canvas.axes.set_xlim(min(self.t), max(self.t))
        self.canvas.axes.xaxis.set_major_formatter(
            mdates.DateFormatter("%H:%M"))
        labels = self.canvas.axes.get_xticklabels()
        plt.setp(labels, rotation=30, fontsize=6)
        self.canvas.axes.set_title("Motor Run: {0}".format(self.time.strftime('%Y-%m-%d')), fontsize=6)
