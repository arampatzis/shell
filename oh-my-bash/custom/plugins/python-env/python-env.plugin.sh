#!/bin/bash
# File              : python-env.plugin.sh
# Author            : George Arampatzis <garampat@ethz.ch>
# Date              : 20.01.2022 18:00
# Last Modified Date: 19.04.2022 12:14
# Last Modified By  : George Arampatzis <garampat@ethz.ch>

if [ -d ~/.venv ]; then
  export VENV_ROOT=~/.venv
fi

mkdir -p ~/.venv

RED="\033[0;31m"
GREEN="\033[0;33m"
RESET="\033[0m"


function ve {
  option="${1}"
  case ${option} in
    # create a new environment
    -n)
      _new_environment "$2"
    ;;
    # activate an environment
    -a)
      _activate_environment "$2"
    ;;
    # list all environments
    -l)
      _list_environments "$2"
    ;;
    # show save folder
    -s)
      _show_save_dir
    ;;
    # delete environment
    -d)
      _delete_environment "$2"
    ;;
    # help
    -h)
      _echo_ve_usage
    ;;
    *)
      if [[ $1 == -* ]]; then
        # unrecognized option
        echo "Unknown option '$1'"
        _echo_ve_usage
        kill -SIGINT $$
        exit 1
      elif [[ $1 == "" ]]; then
        # no args supplied
        _echo_ve_usage
      else
        # non-option supplied as first arg
        _activate_environment "$1"
      fi
    ;;
  esac
}


_echo_ve_usage() {
  echo 'USAGE:'
  echo "ve -h                        - Prints this usage info."
  echo 've -s                        - Prints the save directory of environments.'
  echo 've -n <environment_name>     - Creates a new environment with name "environment_name".'
  echo 've [-a] <environment_name>   - Activates the environment "environment_name".'
  echo 've -d <environment_name>     - Deletes the environment "environment_name".'
}


_show_save_dir() {
    echo -e "Environments are saved in ${RED}${VENV_ROOT}${RESET}"
}


_environment_name_valid() {
    exit_message=""
    if [ -z $1 ]; then
        exit_message="environment name required"
        echo $exit_message
    elif [ "$1" != "$(echo $1 | sed 's/[^A-Za-z0-9_]//g')" ]; then
        exit_message="environment name is not valid"
        echo $exit_message
    fi
}


_new_environment() {
    _environment_name_valid "$@"
    if [ -z "$exit_message" ]; then
        local env_dir=${VENV_ROOT}/$1
        if [ ! -d "${env_dir}" ]; then
            python3 -m venv ${VENV_ROOT}/$1
        else
            echo "environment already exists"
        fi
    fi
}


_activate_environment() {
    _environment_name_valid "$@"
    if [ -z "$exit_message" ]; then
        local env_dir=${VENV_ROOT}/$1
        if [ -d "${env_dir}" ]; then
            source ${VENV_ROOT}/$1/bin/activate
        else
            echo "environment does not exist"
        fi
    fi
}


_list_environments() {
    for d in ${VENV_ROOT}/* ; do
        echo "$(basename $d)"
    done
}


_delete_environment() {
    _environment_name_valid "$@"
    if [ -z "$exit_message" ]; then
        local env_dir=${VENV_ROOT}/$1
        if [ -d "${env_dir}" ]; then
            echo -e "${RED}Do you want to detele ${GREEN}${1}${RED} ? The directory ${GREEN}${env_dir}${RED} will be deleted.${RESET}"
            select yn in "Yes" "No"; do
                case $yn in
                    Yes ) rm -rf ${env_dir}; break
                    ;;
                    No ) break
                    ;;
                esac
            done
        else
            echo "Environment does not exist."
        fi
    fi

}


_complete_environments() {
    local curw
    COMPREPLY=()
    curw=${COMP_WORDS[COMP_CWORD]}
    COMPREPLY=($(compgen -W '`_list_environments`' -- $curw))
    return 0
}


shopt -s progcomp
complete -F _complete_environments ve -a
complete -F _complete_environments ve -d
