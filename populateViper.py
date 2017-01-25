#!/usr/bin/env python
"""
Written by Chris Hupman
Github: https://github.com/chupman/
Example: Take a csv or json file with systems info and create racktable objects

"""
from __future__ import print_function

import argparse
import getpass
import csv
import json
import pycurl

rtuser = "user"
rtpass = "pass"

def GetArgs():
    """
    Supports the command-line arguments listed below.
    """
    parser = argparse.ArgumentParser(
        description='Process args for retrieving all the Virtual Machines')
    parser.add_argument('-s', '--host', required=False, action='store',
                        help='Remote host to connect to')
    parser.add_argument('-o', '--port', type=int, default=443, action='store',
                        help='Port to connect on')
    parser.add_argument('-u', '--user', required=False, action='store',
                        help='User name to use when connecting to host')
    parser.add_argument('-p', '--password', required=False, action='store',
                        help='Password to use when connecting to host')
    parser.add_argument('--json', required=False, action='store_true',
                        help='Write out to json file')
    parser.add_argument('--jsonfile', required=False, action='store',
                        default='getvmsbycluster.json',
                        help='Filename and path of json file')
    parser.add_argument('--silent', required=False, action='store_true',
                        help='supress output to screen')
    args = parser.parse_args()
    return args


def CreateObj(vm, vmname):
    #print(vmname)
    pass

def CreateEntityLink(vm, vmname):
    #print(vm["folder"])
    pass

def depotracktables():
    curl = pycurl.Curl()
    curl.setopt(pycurl.SSL_VERIFYPEER, False) # equivalent to curl's --insecure
    curl.setopt(curl.URL, "http://clp.svl.ibm.com/racktables/api.php?method=get_depot&cfe={$typeid_1504}")
    curl.setopt(pycurl.USERPWD, "%s:%s" % (rtuser, rtpass))
    with open('ViperRTVMs.json', 'w') as f:
        curl.setopt(curl.WRITEFUNCTION, f.write)
        curl.perform()
    

def main():

    args = GetArgs()

    with open(args.jsonfile) as json_file:
        data = json.load(json_file)
        #print(data)

    #print("selecting Viper")
    cluster = data["Top Gun"]["Viper"]
    for host, vms in cluster.iteritems():
        for vmname, attr in vms.iteritems():
            vmobj = cluster[host][vmname]
            CreateObj(vmobj, vmname)
            CreateEntityLink(vmobj, vmname)
    depotracktables()


# Start program
if __name__ == "__main__":
    main()
