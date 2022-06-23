from pybgpstream import BGPStream, BGPElem, BGPRecord
import os
import json
from collections import defaultdict


class basic_infer_path(object):

    def __init__(self, ixp_path, ip_type):
        self.ixp = set()
        self.getIXP(ixp_path)
        self.ip_type = ip_type

    def path_deal(self, elem):

        asn_list = elem.fields["as-path"]
        prefix = elem.fields["prefix"]
        if self.ip_type == "ipv6" and prefix.find(":") == -1:
            return None
        if self.ip_type == "ipv4" and prefix.find(":") != -1:
            return None

        if asn_list.find("{") == -1:
            asn_list = asn_list.split(" ")
            asn_list_deduplication = []
            asn_list_deduplication.append(asn_list[0])
            for asn in asn_list:
                if asn != asn_list_deduplication[-1]:
                    asn_list_deduplication.append(asn)

            asn_list = asn_list_deduplication
            for asn in asn_list:
                if asn in self.ixp:
                    asn_list.remove(asn)
            asn_list = [v for i, v in enumerate(asn_list)
                        if i == 0 or v != asn_list[i - 1]]
            asn_set = set(asn_list)
            if len(asn_set) == 1 or not len(asn_list) == len(asn_set):
                return None
            for asn in asn_list:
                if not self.ASNAllocated(int(asn)):
                    return None
            as_path = "|".join(asn_list) + "\n"
            return as_path

    def getIXP(self, peeringdb_file):
        if peeringdb_file.endswith('json'):
            with open(peeringdb_file) as f:
                data = json.load(f)
            for i in data['net']['data']:
                if i['info_type'] == 'Route Server':
                    self.ixp.add(str(i['asn']))

    def ASNAllocated(self, asn):
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

    def extract_path(self):
        self.as_path = set()
        file_path_list = [os.path.join(self.file_dir, i) for i in os.listdir(self.file_dir) if
                          i not in [".DS_Store", "._.DS_Store"]]
        for filename in file_path_list:
            print(filename)
            stream = BGPStream(
                data_interface="singlefile"
            )

            stream.set_data_interface_option("singlefile", "rib-file", filename)
            for rec in stream.records():
                for elem in rec:
                    # Get the list of ASes in the AS path
                    ases = self.path_deal(elem)
                    if ases == None:
                        continue
                    self.as_path.add(ases)


    def multi_dir_extract_path(self):
        file_path_list = []
        self.as_path = set()
        for file_dir in self.file_dir_list:
            file_path_list.extend([os.path.join(file_dir, i) for i in os.listdir(file_dir) if
                              i not in [".DS_Store", "._.DS_Store"]])
        for filename in file_path_list:
            print(filename)
            stream = BGPStream(
                data_interface="singlefile"
            )

            stream.set_data_interface_option("singlefile", "rib-file", filename)
            for rec in stream.records():
                for elem in rec:
                    ases = self.path_deal(elem)
                    if ases == None:
                        continue
                    self.as_path.add(ases)


    def save_file(self):
        with open(self.as_path_save_path, "w") as file:
            file.writelines(self.as_path)

    def run(self, as_path_save_path, file_dir):
        if os.path.exists(as_path_save_path):
            print("file exit", as_path_save_path)
            exit(0)
        self.file_dir = file_dir
        self.as_path_save_path = as_path_save_path

        self.extract_path()
        self.save_file()

    def multi_run(self, as_path_save_path, file_dir_list):
        if os.path.exists(as_path_save_path):
            print("file exit", as_path_save_path)
            exit(0)
        self.file_dir_list = file_dir_list
        self.as_path_save_path = as_path_save_path

        self.multi_dir_extract_path()
        self.save_file()







