import matplotlib
matplotlib.use('Agg')

import os
import sys
import json
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
from pandas.io.json import json_normalize


csv_dirs = set()
for dirpath, dirnames, filenames in os.walk('.'):
    for fileName in filenames:
        if fileName.endswith(".csv"):
            csv_dirs.add(os.path.dirname(os.path.normpath(dirpath)))


csv_files = set()
csv_dirs = sorted(list(csv_dirs))

for dir in csv_dirs:
    for dirpath, dirnames, filenames in os.walk(dir):
        for fileName in filenames:
            if fileName.endswith(".csv"):
                csv_files.add(fileName)

    print("dir "+dir)
    for name in csv_files:

        means = []
        stats = {'bench': name}

        for dirpath, dirnames, filenames in os.walk(dir):
            for fileName in filenames:
                if fileName.endswith(name):
                    f = dirpath + "/" + fileName
                    df = pd.read_csv(f)
                    df = df.ix[30:]

                    mean = df["m1_rate"].mean()
                    means.append(mean)

                    driverId = os.path.basename(dirpath)
                    stats[driverId+'-m1_rate-mean'] = round(mean)

                    print(f, "m1_rate mean="+str(round(mean)))

        if len(means) > 0:
            stats['max'] = round(max(means))
            stats['min'] = round(min(means))
            stats['dif'] = round(max(means) - min(means))
            stats['ave'] = round(sum(means) / len(means))

            stats_json = json.dumps(stats)
            print(stats_json)

            f = open(dir+"/"+name.replace('.csv', '')+"-m1_rate-stats.txt", "w")
            f.writelines(stats_json)
            f.close()


files = set()
for p in sorted(list(Path(".").rglob("*-stats.txt"))):
    files.add(os.path.basename(p))

for f in files:
    for p in sorted(list(Path(".").rglob(f))):
        print(p)
        data = json.load(open(p))
        print(data)


