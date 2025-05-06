#!/usr/bin/env python3
import os
from image_names import ImageNames
from utils import detach_image_by_id, calculate_disk_location
from one import One, ImageType, ImageDevPrefix, ImageFormat
from states import VMLCMState, ImageState
from qemu import get_qemu_image_size_mb, convert_image_format


if __name__ == "__main__":
    # Set up environment variables and determine image name
    ONE_XMLRPC = os.environ.get("ONE_XMLRPC", "http://localhost:2633/RPC2")
    ONE_AUTH = os.environ.get("ONE_AUTH", "~/.one/one_auth")
    IMAGE_DATASTORE_ID: int = int(os.environ.get("IMAGE_DATASTORE_ID", "-1"))
    VM_ID: int = int(os.environ.get("VM_ID", "-1"))
    CI_PIPELINE_ID = os.environ.get("CI_PIPELINE_ID", "")
    CI_JOB_ID = os.environ.get("CI_JOB_ID", "")
    CI_COMMIT_SHA = os.environ.get("CI_COMMIT_SHA", "")
    DISTRO_NAME = os.environ.get("DISTRO_NAME", "")
    DISTRO_VER = os.environ.get("DISTRO_VER", "")
    DISTRO_EDITION = os.environ.get("DISTRO_EDITION", "")
    IMAGE_NAME_PREFIX = os.environ.get("IMAGE_NAME_PREFIX", "")
    IMAGE_NAME_SUFFIX = os.environ.get("IMAGE_NAME_SUFFIX", "")
    ARCHITECTURE = os.environ.get("ARCHITECTURE", "x64")
    LANGUAGE = os.environ.get("LANGUAGE", "en-US")
    VM_TEMPLATE_PATH = os.environ.get("VM_TEMPLATE_PATH", "template.tmpl")
    DIR_EXPORT = os.environ.get("DIR_EXPORT", ".")
    # Initialize image names
    image_names = ImageNames(IMAGE_NAME_PREFIX, ARCHITECTURE, LANGUAGE, IMAGE_NAME_SUFFIX)
    image_name = DISTRO_NAME + DISTRO_VER + DISTRO_EDITION
    image_long_name = image_names.get_image_name(image_name)
    # Read credentials from ONE_AUTH file
    try:
        with open(os.path.expanduser(ONE_AUTH), "r") as f:
            credentials = f.read().strip()
            if ":" not in credentials:
                raise ValueError("Invalid format in ONE_AUTH file. Expected 'username:password'.")
            username, password = credentials.split(":", 1)
            session = f"{username}:{password}"
    except FileNotFoundError:
        print(f"Error: ONE_AUTH file not found at {ONE_AUTH}")
        exit(1)
    # get QEMU image size
    image_path = os.path.join(DIR_EXPORT, image_name + ".qcow2")
    image_size_mb = get_qemu_image_size_mb(image_path)
    if (image_size_mb == -1):
        exit(1)
    # Inicialize OpenNebula connection
    one = One(url=ONE_XMLRPC, username=username, password=password)
    # Create image
    image_id = one.create_image(
        datastore=IMAGE_DATASTORE_ID,
        image_name=image_long_name,
        image_type=ImageType.OS,
        image_dev_prefix=ImageDevPrefix.SD,
        image_format=ImageFormat.RAW,
        image_size_mb=image_size_mb,
        persistent_image=True,
        CI_PIPELINE_ID=CI_PIPELINE_ID,
        CI_JOB_ID=CI_JOB_ID,
        CI_COMMIT_SHA=CI_COMMIT_SHA
    )
    if (image_id == -1):
        exit(1)
    # Wait for the image to be ready
    one.wait_for_image_state(image_id, ImageState.READY)
    # Attach the image to the VM
    one.attach_vm_image(vm_id=VM_ID, image_id=image_id, dev_prefix=ImageDevPrefix.SD)
    # Wait for the VM to be in the RUNNING state
    one.wait_for_vm_state(VM_ID, VMLCMState.RUNNING)
    # get the TAGRET of the image
    image_target = one.get_vm_image_target(VM_ID, image_id)
    # get the attached block device
    disk_location = calculate_disk_location(image_target)
    block_device_path = f"/dev/disk/by-id/scsi-0QEMU_QEMU_HARDDISK_drive-scsi0-0-{disk_location}-0"
    # Write the image to the block device
    # convert_image_format(image_path, block_device_path, "raw")
    # Detach the image from the VM
    detach_image_by_id(one, VM_ID, image_id)
    # Wait for the VM to be in the RUNNING state
    one.wait_for_vm_state(VM_ID, VMLCMState.RUNNING)
    # Make image not persistent
    one.set_image_persiency(image_id, persistent=False)
    # Read the template for the VM
    with open(VM_TEMPLATE_PATH, "r") as f:
        template = f.read()
    # Substitute placeholders with actual values
    template = template.replace("${TEMPLATE_NAME}", image_long_name)
    template = template.replace("${IMAGE_ID}", str(image_id))
    template += f'\nCI_PIPELINE_ID = "{CI_PIPELINE_ID}"\nCI_JOB_ID = "{CI_JOB_ID}"\nCI_COMMIT_SHA = "{CI_COMMIT_SHA}"\n'
    # Create the VM template
    vm_template_id = one.create_vm_template(template)
    if (vm_template_id == -1):
        exit(1)
