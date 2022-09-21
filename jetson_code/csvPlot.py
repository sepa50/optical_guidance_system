from turtle import end_fill
import pandas as pd
import os
import matplotlib.pyplot as plt

data = pd.read_csv('my_csv.csv')
data.plot()
plt.show()
plt.savefig('test', format='png')
    

    

    