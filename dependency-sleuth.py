from __future__ import absolute_import

import csv
import json
import sys
import urllib.request

from bs4 import BeautifulSoup


def get_package_list_by_user(user):
    ''' Takes a single PyPI user (e.g. a package maintainer) and returns a list
        of all PyPI packages owned by that user. '''
    pypi_user_URL = "http://pypi.org/user/{}/".format(user)
    print("Calling {}".format(pypi_user_URL))
    soup = BeautifulSoup(urllib.request.urlopen(pypi_user_URL), 'html.parser')
    package_list = []
    dependencies = {}
    for heading in soup.find_all("h3", {"class": "package-snippet__title"}):
        package_list.append(heading.get_text())
    for package in package_list:
        required = get_package_dependencies(package)
        if not required:
            pass
        else:
            for dist in required:
                dist_name = dist.split(" ", 1)[0]
                if dist.find(" ") > -1:
                    dist_range = dist.split(" ", 1)[1].split(";", 1)[0]
                else:
                    dist_range = None
                if dist_name not in dependencies:
                    dependencies[dist_name] = {}
                dependencies[dist_name][package] = dist_range
    return package_list, dependencies


def print_package_list_to_file(user, destination):
    ''' Takes a single PyPI user (e.g. a package maintainer) and a local file
        destination and writes to file all the dependencies and their versions
        or version ranges for each PyPI package owned by the passed user. '''
    package_list, dependencies = get_package_list_by_user(user)
    with open('%s/packages.csv' % destination, 'w') as csvfile:
        fieldnames = ['dependency'] + package_list
        datawriter = csv.DictWriter(csvfile, delimiter=',',
                                    fieldnames=fieldnames, quotechar='"')
        datawriter.writeheader()
        for dist_name in dependencies:
            row = {'dependency': dist_name}
            for package_name in dependencies[dist_name]:
                row.update({package_name:
                            dependencies[dist_name][package_name]})
            datawriter.writerow(row)
    print("Packages belonging to PyPI user, {}, written to file."
          .format(user))


def get_package_dependencies(package):
    ''' Takes a single PyPI package (e.g. google-cloud-speech) and returns the
        list of required distributions for the passed package per the
        "requires_dist" property in the "info" object of the PyPI package JSON
        information '''
    package_URL = "http://pypi.python.org/pypi/{}/json".format(package)
    print("Calling {}".format(package_URL))
    response = urllib.request.urlopen(package_URL)
    package_json = json.load(response)
    if 'requires_dist' not in package_json["info"]:
        return
    else:
        return package_json["info"]["requires_dist"]


if __name__ == "__main__":
    if len(sys.argv) == 3:
        print_package_list_to_file(sys.argv[1], sys.argv[2])
    else:
        print("Expected either 1 or 2 arguments. Received {}."
              .format(len(sys.argv) - 1))
