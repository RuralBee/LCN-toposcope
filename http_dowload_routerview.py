import requests
requests.packages.urllib3.disable_warnings()
from bs4 import BeautifulSoup
import os, sys
from multiprocessing import Pool

class Http_routerview(object):
    def __init__(self, web_url,file_save_dir_path, choose_time, process_number, data_type, number):
        self.web_url = web_url
        self.file_save_dir_path  = file_save_dir_path
        self.choose_time = choose_time
        self.process_number = process_number
        self.data_type = data_type
        self.number= number


    def find_directory(self, url):
        response = requests.get(url=url, verify=False)
        soup = BeautifulSoup(response.text, "lxml")
        name = [i["href"] for i in soup.find_all("a")][5:]
        if len(name) == 0:
            print("no file")
        return name


    def create_url(self):

        collctor_dirctory = ["/bgpdata", "/route-views3/bgpdata", "/route-views4/bgpdata",
                     "/route-views5/bgpdata", "/route-views6/bgpdata", "/route-views.amsix/bgpdata",
                     "/route-views.chicago/bgpdata", "/route-views.chile/bgpdata", "/route-views.eqix/bgpdata",
                     "/route-views.flix/bgpdata", "/route-views.gorex/bgpdata", "/route-views.isc/bgpdata",
                     "/route-views.kixp/bgpdata", "/route-views.jinx/bgpdata", "/route-views.linx/bgpdata",
                     "/route-views.napafrica/bgpdata", "/route-views.nwax/bgpdata", "/route-views.phoix/bgpdata",
                     "/route-views.telxatl/bgpdata", "/route-views.wide/bgpdata", "/route-views.sydney/bgpdata",
                     "/route-views.saopaulo/bgpdata", "/route-views2.saopaulo/bgpdata", "/route-views.sg/bgpdata",
                     "/route-views.perth/bgpdata", "/route-views.peru/bgpdata", "/route-views.sfmix/bgpdata",
                     "/route-views.siex/bgpdata", "/route-views.soxrs/bgpdata", "/route-views.mwix/bgpdata",
                     "/route-views.rio/bgpdata", "/route-views.fortaleza/bgpdata", "/route-views.gixa/bgpdata",
                     "/route-views.bdix/bgpdata", "/route-views.bknix/bgpdata", "/route-views.uaeix/bgpdata",
                     "/route-views.ny/bgpdata"
                     ]
        data_platform = "routeviews"

        file_save_dir = [os.path.join(file_save_dir_path, data_platform, i) for i in self.choose_time]
        print(file_save_dir)
        # 创建文件夹
        for path in file_save_dir:
            if not os.path.exists(path):
                os.makedirs(path)
        # 需要下载的文件列表名的url
        time_url = [self.web_url + i for i in collctor_dirctory]
        dowload_file_url = []
        file_save_path = []
        for i in range(len(choose_time)):
            for j in range(len(time_url)):
                if self.data_type:
                    file_name = self.find_directory(time_url[j] + "/" + choose_time[i] + "RIBS")
                    bgp_type = "RIBS/"
                else:
                    file_name = self.find_directory(time_url[j] + "/" + choose_time[i] + "UPDATES")
                    bgp_type = "UPDATES/"
                if file_name:
                    for temp in file_name[:self.number]:
                        dowload_file_url.append(time_url[j] + "/" + choose_time[i]+ bgp_type + temp)

                        file_save_path.append(file_save_dir[i] + time_url[j].split("/")[-2] + "-" +temp)

        return dowload_file_url, file_save_path

    def mulit_dowload(self):
        dowload_file_url, file_save_path = self.create_url()
        process_list = []
        pool = Pool(self.process_number)
        for i in range(len(dowload_file_url)):  # 开启5个子进程执行函数
            pool.apply_async(func=self.download, args=(dowload_file_url[i], file_save_path[i]))
        pool.close()
        pool.join()

    def download(self, url, file_path):
        r1 = requests.get(url, stream=True, verify=False)
        total_size = int(r1.headers['Content-Length'])

        if os.path.exists(file_path):
            temp_size = os.path.getsize(file_path)
        else:
            temp_size = 0
        print(temp_size)
        print(total_size)
        headers = {'Range': 'bytes=%d-' % temp_size}
        r = requests.get(url, stream=True, verify=False, headers=headers)


        with open(file_path, "ab") as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    temp_size += len(chunk)
                    f.write(chunk)
                    f.flush()

                    done = int(50 * temp_size / total_size)
                    sys.stdout.write("\r[%s%s] %d%%" % ('█' * done, ' ' * (50 - done), 100 * temp_size / total_size))
                    sys.stdout.flush()
        print()



if __name__ == '__main__':
    web_url = "http://archive.routeviews.org"
    file_save_dir_path = "../data/"
    choose_time = ["2022.01/", "2021.07/", "2021.01/", "2020.07/"]
    process_number = 20
    data_type = True
    number = 1
    test = Http_routerview(web_url=web_url, file_save_dir_path=file_save_dir_path, choose_time=choose_time, process_number=process_number, data_type=data_type, number=number)
    test.mulit_dowload()


