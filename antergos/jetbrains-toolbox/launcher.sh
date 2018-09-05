#!/bin/bash


toolbox_user_dir="${HOME}/.local/share/JetBrains/Toolbox"
toolbox_system_dir='/opt/JetBrains/Toolbox'
toolbox_user_version=''
toolbox_system_version=''

{ [[ -d "${toolbox_user_dir}" ]] && is_first_run='false'; } || is_first_run='true'



setup_toolbox_user_directory() {
	mkdir -p "${toolbox_user_dir}"
	ln -s "${toolbox_system_dir}/.settings.json" "${toolbox_user_dir}/.settings.json"
	ln -s /usr/share/pixmaps/jetbrains-toolbox.svg "${toolbox_user_dir}/toolbox.svg"
}


versions_match() {
	[[ -e "${toolbox_user_dir}/.installed_version" ]] || return 1
	[[ -e "${toolbox_system_dir}/.installed_version" ]] || return 1

	toolbox_user_version=$(<"${toolbox_user_dir}/.installed_version")
	toolbox_system_version=$(<"${toolbox_system_dir}/.installed_version")

	[[ "${toolbox_user_version}" = "${toolbox_system_version}" ]] && return 0

	return 1
}


remove_symlink_to_binary() {
	unlink "${toolbox_user_dir}/bin"
}


move_binary_and_create_symlink() {
	cp -r "${toolbox_user_dir}/bin" "${toolbox_system_dir}"
	rm -rf "${toolbox_user_dir:?}/bin"
	ln -s "${toolbox_system_dir}/bin" "${toolbox_user_dir}/bin"
}


copy_lastest_installed_version_file() {
	cp "${toolbox_system_dir}/.installed_version" "${toolbox_user_dir}/.installed_version"
}


run_toolbox() {
	exec "${toolbox_system_dir}/jetbrains-toolbox" --disable-seccomp-filter-sandbox "$@"
}



if [[ 'true' = "${is_first_run}" ]]; then
	setup_toolbox_user_directory
	copy_lastest_installed_version_file
	run_toolbox

elif ! [[ -h "${toolbox_user_dir}/bin" ]]; then
	move_binary_and_create_symlink

elif ! versions_match; then
	remove_symlink_to_binary
	copy_lastest_installed_version_file
	run_toolbox
fi

export LD_LIBRARY_PATH="/usr/lib/openssl-1.0:$LD_LIBRARY_PATH"
exec "${toolbox_user_dir}/bin/jetbrains-toolbox" "$@"

