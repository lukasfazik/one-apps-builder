from one import One
from states import VMLCMState

def calculate_disk_location(disk_target: str) -> int:
    """
    Calculate the disk location based on the target string.
    The target string is expected to be in the format "sdX", where X is a letter.
    """
    return ord(disk_target.lower()[2]) - ord("a")


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
            
    return True
