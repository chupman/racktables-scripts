#!/usr/bin/env python
"""
Written by Chris Hupman
Github: https://github.com/chupman/
Example: take pyvmomi output and sync racktables objects.

"""
from __future__ import print_function

import argparse
import getpass
import json
import requests
from requests.auth import HTTPBasicAuth
import pprint


def GetArgs():
    """
    Supports the command-line arguments listed below.
    """
    parser = argparse.ArgumentParser(
        description='Process args for retrieving all the Virtual Machines')
    parser.add_argument('-s', '--host', required=False, action='store',
                        help='Remote host to connect to')
    parser.add_argument('-u', '--user', required=False, action='store',
                        help='User name to use when connecting to host')
    parser.add_argument('-p', '--password', required=False, action='store',
                        help='Password to use when connecting to host')
    parser.add_argument('--silent', required=False, action='store_true',
                        help='supress output to screen')
    parser.add_argument('-t', '--test', required=False, action='store_true',
                        help='Display differences without updating racktables')
    parser.add_argument('--jsonfile', required=False, action='store',
                        default='getvmsbycluster.json',
                        help='Filename and path of vmdata file')
    args = parser.parse_args()
    return args


def CreateObj(vm, vmname):
    pass

def CreateEntityLink(vm, vmname):
    pass


def GetRTData(args):
    res = requests.get("http://clp.svl.ibm.com/racktables/api.php?method=get_depot&andor=and&cft%5B%5D=15&cfe=%7B%24typeid_1504%7D&include_attrs=1", auth=HTTPBasicAuth(args.user, args.password))
    rtdata = res.json()
    #pprint.pprint(rtdata["response"])
    return rtdata


def GetDiff(vmdata, rtdata, args):
    # Get vm names of systems already in racktables
    rtlist = []
    vmlist = []
    for id, val in rtdata["response"].iteritems():
        print(val["name"])
        rtlist.append(val["name"]) # add names into a list


    # Get vm names of
    dc = vmdata["Top Gun"]
    for cluster, hosts in dc.iteritems():    
        cluster = vmdata["Top Gun"][cluster]
        for host, vms in cluster.iteritems():
            for vmname, attr in vms.iteritems():
                #print(vmname)
                vmlist.append(vmname)  #add vm names into a list
                vmobj = cluster[host][vmname]
                #print(vmobj)
                #CreateObj(vmobj, vmname)
                #CreateEntityLink(vmobj, vmname)

    match = set(vmlist).intersection(rtlist)  # VMs that exist in both systems
    diff = set(vmlist).difference(rtlist)  # VMs that need to be added

    print("Match:")
    print(match)
    print("Diff:")
    print(diff)


def main():

    args = GetArgs()

    if args.password:
        password = args.password
    else:
        password = getpass.getpass(prompt='Enter password for host %s and '
                                   'user %s: ' % (args.host, args.user))

    with open(args.jsonfile) as json_file:
        vmdata = json.load(json_file)

    rtdata = GetRTData(args)

    GetDiff(vmdata, rtdata, args)


# Start program
if __name__ == "__main__":
    main()
