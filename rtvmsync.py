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
    parser.add_argument('-a', '--api', required=False, action='store',
                        default="http://clp.svl.ibm.com/racktables/api.php?",
                        help='User name to use when connecting to host')
    parser.add_argument('-p', '--password', required=False, action='store',
                        help='Password to use when connecting to host')
    parser.add_argument('--silent', required=False, action='store_true',
                        help='supress output to screen')
    parser.add_argument('-t', '--test', required=False, action='store_true',
                        help='Display differences without updating racktables')
    parser.add_argument('--jsonfile', required=False, action='store',
                        default='getVMsWithPlacement.json',
                        help='Filename and path of vmdata file')
    args = parser.parse_args()
    return args


def CreateObj(vmname, args):
    addobj = "method=add_object"
    type = "&object_type_id=1504"
    objname = "&object_name=" + vmname
    url = args.api + addobj + type + objname


def AddTags(vmname, id, taglist, args):
    addtags = "method=update_object_tag"
    object_id = "&object_id=" + id
    tags = "&taglist=" + taglist
    url = args.api + addtags + object_id + tags


def AddContainer(vmname, id, cluster_id, args):
    addcontainer = "method=link_entities"
    chtype = "&child_entity_type=object"
    chid = "&child_entity_id=" + id
    partype = "&parent_entity_type=object"
    parid = "&parent_entity_id=" + cluster_id
    url = args.api + addcontainer + chtype + chid + partype + parid


def GetRTData(args):
    # Connect to racktables and return requested data as json
    depot = "method=get_depot"
    exp = "&andor=and&cft%5B%5D=15&cfe=%7B%24typeid_1504%7D&include_attrs=1"
    url = args.api + depot + exp
    res = requests.get(url, auth=HTTPBasicAuth(args.user, args.password))
    rtdata = res.json()
    return rtdata


def GetDiff(vmdata, rtdata, args):
    # Get vm names of systems already in racktables
    rtlist = []
    vmlist = []
    rtdict = {}
    for id, val in rtdata["response"].iteritems():
        name = val["name"]
        rtlist.append(name)  # add names into a list
        rtdict[name] = {}
        rtdict[name]["parent_type_id"] = val["container_objtype_id"]
        rtdict[name]["cluster"] = val["container_name"]
        rtdict[name]["tags"] = val["itags"]
        rtdict[name]["project"] = val["etags"]  # nested by project tag ids with info nested
        rtdict[name]["ips"] = val["ipv4"]
        rtdict[name]["id"] = val["id"]
    # Get vm names of
    for vmname, attrs in vmdata.iteritems():
        vmlist.append(vmname)  # add vm names into a list

    match = set(vmlist).intersection(rtlist)  # VMs that exist in both systems
    diff = set(vmlist).difference(rtlist)  # VMs that need to be added

    if not args.silent:
        print("Match:")
        print(list(match))
        print("Diff:")
        print(list(diff))
    for vmname in list(diff):
        CreateObj(vmname, args)
    pprint.pprint(rtdict)


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
