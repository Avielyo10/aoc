# AOC

My multi-cluster management tool

This basically a wrapper around `oc` tool with some commands to help managing multiple clusters.  
So it can be used exactly like `oc`, for example `aoc get pods -A`.  

To make it work seamlessly like a regular `oc`, create an alias under your shell configuration.
```bash
# bash
echo "alias oc=aoc" >> ~/.bashrc
source ~/.bashrc
# zsh
echo "alias oc=aoc" >> ~/.zshrc
source ~/.zshrc
```

## prerequisites
- python>=3.5
- oc

## Installation

```bash
pip3 install aoc
```

## Usage

```
Usage: aoc [OPTIONS] COMMAND [ARGS]...

    __ _  ___   ___ 
   / _` |/ _ \ / __|
  | (_| | (_) | (__ 
   \__,_|\___/ \___|

    Multi-cluster management tool

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.

Commands:
  add-kube     Add a new cluster to aoc
  auto-keep    Enable/disable auto keep
  delete-kube  Remove a cluster from aoc
  list         Show list of kubeconfigs
  rename-kube  Rename cluster
  switch-kube  Set the current kube
```