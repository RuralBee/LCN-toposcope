import requests
requests.packages.urllib3.disable_warnings()
from bs4 import BeautifulSoup
import os, sys
from multiprocessing import Pool

class Http_ripe(object):
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


        collctor_dirctory = ['rrc00/', 'rrc01/', 'rrc02/', 'rrc03/', 'rrc04/', 'rrc05/', 'rrc06/', 'rrc07/', 'rrc08/', 'rrc09/', 'rrc10/', 'rrc11/', 'rrc12/', 'rrc13/', 'rrc14/', 'rrc15/', 'rrc16/', 'rrc17/', 'rrc18/', 'rrc19/', 'rrc20/', 'rrc21/', 'rrc22/', 'rrc23/', 'rrc24/', 'rrc25/', 'rrc26/']
        data_platform = "ripe"

        file_save_dir = [os.path.join(file_save_dir_path, data_platform, i) for i in self.choose_time]
        print(file_save_dir)
        for path in file_save_dir:
            if not os.path.exists(path):
                os.makedirs(path)
        time_url = [self.web_url + i for i in collctor_dirctory]
        dowload_file_url = []
        file_save_path = []
        for i in range(len(choose_time)):
            for j in range(len(time_url)):
                file_name = self.find_directory(time_url[j]  + choose_time[i])
                if file_name:
                    if self.data_type:
                        file_url = [i for i in file_name if i.startswith("bview")]
                    else:
                        file_url = [i for i in file_name if i.startswith("updates")]
                    for temp in file_url[-self.number:]:
                        dowload_file_url.append(time_url[j]  + choose_time[i] + temp)

                        file_save_path.append(file_save_dir[i] + time_url[j].split("/")[-2] + "-" +temp)
        return dowload_file_url, file_save_path

    def mulit_dowload(self):
        dowload_file_url, file_save_path = self.create_url()
        process_list = []
        pool = Pool(self.process_number)
        for i in range(len(dowload_file_url)):
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
    web_url = "https://data.ris.ripe.net/"
    file_save_dir_path = "../data/"
    choose_time = ["2022.01/", "2021.07/", "2021.01/", "2020.07/"]
    process_number = 20
    data_type = True
    number = 1
    test = Http_ripe(web_url=web_url, file_save_dir_path=file_save_dir_path, choose_time=choose_time, process_number=process_number, data_type=data_type, number=number)
    test.mulit_dowload()


