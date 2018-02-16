from __future__ import absolute_import
from __future__ import division

import csv
import json
import sys
import urllib2

from bs4 import BeautifulSoup


def get_package_list_by_user(user):
    pypi_user_URL = "http://pypi.org/user/{}/".format(user)
    print "Calling {}".format(pypi_user_URL)
    soup = BeautifulSoup(urllib2.urlopen(pypi_user_URL), 'html.parser')
    package_list = []
    for heading in soup.find_all("h3", {"class": "package-snippet__title"}):
        package_list.append(heading.get_text())
    return package_list


def print_package_list_to_file(user, destination):
    dependencies = {}
    with open('%s/packages.csv' % destination, 'w') as csvfile:
        package_list = get_package_list_by_user(user)
        fieldnames = ['dependency'] + package_list
        datawriter = csv.DictWriter(csvfile, delimiter=',',
                                    fieldnames=fieldnames, quotechar='"')
        datawriter.writeheader()
        for package in package_list:
            required = get_package_deps(package)
            if not required:
                pass
            else:
                for dist in required:
                    dist_name = dist.split(" ",1)[0]
                    if dist.find(" ") > -1:
                        dist_range = dist.split(" ",1)[1].split(";",1)[0]
                    else:
                        dist_range = None
                    if dist not in dependencies:
                        dependencies[dist] = {}
                        dependencies[dist][package] = dist_range
                    row = {'dependency':dist.split(" ",1)[0]}
                    if dist.find(" ") > -1:
                        row.update({package:dist.split(" ",1)[1]})
                print row
                datawriter.writerow(row)
    print "Dependencies of packages belonging to PyPI user, {},\
           written to file.".format(user)


def get_package_deps(package):
    package_URL = "http://pypi.python.org/pypi/{}/json".format(package)
    print ("Calling {}".format(package_URL))
    response = urllib2.urlopen(package_URL)
    package_meta = json.load(response)
    version = package_meta["info"]["version"]
    if 'requires_dist' not in package_meta["info"]:
        return
    else:
        return package_meta["info"]["requires_dist"]


if __name__ == "__main__":
    if len(sys.argv) == 1:
        print "At least one argument (PyPI user) is required."
    elif len(sys.argv) == 2:
        for package in get_package_list_by_user(sys.argv[1]):
            for dep in get_package_deps(package):
                print package, ": ", dep
            print "==========================================================="

    elif len(sys.argv) == 3:
        print_package_list_to_file(sys.argv[1], sys.argv[2])
    else:
        print "Expected either 1 or 2 arguments. Received {}."\
              .format(len(sys.argv) - 1)
