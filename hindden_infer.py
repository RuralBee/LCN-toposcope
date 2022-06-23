from cleanPrefix import UniquePrefix
from multiprocessing import Process
import os, time
from newlink import Newlink

if __name__ == '__main__':

    as_pfx_path = "./202107data/asprefix.txt"
    peering_name_path = "./202107data/peeringdb_2_dump_2021_07_31.json"

    prefix = UniquePrefix(peering_name_path)
    prefix.groupPrefix(as_pfx_path)
    prefix.writePrefix()
    print("数据生成完毕，开始处理aspath")
    process_list = []
    aspath_name_list = ["perl asrank.pl ./hidden-data/aspaths0.txt > ./hidden-data/asrel0.txt", "perl asrank.pl ./hidden-data/aspaths1.txt > ./hidden-data/asrel1.txt"]
    for name in aspath_name_list:
        p = Process(target=os.system, args=(name,))  # 实例化进程对象
        p.start()
        process_list.append(p)
    for i in process_list:
        p.join()
    print("two as infer end")

    print("getMissEdge begin")
    os.system("python getMissEdge.py")
    print("getMissEdge end")

    print("chooseAS begin")
    os.system("python chooseAS.py")
    print("chooseAS end")

    print("newlink begin")

    prefix_name_path = "./202107data/routeviews-rv2-20210713-2200.pfx2as"

    start = time.time()
    process_list = []
    for part in ['0', '1']:
        print(i)
        p = Process(target=Newlink, args=(part, prefix_name_path))
        p.start()
        process_list.append(p)
    for i in process_list:
        p.join()
    print("end time", time.time() - start)
    print("newlink end")


    print("linkRel bgegin")
    os.system("python linkRel.py")
    print("linkRel end")






