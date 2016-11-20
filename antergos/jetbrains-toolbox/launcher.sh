#!/bin/bash


toolbox_user_dir="${HOME}/.local/share/JetBrains/Toolbox"
toolbox_system_dir='/opt/JetBrains/Toolbox'
toolbox_user_version=''
toolbox_system_version=''

{ [[ -h "${toolbox_user_dir}" ]] && is_first_run='true'; } || is_first_run='false'



setup_toolbox_user_directory() {
	mkdir -p "${toolbox_user_dir}"
	ln -s "${toolbox_system_dir}/.settings.json" "${toolbox_user_dir}/.settings.json"
	ln -s /usr/share/pixmaps/jetbrains-toolbox.svg "${toolbox_user_dir}/toolbox.svg"
}


versions_match() {
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



if [[ 'true' = "${is_first_run}" ]]; then
	setup_toolbox_user_directory
	exec "${toolbox_system_dir}/jetbrains-toolbox" "$@"

elif ! [[ -h "${toolbox_user_dir}/bin" ]]; then
	move_binary_and_create_symlink

elif ! versions_match; then
	remove_symlink_to_binary
	cp "${toolbox_system_dir}/.installed_version" "${toolbox_user_dir}/.installed_version"
	exec "${toolbox_system_dir}/jetbrains-toolbox" "$@"
fi


exec "${toolbox_system_dir}/bin/jetbrains-toolbox" "$@"

