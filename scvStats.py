import matplotlib
matplotlib.use('Agg')

import sys
import os
import pandas as pd
import matplotlib.pyplot as plt
import glob

dirs = set()
for dirpath, dirnames, filenames in os.walk('.'):
    for fileName in filenames:
        if fileName.endswith(".csv"):
            dirs.add(os.path.dirname(os.path.normpath(dirpath)))


names = set()
dirs = sorted(list(dirs))

for dir in dirs:
    for dirpath, dirnames, filenames in os.walk(dir):
        for fileName in filenames:
            if fileName.endswith(".csv"):
                names.add(fileName)

    print("dir "+dir)
    for name in names:

        means = []

        for dirpath, dirnames, filenames in os.walk(dir):
            for fileName in filenames:
                if fileName.endswith(name):
                    f = dirpath + "/" + fileName
                    df = pd.read_csv(f)
                    df = df.ix[30:]

                    mean = df["m1_rate"].mean()
                    means.append(mean)

                    print(f, "m1_rate mean="+str(round(mean)))

        if len(means) > 0:
            maxz = max(means)
            minz = min(means)
            diff = maxz - minz
            ave = sum(means) / len(means)

            print(dir+"/*/"+name, "ave="+str(round(ave)))

            print("range="+str(round(diff)), "max="+str(round(maxz)), "min="+str(round(minz)))






