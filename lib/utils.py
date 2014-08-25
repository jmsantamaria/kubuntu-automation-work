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
