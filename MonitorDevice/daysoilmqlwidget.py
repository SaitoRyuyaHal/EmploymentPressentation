from PyQt5.QtWidgets import *
from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib.figure import Figure
from qbstyles import mpl_style
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import datetime 
from VegetableDatabase import VegetableCsv


class DaySoilMqlWidget(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.date_base = VegetableCsv()
        self.canvas = FigureCanvas(Figure())
        self.y = np.array([])
        self.t = np.array([])
        self.vertical_layout = QVBoxLayout()
        self.vertical_layout.addWidget(self.canvas)
        self.canvas.axes = self.canvas.figure.add_subplot(111)
        self.canvas.axes.set_ylim(0, 100)
        self.time = datetime.datetime.now()
        self.date_update()
        self.plot, = self.canvas.axes.plot(self.t, self.y,
            label="soil moisture")
        self.canvas.axes.legend(loc="center right",
            bbox_to_anchor=(0.5, 0, 0.5, 1))
        self.canvas_plot()
        self.setLayout(self.vertical_layout)

    def date_update(self):
        soil_dates = self.date_base.read_day_soil(self.time)
        for i in soil_dates:
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
        self.canvas.axes.set_title("Soil Moisture: {0}".format(self.time.strftime('%Y-%m-%d')), fontsize=6)

