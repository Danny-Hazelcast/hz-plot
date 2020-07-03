import matplotlib
matplotlib.use('Agg')

import argparse
import BenchDrivers as bds


parser = argparse.ArgumentParser(description="")
parser.add_argument("-H", "--Help", help="Example: Help argument", required=False, default="")
parser.add_argument('dirs', metavar='N', type=str, nargs='+', help='dirs')
parser.add_argument("-d", "--drop", type=int, help="drop first n rows", required=False, default="5")

argument = parser.parse_args()
drop = argument.drop

benchDrivers_list = []
for base_dir in argument.dirs:
    benchDrivers_list.append(bds.BenchDrivers(base_dir))


while bds.BenchDrivers.has_any_bench(benchDrivers_list):
    out_dir = ''
    title = ''

    for benchDriver in benchDrivers_list:
        if benchDriver.next_benchmark():
            benchDriver.drop(drop)
            benchDriver.plot_data()
        title += benchDriver.get_bench_name()+" Vs "
        out_dir += benchDriver.get_cluster_id()+"-vs-"

    title = title[:-4]
    out_dir = out_dir[:-4]

    if len(benchDrivers_list) > 1:
        bds.BenchDrivers.plot_comparison(title, out_dir, benchDrivers_list)
