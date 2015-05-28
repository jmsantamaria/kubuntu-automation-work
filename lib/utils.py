import json

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
    with open("/home/jr/src/kubuntu-automation/kubuntu-automation/upstream-names.json") as upstreamfile:
        pkgmap = json.load(upstreamfile)
        if package in pkgmap:
          return pkgmap[package]
        else:
          return package
