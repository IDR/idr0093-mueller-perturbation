#!/usr/bin/env python
#
# Requires:
# conda create -n prefect -c ome -c conda-forge omero-py prefect
#

from omero import proxy_to_instance
from omero.cli import CLI, cli_login
from prefect import Flow, Parameter, task
from prefect.tasks.shell import ShellTask
from prefect.utilities.debug import raise_on_exception


object = Parameter("object")


shell = ShellTask(
    return_all=True,
    log_stderr=True)


BULKMAP = "/uod/idr/metadata/idr0093-mueller-perturbation/screenA/idr0093-screenA-bulkmap-config.yml"

COMMAND = "omero metadata populate --context deletemap --report --wait 300 --batch 100 "

CONFIG = (
        """--localcfg '{"ns":["openmicroscopy.org/mapr/organism", "openmicroscopy.org/mapr/antibody", """
        """"openmicroscopy.org/mapr/gene", "openmicroscopy.org/mapr/cell_line", "openmicroscopy.org/mapr/phenotype", """
        """"openmicroscopy.org/mapr/sirna", "openmicroscopy.org/mapr/compound"], "typesToIgnore":["Annotation"]}' """
)


@task
def print_output(prefix, output):
    print(prefix, output)
    return output


## TODO: loop over prefix like "idr0093" to find all screens
## TODO: look config file

@task
def delete_annotations(object):
    return f"{COMMAND} {CONFIG} --cfg {BULKMAP} {object}"


@task
def delete_remaining(object, ignore):
    return f"{COMMAND} --cfg {BULKMAP} {object}"


@task
def delete_bulk(object, ignore):
    return f"omero metadata deletebulkanns {object}"


@task
def query(object):
    """
    Unused; this can be used via: children = shell(query(object))
    """
    prx = proxy_to_instance(object)
    kls = prx.__class__.__name__
    if kls.endswith("I"):
        kls = kls[:-1]
    return f"omero hql -q --all --style=plain 'from {kls} x where x.id = {prx.id.val}'"


@task
def to_delete(child):
    # TODO: add options: dry-run, report
    return f"omero delete {child}"


@task
def list_children(object, ignore):

        import omero.all
        from omero.cmd import FindChildren
        import omero.callbacks

        prx = proxy_to_instance(object)
        kls = prx.__class__.__name__
        if kls.endswith("I"):
            kls = kls[:-1]

        req = FindChildren()
        req.targetObjects = {kls: [prx.id.val]}
        req.typesOfChildren = ["Plate", "Dataset"]

        with cli_login() as cli:
            client = cli.get_client()
            rsp = client.submit(req, loops=500).getResponse()
            rv = []
            for kls, ids in rsp.children.items():
                for item in ids:
                    rv.append(f"{kls}:{item}")
            return rv


with Flow("delete_idr0093") as flow:
    # TODO: re-enable annotation delete
    key = shell(command="omero sessions key")
    second = shell(delete_remaining(object, first))
    third = shell(delete_bulk(object, second))
    children = list_children(object, third)
    commands = to_delete.map(children)
    deleted = shell.map(command=commands)
    print_output("Result:", deleted)

if __name__ == "__main__":
    with raise_on_exception():
        flow.run(object="Screen:2751")
