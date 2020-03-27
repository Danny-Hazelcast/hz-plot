import matplotlib
matplotlib.use('Agg')

import os
import json
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt


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
        stats = {'bench': name.replace('.csv', ''), 'dir': dir, 'colName': "m1_rate"}

        for dirpath, dirnames, filenames in os.walk(dir):
            for fileName in filenames:
                if fileName.endswith(name):
                    f = dirpath + "/" + fileName
                    df = pd.read_csv(f)

                    df = df.ix[30:]

                    maxi = df["m1_rate"].max()
                    mini = df["m1_rate"].min()
                    diff = maxi - mini
                    pdif = round((diff / ((maxi + mini) / 2)) * 100.0)

                    mean = df["m1_rate"].mean()
                    std = df["m1_rate"].std()
                    variance = df["m1_rate"].var()

                    means.append(mean)

                    driverId = os.path.basename(dirpath)
                    stats[driverId+'-max'] = round(maxi)
                    stats[driverId+'-min'] = round(mini)
                    stats[driverId+'-pdif'] = round(pdif)
                    stats[driverId+'-mean'] = round(mean)
                    stats[driverId+'-std'] = round(std)
                    stats[driverId + '-variance'] = round(std)

                    print(df.shape, f, "m1_rate mean="+str(round(mean)))

        if len(means) > 0:
            maxi = max(means)
            mini = min(means)
            diff = maxi - mini
            stats['max'] = round(maxi)
            stats['min'] = round(mini)
            stats['dif'] = round(diff)
            stats['pdif'] = round((diff / ((maxi+mini)/2)) * 100.0)
            stats['sum'] = round(sum(means))
            stats['drivers'] = round(len(means))
            stats['ave'] = round(sum(means) / len(means))

            stats_json = json.dumps(stats)

            f = open(dir+"/"+name.replace('.csv', '')+"-m1_rate-stats.txt", "w")
            f.writelines(stats_json)
            f.close()


stats_txt = set()
for p in sorted(list(Path(".").rglob("*-stats.txt"))):
    stats_txt.add(os.path.basename(p))

for f in stats_txt:
    df = pd.DataFrame()

    for p in sorted(list(Path(".").rglob(f))):
        data = json.load(open(p))
        df = df.append(data, ignore_index=True)

    name=df['bench'].iloc[0]+"-"+df['colName'].iloc[0]
    df.to_csv(name+".txt", index=False)

    df.plot.bar(x='dir', y='pdif', rot=90)
    plt.savefig(name+"-pdif.png")
    plt.close()

    df.plot.bar(x='dir', y='ave', rot=90)
    plt.savefig(name+"-ave.png")
    plt.close()

    df.plot.bar(x='dir', y='sum', rot=90)
    plt.savefig(name+"-sum.png")
    plt.close()

    df.plot.bar(x='dir', y='max', rot=90)
    plt.savefig(name+"-max.png")
    plt.close()

    idx = df['pdif'].argmax()
    print("max range "+df.at[idx, 'dir']+" "+df.at[idx, 'bench']+" "+df.at[idx, 'colName']+" "+str(df.at[idx, 'pdif']))

    idx = df['pdif'].argmin()
    print("min range "+df.at[idx, 'dir']+" "+df.at[idx, 'bench']+" "+df.at[idx, 'colName']+" "+str(df.at[idx, 'pdif']))


    idx = df['sum'].argmax()
    print("max total ops "+df.at[idx, 'dir']+" "+df.at[idx, 'bench']+" "+df.at[idx, 'colName']+" "+str(df.at[idx, 'sum']))

    idx = df['sum'].argmin()
    print("min total ops "+df.at[idx, 'dir']+" "+df.at[idx, 'bench']+" "+df.at[idx, 'colName']+" "+str(df.at[idx, 'sum']))
