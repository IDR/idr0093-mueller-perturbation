# Import OMERO Python BlitzGateway
from getpass import getpass
import omero.gateway
from omero.gateway import BlitzGateway


# Step 1
def connect(hostname, username, password):
    """
    Connect to an OMERO server
    :param hostname: Host name
    :param username: User
    :param password: Password
    :return: Connected BlitzGateway
    """
    conn = BlitzGateway(username, password,
                        host=hostname, secure=True)
    conn.connect()
    conn.c.enableKeepAlive(60)
    return conn


# Step 2
def add_annotation(conn, screen_id, delete_annotation):
    """
    Load the plates in the specified screen
    :param conn: The BlitzGateway
    :param screen_id: The screen's id
    :param delete_annotation: Pass True to delete the annotation, False otherwise
    """
    notebook_name = "idr0093_expore.ipynb"
    ref_url = "https://mybinder.org/v2/gh/IDR/idr0093-mueller-perturbation/master?urlpath=notebooks%2Fnotebooks%2Fidr0093_explore.ipynb%3FplateId%3D"
    namespace = "openmicroscopy.org/idr/analysis/notebook"
    for plate in conn.getObjects('Plate', opts={'screen': screen_id}):
        if delete_annotation:
            to_delete = []
            for ann in plate.listAnnotations(ns=namespace):
                to_delete.append(ann.id)
            conn.deleteObjects('Annotation', to_delete, wait=True)
        url = ref_url + str(plate.getId())
        key_value_data = [["Study Notebook", notebook_name],
                      ["Study Notebook URL", url]]
        map_ann = omero.gateway.MapAnnotationWrapper(conn)
        map_ann.setValue(key_value_data)
        map_ann.setNs(namespace)
        map_ann.save()
        plate.linkAnnotation(map_ann)


# main
if __name__ == "__main__":
    try:
        # Collect parameters
        host = input("Host [localhost]: ") or 'localhost'  # noqa
        username = input("Username [demo]: ") or 'demo'
        password = getpass("Password: ")
        screen_id = input("Screen ID [2551]: ") or '2551'
        delete_annotation = input("Delete annotation [False]: ") or 'False'

        # Connect to the server
        conn = connect(host, username, password)

        # Annotate the plate in the specified screen
        add_annotation(conn, screen_id, delete_annotation)
    finally:
        conn.close()
    print("done")