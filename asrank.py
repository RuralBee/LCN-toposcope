import os.path
import re
import sys
import json
import time
from multiprocessing import Pool
# from gql import gql, Client
# from gql.transport.requests import RequestsHTTPTransport
from graphqlclient import GraphQLClient

URL = "https://api.asrank.caida.org/v2/graphql"
verbose = False
PAGE_SIZE = 10000
decoder = json.JSONDecoder()
encoder = json.JSONEncoder()



######################################################################
## Main code
######################################################################
def main():
    # fname = "asn-list"
    history_time_list = ["2021.07.01"]
    name_list = ["asn-list.txt"]
    file_dir = "202107data"
    fname_list = [os.path.join(file_dir, i) for i in name_list]

    for i in range(len(history_time_list)):

        DownloadList(URL, fname_list[i], AsnsQuery,history_time_list[i])




######################################################################
## Walks the list until it is empty
######################################################################
def DownloadList(url, fname, function, history_time):
    hasNextPage = True
    first = PAGE_SIZE
    offset = 0

    # Used by nested calls

    start = time.time()
    print("writting", fname)
    with open(fname, "w") as f:
        while hasNextPage:
            type, query = function(first, offset, history_time)
            if offset == 0 and verbose:
                print(query)

            data = DownloadQuery(url, query)
            if not ("data" in data and type in data["data"]):
                print("Failed to parse:", data, file=sys.stderr)
                sys.exit()
            data = data["data"][type]
            for node in data["edges"]:
                print(encoder.encode(node["node"]), file=f)

            hasNextPage = data["pageInfo"]["hasNextPage"]
            offset += data["pageInfo"]["first"]

            if verbose:
                print("    ", offset, "of", data["totalCount"], " ", time.time() - start, "(sec)", file=sys.stderr)
                start = time.time()



def DownloadQuery(url, query):
    client = GraphQLClient(url)
    return decoder.decode(client.execute(query))


######################################################################
## Queries
######################################################################

def AsnsQuery(first, offset, history_time):
    # print(history_time)
    result = [
        "asns",
        """{
        asns(first:%s, offset:%s, dateStart:"%s", dateEnd:"%s") {
            totalCount
            pageInfo {
                first
                hasNextPage
            }
            edges {
                node {
                    asn
                    asnName
                    rank
                    date
                    organization {
                        orgId
                        orgName
                    }
                    cliqueMember
                    seen
                    country {
                        iso
                        name
                    }
                }
            }
        }
    }""" % (first, offset, history_time, history_time)
    ]
    return result

# run the main method
main()
