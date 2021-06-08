import os
import shutil
import click

from .config import Config
from .util import save_configuration, setup_kube_auto_keep, remove_cluster_directory, \
    YES, CLUSTERS_PATH, DEFAULT_KUBECONFIG_PATH
from tabulate import tabulate
from subprocess import call


class AOCGroup(click.Group):
    def get_command(self, ctx, cmd_name):
        rv = click.Group.get_command(self, ctx, cmd_name)
        if rv is not None:
            return rv
        else:
            return oc_runner()


@click.group(cls=AOCGroup)
@click.version_option()
@click.pass_context
def main(ctx):
    """\b
    __ _  ___   ___ 
   / _` |/ _ \ / __|
  | (_| | (_) | (__ 
   \__,_|\___/ \___|

    Multi-cluster management tool
    """
    ctx.obj = Config()


@main.command()
@click.pass_obj
def list(config):
    """
    Show list of kubeconfigs
    """
    headers = ['Name', 'Path', 'Current']
    clusters = config.get_clusters()
    current_kube = config.to_dict()['current_kube']
    clusters = [[cluster[0], cluster[1], YES if cluster[0]
                 == current_kube else ''] for cluster in clusters]
    print(tabulate(clusters, headers, tablefmt="pretty"))


@main.command()
@click.option('--name', '-n', required=True, type=str, help="Kube name, must be unique.")
@click.option('--path', '-p', required=True, type=click.Path(exists=True), help="Kubeconfig path.")
@click.option('--current', '-c', is_flag=True, help="Set this kubeconfig as current kubeconfig.")
@click.option('--keep', '-k', is_flag=True, help="Move kubeconfig to ~/.aoc.")
@click.pass_obj
def add_kube(config, name, path, current, keep):
    """
    Add a new cluster to aoc
    """
    aoc_config = config.to_dict()
    clusters = aoc_config.get('clusters', {'default': DEFAULT_KUBECONFIG_PATH})
    if keep or aoc_config.get('kube_auto_keep', False):
        path = setup_kube_auto_keep(name, path)
    clusters[name] = path
    if not config.is_cluster_exist(aoc_config.get('current_kube', 'default')):
        aoc_config['current_kube'] = name
    if current:
        aoc_config['current_kube'] = name
    aoc_config['clusters'] = clusters
    save_configuration(aoc_config)


@main.command()
@click.argument('name', required=True, type=str)
@click.pass_obj
def switch_kube(config, name):
    """
    Set the current kube
    """
    if config.is_cluster_exist(name):
        aoc_config = config.to_dict()
        aoc_config['current_kube'] = name
        save_configuration(aoc_config)
    else:
        click.secho(f"[ERROR] No such cluster {name}", fg='red', bold=True)


@main.command()
@click.argument('name', required=True, type=str)
@click.option('--yes', '-y', is_flag=True)
@click.pass_obj
def delete_kube(config, name, yes):
    """
    Remove a cluster from aoc
    """
    if not yes:
        click.confirm(f'Remove {name}?', abort=True)
    if config.is_cluster_exist(name):
        aoc_config = config.to_dict()
        clusters = config.clusters
        clusters.pop(name, None)
        aoc_config['clusters'] = clusters
        if config.current_kube == name and clusters:
            aoc_config['current_kube'] = next(iter(clusters))
        save_configuration(aoc_config)
        remove_cluster_directory(name)
    else:
        click.secho(f"[ERROR] No such cluster {name}", fg='red', bold=True)


@main.command()
@click.argument('current_name', required=True, type=str)
@click.argument('future_name', required=True, type=str)
@click.pass_obj
def rename_kube(config, current_name, future_name):
    """
    Rename cluster
    """
    if config.is_cluster_exist(current_name):
        aoc_config = config.to_dict()
        clusters = config.clusters
        current_path = clusters.pop(current_name, None)
        aoc_current_path = os.path.join(CLUSTERS_PATH, current_name)
        current_kubeconfig_aoc_path = os.path.join(
            aoc_current_path, 'kubeconfig')

        if current_name == aoc_config.get('current_kube', 'default'):
            aoc_config['current_kube'] = future_name
        if current_kubeconfig_aoc_path == current_path:
            try:
                aoc_new_path = os.path.join(CLUSTERS_PATH, future_name)
                shutil.move(aoc_current_path, aoc_new_path)
                clusters[future_name] = os.path.join(
                    aoc_new_path, 'kubeconfig')
            except shutil.Error as e:
                click.echo(e.strerror)
        else:
            clusters[future_name] = current_path
        aoc_config['clusters'] = clusters
        save_configuration(aoc_config)
    else:
        click.secho(f"[ERROR] No such cluster {current_name}", fg='red', bold=True)


@main.command()
@click.option('--yes/--no', default=None)
@click.pass_obj
def auto_keep(config, yes):
    """
    Enable/disable auto keep
    """
    if yes is not None:
        aoc_config = config.to_dict()
        aoc_config['kube_auto_keep'] = yes
        save_configuration(aoc_config)
    else:
        click.secho(f"[INFO] Try running `aoc auto-keep --yes` or `aoc auto-keep --no`", fg='blue', bold=True)


@click.command(context_settings=dict(
    ignore_unknown_options=True, allow_extra_args=True
))
@click.argument('args', nargs=-1, type=click.UNPROCESSED)
def oc_runner(args):
    config = Config()
    clusters = config.clusters
    os.environ['KUBECONFIG'] = clusters.get(
        config.current_kube, DEFAULT_KUBECONFIG_PATH)
    call(args=['oc'] + [arg for arg in args], env=os.environ)
