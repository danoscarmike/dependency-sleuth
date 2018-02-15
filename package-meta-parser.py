from __future__ import absolute_import
from __future__ import division

import sys
import urllib2

from bs4 import BeautifulSoup


def get_package_list_by_user(user):
    pypi_user_URL = "http://pypi.org/user/{}/".format(str(user))
    print "Calling {}".format(pypi_user_URL)
    soup = BeautifulSoup(urllib2.urlopen(pypi_user_URL), 'html.parser')
    package_list = []
    for heading in soup.find_all("h3", {"class": "package-snippet__title"}):
        package_list.append(heading)
    return package_list


def print_package_list_to_file(user, destination):
    with open('%s/PACKAGES' % str(destination), 'w') as textfile:
        for package in get_package_list_by_user(user):
            textfile.write(package.get_text())
            textfile.write("\n")
    print "Package list for PyPI user {} written to file.".format(user)


if __name__ == "__main__":
    if len(sys.argv) == 1:
        print "At least one argument (PyPI user) is required."
    elif len(sys.argv) == 2:
        for package in get_package_list_by_user(sys.argv[1]):
            print package
    elif len(sys.argv) == 3:
        print_package_list_to_file(sys.argv[1], sys.argv[2])
    else:
        print "Expected either 1 or 2 arguments. Received {}."\
              .format(len(sys.argv) - 1)
