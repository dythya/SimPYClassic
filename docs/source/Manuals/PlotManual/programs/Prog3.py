# Prog3.py
from SimPy.SimPlot import *
plt = SimPlot()
plt.plotStep([[0, 0], [1, 1], [2, 4], [3, 9]],
             color="red", width=2)
plt.mainloop()
