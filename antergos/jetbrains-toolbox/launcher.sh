#!/bin/bash


_jbl_toolbox_user_dir="${HOME}/.local/share/JetBrains/Toolbox"
_jbl_toolbox_system_dir='/opt/JetBrains/Toolbox'
_jbl_user_version=''
_jbl_system_version=''

[[ -d  "${_jbl_toolbox_user_dir}" ]] && _jbl_is_first_run='false' || _jbl_is_first_run='true'
[[ 'false' = "${_jbl_is_first_run}" ]] 


is_first_run() {
	[[ 'true' = "${_jbl_is_first_run}" ]] && return 0
	return 1
}


maybe_create_symlinks() {
	is_first_run || return 1

	mkdir -p "${_jbl_toolbox_user_dir}"
	ln -s "${_jbl_toolbox_system_dir}/.settings.json" "${_jbl_toolbox_user_dir}/.settings.json"
	ln -s /usr/share/pixmaps/jetbrains-toolbox.svg "${_jbl_toolbox_user_dir}/toolbox.svg"

	return 0
}


versions_match() {
	_jbl_user_version=$(<"${_jbl_toolbox_user_dir}/.installed_version")
	_jbl_system_version=$(<"${_jbl_toolbox_system_dir}/.installed_version")

	[[ "${_jbl_user_version}" = "${_jbl_system_version}" ]] && return 0

	return 1
}


is_first_run_after_upgrade() {
	{ is_first_run || versions_match; } && return 1

	return 0
}


maybe_remove_symlink_to_binary() {
	is_first_run_after_upgrade || return 1

	unlink "${_jbl_toolbox_user_dir}/bin"

	return 0
}


maybe_move_binary() {
	is_first_run && return 1
	[[ -h "${_jbl_toolbox_user_dir}/bin" ]] && return 1

	cp -r "${_jbl_toolbox_user_dir}/bin" "${_jbl_toolbox_system_dir}"
	rm -rf "${_jbl_toolbox_user_dir}/bin"
	ln -s "${_jbl_toolbox_system_dir}/bin" "${_jbl_toolbox_user_dir}/bin"

	
}



maybe_create_symlinks || maybe_move_binary

if is_first_run; then
	exec "${_jbl_toolbox_system_dir}/jetbrains-toolbox" "$@"
else
	exec "${_jbl_toolbox_system_dir}/bin/jetbrains-toolbox" "$@"
fi


