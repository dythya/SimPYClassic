# AdvancedAPI.py
from SimPy. SimPlot import *
plt = SimPlot()                                   # step 1
plt.root.title("Advanced API example")            # step 3
line = plt.makeLine([[0, 42], [1, 1], [4, 16]])      # step 4
bar = plt.makeBars([[0, 42], [1, 1], [4, 16]],
                   color='blue')                  # step 4
sym = plt.makeSymbols([[1, 1]], marker="triangle",
                      size=3, fillcolor="red")    # step 4
obj = plt.makeGraphObjects([line, bar, sym])      # step 5
frame = Frame(plt.root)                           # step 6
graph = plt.makeGraphBase(frame, 500, 300,
                          title="Line and bars")  # step 7
graph.pack()                                      # step 8
graph.draw(obj)                                   # step 9
frame.pack()                                      # step 10
graph.postscr()                                   # step 11
plt.mainloop()                                    # step 12
