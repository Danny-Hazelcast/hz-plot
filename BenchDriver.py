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

        #print(dirpath+"/"+fileName, self.id, self.df.shape)

    def set_data_length(self, min_len):
        sz = self.df.shape[0] - min_len
        if sz != 0:
            #self.df = self.df[:-sz]
            self.df = self.df[sz:]
        print(self.id, self.df.shape)



    def drop(self, percentage):
        length = self.df.shape[0]
        drop = length*percentage
        self.df = self.df.ix[drop:]

    def save_chart(self, ylabel, title, fileName):
        plt.title(title)
        plt.ylim(ymin=0)
        plt.grid(True)
        plt.xlabel("bench duration")
        plt.ylabel(ylabel)
        os.makedirs(self.outPath+"/", exist_ok=True)
        plt.savefig(self.outPath+"/"+fileName)
        plt.clf()
        plt.close()

    def chart_individual(self):
        print("plotting "+self.id)

        self.df[["max"]].plot(figsize=(10, 4))
        self.save_chart('operation latency ms', self.id+' latency percentiles', self.id+'-maxlat.png')

        self.df[["p75", "p99", "min"]].plot(figsize=(10, 4))
        self.save_chart('operation latency ms', self.id+' latency percentiles', self.id+'-latencys.png')

        self.df[["m1_rate"]].plot(figsize=(10, 4))
        self.save_chart("operations per second", self.id+' operation throughput', self.id+"-throughput.png")
