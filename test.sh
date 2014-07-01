#!/bin/bash

for file in /data/Build/antergos-packages/*;
do
	if [[ -d ${file} ]]; then
		cd ${file}
		echo "False" > .flag
		cd ..
	fi
done
