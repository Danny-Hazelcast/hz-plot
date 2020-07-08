import matplotlib.pyplot as plt
import pandas as pd
import os


class BenchDriver(object):
    def __init__(self, dirpath, fileName):
        self.df = pd.read_csv(dirpath + "/" + fileName)
        self.outPath = dirpath+"/plots/"+fileName.replace('.csv', '')
        self.id = os.path.basename(os.path.normpath(dirpath))

        if "t" not in self.df.columns :
            self.df.to_csv(dirpath + "/" + fileName, header=False)
            self.df = pd.read_csv(dirpath + "/" + fileName)

        self.df['qty'] = self.df['count'].diff()
        self.df['qty'].iloc[0] = self.df['count'].iloc[0]


    def set_data_length(self, min_len):
        sz = self.df.shape[0] - min_len
        if sz != 0:
            self.df = self.df[sz:]
            self.df = self.df[:-1]

    def drop(self, ticks):
        #self.df = self.df.ix[ticks:]
        self.df = self.df.iloc[ticks:]

    def save_chart(self, ylabel, title, fileName):
        plt.title(title)

        #plt.ylim(ymin=0)
        plt.ylim(bottom=0)

        plt.grid(True)
        plt.xlabel("duration seconds")
        plt.ylabel(ylabel)
        os.makedirs(self.outPath+"/", exist_ok=True)
        plt.savefig(self.outPath+"/"+fileName)
        plt.clf()
        plt.close()
        print(self.outPath+"/"+fileName)

    def chart_individual(self):
        print("plotting "+self.id, self.df.shape)

        self.df[["max"]].plot(figsize=(10, 4))
        self.save_chart('operation latency ms', self.id+' latency percentiles', self.id+'-maxlat.png')

        self.df[["p75", "p99", "min"]].plot(figsize=(10, 4))
        self.save_chart('operation latency ms', self.id+' latency percentiles', self.id+'-latencys.png')

        self.df[["m1_rate"]].plot(figsize=(10, 4))
        self.save_chart("operations per second", self.id+' operation throughput', self.id+"-throughput.png")

        self.df[["qty"]].plot(figsize=(10, 4))
        self.save_chart("operations per second", self.id+' operation throughput', self.id+"-ops-qty.png")
