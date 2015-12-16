#!/usr/bin/python3
# kate: space-indent on; indent-width 4; replace-tabs on; indent-mode python; remove-trailing-space modified;
# vim: expandtab ts=4

############################################################################
#   Copyright © 2015 José Manuel Santamaría Lema <panfaust@gmail.com>      #
#                                                                          #
#   This program is free software; you can redistribute it and/or modify   #
#   it under the terms of the GNU General Public License as published by   #
#   the Free Software Foundation; either version 2 of the License, or      #
#   (at your option) any later version.                                    #
############################################################################

import os
import json

from debian import deb822
from debian.changelog import Changelog, Version


def link_upstream_tarball(releaseType):
    #Find out the tarball link name
    upstream_name = os.path.basename( os.getcwd() )
    #paragraphs = deb822.Packages.iter_paragraphs(open('./debian/copyright', 'r'));
    #upstream_name = next(paragraphs)['Upstream-Name']
    
    changelog = Changelog()
    changelog.parse_changelog(open('./debian/changelog', 'r'))
    src_package_name = changelog.get_package()
    upstream_version = changelog.get_version().upstream_version
    #Handle packages with updated tarballs
    #e.g. 5.0.0a version instead of 5.0.0
    last_char = upstream_version[-1]
    if last_char.isalpha():
        real_upstream_version = upstream_version.rstrip(last_char)
    else:
        real_upstream_version = upstream_version
    
    link_name = '../' + src_package_name + '_' + upstream_version + '.orig.tar.xz'
    #Find out the tarball link target path
    cwd = os.path.dirname(os.path.realpath(__file__))
    config_tarball_loc = json.load(open(cwd + "/../conf/tarball-locations.json"))
    config_versions = json.load(open(cwd + "/../conf/versions.json"))
    link_target = os.path.expanduser(config_tarball_loc[releaseType]) 
    link_target += '/' + config_versions[releaseType] + '/'
    link_target += upstream_name + '-' + real_upstream_version + ".tar.xz"
    #Create the link
    try:
        os.symlink(link_target,link_name)
    except:
        pass


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Link the orig tarball.")
    parser.add_argument("-r", "--releasetype",
        help="KDE Release Type [frameworks,plasma,applications]",
        required=True)
    args = parser.parse_args()
    link_upstream_tarball(args.releasetype)
