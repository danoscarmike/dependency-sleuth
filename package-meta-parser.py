from __future__ import absolute_import
from __future__ import division

import sys
import urllib2
import json


def get_package_deps(package):
    package_URL = "http://pypi.python.org/pypi/{}/json".format(package)
    print ("Calling {}".format(package_URL))
    response = urllib2.urlopen(package_URL)
    package_meta = json.load(response)
    version = package_meta["info"]["version"]
    deps = package_meta["info"]["requires_dist"]
    if len(deps) > 0:
        print("Returning required packages for {0}@{1}".format(package,
                                                               version))
        return deps
    else:
        print("No dependencies listed for {0}@{1}".format(package, version))
        return False


if __name__ == "__main__":
    with open(sys.argv[1]) as f:
        package_list = [x.strip() for x in f.readlines()]
    for package in package_list:
        get_package_deps(package)
