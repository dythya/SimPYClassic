# Prog2.py
from SimPy.SimPlot import *
plt = SimPlot()
plt.plotLine([[0, 0], [1, 1], [2, 4], [3, 9]], title="This is prettier",
             color="red", width=2, smooth=True)
plt.mainloop()
