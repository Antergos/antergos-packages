#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  check_versions.py
#
#  Copyright © 2013-2015 Antergos
#
#  This file is part of Antergos.
#
#  Antergos is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 3 of the License, or
#  (at your option) any later version.
#
#  Antergos is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  The following additional terms are in effect as per Section 7 of the license:
#
#  The preservation of all legal notices and author attributions in
#  the material or in the Appropriate Legal Notices displayed
#  by works containing it is required.
#
#  You should have received a copy of the GNU General Public License
#  along with Antergos; If not, see <http://www.gnu.org/licenses/>.

import os
import subprocess

DIR="/data/antergos/antergos-packages"

dirs = os.listdir(DIR)

repos = ["core", "extra", "community", "multilib", "antergos", "aur"]
versions = {}

print("Checking versions...")

for dir in dirs:
    if os.path.isdir(dir) and dir != ".git":
        try:
            out = subprocess.check_output(["yaourt", "-Ss", dir]).decode().split('\n')
            for line in out:
                for repo in repos:
                    txt = "{0}/{1} ".format(repo, dir)
                    if txt in line:
                        version = line.split()[1].split('-')[0]
                        if not dir in versions.keys():
                            versions[dir] = [(repo,version)]
                        else:
                            versions[dir].append((repo,version))
            if len(versions[dir]) > 1:
                tmp_versions = []
                for (repo, version) in versions[dir]:
                    tmp_versions.append(version)
                if tmp_versions[0] != tmp_versions[1]:
                    print(dir, versions[dir])
        except subprocess.CalledProcessError as err:
            pass
            #print("\n", err)
