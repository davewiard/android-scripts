#!/usr/bin/env bash

GIT_BASE_PATH=$HOME/storage/git/android-scripts

ln -snf /storage/emulated/0/Git $HOME/git
ln -snf /storage/emulated/0/Git $HOME/storage/git
ln -snf /storage/emulated/0/Fonts $HOME/storage/fonts

ln -sf $GIT_BASE_PATH/zsh/zshrc $HOME/.zshrc
ln -sf $GIT_BASE_PATH/zsh/zshrc-aliases $HOME/.zshrc-aliases
ln -sf $GIT_BASE_PATH/zsh/zshrc-functions $HOME/.zshrc-functions
ln -sf $GIT_BASE_PATH/zsh/p10k.zsh $HOME/.p10k.zsh
