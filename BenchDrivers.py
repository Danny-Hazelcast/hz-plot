import os
import pandas as pd
import matplotlib.pyplot as plt
import BenchDriver as db


class BenchDrivers(object):
    def __init__(self, base_dir):
        self.cluster_id = os.path.basename(os.path.normpath(base_dir))
        self.baseInputDir = base_dir
        self.baseOutputDir = base_dir + "/plots"
        self.drivers = None
        self.benchMarks_list = self.get_benchmarks()
        self.bench = None

    def get_cluster_id(self):
        return self.cluster_id

    def get_benchmarks(self):
        csv_files = set()
        for dirpath, dirnames, filenames in os.walk(self.baseInputDir):
            for fileName in filenames:
                if fileName.endswith(".csv"):
                    csv_files.add(fileName)

        return sorted(list(csv_files))

    def set_benchmark(self, bench):
        self.bench = bench.replace('.csv', '')
        self.drivers = self.bench_drivers_data_frames(bench)

    def has_benchmark(self):
        if len(self.benchMarks_list) == 0:
            return False
        return True

    @staticmethod
    def has_any_bench(bench_drivers_list):
        for driver in bench_drivers_list:
            if not driver.has_benchmark():
                return False
        return True

    def next_benchmark(self):
        if len(self.benchMarks_list) == 0:
            return False

        self.bench = self.benchMarks_list.pop(0).replace('.csv', '')
        self.drivers = self.bench_drivers_data_frames(self.bench+'.csv')
        return True

    def get_bench_name(self):
        return self.bench

    def bench_drivers_data_frames(self, bench):
        res = set()
        for dirpath, dirnames, filenames in os.walk(self.baseInputDir):
            for fileName in filenames:
                if fileName.endswith(bench):
                        res.add(db.BenchDriver(dirpath, fileName))

        lengths = []
        for driver in res:
            lengths.append(driver.df.shape[0])

        min_len = min(lengths)

        for driver in res:
            driver.set_data_length(min_len)

        return res

    def drop(self, percentage):
        for driver in self.drivers:
            driver.drop(percentage)

    def collate_columns(self, col_name):
        cols = []
        keys = []
        for driver in self.drivers:
            cols.append(driver.df[col_name])
            keys.append(driver.id + "-" + col_name)
        return pd.concat(cols, axis=1, keys=keys)

    def get_col_sum(self, col_name):
        df = self.collate_columns(col_name)
        sum_df = pd.DataFrame()
        sum_df[self.cluster_id + '-drivers_sum-' + col_name] = df.sum(axis=1)
        return sum_df

    def get_col_mean(self, *col_names):
        result_df = pd.DataFrame()
        for colName in col_names:
            df = self.collate_columns(colName)
            result_df[self.cluster_id + '-drivers_mean-' + colName] = df.mean(axis=1)
        return result_df

    def get_col_max(self, *col_names):
        max_df = pd.DataFrame()
        for colName in col_names:
            df = self.collate_columns(colName)
            max_df[self.cluster_id + '-drivers_max-' + colName] = df.apply(max, axis=1)
        return max_df

    def get_col_min(self, *col_names):
        max_df = pd.DataFrame()
        for colName in col_names:
            df = self.collate_columns(colName)
            max_df[self.cluster_id + '-drivers_min-' + colName] = df.apply(min, axis=1)
        return max_df

    def save_chart(self, ylabel, post_fix):
        os.makedirs(self.baseOutputDir+"/"+self.bench, exist_ok=True)
        plt.ylim(ymin=0)
        plt.title(self.bench)
        plt.grid(True)
        plt.ylabel(ylabel)
        plt.xlabel("duration seconds")

        plt.gca().get_legend_handles_labels()
        handles, labels = plt.gca().get_legend_handles_labels()
        labels, handles = zip(*sorted(zip(labels, handles), key=lambda t: t[0]))
        plt.legend(handles, labels)

        plt.savefig(self.baseOutputDir + "/" + self.bench + "/" + post_fix + ".png")
        plt.close()
        print(self.baseOutputDir + "/" + self.bench + "/" + post_fix + ".png")

    def chart_individual(self):
        for driver in self.drivers:
            driver.chart_individual()

    def chart(self, ylabel, col_name):
        df = self.collate_columns(col_name)

        df.sort_index(axis=1, inplace=True)
        df.plot(figsize=(10, 4))

        #print(df.head(n=10))

        self.save_chart(ylabel, col_name)

    def chart_sum(self, ylabel, col_name):
        sum_df = self.get_col_sum(col_name)

        for column in sum_df.columns:
            print(column, sum_df[column].mean())

        sum_df.plot(figsize=(10, 4))
        self.save_chart(ylabel, col_name + "-sum")

    def chart_max(self, ylabel, *col_names):
        max_df = self.get_col_max(*col_names)
        max_df.plot(figsize=(10, 4))
        file_post_fix = ''
        for colName in col_names:
            file_post_fix += colName
        self.save_chart(ylabel, file_post_fix+"-max")

    def chart_min_max(self, ylabel, *col_names):
        file_post_fix = ''
        min_max = pd.DataFrame()
        for colName in col_names:
            df = self.collate_columns(colName)
            file_post_fix += colName
            min_max[self.cluster_id + '-drivers_max-' + colName] = df.apply(max, axis=1)
            min_max[self.cluster_id + '-drivers_min-' + colName] = df.apply(min, axis=1)

        min_max.plot(figsize=(10, 4))
        self.save_chart(ylabel, file_post_fix+"-min-max")

    def chart_min_mean_max(self, ylabel, *col_names):
        file_post_fix = ''
        min_mean_max_df = pd.DataFrame()
        for colName in col_names:
            df = self.collate_columns(colName)
            file_post_fix += colName
            min_mean_max_df[self.cluster_id + '-drivers_max-' + colName] = df.apply(max, axis=1)
            min_mean_max_df[self.cluster_id + '-drivers_mean-' + colName] = df.mean(axis=1)
            min_mean_max_df[self.cluster_id + '-drivers_min-' + colName] = df.apply(min, axis=1)

        min_mean_max_df.plot(figsize=(10, 4))
        self.save_chart(ylabel, file_post_fix+"-min-mean-max")

    def plot_data(self):

        #self.chart_individual()
        self.chart("operation latency ms", 'max')
        self.chart("operation latency ms", 'p50')
        self.chart("operation latency ms", 'p75')
        self.chart("operation latency ms", 'p95')
        self.chart("operation latency ms", 'p99')
        self.chart("operation latency ms", 'p999')
        self.chart("operation latency ms", 'min')
        self.chart("operation latency ms", 'mean')
        self.chart("operation running total", 'count')
        self.chart("operations per second", "mean_rate")
        self.chart("operations per second", "m1_rate")

        self.chart_sum("total cluster ops per second", "mean_rate")
        self.chart_sum("total cluster ops per second", "m1_rate")
        self.chart_sum("total cluster ops running sum", "count")

        self.chart_min_mean_max("cluster wide per second", 'm1_rate')
        self.chart_min_mean_max("cluster wide per second", 'mean_rate')

        self.chart_min_mean_max("cluster wide operation latency ms", 'p75')
        self.chart_min_mean_max("cluster wide operation latency ms", 'p99')
        self.chart_min_mean_max("cluster wide operation latency ms", 'p999')
        self.chart_min_mean_max("cluster wide operation latency ms", 'min')
        self.chart_min_mean_max("cluster wide operation latency ms", 'max')

        self.chart_max("cluster wide max operation latency ms", 'min', 'p75', 'p99', 'max')

    @staticmethod
    def save_chart_static(ylabel, title, path, filename):
        plt.ylim(ymin=0)
        plt.title(title)
        plt.grid(True)
        plt.ylabel(ylabel)
        plt.xlabel("duration seconds")
        os.makedirs(path, exist_ok=True)
        plt.savefig(path+"/"+filename)
        plt.close()
        print(path + "/" + filename)

    @staticmethod
    def comp_column_sum(ylabel, col_name, title, output_dir, bench_drivers):

        dfs = []
        additional_path = ''
        for benchDriver in bench_drivers:
            dfs.append(benchDriver.get_col_sum(col_name))
            additional_path += benchDriver.get_bench_name() + '-'
        additional_path = additional_path[:-1]

        df = pd.concat(dfs, axis=1)
        df.plot(figsize=(10, 4))

        filename = title.replace(' ', '-')+"-"+col_name+"-sum.png"
        BenchDrivers.save_chart_static(ylabel, title, output_dir+"/"+additional_path, filename)

    @staticmethod
    def comp_column_max(ylabel, col_name, title, output_dir, bench_drivers):

        dfs = []
        additional_path = ''
        for benchDriver in bench_drivers:
            dfs.append(benchDriver.get_col_max(col_name))
            additional_path += benchDriver.get_bench_name() + '-'
        additional_path = additional_path[:-1]

        df = pd.concat(dfs, axis=1)
        df.plot(figsize=(10, 4))

        filename = title.replace(' ', '-')+"-"+col_name+"-max.png"
        BenchDrivers.save_chart_static(ylabel, title, output_dir+"/"+additional_path, filename)

    @staticmethod
    def comp_column_mean(ylabel, col_name, title, output_dir, bench_drivers):

        dfs = []
        additional_path = ''
        for benchDriver in bench_drivers:
            dfs.append(benchDriver.get_col_mean(col_name))
            additional_path += benchDriver.get_bench_name() + '-'
        additional_path = additional_path[:-1]

        df = pd.concat(dfs, axis=1)
        df.plot(figsize=(10, 4))

        filename = title.replace(' ', '-')+"-"+col_name+"-mean.png"
        BenchDrivers.save_chart_static(ylabel, title, output_dir+"/"+additional_path, filename)

    @staticmethod
    def comp_column_min_max_mean(ylabel, col_name, title, output_dir, bench_drivers):

        dfs = []
        additional_path = ''
        for benchDriver in bench_drivers:
            dfs.append(benchDriver.get_col_min(col_name))
            dfs.append(benchDriver.get_col_max(col_name))
            dfs.append(benchDriver.get_col_mean(col_name))
            additional_path += benchDriver.get_bench_name() + '-'
        additional_path = additional_path[:-1]

        df = pd.concat(dfs, axis=1)
        df.plot(figsize=(10, 4))

        filename = title.replace(' ', '-') + "-" + col_name + "-min-max-mean.png"
        BenchDrivers.save_chart_static(ylabel, title, output_dir + "/" + additional_path, filename)

    @staticmethod
    def comp_column_min_max(ylabel, col_name, title, output_dir, bench_drivers):

        dfs = []
        additional_path = ''
        for benchDriver in bench_drivers:
            dfs.append(benchDriver.get_col_min(col_name))
            dfs.append(benchDriver.get_col_max(col_name))
            additional_path += benchDriver.get_bench_name() + '-'
        additional_path = additional_path[:-1]

        df = pd.concat(dfs, axis=1)
        df.plot(figsize=(10, 4))

        filename = title.replace(' ', '-') + "-" + col_name + "-min-max.png"
        BenchDrivers.save_chart_static(ylabel, title, output_dir + "/" + additional_path, filename)

    @staticmethod
    def comp_column(ylabel, col_name, title, output_dir, bench_drivers):
        dfs = []
        additional_path = ''
        for benchDriver in bench_drivers:
            dfs.append(benchDriver.collate_columns(col_name))
            additional_path += benchDriver.get_bench_name() + '-'
        additional_path = additional_path[:-1]

        df = pd.concat(dfs, axis=1)
        df.plot(figsize=(10, 4))

        filename = title.replace(' ', '-')+"-"+col_name+".png"
        BenchDrivers.save_chart_static(ylabel, title, output_dir+"/"+additional_path, filename)

    @staticmethod
    def plot_comparison(title, out_dir, drivers):
        BenchDrivers.comp_column("cluster total operations per sec", "m1_rate", title, out_dir, drivers)

        BenchDrivers.comp_column_mean("cluster total operations per sec", "m1_rate", title, out_dir, drivers)
        BenchDrivers.comp_column_sum("cluster total operations per sec", "m1_rate", title, out_dir, drivers)
        BenchDrivers.comp_column_min_max("cluster total operations per sec", "m1_rate", title, out_dir, drivers)

        BenchDrivers.comp_column_max("cluster wide operation latency ms", 'min', title, out_dir, drivers)
        BenchDrivers.comp_column_max("cluster wide operation latency ms", 'p50', title, out_dir, drivers)
        BenchDrivers.comp_column_max("cluster wide operation latency ms", 'p75', title, out_dir, drivers)
        BenchDrivers.comp_column_max("cluster wide operation latency ms", 'p95', title, out_dir, drivers)
        BenchDrivers.comp_column_max("cluster wide operation latency ms", 'p99', title, out_dir, drivers)
        BenchDrivers.comp_column_max("cluster wide operation latency ms", 'p999', title, out_dir, drivers)
        BenchDrivers.comp_column_max("cluster wide operation latency ms", 'max', title, out_dir, drivers)

        #BenchDrivers.comp_column_mean("cluster wide operation latency ms", 'min', title, out_dir, drivers)
        #BenchDrivers.comp_column_mean("cluster wide operation latency ms", 'p50', title, out_dir, drivers)
        #BenchDrivers.comp_column_mean("cluster wide operation latency ms", 'p75', title, out_dir, drivers)
        #BenchDrivers.comp_column_mean("cluster wide operation latency ms", 'p95', title, out_dir, drivers)
        #BenchDrivers.comp_column_mean("cluster wide operation latency ms", 'p99', title, out_dir, drivers)
        #BenchDrivers.comp_column_mean("cluster wide operation latency ms", 'p999', title, out_dir, drivers)
        #BenchDrivers.comp_column_mean("cluster wide operation latency ms", 'max', title, out_dir, drivers)
