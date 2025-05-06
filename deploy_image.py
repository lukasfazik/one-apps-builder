#!/usr/bin/env python3

import os
from image_names import ImageNames
from one import One, ImageType, ImageDevPrefix, ImageFormat
from states import VMLCMState, ImageState

def detach_image_by_id(one: One, vm_id: int, image_id: int) -> bool:
    """
    Detaches all images from the VM that have the corresponding ID
    """
    vm = one.get_vm(vm_id)
    if vm is None:
        print(f"VM with ID {vm_id} not found.")
        return False
    
    for disk in one.get_vm_disks(vm):
        if (vm_image_id := disk.get("IMAGE_ID")) and image_id == int(vm_image_id):
            disk_id = int(disk.get("DISK_ID"))
            one.wait_for_vm_state(vm_id, VMLCMState.RUNNING)
            one.detach_vm_image(vm_id, disk_id)
            print(f"Image ({image_id}) DISK_ID: ({disk_id}) detached from VM ({vm_id})")
            
    return True

if __name__ == "__main__":
    # Set up environment variables
    ONE_XMLRPC = os.environ.get("ONE_XMLRPC", "http://localhost:2633/RPC2")
    ONE_AUTH = os.environ.get("ONE_AUTH", "~/.one/one_auth")
    VM_ID = os.environ.get("VM_ID")
    CI_PIPELINE_ID = os.environ.get("CI_PIPELINE_ID", "")
    DISTRO_NAME = os.environ.get("DISTRO_NAME", "")
    DISTRO_VERSION = os.environ.get("DISTRO_VERSION", "")
    DISTRO_EDITION = os.environ.get("DISTRO_EDITION", "")
    IMAGE_NAME = DISTRO_NAME + DISTRO_VERSION + DISTRO_EDITION
    IMAGE_NAME = "windows10Home"
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
    # Inicialize OpenNebula connection
    one = One(url=ONE_XMLRPC, username=username, password=password)
    vm_id = 12205
    image_id = one.create_image(
        datastore=100,
        image_name="TEST2",
        image_description="Test image",
        image_type=ImageType.DATABLOCK,
        image_dev_prefix=ImageDevPrefix.VD,
        image_format=ImageFormat.RAW,
        image_size_mb=1024,
        persistent_image=False
    )
    print(f"Image created with ID: {image_id}")
    one.wait_for_image_state(image_id, ImageState.READY)
    for i in range(1):
        one.wait_for_vm_state(vm_id, VMLCMState.RUNNING)
        one.attach_vm_image(vm_id=vm_id, image_id=image_id, target="vdl")
        print(f"Image ({image_id}) attached to VM ({vm_id})")
        
    # Detach the image from the VM
    detach_image_by_id(one, vm_id, image_id)
    
    one.wait_for_image_state(image_id, ImageState.READY)
    one.delete_image(image_id)
    print(f"Image ({image_id}) deleted")
