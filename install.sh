#!/usr/bin/env bash

BIN_PATH=$HOME/bin
GIT_BASE_PATH=$HOME/storage/git/android-scripts

function check_dirs
{
  if [[ ! -d $BIN_PATH ]];
    printf "Creating $BIN_PATH ...\n"
    mkdir $BIN_PATH
  fi
}

function create_link()
{
  ln -snf $1 $2
}

function install_oh_my_zsh()
{
  sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
}

function links_dirs()
{
  create_link /storage/emulated/0/Git $HOME/git
  create_link /storage/emulated/0/Git $HOME/storage/git
  create_link /storage/emulated/0/Fonts $HOME/storage/fonts
}

function links_config()
{
  create_link $GIT_BASE_PATH/zsh/zshrc $HOME/.zshrc
  create_link $GIT_BASE_PATH/zsh/zshrc-aliases $HOME/.zshrc-aliases
  create_link $GIT_BASE_PATH/zsh/zshrc-functions $HOME/.zshrc-functions
  create_link $GIT_BASE_PATH/zsh/p10k.zsh $HOME/.p10k.zsh
}

# install and configure oh my zsh if it doesn't already appear to be installed
if [[ ! -e $HOME/.oh-my-zsh ]]; then
  install_oh_my_zsh
fi

check_dirs

cp $0 $BIN_PATH/.
chmod 700 $BIN_PATH/${0##*/}

links_dirs
links_config
