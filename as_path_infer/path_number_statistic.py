import time, os
import basicAtts
import networkx as nx
import json
from multiprocessing import Process
from collections import defaultdict


class Dijkstra(object):

    def __init__(self,arel_path, save_file_name, weight):
        self.grap = basicAtts.BasicAtts(arel_path, weight)
        self.save_file_name = save_file_name
        self.run()

    def dijkstra(self):
        grap = self.grap
        choose_asn = []
        for i in grap.customer:
            if len(grap.customer[i]) != 0:
                choose_asn.append(i)

        path_generator = nx.all_pairs_dijkstra_path(grap.short_graph)
        asn_statistic = defaultdict()
        path_number = 0
        non_asn_statistic = defaultdict()
        non_path_number = 0
        t=1
        start = time.time()
        starttt = time.time()
        for path_tuple in path_generator:
            path_source, path_dict = path_tuple
            if path_source in choose_asn:
                continue
            t += 1

            if t % 100 == 0:
                print(t)
                print("100 time",time.time() - start)

            for asn in choose_asn:
                try:
                    path_dict.pop(asn)
                except:
                    continue
            for key in path_dict:
                # 判断是否是无谷路径
                if self.grap.is_effictive(path_dict[key]):
                    path_number += 1
                    non_path_number += 1
                    for asn in path_dict[key]:
                        try:
                            asn_statistic[asn] = asn_statistic[asn] + 1
                            non_asn_statistic[asn] = non_asn_statistic[asn] + 1
                        except:
                            asn_statistic[asn] = 1
                            non_asn_statistic[asn] = 1
                else:
                    non_path_number += 1
                    for asn in path_dict[key]:
                        try:
                            non_asn_statistic[asn] = non_asn_statistic[asn] + 1
                        except:
                            non_asn_statistic[asn] = 1

            self.path_number = path_number
            self.non_path_number = non_path_number
            return asn_statistic, non_asn_statistic

    def save_distacne_path(self, asn_statistic, non_asn_statistic):

        file_name = self.save_file_name + "--" + str(self.path_number) + ".txt"
        with open(file_name, "w") as file:
            json.dump(asn_statistic, file, indent=1)

        file_name = self.save_file_name + "-non-" + str(self.non_path_number) + ".txt"
        with open(file_name, "w") as file:
            json.dump(non_asn_statistic, file, indent=1)




    def open_distacne_path_file(self, filename):

        with open(filename, "r") as file:

            asn_statistic= json.load(file)
            return asn_statistic

    def run(self):
        asn_statistic, non_asn_statistic = self.dijkstra()
        self.save_distacne_path(asn_statistic, non_asn_statistic )





if __name__ == '__main__':

    start = time.time()
    dictionary = "../basic_data/"
    asrel_name = ["asrel"]
    process_list = []
    weight_list = [0.5, 0.9, 0.99, 0.999, 0.9999]
    weight_list_name = ["05-", "09-", "099-", '0999-', "09999-"]
    for weight_id in range(len(weight_list)):
        for i in range(len(asrel_name)):
            asrel_path = os.path.join(dictionary, asrel_name[i])
            save_path = os.path.join(dictionary, asrel_name[i].split(".")[0] + weight_list_name[weight_id])
            p = Process(target=Dijkstra, args=(asrel_path, save_path, weight_list[weight_id]))
            p.start()
            process_list.append(p)
    for i in process_list:
        p.join()

    print("end time", time.time() - start)
