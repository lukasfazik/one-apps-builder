import enum
import pyone
from typing import Optional, List, Tuple
from states import ImageState, VMState, VMLCMState
import time
import logging

logger = logging.getLogger("main." + __name__)

class ImageDevPrefix(enum.Enum):
    HD = "hd"
    SD = "sd"
    VD = "vd"

class ImageType(enum.Enum):
    OS = "OS"
    CDROM = "CDROM"
    DATABLOCK = "DATABLOCK"

class ImageFormat(enum.Enum):
    RAW = "RAW"
    QCOW2 = "QCOW2"


class One:
    def __init__(self, url: str, username: str, password: str, timeout: int = 10) -> None:
        """
        Initialize the OpenNebula connection.
        :param url: URL of the OpenNebula server.
        :param username: Username for OpenNebula authentication.
        :param password: Password for OpenNebula authentication.
        :param timeout: Timeout for OpenNebula requests.
        """
        logger.debug(f"Initializing OpenNebula connection to {url} as user {username}")
        session = ":".join((username, password))
        self._one = pyone.OneServer(uri=url, session=session, timeout=timeout)
        logger.debug(f"OpenNebula connection initialized successfully")

    def get_image(self, image_id: int) -> Optional[pyone.bindings.IMAGESub]:
        """
        Get image information by ID.
        :param image_id: Image ID.
        :return: Image object or None if image is not found or error happened.
        """
        try:
            logger.debug(f"Getting image info for image ID: {image_id}")
            return self._one.image.info(image_id)
        except pyone.OneException as e:
            logger.error(f"Failed to get image info for image ID: {image_id}, error: {str(e)}")
            return None

    def get_image_state(self, image_id: int) -> Optional[ImageState]:
        """
        Get the current state of the image.
        :param image_id: Image ID.
        :return: ImageState enum value or None if image is not found or error happened.
        """
        logger.debug(f"Getting image state for image ID: {image_id}")
        image = self.get_image(image_id)
        if image is not None:
            logger.debug(f"Got image state: {image.STATE}")
            return ImageState(image.STATE)
        logger.error(f"Failed to get image state for image ID: {image_id}")
        return None

    def create_image(self, datastore: int, image_name: str, image_description: Optional[str] = None, image_path: Optional[str] = None, image_type: ImageType = ImageType.DATABLOCK, image_dev_prefix: Optional[ImageDevPrefix] = None, image_format: ImageFormat = ImageFormat.RAW, image_size_mb: Optional[int] = None, persistent_image: bool = False, **kwargs) -> int:
        """
        Creates Opennebula image with the given parameters.
        :param datastore: Datastore ID where the image will be created.
        :param image_name: Name of the image.
        :param image_description: Description of the image.
        :param image_path: Optional path to the image file.
        :param image_type: Type of the image.
        :param image_dev_prefix: Device prefix for the image.
        :param image_format: Format of the image.
        :param image_size_mb: Size of the image in MB. Must be specified if no path is provided.
        :param persistent_image: Whether the image should be persistent or not.
        :param kwargs: Additional KEY=VALUE parameters for the image.
        :return: Image ID if successful, -1 if an error occurred.
        """
        logger.debug("Building image template")
        image_template: List[str] = []
        image_template.append(f'NAME = "{image_name}"')
        image_template.append(f'TYPE = "{image_type.value}"')
        image_template.append(f'FORMAT = "{image_format.value}"')
        if image_dev_prefix is not None:
            image_template.append(f'DEV_PREFIX = "{image_dev_prefix.value}"')
        if image_path is not None:
            image_template.append(f'PATH = "{image_path}"')
        if image_size_mb is not None:
            image_template.append(f'SIZE = "{image_size_mb}"')
        if persistent_image:
            image_template.append('PERSISTENT = "YES"')
        else:
            image_template.append('PERSISTENT = "NO"')
        if image_description:
            image_template.append(f'DESCRIPTION = "{image_description}"')
        for key, value in kwargs.items():
            image_template.append(f'{key} = "{value}"')

        image_definition = "\n".join(image_template)
        try:
            logger.debug(f"Creating image in datastore {datastore} with definition: {image_definition}")
            return self._one.image.allocate(image_definition, datastore)
        except pyone.OneException as e:
            logger.error(f"Failed to create image, error: {e}")
            return -1

    def delete_image(self, image_id: int) -> bool:
        """
        Delete an image by ID.
        :param image_id: Image ID.
        :return: True if successful, False if an error occurred.
        """
        logger.debug(f"Deleting image with ID: {image_id}")
        try:
            return self._one.image.delete(image_id) != -1
        except pyone.OneException as e:
            logger.error(f"Failed to delete image with ID: {image_id}, error: {e}")
            return False

    def set_image_persiency(self, image_id: int, persistent: bool) -> int:
        """
        Set the persisting state of an image.
        :param image_id: Image ID.
        :param persistent: True to set the image as persistent, False to set it as non-persistent.
        """
        logger.debug(f"Setting image persisting state for image ID: {image_id} to {persistent}")
        try:
            return self._one.image.persistent(image_id, persistent)
        except pyone.OneException as e:
            logger.error(f"Failed to set image persisting state to {persistent}, image ID: {image_id} error: {e}")
            return -1

    def get_vm_template(self, id: int) -> Optional[pyone.bindings.TEMPLATETypeSub]:
        logger.debug(f"Getting VM template with ID: {id}")
        try:
            return self._one.template.info(id)
        except pyone.OneException as e:
            logger.error(f"Failed to get VM template with ID: {id}, error: {e}")
            return None

    def create_vm_template(self, template: str) -> int:
        """
        Create a VM template in OpenNebula.
        :param template: Template string to be used for creating the VM.
        :return: Template ID if successful, -1 if an error occurred.
        """
        logger.debug(f"Creating new VM template with definition: {template}")
        try:
            return self._one.template.allocate(template)
        except pyone.OneException as e:
            logger.error(f"Failed to create new VM template: {e}")
            return -1

    def delete_vm_template(self, template_id: int, delete_images: bool = False) -> bool:
        """
        Delete a VM template by ID.
        :param template_id: Template ID.
        :return: True if successful, False if an error occurred.  
        """
        logger.debug(f"Deleting VM template with ID: {template_id}")
        try:
            return self._one.template.delete(template_id, delete_images) != -1
        except pyone.OneException as e:
            logger.error(f"Failed to delete VM template with ID: {template_id}: {e}")
            return False

    def get_vm(self, vm_id: int) -> Optional[pyone.bindings.VMSub]:
        """
        Get VM information by ID.
        :param vm_id: VM ID.
        :return: VM object or None if VM is not found or error happened.
        """
        logger.debug(f"Getting VM info for VM with ID: {vm_id}")
        try:
            return self._one.vm.info(vm_id)
        except pyone.OneException as e:
            logger.error(f"Failed to get VM with ID: {vm_id}, error: {e}")
            return None

    def get_vm_disks(self, vm_id: int) -> Optional[List[pyone.bindings.DISKTypeSub]]:
        """
        Get the disks of a VM by ID.
        :param vm_id: VM ID.
        :return: List of dicts which represent Opennebula disk vectors. Or None if VM is not found or error happened.
        """
        logger.debug(f"Getting attached disks for VM with ID: {vm_id}")
        vm_info = self.get_vm(vm_id)
        if vm_info is None:
            logger.error(f"Failed to get attached disks for VM with ID: {vm_id}")
            return None
        disks = list()
        vm_template = vm_info.TEMPLATE
        vm_template_disk = vm_template.get("DISK")
        if vm_template_disk is not None:
            if isinstance(vm_template_disk, list):
                logger.debug(f"Multiple disks present in the VM template")
                disks = vm_template_disk
            else:
                logger.debug(f"Only one disk present in the VM template")
                logger.debug(f"Creating a list with the disk dictionary")
                disks = [vm_template_disk]
        return disks
    
    
    def get_vm_state(self, vm_id: int) -> Optional[Tuple[VMState, VMLCMState]]:
        """
        Get the current VMState and VMLCMState of the VM.
        :param vm_id: VM ID.
        :return: Tuple of VMState and VMLCMState or None if VM is not found or error happened.
        """
        logger.debug(f"Getting VM state for VM ID: {vm_id}")
        vm = self.get_vm(vm_id)
        if vm is not None:
            vm_state = VMState(vm.STATE)
            vm_lcm_state = VMLCMState(vm.LCM_STATE)
            logger.debug(f"Got VM state: {vm_state.name}, LCM state: {vm_lcm_state.name}")
            return (vm_state, vm_lcm_state)
        logger.error(f"Failed to get VM state for VM ID: {vm_id}")
        return None

    def attach_vm_image(self, vm_id: int, image_id: int, dev_prefix: Optional[ImageDevPrefix] = None, target: str = "") -> bool:
        """
        Attach an image to a VM.
        :param vm_id: VM ID.
        :param image_id: Image ID.
        :param dev_prefix: Optional device prefix for the attached image.
        :param target: Optional target device name (e.g., "sda").
        :return: True if successful, False if an error occurred.
        """
        logger.debug(f"Attaching image ID: {image_id} to VM ID: {vm_id}")
        disk_vector_prefix = "DISK = [ "
        disk_vector_suffix = " ]"
        disk_vector_template = list()
        if dev_prefix:
            logger.debug(f"Using device prefix: {dev_prefix.value}")
            disk_vector_template.append(f'DEV_PREFIX = "{dev_prefix.value}"')
        if target:
            logger.debug(f"Using target: {target}")
            disk_vector_template.append(f'TARGET = "{target}"')
        disk_vector_template.append(f'IMAGE_ID = "{image_id}"')
        disk_vector = disk_vector_prefix + ", ".join(disk_vector_template) + disk_vector_suffix
        logger.debug(f"Disk vector: {disk_vector}")
        try:
            logger.debug(f"Attaching image to VM")
            return self._one.vm.attach(vm_id, disk_vector) != -1
        except pyone.OneException as e:
            logger.error(f"Failed to attach image with ID: {image_id} to VM with ID: {vm_id}, error: {e}")
            return False

    def detach_vm_image(self, vm_id: int, disk_id: int) -> bool:
        """
        Detach an image from a VM.
        :param vm_id: VM ID.
        :param disk_id: Disk ID to detach. Not the IMAGE_ID.
        :return: True if successful, False if an error occurred.
        """
        logger.debug(f"Detaching disk ID: {disk_id} from VM ID: {vm_id}")
        try:
            return self._one.vm.detach(vm_id, disk_id) != -1
        except pyone.OneException as e:
            logger.error(f"Failed to detach disk with ID: {disk_id} from VM with ID: {vm_id}, error: {e}")
            return False

    def get_vm_image_target(self, vm_id: int, image_id: int) -> Optional[str]:
        """
        Get the target of the first matching disk image attached to the VM based on the image_id
        :param vm_id: VM ID.
        :param image_id: Image ID.
        :return: Target device name (e.g., "sda") or None if not found or error occured.
        """
        logger.debug(f"Getting target for image ID: {image_id} attached to VM ID: {vm_id}")
        disks = self.get_vm_disks(vm_id)
        for disk in disks:
            if disk.get("IMAGE_ID") == str(image_id):
                return disk.get("TARGET", None)
        return None

    def wait_for_image_state(self, image_id: int, target_state: ImageState, timeout: int = 60) -> bool:
        """
        Wait for the image to reach the target state. Timeout is in seconds.
        Function checks the image state every second.
        :param image_id: Image ID.
        :param target_state: Target state to wait for.
        :param timeout: Timeout in seconds.
        :return: True if the image reached the target state, False if timeout occurred or error happened.
        """
        logger.debug(f"Waiting for image ID: {image_id} to reach state: {target_state.name}")
        start_time = time.time()
        logger.debug(f"Start time: {start_time}")
        while True:
            current_state = self.get_image_state(image_id)
            if (current_state is None):
                logger.error(f"Can not retrieve image state for image ID: {image_id}")
                return False
            logger.debug(f"Current state: {current_state.name}")
            if current_state == target_state:
                logger.debug(f"Image ID: {image_id} reached target state: {target_state.name}")
                return True
            if time.time() - start_time > timeout:
                logger.warning(f"Timeout waiting for image {image_id} to reach state {target_state.name}, last state: {current_state.name}")
                return False
            time.sleep(1)

    def wait_for_vm_state(self, vm_id: int, target_state: VMState | VMLCMState, timeout: int = 60) -> bool:
        """
        Wait for the VM to reach the target state. Timeout is in seconds.
        Function checks the VM state every second.
        :param vm_id: VM ID.
        :param target_state: Target VM or LCM state to wait for.
        :param timeout: Timeout in seconds.
        :return: True if the VM reached the target state, False if timeout occurred or error happened.
        """
        logger.debug(f"Waiting for VM ID: {vm_id} to reach state: {target_state.name}")
        start_time = time.time()
        logger.debug(f"Start time: {start_time}")

        state_index = 0 if isinstance(target_state, VMState) else 1

        while True:
            current_state = self.get_vm_state(vm_id)
            if current_state is None:
                logger.error(f"Cannot retrieve VM state for VM ID: {vm_id}")
                return False

            logger.debug(f"Current state: {current_state[state_index].name}")
            if current_state[state_index] == target_state:
                logger.debug(f"VM ID: {vm_id} reached target state: {target_state.name}")
                return True
            current_time = time.time()
            logger.debug(f"Current time: {current_time}")
            if current_time - start_time > timeout:
                logger.warning(f"Timeout waiting for VM {vm_id} to reach state {target_state.name}, last state: {current_state[state_index].name}")
                return False
            time.sleep(1)

    def find_templates_by_attributes(self, filter: int, attributes: dict) -> Optional[List[int]]:
        """
        Find a VM template by its attributes.
        :param filter: The filter values dictate which resources to search:
                        -4: Resources belonging to the user’s primary group.
                        -3: Resources belonging to the user (default).
                        -2: All resources.
                        -1: Resources belonging to the user and any of his groups.
                        >= 0: Resources belonging to the UID (User’s Resources).
        :param **kwargs: Attributes to search for in the template.
        :return: Template ID if found, None otherwise.
        """
        logger.debug(f"Finding VM template by attributes: {attributes}")
        result = list()
        try:
            templates = self._one.templatepool.info(filter, -1, -1)
            for template in templates.VMTEMPLATE:
                match = all(template.TEMPLATE.get(key) == value for key, value in attributes.items())
                if match:
                    logger.debug(f"Found VM template with ID: {template.ID}")
                    result.append(template.ID)
        except pyone.OneException as e:
            logger.error(f"Failed to find VM template by attributes, error: {e}")
            return None
        if len(result) == 0:
            logger.warning(f"No VM templates found with the given attributes")
        return result
