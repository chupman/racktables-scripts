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


def getArgs():
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


def createObj(vmname, args):
    addobj = "method=add_object"
    type = "&object_type_id=1504"
    objname = "&object_name=" + vmname
    url = args.api + addobj + type + objname
    res = requests.get(url, auth=HTTPBasicAuth(args.user, args.password))
    code = res.status_code
    if code == 200:
        print("Created object " + vmname + " successfully")


def addTags(id, tagid, args):
    # TODO add check to see if tag is already on the vm
    addtags = "method=update_object_tags"
    object_id = "&object_id=" + id
    tags = "&taglist[]=" + tagid
    url = args.api + addtags + object_id + tags
    print(url)
    res = requests.get(url, auth=HTTPBasicAuth(args.user, args.password))
    code = res.status_code
    print(code)
    print(res.text)
    if code == 200:
        print("Added Tag: " + tagid + " successfully")


def addContainer(id, cluster_id, args):
    # TODO add check to see if container is already on the vm
    addcontainer = "method=link_entities"
    chtype = "&child_entity_type=object"
    chid = "&child_entity_id=" + id
    partype = "&parent_entity_type=object"
    parid = "&parent_entity_id=" + cluster_id
    url = args.api + addcontainer + chid + parid + chtype + partype
    print(url)
    res = requests.get(url, auth=HTTPBasicAuth(args.user, args.password))
    code = res.status_code
    print(code)
    if code == 200:
        print("Added Container successfully")


def getRTData(args):
    # Connect to racktables and return requested data as json
    depot = "method=get_depot"
    #exp = "&andor=and&cft%5B%5D=15&cfe=%7B%24typeid_1504%7D&include_attrs=1"
    exp = "&andor=and&cfe=%7B%24typeid_1504%7D&include_attrs=1"
    url = args.api + depot + exp
    res = requests.get(url, auth=HTTPBasicAuth(args.user, args.password))
    rtdata = res.json()
    return rtdata


def getDiff(vmdata, rtdata, args):
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
        rtdict[name]["project"] = val["etags"]  # Project tag ids nested
        eth = 0
        rtdict[name]["ips"] = {}
        for ipbin, v in val["ipv4"].iteritems():
            # pprint.pprint(val["ipv4"][ipbin])
            addr = val["ipv4"][ipbin]["addrinfo"]["ip"]
            rtdict[name]["ips"][eth] = {"ip": addr}
            eth += 1
        rtdict[name]["id"] = val["id"]
    # Get vm names of
    for vmname, attrs in vmdata.iteritems():
        if attrs["state"] == "poweredOn":  # Only add powered on VMs
            vmlist.append(vmname)  # Add vm names into a list

    match = set(vmlist).intersection(rtlist)  # VMs that exist in both systems
    diff = set(vmlist).difference(rtlist)  # VMs that need to be added

    return diff, match, rtdict


def getProjectTags(args):
    # depot = "method=get_depot"
    # exp = "&andor=and&cft%5B%5D=15"
    gettaglist = "method=get_taglist"
    # url = args.api + depot + exp
    url = args.api + gettaglist
    res = requests.get(url, auth=HTTPBasicAuth(args.user, args.password))
    tagtree = res.json()
    projectTags = {}
    # Iterate through returned json and restructure data
    for k, v in tagtree["response"].iteritems():
        # Only populate if it's under the projects tag umbrella
        trace = tagtree["response"][k]["trace"]
        if "0" in trace:
            trace0 = tagtree["response"][k]["trace"]["0"]
        if "0" in trace and trace["0"] == "15":
            projectName = tagtree["response"][k]["tag"]
            projectID = tagtree["response"][k]["id"]
            projectTags[projectName] = projectID
    return projectTags


def getClusterList(args):
    depot = "method=get_depot"
    exp = "&andor=and&cfe=%7B%24typeid_1505%7D"
    url = args.api + depot + exp
    res = requests.get(url, auth=HTTPBasicAuth(args.user, args.password))
    clusters = res.json()
    clusterDict = {}
    # Iterate through returned json and restructure data
    for k, v in clusters["response"].iteritems():
        clusterName = clusters["response"][k]["name"]
        id = clusters["response"][k]["id"]
        clusterDict[clusterName] = id
    return clusterDict


def main():

    args = getArgs()

    if args.password:
        password = args.password
    else:
        password = getpass.getpass(prompt='Enter password for host %s and '
                                   'user %s: ' % (args.host, args.user))

    with open(args.jsonfile) as json_file:
        vmdata = json.load(json_file)

    rtdata = getRTData(args)
    pprint.pprint(rtdata)
    exit
    projectTags = getProjectTags(args)
    clusterDict = getClusterList(args)
    diff, match, rtdict = getDiff(vmdata, rtdata, args)
    if not args.silent:
        print("Match:" + str(len(list(match))) + "Systems in match list")
        print(list(match))
        print("Diff:" + str(len(list(diff))) + "Systems in diff list" )
        print(list(diff))
    if diff is not []:
        for vmname in list(diff):
            createObj(vmname, args)
        rtdata = getRTData(args) # Rerun to get IDs on newly created VMs
        diff, match, rtdict = getDiff(vmdata, rtdata, args)

    for vm in match:
        print(vm)
        id = rtdict[vm]["id"]  # Get racktables object id of VM
        tagid = projectTags[vmdata[vm]["folder"]]  # Get tagid of project
        cluster_id = clusterDict[vmdata[vm]["cluster"]]  # Get Cluster id
        # Check for project association in RT and add if abscent
        # TODO If the wrong project association is present delete it
        if  rtdict[vm]["tags"] == {}:
            addTags(id, tagid, args)
        # Check for Cluster association in RT and add if abscent
        # TODO If the wrong cluster association is present delete it
        if  rtdict[vm]["cluster"] == '':
            addContainer(id, cluster_id, args)
        if rtdict[vm]["ips"] == {}:
            #addIPs()
            pass
# Start program
if __name__ == "__main__":
    main()
