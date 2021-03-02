#!/usr/bin/env python
#
# Requires:
# conda create -n prefect -c conda-forge prefect
#

from prefect import Flow, Parameter, task
from prefect.executors import LocalDaskExecutor
from prefect.tasks.shell import ShellTask
from prefect.utilities.debug import raise_on_exception
from omero.cli import cli_login
from omero.gateway import BlitzGateway

name = Parameter("name")


shell = ShellTask(
    return_all=True,
    log_stderr=True)


COMMAND = "/opt/omero/server/OMERO.server/bin/omero"


RENDER_CONFIG = "/uod/idr/metadata/idr0093-mueller-perturbation/screenA/rendering_settings.yml"


@task
def render(object):
    return f"{COMMAND} render set {object} {RENDER_CONFIG}"


@task
def list_children(name, ignore):
    with cli_login() as cli:
        conn = BlitzGateway(client_obj=cli.get_client())
        screen = conn.getObject('Screen', attributes={'name': name})
        return [f"Plate:{x.id}" for x in screen.listChildren()]


with Flow("idr0093") as flow:
    key = shell(command=f"{COMMAND} login demo@localhost")
    children = list_children(name, key)
    render_commands = render.map(children)
    rendered = shell.map(command=render_commands)

if __name__ == "__main__":
    with raise_on_exception():
        flow.executor = LocalDaskExecutor(scheduler="threads", num_workers=5)
        flow.run(name="idr0093-mueller-perturbation/screenA")
