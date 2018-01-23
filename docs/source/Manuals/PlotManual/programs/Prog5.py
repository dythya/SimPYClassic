# Prog5.py
from SimPy.SimPlot import *
plt = SimPlot()
plt.plotScatter([[0, 0], [1, 1], [2, 4], [3, 9]],
                color="green", size=2, marker='triangle')
plt.mainloop()
