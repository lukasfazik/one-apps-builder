import enum
import pyone
from typing import Optional, List, Tuple
from states import ImageState, VMState, VMLCMState

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
        session = ":".join((username, password))
        self._one = pyone.OneServer(uri=url, session=session, timeout=timeout)

    @classmethod
    def get_vm_disks(cls, vm: pyone.bindings.VMSub) -> List[pyone.bindings.DISKTypeSub]:
        vm_template = vm.TEMPLATE
        vm_template_disk = vm_template.get("DISK")
        disks = list()
        if vm_template_disk is not None:
            if isinstance(vm_template_disk, list):
                disks = vm_template_disk
            else:
                disks = [vm_template_disk]
        return disks
    
    def get_image(self, id: int) -> Optional[pyone.bindings.IMAGESub]:
        try:
            return self._one.image.info(id)
        except pyone.OneException as e:
            print(f"Error getting image: {str(e)}")
            return None

    def get_image_state(self, image_id: int) -> Optional[ImageState]:
        image = self.get_image(image_id)
        if image is not None:
            return ImageState(image.STATE)
        return None

    def create_image(self, datastore: int, image_name: str, image_description: Optional[str] = None, image_path: Optional[str] = None, image_type: ImageType = ImageType.DATABLOCK, image_dev_prefix: Optional[ImageDevPrefix] = None, image_format: ImageFormat = ImageFormat.RAW, image_size_mb: Optional[int] = None, persistent_image: bool = False) -> int:
        image_template: List[str] = []
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
        image_template.append(f'NAME = "{image_name}"')
        image_template.append(f'DESCRIPTION = "{image_description}"')
        image_template.append(f'TYPE = "{image_type.value}"')
        
        image_definition = "\n".join(image_template)
        try:
            return self._one.image.allocate(image_definition, datastore)
        except pyone.OneException as e:
            print(f"Error creating image: {str(e)}")
            return -1

    def delete_image(self, id: int) -> int:
        try:
            return self._one.image.delete(id)
        except pyone.OneException as e:
            print(f"Error deleting image: {str(e)}")
            return -1

    def get_vm_template(self, id: int) -> Optional[pyone.bindings.TEMPLATETypeSub]:
        try:
            return self._one.template.info(id)
        except pyone.OneException as e:
            print(f"Error getting VM template: {str(e)}")
            return None

    def create_vm_template(self, template: str) -> int:
        try:
            return self._one.template.allocate(template)
        except pyone.OneException as e:
            print(f"Error creating VM template: {str(e)}")
            return -1

    def delete_vm_template(self, id: int) -> int:
        try:
            return self._one.template.delete(id)
        except pyone.OneException as e:
            print(f"Error deleting VM template: {str(e)}")
            return -1

    def get_vm(self, id: int) -> Optional[pyone.bindings.VMSub]:
        try:
            return self._one.vm.info(id)
        except pyone.OneException as e:
            print(f"Error getting VM: {str(e)}")
            return None

    def get_vm_state(self, vm_id: int) -> Optional[Tuple[VMState, VMLCMState]]:
        vm = self.get_vm(vm_id)
        if vm is not None:
            return (VMState(vm.STATE), VMLCMState(vm.LCM_STATE))
        return None

    def attach_vm_image(self, vm_id: int, image_id: int, dev_prefix: Optional[ImageDevPrefix] = None, target: str = "") -> int:
        disk_vector_prefix = "DISK = [ "
        disk_vector_suffix = " ]"
        disk_vector_template = list()
        if dev_prefix:
            disk_vector_template.append(f'DEV_PREFIX = "{dev_prefix.value}"')
        if target:
            disk_vector_template.append(f'TARGET = "{target}"')
        disk_vector_template.append(f'IMAGE_ID = "{image_id}"')
        disk_vector = disk_vector_prefix + ", ".join(disk_vector_template) + disk_vector_suffix
        try:
            return self._one.vm.attach(vm_id, disk_vector)
        except pyone.OneException as e:
            print(f"Error attaching image: {str(e)}")
            return -1

    def detach_vm_image(self, vm_id: int, disk_id: int) -> int:
        try:
            return self._one.vm.detach(vm_id, disk_id)
        except pyone.OneException as e:
            print(f"Error detaching image: {str(e)}")
            return -1

    def get_vm_image_target(self, vm_id: int, image_id: int) -> Optional[str]:
        vm = self.get_vm(vm_id)
        if vm is None:
            return None
        disks = self.get_vm_disks(vm)
        for disk in disks:
            if disk.geT("IMAGE_ID") == str(image_id):
                return disk.get("TARGET", None)
        return None

    def wait_for_image_state(self, image_id: int, target_state: ImageState, timeout: int = 60) -> bool:
        """
        Wait for the image to reach the target state. Timeout is in seconds.
        """
        import time
        start_time = time.time()
        while True:
            current_state = self.get_image_state(image_id)
            if current_state == target_state:
                return True
            if time.time() - start_time > timeout:
                print(f"Timeout waiting for image {image_id} to reach state {target_state.name}")
                return False
            time.sleep(1)
            
    def wait_for_vm_state(self, vm_id: int, target_state: VMState | VMLCMState, timeout: int = 60) -> bool:
        
        if isinstance(target_state, VMState):
            state_index = 0
        else:
            state_index = 1
        
        import time
        start_time = time.time()
        while True:
            current_state = self.get_vm_state(vm_id)
            if current_state is not None and current_state[state_index] == target_state:
                return True
            if time.time() - start_time > timeout:
                print(f"Timeout waiting for VM {vm_id} to reach state {target_state.name}")
                return False
            time.sleep(1)