from __future__ import absolute_import

import csv
import json
import sys
import urllib.request

from bs4 import BeautifulSoup


def main(user, destination):
    gcp_python = {}
    packages = get_user_packages(user)
    for package in packages:
        if package not in gcp_python:
            gcp_python[package] = {}
        versions = get_package_versions(package)
        for version in versions:
            if version not in gcp_python[package]:
                gcp_python[package][version] = {}
            dependencies = get_version_dependencies(package, version)
            if not dependencies:
                pass
            else:
                for dep in dependencies:
                    if " " in dep:
                        dep_name = dep.split(" ", 1)[0]
                        dep_range = dep.split(" ", 1)[1].split(";", 1)[0]
                    else:
                        dep_name = dep
                        dep_range = None
                    if dep_name not in gcp_python[package][version]:
                        gcp_python[package][version][dep_name] = dep_range
    status = print_to_file(gcp_python, destination)
    if status:
        print("Dependencies for all versions of {}'s packages written to file."
              .format(user))


def get_user_packages(user):
    ''' Takes a single PyPI user (e.g. a package maintainer) and returns a list
        of all PyPI packages owned by that user. '''
    pypi_user_URL = "http://pypi.org/user/{}/".format(user)
    print("Retrieving package list for {}. Hang tight.".format(user))
    soup = BeautifulSoup(urllib.request.urlopen(pypi_user_URL), 'html.parser')
    package_list = []
    for heading in soup.find_all("h3", {"class": "package-snippet__title"}):
        package_list.append(heading.get_text())
    return package_list


def get_package_versions(package):
    ''' Takes a single PyPI package (e.g. google-cloud-speech) and returns a
        list of release versions for the passed package per the
        "releases" object of the PyPI package JSON information '''
    package_URL = "http://pypi.python.org/pypi/{}/json".format(package)
    response = urllib.request.urlopen(package_URL)
    package_json = json.load(response)
    versions = []
    for release in package_json["releases"]:
        versions.append(release)
    return versions


def get_version_dependencies(package, version):
    ''' Takes a single PyPI package and version (e.g. google-cloud-speech) and
        returns the list of required distributions for the passed package per
        the "requires_dist" property in the "info" object of the PyPI package
        JSON information '''
    version_URL = "http://pypi.python.org/pypi/{}/{}/json".format(package,
                                                                  version)
    response = urllib.request.urlopen(version_URL)
    version_json = json.load(response)
    if 'requires_dist' not in version_json["info"]:
        return
    else:
        return version_json["info"]["requires_dist"]


def print_to_file(data, destination):
    ''' Takes a set of package dependency data and a local file destination and
        writes to file all the dependencies and their versions or version
        ranges for each PyPI package owned by the passed user. '''
    fieldnames = ['package_name', 'package_version', 'dep_name', 'dep_version']
    with open('%s/gcp_python.csv' % destination, 'w') as csvfile:
        print("Printing to file: {}/gcp_python.csv".format(destination))
        datawriter = csv.DictWriter(csvfile, delimiter=',',
                                    fieldnames=fieldnames, quotechar='"')
        datawriter.writeheader()
        for package in data:
            row = {'package_name': package}
            for package_version in data[package]:
                row.update({'package_version': package_version})
                for dep in data[package][package_version]:
                    row.update({'dep_name': dep, 'dep_version':
                                data[package][package_version][dep]})
                    datawriter.writerow(row)
    return True


if __name__ == "__main__":
    if len(sys.argv) == 3:
        main(sys.argv[1], sys.argv[2])
    else:
        print("Expected either 1 or 2 arguments. Received {}."
              .format(len(sys.argv) - 1))
