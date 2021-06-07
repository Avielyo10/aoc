import os
import yaml
from shutil import move, Error
from pathlib import Path

DEFAULT_KUBECONFIG_PATH = os.path.join(str(Path.home()), '.kube', 'config')
AOC_PATH = os.path.join(str(Path.home()), '.aoc')
DEFAULT_CONFIG_PATH = os.path.join(AOC_PATH, 'config.yaml')
YES = '✔'
NO = '✗'


def setup_aoc_dir():
    """
    Creates ~/.aoc directory if not exist
    Creates ~/.aoc/config.yaml if not exist & set defaults
    """
    Path(AOC_PATH).mkdir(parents=True, exist_ok=True)
    Path(DEFAULT_CONFIG_PATH).touch(exist_ok=True)
    with open(DEFAULT_CONFIG_PATH, 'r+') as config_file:
        if yaml.load(config_file, Loader=yaml.FullLoader) is None:
            config = {
                'kube_auto_keep': False,
                'clusters': {
                    'default': DEFAULT_KUBECONFIG_PATH
                },
                'current_kube': 'default'
            }
            config_file.write(yaml.dump(config))


def read_config():
    """
    Read aoc configuration file
    """
    setup_aoc_dir()
    with open(DEFAULT_CONFIG_PATH, 'r+') as config_file:
        return yaml.load(config_file, Loader=yaml.FullLoader)


def set_current_kube(current_kube, config=None):
    """
    Set the current kube from aoc configuration file
    """
    if config is None:
        config = read_config()

    with open(DEFAULT_CONFIG_PATH, 'w') as config_file:
        config['current_kube'] = current_kube
        config_file.write(yaml.dump(config))


def get_current_kube():
    """
    Get the current kube from aoc configuration file
    """
    config = read_config()
    if 'current_kube' in config:
        current_kube = config['current_kube']
    else:
        current_kube = 'default'
        set_current_kube(current_kube, config)
    return current_kube


def get_current_kube_path():
    """
    Get the current kube path from aoc configuration file
    """
    current_kube = get_current_kube()
    return dict(get_clusters()).get(current_kube, DEFAULT_KUBECONFIG_PATH)


def set_kube_auto_keep(kube_auto_keep, config=None):
    """
    Set the kube_auto_keep value from aoc configuration file
    """
    if config is None:
        config = read_config()
    with open(DEFAULT_CONFIG_PATH, 'w') as config_file:
        config['kube_auto_keep'] = kube_auto_keep
        config_file.write(yaml.dump(config))


def get_kube_auto_keep():
    """
    Get the kube_auto_keep value from aoc configuration file
    """
    config = read_config()
    if 'kube_auto_keep' in config:
        kube_auto_keep = config['kube_auto_keep']
    else:
        kube_auto_keep = False
        set_kube_auto_keep(kube_auto_keep, config)
    return kube_auto_keep


def set_clusters(clusters, config=None):
    """
    Set clusters from aoc configuration file
    """
    if config is None:
        config = read_config()
    with open(DEFAULT_CONFIG_PATH, 'w') as config_file:
        config['clusters'] = clusters
        config_file.write(yaml.dump(config))


def get_clusters():
    """
    Get a list of clusters & their paths
    """
    config = read_config()
    clusters = list()
    for name, path in config['clusters'].items():
        clusters.append([name, path])
    return clusters


def is_cluster_exist(kube_name):
    """
    Lookup for the cluster in config
    """
    return kube_name in dict(get_clusters())


def kube_auto_keep(kube_name, kube_path):
    dir_path = os.path.join(AOC_PATH, 'clusters', kube_name)
    config_path = os.path.join(dir_path, 'kubeconfig')
    Path(dir_path).mkdir(parents=True, exist_ok=True)
    Path(config_path).touch(exist_ok=True)
    try:
        move(kube_path, config_path)
    except Error as e:
        print(e.strerror)
    return config_path
