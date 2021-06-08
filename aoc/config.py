from .util import setup_aoc_dir, DEFAULT_KUBECONFIG_PATH


class Config():
    def __init__(self):
        json_conf = setup_aoc_dir()
        self.clusters = json_conf['clusters']
        self.kube_auto_keep = json_conf['kube_auto_keep']
        self.current_kube = json_conf['current_kube']

    def to_dict(self) -> dict:
        """
        Convert the configuration into a dictionary
        """
        config = {
            'kube_auto_keep': self.kube_auto_keep,
            'clusters': self.clusters,
            'current_kube': self.current_kube
        }
        return config

    def get_clusters(self) -> list:
        """
        Get a list of clusters & their paths
        """
        clusters = list()
        for name, path in self.clusters.items():
            clusters.append([name, path])
        return clusters

    def is_cluster_exist(self, kube_name) -> bool:
        """
        Lookup for the cluster in config
        """
        return kube_name in self.clusters
