#!/bin/bash


_jbl_toolbox_user_dir="${HOME}/.local/share/JetBrains/Toolbox"
_jbl_toolbox_system_dir='/opt/JetBrains/Toolbox'

[[ -d  "${_jbl_toolbox_user_dir}" ]] && _jbl_is_first_run='false' || _jbl_is_first_run='true'


is_first_run() {
	[[ 'true' = "${_jbl_is_first_run}" ]] && return 0
	return 1
}


maybe_create_symlinks() {
	is_first_run || return 1

	mkdir -p "${_jbl_toolbox_user_dir}"
	ln -s "${_jbl_toolbox_system_dir}/bin" "${_jbl_toolbox_user_dir}/bin"
	ln -s "${_jbl_toolbox_system_dir}/.settings.json" "${_jbl_toolbox_user_dir}/.settings.json"
	ln -s /usr/share/pixmaps/jetbrains-toolbox.svg "${_jbl_toolbox_user_dir}/toolbox.svg"

	return 0
}



maybe_create_symlinks

if is_first_run; then
	exec "${_jbl_toolbox_system_dir}/jetbrains-toolbox" "$@"
else
	exec "${_jbl_toolbox_system_dir}/bin/jetbrains-toolbox" "$@"
fi


