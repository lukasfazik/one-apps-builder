#!/usr/bin/env python3

# Copyright 2025 Lukáš Fázik
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
from image_names import ImageNames
from utils import detach_image_by_id, calculate_disk_location, acquire_lock, unlock
from one import One, ImageType, ImageDevPrefix, ImageFormat
from states import VMLCMState, ImageState
from qemu import get_qemu_image_size_mb, convert_image_format
import logging

if __name__ == "__main__":
    try:
        # Setup logging
        DEBUG = os.environ.get("DEBUG", "false")
        if DEBUG == "true":
            log_level = logging.DEBUG
        else:
            log_level = logging.INFO
        # Init logging handler
        loggger = logging.getLogger("main")
        loggger.setLevel(log_level)
        # Create formatter
        log_formatter = logging.Formatter('[%(asctime)s] %(levelname)-8s %(module)s %(funcName)s -> %(message)s', "%d-%m-%Y %H:%M:%S")
        # Create stream handler (console)
        log_stream_handler = logging.StreamHandler()
        log_stream_handler.setFormatter(log_formatter)
        # Add stream handler to logger
        loggger.addHandler(log_stream_handler)    
        # Set up environment variables and determine image name
        ONE_XMLRPC = os.environ.get("ONE_XMLRPC", "http://localhost:2633/RPC2")
        loggger.debug(f"ONE_XMLRPC: {ONE_XMLRPC}")
        ONE_AUTH = os.environ.get("ONE_AUTH", "~/.one/one_auth")
        loggger.debug(f"ONE_AUTH: {ONE_AUTH}")
        IMAGE_DATASTORE_ID: int = int(os.environ.get("IMAGE_DATASTORE_ID", "-1"))
        loggger.debug(f"IMAGE_DATASTORE_ID: {IMAGE_DATASTORE_ID}")
        VM_ID: int = int(os.environ.get("VM_ID", "-1"))
        loggger.debug(f"VM_ID: {VM_ID}")
        CI_PIPELINE_ID = os.environ.get("CI_PIPELINE_ID", "")
        loggger.debug(f"CI_PIPELINE_ID: {CI_PIPELINE_ID}")
        CI_JOB_ID = os.environ.get("CI_JOB_ID", "")
        loggger.debug(f"CI_JOB_ID: {CI_JOB_ID}")
        CI_COMMIT_SHA = os.environ.get("CI_COMMIT_SHA", "")
        loggger.debug(f"CI_COMMIT_SHA: {CI_COMMIT_SHA}")
        DISTRO_NAME = os.environ.get("DISTRO_NAME", "")
        loggger.debug(f"DISTRO_NAME: {DISTRO_NAME}")
        DISTRO_VER = os.environ.get("DISTRO_VER", "")
        loggger.debug(f"DISTRO_VER: {DISTRO_VER}")
        DISTRO_EDITION = os.environ.get("DISTRO_EDITION", "")
        loggger.debug(f"DISTRO_EDITION: {DISTRO_EDITION}")
        IMAGE_NAME_PREFIX = os.environ.get("IMAGE_NAME_PREFIX", "")
        loggger.debug(f"IMAGE_NAME_PREFIX: {IMAGE_NAME_PREFIX}")
        IMAGE_NAME_SUFFIX = os.environ.get("IMAGE_NAME_SUFFIX", "")
        loggger.debug(f"IMAGE_NAME_SUFFIX: {IMAGE_NAME_SUFFIX}")
        ARCHITECTURE = os.environ.get("ARCHITECTURE", "x64")
        loggger.debug(f"ARCHITECTURE: {ARCHITECTURE}")
        LANGUAGE = os.environ.get("LANGUAGE", "en-US")
        loggger.debug(f"LANGUAGE: {LANGUAGE}")
        VM_TEMPLATE_PATH = os.environ.get("VM_TEMPLATE_PATH", "template.tmpl")
        loggger.debug(f"VM_TEMPLATE_PATH: {VM_TEMPLATE_PATH}")
        DIR_EXPORT = os.environ.get("DIR_EXPORT", ".")
        loggger.debug(f"DIR_EXPORT: {DIR_EXPORT}")
        DIR_DEV = os.environ.get("DIR_DEV", "/dev")
        loggger.debug(f"DIR_DEV: {DIR_DEV}")
        LOCK_FILE_PATH = os.environ.get("LOCK_FILE_PATH", "/tmp/one.lock")
        loggger.debug(f"LOCK_FILE_PATH: {LOCK_FILE_PATH}")
        # Initialize image names
        image_names = ImageNames(IMAGE_NAME_PREFIX, ARCHITECTURE, LANGUAGE, IMAGE_NAME_SUFFIX)
        image_name = DISTRO_NAME + DISTRO_VER + DISTRO_EDITION
        loggger.info(f"Image to deploy: {image_name}")
        image_long_name = image_names.get_image_name(image_name)
        loggger.info(f"Full image name: {image_long_name}")
        # Read credentials from ONE_AUTH file
        try:
            loggger.info(f"Reading Opennebula credentials from {ONE_AUTH}")
            with open(os.path.expanduser(ONE_AUTH), "r") as f:
                credentials = f.read().strip()
                if ":" not in credentials:
                    loggger.critical(f"Error: Invalid credentials format in {ONE_AUTH}. Expected 'username:password'")
                    exit(1)
                username, password = credentials.split(":", 1)
                session = f"{username}:{password}"
        except FileNotFoundError:
            loggger.critical(f"ONE_AUTH file not found at {ONE_AUTH}")
            exit(1)
        # get QEMU image size
        image_path = os.path.join(DIR_EXPORT, image_name + ".qcow2")
        loggger.info(f"Image path: {image_path}")
        image_size_mb = get_qemu_image_size_mb(image_path)
        if (image_size_mb == -1):
            exit(1)
        loggger.info(f"Image size: {image_size_mb} MB")
        # Inicialize OpenNebula connection
        one = One(url=ONE_XMLRPC, username=username, password=password)
        # Create image
        loggger.info(f"Creating Empty image in OpenNebula")
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
        loggger.info(f"Image created with ID: {image_id}")
        # Wait for the image to be ready
        loggger.info(f"Waiting for image {image_id} to be ready")
        one.wait_for_image_state(image_id, ImageState.READY)
        # Attach the image to the VM
        loggger.info(f"Attaching image {image_id} to VM {VM_ID}")
        if acquire_lock(LOCK_FILE_PATH, CI_JOB_ID) is False:
            loggger.critical(f"Failed to acquire lock: {LOCK_FILE_PATH}")
            exit(1)
        one.attach_vm_image(vm_id=VM_ID, image_id=image_id, dev_prefix=ImageDevPrefix.SD)
        # Wait for the VM to be in the RUNNING state
        one.wait_for_vm_state(VM_ID, VMLCMState.RUNNING)
        unlock(LOCK_FILE_PATH, CI_JOB_ID)
        # get the TAGRET of the image
        loggger.info(f"Getting attached image target")
        image_target = one.get_vm_image_target(VM_ID, image_id)
        if image_target is None:
            exit(1)
        loggger.info(f"Image target: {image_target}")
        # get the attached block device
        disk_location = calculate_disk_location(image_target)
        loggger.info(f"Disk location: {disk_location}")
        block_device_path = os.path.join(DIR_DEV, f"disk/by-id/scsi-0QEMU_QEMU_HARDDISK_drive-scsi0-0-{disk_location}-0")
        loggger.info(f"Block device path: {block_device_path}")
        # Write the image to the block device
        loggger.info(f"Writing image to block device...")
        if convert_image_format(image_path, block_device_path, "raw") is False:
            loggger.critical(f"Failed to write image")
            loggger.info(f"Detaching image from the VM...")
            if acquire_lock(LOCK_FILE_PATH, CI_JOB_ID) is False:
                loggger.critical(f"Failed to acquire lock: {LOCK_FILE_PATH}")
                exit(1)
            detach_image_by_id(one, VM_ID, image_id)
            one.wait_for_vm_state(VM_ID, VMLCMState.RUNNING)
            unlock(LOCK_FILE_PATH, CI_JOB_ID)
            one.wait_for_image_state(image_id, ImageState.READY)
            loggger.info(f"Deleting image...")
            one.delete_image(image_id)
            exit(1)
        loggger.info(f"Image written to block device")
        # Detach the image from the VM
        loggger.info(f"Detaching image from the VM...")
        if acquire_lock(LOCK_FILE_PATH, CI_JOB_ID) is False:
            loggger.critical(f"Failed to acquire lock: {LOCK_FILE_PATH}")
            exit(1)
        detach_image_by_id(one, VM_ID, image_id)
        # Wait for the VM to be in the RUNNING state
        one.wait_for_vm_state(VM_ID, VMLCMState.RUNNING)
        unlock(LOCK_FILE_PATH, CI_JOB_ID)
        # Make image not persistent
        loggger.info(f"Making image not persistent...")
        one.set_image_persiency(image_id, persistent=False)
        # Read the template for the VM
        loggger.info(f"Reading VM template from {VM_TEMPLATE_PATH}")
        with open(VM_TEMPLATE_PATH, "r") as f:
            template = f.read()
        # Substitute placeholders with actual values
        template = template.replace("${TEMPLATE_NAME}", image_long_name)
        template = template.replace("${IMAGE_ID}", str(image_id))
        template += f'\nCI_PIPELINE_ID = "{CI_PIPELINE_ID}"\nCI_JOB_ID = "{CI_JOB_ID}"\nCI_COMMIT_SHA = "{CI_COMMIT_SHA}"\n'
        # Create the VM template
        loggger.info(f"Creating VM template...")
        vm_template_id = one.create_vm_template(template)
        if (vm_template_id == -1):
            exit(1)
        loggger.info(f"VM template created with ID: {vm_template_id}")
    except Exception as e:
        loggger.critical(f"Generall exception caught: {e}")
        loggger.info(f"Unlocking lock file: {LOCK_FILE_PATH}, key: {CI_JOB_ID}")
        unlock(LOCK_FILE_PATH, CI_JOB_ID)
        exit(1)