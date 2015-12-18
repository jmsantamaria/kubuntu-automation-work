############################################################################
#   Copyright © 2014 Harald Sitter                                         #
#   Copyright © 2015 Philip Muskovac                                       #
#   Copyright © 2015 Jonathan Riddell                                      #
#   Copyright © 2015 José Manuel Santamaría Lema <panfaust@gmail.com>      #
#                                                                          #
#   This program is free software; you can redistribute it and/or modify   #
#   it under the terms of the GNU General Public License as published by   #
#   the Free Software Foundation; either version 2 of the License, or      #
#   (at your option) any later version.                                    #
############################################################################


import json
import os
import subprocess
import re
import sys

def readAllFromFile(filename):
    f = open(filename, "r")
    result = f.read()
    f.close()
    return result

def readPackages(filename):
    f = open(filename, "r")
    packages = f.readlines()
    f.close()

    packages = map(lambda line: line.strip("\r\n\t "), packages)
    packages = filter(lambda line: line and not line.startswith("#"), packages)

    return packages

def upstreamName(package):
    cwd = os.path.dirname(os.path.realpath(__file__))
    with open(cwd + "/../upstream-names.json") as upstreamfile:
        pkgmap = json.load(upstreamfile)
        if package in pkgmap:
          return pkgmap[package]
        else:
          return package

def repoName(package):
    cwd = os.path.dirname(os.path.realpath(__file__))
    with open(cwd + "/../repo-names.json") as repofile:
        pkgmap = json.load(repofile)
        if package in pkgmap:
          return pkgmap[package]
        else:
          return package

#Returns a map with the configuration items present in the file
def readConfigFile(config_file_name):
    cwd = os.path.dirname(os.path.realpath(__file__))
    config_file = open(cwd + "/../conf/" + config_file_name)
    result = json.load(config_file)
    if config_file_name == "tarball-locations.json":
        #expand "~" in the tarball paths
        for i in result:
            result[i] = os.path.expanduser(result[i])
    return result

# ReleaseType example:
# ["frameworks","plasma","applications"]
# it would get a map of everything of frameworks/plasma/applications
def getFtpVersionMap(releaseType):
    #Populate and return the map
    packageVersionMap = {}
    #Find out the version
    cwd = os.path.dirname(os.path.realpath(__file__))
    config_file = open(cwd + "/../conf/versions.json")
    config_map = json.load(config_file)
    version = config_map[releaseType]
    #If the result is cached return it
    cache_dir = cwd + "/../.cache/kubuntu-automation/"
    cache_file_path = cache_dir + releaseType + "-" + version + ".json"
    try:
        fp = open(cache_file_path, 'r')
        packageVersionMap = json.load(fp)
        return packageVersionMap
    except:
        pass
    #Find out which subdirectories we have to inspeact in the ftp
    ftp_subdirs = []
    if releaseType == "frameworks":
        ftp_subdirs = ["","portingAids"]
    elif releaseType == "plasma":
        ftp_subdirs = [""]
    elif releaseType == "applications":
        ftp_subdirs = ["src"]
    #Find out the stability
    versionParts = version.split(".")
    lastDigit = int(versionParts[-1])
    if lastDigit >= 80:
        stability = "unstable"
    else:
        stability = "stable"
    #Inspect the ftp
    for subdir in ftp_subdirs:
        ftp_command = ["sftp", "-b", "-", "depot.kde.org:%s/%s/%s/%s" % (stability, releaseType, version, subdir)]
        p = subprocess.Popen(ftp_command, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        output, _ = p.communicate(bytes("ls *xz", 'utf-8'))

        if p.returncode != 0:
            print("The sftp process failed with return code: " + str(p.returncode))
            print("Command attempted: " + " ".join(ftp_command))
            sys.exit(1)

        for line in output.splitlines():
            line = line.decode('utf-8')
            match = re.search(r'([a-zA-Z0-9\-]+)-' + '([\d.]*)' + r'\.tar\.', line)
            if match:
                package = match.group(1)
                package_version = match.group(2)
                packageVersionMap[package] = package_version
    #Store the result in cache
    try:
        os.makedirs(cache_dir)
    except:
        pass
    print(cache_dir)
    cache_file = open(cache_file_path, 'w')
    json.dump(packageVersionMap, cache_file)
    cache_file.close()
    #Return the resulting map
    return packageVersionMap

# vim: expandtab ts=4