# -
# --------------------------------------
class hidden_infer_path(object):

    def __init__(self, ixp_path, ip_type):
        self.ixp = set()
        self.getIXP(ixp_path)
        self.ip_type = ip_type

    def path_deal(self, elem):

        asn_list = elem.fields["as-path"]
        prefix = elem.fields["prefix"]
        if self.ip_type == "ipv6" and prefix.find(":") == -1:
            return None, None
        if self.ip_type == "ipv4" and prefix.find(":") != -1:
            return None, None
        if asn_list.find("{") == -1:
            asn_list = asn_list.split(" ")
            asn_list_deduplication = []
            asn_list_deduplication.append(asn_list[0])
            for asn in asn_list:
                if asn != asn_list_deduplication[-1]:
                    asn_list_deduplication.append(asn)

            asn_list = asn_list_deduplication
            for asn in asn_list:
                if asn in self.ixp:
                    asn_list.remove(asn)
            asn_list = [v for i, v in enumerate(asn_list)
                        if i == 0 or v != asn_list[i - 1]]
            asn_set = set(asn_list)
            if len(asn_set) == 1 or not len(asn_list) == len(asn_set):
                return None, None
            for asn in asn_list:
                if not self.ASNAllocated(int(asn)):
                    return None, None
            as_path = "|".join(asn_list)
            return as_path, prefix
        return None, None

    def getIXP(self, peeringdb_file):
        if peeringdb_file.endswith('json'):
            with open(peeringdb_file) as f:
                data = json.load(f)
            for i in data['net']['data']:
                if i['info_type'] == 'Route Server':
                    self.ixp.add(str(i['asn']))

    def ASNAllocated(self, asn):
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

    def multi_dir_extract_path(self):
        file_path_list = []
        self.as_path = defaultdict(set)
        for file_dir in self.file_dir_list:
            file_path_list.extend([os.path.join(file_dir, i) for i in os.listdir(file_dir) if
                              i not in [".DS_Store", "._.DS_Store"]])
        for filename in file_path_list:
            print(filename)
            stream = BGPStream(
                data_interface="singlefile"
            )
            stream.set_data_interface_option("singlefile", "rib-file", filename)
            for rec in stream.records():
                for elem in rec:
                    try:
                        ases, prefx = self.path_deal(elem)
                    except:
                        print("goding")
                        print("wodetain", self.path_deal(elem))
                        exit(0)
                    if ases == None:
                        continue
                    self.as_path[ases].add(prefx)

    def extract_path(self):
        self.as_path = defaultdict(set)
        file_path_list = [os.path.join(self.file_dir, i) for i in os.listdir(self.file_dir) if
                          i not in [".DS_Store", "._.DS_Store"]]
        for filename in file_path_list:
            print(filename)
            stream = BGPStream(
                data_interface="singlefile"
            )
            stream.set_data_interface_option("singlefile", "rib-file", filename)
            for rec in stream.records():
                for elem in rec:
                    ases, prefx = self.path_deal(elem)
                    if ases == None:
                        continue
                    self.as_path[ases].add(prefx)


    def save_file(self):
        with open(self.as_path_save_path, "w") as file:
            for i in self.as_path:
                file.write(i + "&" + "%".join(self.as_path[i]) + "\n")


    def run(self, as_path_save_path, file_dir):
        if os.path.exists(as_path_save_path):
            print("file exit", as_path_save_path)
            exit(0)
        self.file_dir = file_dir
        self.as_path_save_path = as_path_save_path

        self.extract_path()
        self.save_file()


    def multi_run(self, as_path_save_path, file_dir_list):
        if os.path.exists(as_path_save_path):
            print("file exit", as_path_save_path)
            exit(0)
        self.file_dir_list = file_dir_list
        self.as_path_save_path = as_path_save_path
        self.multi_dir_extract_path()
        self.save_file()


class community(object):

    def __init__(self, ixp_path, ip_type):
        self.ixp = set()
        self.getIXP(ixp_path)
        self.ip_type = ip_type

    def path_deal(self, elem):

        community_list = elem.fields["communities"]
        prefix = elem.fields["prefix"]
        if self.ip_type == "ipv6" and prefix.find(":") == -1:
            return None
        if self.ip_type == "ipv4" and prefix.find(":") != -1:
            return None
        community_list = community_list.split(" ")
        community = "|".join(community_list) + "\n"
        return community

    def getIXP(self, peeringdb_file):
        if peeringdb_file.endswith('json'):
            with open(peeringdb_file) as f:
                data = json.load(f)
            for i in data['net']['data']:
                if i['info_type'] == 'Route Server':
                    self.ixp.add(str(i['asn']))

    def ASNAllocated(self, asn):
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

    def extract_path(self):
        self.as_path = set()
        file_path_list = [os.path.join(self.file_dir, i) for i in os.listdir(self.file_dir) if
                          i not in [".DS_Store", "._.DS_Store"]]
        for filename in file_path_list:
            print(filename)
            stream = BGPStream(
                data_interface="singlefile"
            )

            stream.set_data_interface_option("singlefile", "rib-file", filename)
            for rec in stream.records():
                for elem in rec:
                    ases = self.path_deal(elem)
                    if ases == None:
                        continue
                    self.as_path.add(ases)


    def multi_dir_extract_path(self):
        file_path_list = []
        self.as_path = set()
        for file_dir in self.file_dir_list:
            file_path_list.extend([os.path.join(file_dir, i) for i in os.listdir(file_dir) if
                              i not in [".DS_Store", "._.DS_Store"]])
        for filename in file_path_list:
            print(filename)
            stream = BGPStream(
                data_interface="singlefile"
            )
            stream.set_data_interface_option("singlefile", "rib-file", filename)
            for rec in stream.records():
                for elem in rec:
                    ases = self.path_deal(elem)
                    if ases == None:
                        continue
                    self.as_path.add(ases)


    def save_file(self):
        with open(self.as_path_save_path, "w") as file:
            file.writelines(self.as_path)

    def run(self, as_path_save_path, file_dir):
        if os.path.exists(as_path_save_path):
            print("file exit", as_path_save_path)
            exit(0)
        self.file_dir = file_dir
        self.as_path_save_path = as_path_save_path

        self.extract_path()
        self.save_file()

    def multi_run(self, as_path_save_path, file_dir_list):
        if os.path.exists(as_path_save_path):
            print("file exit", as_path_save_path)
            exit(0)
        self.file_dir_list = file_dir_list
        self.as_path_save_path = as_path_save_path

        self.multi_dir_extract_path()
        self.save_file()

if __name__ == '__main__':
    file_dir = "/Volumes/T7/data/Isolario_MRT_data/2021_10/"

    as_path_save_path = "./isolario_aspaths_2021_10_10.txt"
    ixp_path = "./peeringdb_2_dump_2021_12_31.json"
    ip_type = "ipv4"
    test = hidden_infer_path(ixp_path=ixp_path, ip_type=ip_type)
    test.run(file_dir=file_dir, as_path_save_path=as_path_save_path)

