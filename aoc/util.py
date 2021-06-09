import os
import yaml
from shutil import move, rmtree, Error
from pathlib import Path

DEFAULT_KUBECONFIG_PATH = os.path.join(str(Path.home()), '.kube', 'config')
AOC_PATH = os.path.join(str(Path.home()), '.aoc')
CLUSTERS_PATH = os.path.join(AOC_PATH, 'clusters')
DEFAULT_CONFIG_PATH = os.path.join(AOC_PATH, 'config.yaml')
YES = '✔'
NO = '✗'
DEFAULT_CONFIGURATION = {
    'kube_auto_keep': False,
    'clusters': {
        'default': DEFAULT_KUBECONFIG_PATH
    },
    'current_kube': 'default'
}


def setup_aoc_dir():
    """
    Creates ~/.aoc directory if not exist
    Creates ~/.aoc/config.yaml if not exist & set defaults
    returns aoc configuration
    """
    Path(AOC_PATH).mkdir(parents=True, exist_ok=True)
    Path(DEFAULT_CONFIG_PATH).touch(exist_ok=True)
    with open(DEFAULT_CONFIG_PATH, 'r+') as config_file:
        content = yaml.load(config_file, Loader=yaml.FullLoader)
        if content is None:
            config_file.write(yaml.dump(DEFAULT_CONFIGURATION))
            content = DEFAULT_CONFIGURATION
        return content


def save_configuration(configuration):
    """
    Save configuration to ~/.aoc/config.yaml
    """
    with open(DEFAULT_CONFIG_PATH, 'w') as config_file:
        config_file.write(yaml.dump(configuration))


def setup_kube_auto_keep(kube_name, kube_path):
    """
    Creates ~/.aoc/clusters/<kube_name> directory if not exist
    overwrite ~/.aoc/clusters/<kube_name>/kubeconfig
    """
    dir_path = os.path.join(CLUSTERS_PATH, kube_name)
    config_path = os.path.join(dir_path, 'kubeconfig')
    Path(dir_path).mkdir(parents=True, exist_ok=True)
    Path(config_path).touch(exist_ok=True)
    try:
        move(kube_path, config_path)
    except Error as e:
        print(e.strerror)
    return config_path


def remove_cluster_directory(kube_name):
    """
    Remove cluster directory from ~/.aoc/clusters/
    """
    dir_path = os.path.join(AOC_PATH, 'clusters', kube_name)
    rmtree(dir_path, ignore_errors=True)
