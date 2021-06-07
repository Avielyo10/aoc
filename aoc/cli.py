import os
import shutil
import click

from .config_handler import get_clusters, get_current_kube, get_kube_auto_keep, \
    get_current_kube_path, is_cluster_exist, kube_auto_keep, remove_cluster_directory, \
    set_clusters, set_current_kube, set_kube_auto_keep, get_current_kube_path, \
    YES, CLUSTERS_PATH
from tabulate import tabulate
from subprocess import call


class AOCGroup(click.Group):
    def get_command(self, ctx, cmd_name):
        rv = click.Group.get_command(self, ctx, cmd_name)
        if rv is not None:
            return rv
        else:
            return runner()


@click.group(cls=AOCGroup)
@click.version_option()
def main():
    """\b
    __ _  ___   ___ 
   / _` |/ _ \ / __|
  | (_| | (_) | (__ 
   \__,_|\___/ \___|

    Multi-cluster management tool
    """
    pass


@main.command()
def list():
    """
    Show list of kubeconfigs
    """
    headers = ['Name', 'Path', 'Current']
    clusters = get_clusters()
    current_kube = get_current_kube()
    clusters = [[cluster[0], cluster[1], YES if cluster[0]
                 == current_kube else ''] for cluster in clusters]
    print(tabulate(clusters, headers, tablefmt="pretty"))


@main.command()
@click.option('--name', '-n', required=True, type=str, help="Kube name, must be unique.")
@click.option('--path', '-p', required=True, type=click.Path(exists=True), help="Kubeconfig path.")
@click.option('--current', '-c', is_flag=True, help="Set this kubeconfig as current kubeconfig.")
@click.option('--keep', '-k', is_flag=True, help="Move kubeconfig to ~/.aoc.")
@click.pass_context
def add_kube(ctx, name, path, current, keep):
    """
    Add a new cluster to aoc
    """
    clusters = dict(get_clusters())
    if keep or get_kube_auto_keep():
        path = kube_auto_keep(name, path)
    clusters[name] = path
    set_clusters(clusters)
    if not is_cluster_exist(get_current_kube()):
        ctx.invoke(switch_kube, name=name)
    if current:
        ctx.invoke(switch_kube, name=name)


@main.command()
@click.argument('name', required=True, type=str)
def switch_kube(name):
    """
    Set the current kube
    """
    if is_cluster_exist(name):
        set_current_kube(name)
    else:
        click.secho(
            "[ERROR] Cluster can't be found, try to add it first.", fg='red')


@main.command()
@click.argument('name', required=True, type=str)
@click.option('--yes', '-y', is_flag=True)
@click.pass_context
def delete_kube(ctx, name, yes):
    """
    Remove a cluster from aoc
    """
    if not yes:
        click.confirm(f'Remove {name}?', abort=True)
    if is_cluster_exist(name):
        clusters = dict(get_clusters())
        clusters.pop(name, None)
        set_clusters(clusters)
        if get_current_kube() == name and clusters:
            ctx.invoke(switch_kube, name=next(iter(clusters)))
        remove_cluster_directory(name)
    else:
        click.secho(f"[INFO] No such cluster {name}", fg='blue')


@main.command()
@click.argument('current_name', required=True, type=str)
@click.argument('future_name', required=True, type=str)
def rename_kube(current_name, future_name):
    clusters = dict(get_clusters())
    current_path = clusters.pop(current_name, None)
    aoc_current_path = os.path.join(CLUSTERS_PATH, current_name)
    current_kubeconfig_aoc_path = os.path.join(aoc_current_path, 'kubeconfig')

    if current_name == get_current_kube():
        set_current_kube(future_name)
    if current_kubeconfig_aoc_path == current_path:
        try:
            aoc_new_path = os.path.join(CLUSTERS_PATH, future_name)
            shutil.move(aoc_current_path, aoc_new_path)
            clusters[future_name] = os.path.join(aoc_new_path, 'kubeconfig')
        except shutil.Error as e:
            click.echo(e.strerror)
    else:
        clusters[future_name] = current_path
    set_clusters(clusters)


@main.command()
@click.option('--yes/--no', default=None)
def auto_keep(yes):
    """
    Enable/disable auto keep
    """
    if yes is not None:
        set_kube_auto_keep(yes)


@click.command(context_settings=dict(
    ignore_unknown_options=True, allow_extra_args=True
))
@click.argument('args', nargs=-1, type=click.UNPROCESSED)
def runner(args):
    os.environ['KUBECONFIG'] = get_current_kube_path()
    call(args=['oc'] + [arg for arg in args], env=os.environ)
