#!  /usr/bin/env python3
import re
import argparse
import sys
import json
import time
#from gql import gql, Client
#from gql.transport.requests import RequestsHTTPTransport
from graphqlclient import GraphQLClient

URL = "https://api.asrank.caida.org/v2/graphql"
verbose = False
PAGE_SIZE = 10000
decoder = json.JSONDecoder()
encoder = json.JSONEncoder()

#method to print how to run script
def print_help():
    print (sys.argv[0],"-u as-rank.caida.org/api/v1")
    
######################################################################
## Parameters
######################################################################
parser = argparse.ArgumentParser()
parser.add_argument("-v", dest="verbose", help="prints out lots of messages", action="store_true")
parser.add_argument("-a", dest="asns", help="download asns", type=str) 
parser.add_argument("-o", dest="organizations", help="download organizations", type=str)
parser.add_argument("-l", dest="asnLinks", help="download asn links", type=str)
parser.add_argument("-q", dest="query", help="single query", type=str)
parser.add_argument("-Q", dest="query", help="list query", type=str)
parser.add_argument("-u", dest="url", help="API URL (https://api.asrank.caida.org/v2/graphiql)", type=str, default="https://api.asrank.caida.org/v2/graphql")
parser.add_argument("-d", dest="debug_limit", help="sets the number to download", type=int)
args = parser.parse_args()

######################################################################
## Main code
######################################################################
def main():
    did_nothing = True
    for fname,function in [
            [args.asns, AsnsQuery], 
            [args.organizations, OrganizationsQuery],
            [args.asnLinks, AsnLinksQuery]
            ]:
        if fname:
            DownloadList(args.url, fname, function, args.debug_limit)
            did_nothing = False
    if did_nothing:
        parser.print_help()
        sys.exit()

######################################################################
## Walks the list until it is empty
######################################################################
def DownloadList(url, fname, function, debug_limit):
    hasNextPage = True
    first = PAGE_SIZE
    offset = 0

    # Used by nested calls

    start = time.time()
    print ("writting",fname)
    with open(fname,"w") as f:
        while hasNextPage:
            type,query = function(first, offset)
            if offset == 0 and args.verbose:
                print (query)

            data = DownloadQuery(url, query)
            if not ("data" in data and type in data["data"]):
                print ("Failed to parse:",data,file=sys.stderr)
                sys.exit()
            data = data["data"][type]
            for node in data["edges"]:
                print (encoder.encode(node["node"]), file=f)

            hasNextPage = data["pageInfo"]["hasNextPage"]
            offset += data["pageInfo"]["first"]

            if args.verbose:
                print ("    ",offset,"of",data["totalCount"], " ",time.time()-start,"(sec)",file=sys.stderr)
                start = time.time()

            if debug_limit and debug_limit < offset:
                hasNextPage = False

def DownloadQuery(url, query):
    client = GraphQLClient(url)
    return decoder.decode(client.execute(query))


######################################################################
## Queries
######################################################################

def AsnsQuery(first,offset):
    return [
        "asns", 
        """{
        asns(first:%s, offset:%s) {
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
                    organization {
                        orgId
                        orgName
                    }
                    cliqueMember
                    seen
                    longitude
                    latitude
                    cone {
                        numberAsns
                        numberPrefixes
                        numberAddresses
                    }
                    country {
                        iso
                        name
                    }
                    asnDegree {
                        provider
                        peer
                        customer
                        total
                        transit
                        sibling
                    }
                    announcing {
                        numberPrefixes
                        numberAddresses
                    }
                }
            }
        }
    }""" % (first, offset)
    ]

def OrganizationsQuery(first, offset):
    return [
        "organizations",
        """{
        organizations(first:%s, offset:%s) {
            totalCount
            pageInfo {
                first
                hasNextPage
            }
            edges {
                node {
                    orgId
                    orgName
                    rank
                    seen
                    country {
                        iso
                        name
                    }
                    asnDegree {
                        provider
                        peer
                        customer
                        total
                        transit
                        sibling
                    }
                    orgDegree {
                        total
                        transit
                    }
                    cone {
                        numberAsns
                        numberPrefixes
                        numberAddresses
                    }
                }
            }
        }
    }""" % (first,offset)
    ]

def AsnLinksQuery(first, offset):
    return [
        "asnLinks",
        """{
        asnLinks(first:%s, offset:%s) {
            totalCount
            pageInfo {
                first
                hasNextPage
            }
            edges {
                node {
                    relationship
                    asn0 {
                        asn
                    }
                    asn1 {
                        asn
                    }
                    numberPaths
                }
            } 
        }
    }"""  % (first, offset)
    ]

#run the main method
main()
