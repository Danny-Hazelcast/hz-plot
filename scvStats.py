import matplotlib
matplotlib.use('Agg')

import sys
import os
import pandas as pd
import matplotlib.pyplot as plt

csv_files = set()
dirpaths = set()
for dirpath, dirnames, filenames in os.walk('.'):
    for fileName in filenames:
        if fileName.endswith(".csv"):
            csv_files.add(fileName)
            print(dirpath)
            print(dirnames)
            print(filenames)
