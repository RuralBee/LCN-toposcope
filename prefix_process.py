import process_rib_path as prp
from multiprocessing import Process

def path_process():
    ixp_path = "./peeringdb_2_dump_2021_07_31.json"
    ip_type = "ipv6"
    proc = prp.basic_infer_path(ixp_path, ip_type)
    file_dir_list = ["../spider/data/Isolario_MRT_data/2021_07/",
                     "../spider/data/ripe/2021.07/",
                     "../spider/data/routeviews/2021.07/"]
    save_file_name = "../202107topology/202107data/aspath.txt"
    save_file_name = "../202107topology/202107data/ip6_aspath.txt"
    proc.multi_run(file_dir_list=file_dir_list, as_path_save_path=save_file_name)

def prefix_process():

    ixp_path = "./peeringdb_2_dump_2021_07_31.json"
    ip_type = "ipv6"
    proc = prp.hidden_infer_path(ixp_path, ip_type)
    file_dir_list = ["../spider/data/Isolario_MRT_data/2021_07/",
                     "../spider/data/ripe/2021.07/",
                     "../spider/data/routeviews/2021.07/"]
    save_file_name = "../202107topology/202107data/asprefix.txt"
    save_file_name = "../202107topology/202107data/ip6_asprefix.txt"
    proc.multi_run(file_dir_list=file_dir_list, as_path_save_path=save_file_name)

if __name__ == '__main__':
    process_list = []
    for func in [prefix_process, path_process]:
        p = Process(target=func)
        p.start()
        process_list.append(p)
    for i in process_list:
        p.join()

    print('test end')