import json
import math
from math import radians, cos, sin, asin, sqrt, pi, acos, log10


class asn_attr(object):
    def __init__(self, filename):
        self.filename = filename
        self.asn_lon_lat = {}
        self.asn_country = {}
        self.asn_org_id = {}

        self.create_dict()

    def create_dict(self):
        with open(self.filename, "r") as file:
            content_lists = file.readlines()
            for content in content_lists:
                content_dir = json.loads(content)
                self.asn_lon_lat[content_dir["asn"]] = [content_dir["longitude"], content_dir["latitude"]]
                self.asn_country[content_dir["asn"]] = content_dir["country"]["name"]
                try:
                    self.asn_org_id[content_dir["asn"]] = content_dir["organization"]["orgId"]
                except:
                    self.asn_org_id[content_dir["asn"]] = None

    def find_asn(self, asn):

        with open("asn-list.txt", "r") as file:
            content_lists = file.readlines()
            for content in content_lists:
                content_dir = json.loads(content)
                if content_dir["asn"] == str(asn):
                    return [content_dir["longitude"], content_dir["latitude"]]

    def geo2xyz(self, lat, lng, r=6400):

        thera = (pi * lat) / 180
        fie = (pi * lng) / 180
        x = r * cos(thera) * cos(fie)
        y = r * cos(thera) * sin(fie)
        z = r * sin(thera)
        return [x, y, z]

    def get_angle(self, l1, l2, l3):

        p1 = self.geo2xyz(l1[1], l1[0])
        p2 = self.geo2xyz(l2[1], l2[0])
        p3 = self.geo2xyz(l3[1], l3[0])

        _P1P2 = sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2 + (p2[2] - p1[2]) ** 2)
        _P2P3 = sqrt((p3[0] - p2[0]) ** 2 + (p3[1] - p2[1]) ** 2 + (p3[2] - p2[2]) ** 2)
        P = (p1[0] - p2[0]) * (p3[0] - p2[0]) + (p1[1] - p2[1]) * (p3[1] - p2[1]) + (p1[2] - p2[2]) * (p3[2] - p2[2])
        angle = (acos(P / (_P1P2 * _P2P3)) / pi)
        return angle

    def haversine(self, lon1_lat1, lon2_lat2):

        lon1, lat1 = lon1_lat1
        lon2, lat2 = lon2_lat2
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * asin(sqrt(a))
        r = 6371
        return c

    def distance_degree(self, triangle):
        (asn1, asn2, asn3) = triangle
        log_lat1 = self.asn_lon_lat[asn1]
        log_lat2 = self.asn_lon_lat[asn2]
        log_lat3 = self.asn_lon_lat[asn3]
        distance = self.haversine(log_lat1, log_lat3)
        try:
            distance = log10(distance)
        except:
            distance = distance
        try:
            triangle_degree = self.get_angle(log_lat1, log_lat2, log_lat3)
        except:
            triangle_degree = 1
        try:
            triangle_degree1 = self.get_angle(log_lat1, log_lat2, log_lat3)
        except:
            triangle_degree1 = 1
        try:
            triangle_degree3 = self.get_angle(log_lat1, log_lat2, log_lat3)
        except:
            triangle_degree3 = 1
        return [distance, triangle_degree]

    def is_country(self, triangle):
        (asn1, asn2, asn3) = triangle
        coutry1 = self.asn_country[asn1]
        coutry2 = self.asn_country[asn2]
        coutry3 = self.asn_country[asn3]
        same = []
        if coutry1 == coutry2:
            same.append(1)
        else:
            same.append(0)

        if coutry1 == coutry3:
            same.append(1)
        else:
            same.append(0)
        if coutry2 == coutry3:
            same.append(1)
        else:
            same.append(0)
        if coutry1 == coutry2 and coutry2 == coutry3:
            same.append(1)
        else:
            same.append(0)
        return same

    def is_org(self, triangle):
        (asn1, asn2, asn3) = triangle
        org_id1 = self.asn_org_id[asn1]
        org_id2 = self.asn_org_id[asn2]
        org_id3 = self.asn_org_id[asn3]
        if org_id1 == None or org_id2 == None or org_id3 == None:
            return [0, 0, 0, 0]
        same = []
        if org_id1 == org_id2:
            same.append(1)
        else:
            same.append(0)

        if org_id1 == org_id3:
            same.append(1)
        else:
            same.append(0)
        if org_id2 == org_id3:
            same.append(1)
        else:
            same.append(0)
        if org_id1 == org_id2 and org_id2 == org_id3:
            same.append(1)
        else:
            same.append(0)
        return same

    def get_feature(self, triangle):
        feature_list = self.distance_degree(triangle)
        feature_list.extend(self.is_country(triangle))
        feature_list.extend(self.is_org(triangle))

        return feature_list


if __name__ == '__main__':
    test = asn_attr("asn-list.txt")
    a = test.get_feature(('63199', '17408', '6939'))
    print(a)