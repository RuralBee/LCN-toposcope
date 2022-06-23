import copy
import os
import sys, random, json, sqlite3, argparse
from collections import defaultdict
from multiprocessing import Process
class UniquePrefix(object):
    def __init__(self, peering_name):
        self.ixp = set()
        self.vp_group = [set(), set()]
        self.path_group = [set(), set()]
        self.prefix_group = [set(), set()]
        self.vp = defaultdict(set)
        self.getIXP(peering_name)

    def getIXP(self, peeringdb_file):
        if peeringdb_file.endswith('json'):
            with open(peeringdb_file) as f:
                data = json.load(f)
            for i in data['net']['data']:
                if i['info_type'] == 'Route Server':
                    self.ixp.add(str(i['asn']))

        elif peeringdb_file.endswith('sqlite'):
            conn = sqlite3.connect(peeringdb_file)
            c = conn.cursor()
            for row in c.execute("SELECT asn, info_type FROM 'peeringdb_network'"):
                asn, info_type = row
                if info_type == 'Route Server':
                    self.ixp.add(str(asn))

        else:
            raise TypeError('PeeringDB file must be either a json file or a sqlite file.')

    def ASNAllocated(self, asn):
        # 去除无效asn
        if asn in [23456, 0, 112]:
            return False
        elif asn >= 64495 and asn <= 64511:
            return False
        elif asn >= 64512 and asn <= 65535:
            return False
        elif asn >= 65536 and asn <= 65551:
            return False
        elif asn >= 4200000000 and asn <= 4294967295:
            return False
        else:
            return True

    def groupPrefix(self, name):
        with open(name) as f:
            for line in f:
                if line.strip() == '':
                    continue
                [path, prefix] = line.strip().split('&')
                asn_list = path.split('|')
                asn_temp = copy.deepcopy(asn_list)
                for asn in asn_list:
                    if asn in self.ixp:
                        asn_list.remove(asn)
                asn_list = [v for i, v in enumerate(asn_list)
                            if i == 0 or v != asn_list[i-1]]
                asn_set = set(asn_list)
                if len(asn_set) <= 1 or not len(asn_list) == len(asn_set):
                    continue
                for asn in asn_list:
                    if not self.ASNAllocated(int(asn)):
                        break
                else:
                    vp = asn_list[0]

                    for AS in asn_list:
                        self.vp[vp].add(AS)
                    if vp not in self.vp_group[0] and vp not in self.vp_group[1]:
                        self.vp_group[random.randint(0, 1)].add(vp)
                    if vp in self.vp_group[0]:
                        self.path_group[0].add('|'.join(asn_list))
                        self.prefix_group[0].add('|'.join(asn_list) + '&' + prefix)
                    if vp in self.vp_group[1]:
                        self.path_group[1].add('|'.join(asn_list))
                        self.prefix_group[1].add('|'.join(asn_list) + '&' + prefix)
                continue

    def writePrefix(self):
        for choose in [0, 1]:
            fout = open('./hidden-data/chooseVP' + str(choose) + '.txt', 'w')
            for vp in self.vp_group[choose]:
                fout.write(vp + '\n')
            fout.close()

            fout = open('./hidden-data/aspaths' + str(choose) + '.txt', 'w')
            for path in self.path_group[choose]:
                fout.write(path + '\n')
            fout.close()

            fout = open('./hidden-data/asprefix' + str(choose) + '.txt', 'w')
            for prefix in self.prefix_group[choose]:
                fout.write(prefix + '\n')
            fout.close()
        fout = open('./hidden-data/fullVP.txt', 'w')
        for vp in self.vp.keys():
            if 65000*0.8 < len(self.vp[vp]):
                fout.write(vp + '\n')
        fout.close()

if __name__ == '__main__':

    as_pfx_path = "./data/hidden_as_pfx_paths_2021_10_01.txt"
    peering_name_path = "./data/peeringdb_2_dump_2021_10_01.json"

    prefix = UniquePrefix(peering_name_path)
    prefix.groupPrefix(as_pfx_path)
    prefix.writePrefix()
    process_list = []
    aspath_name_list = ["perl asrank.pl ./hidden-data/aspaths0.txt > asrel0.txt", "perl asrank.pl ./hidden-data/aspaths1.txt > asrel1.txt"]
    for name in aspath_name_list:
        p = Process(target=os.system, args=(name,))
        p.start()
        process_list.append(p)
    for i in process_list:
        p.join()
    print("program end")