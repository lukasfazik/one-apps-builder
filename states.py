import enum

class ImageState(enum.Enum):
    """
    Image states as defined in OpenNebula documentation.
    Reference: https://docs.opennebula.io/6.10/integration_and_development/references/img_states.html
    """
    INIT             = 0   # Initialization state                  
    READY            = 1   # Image ready to use                    
    USED             = 2   # The image is being used by other VM     
    DISABLED         = 3   # Image can not be instantiated by a VM   
    LOCKED           = 4   # FS operation for the Image in process  
    ERROR            = 5   # Error state the operation FAILED      
    CLONE            = 6   # Image is being cloned                 
    DELETE           = 7   # DS is deleting the image              
    USED_PERS        = 8   # Image is in use and persistent        
    LOCKED_USED      = 9   # FS operation in progress, VMs waiting 
    LOCKED_USED_PERS = 10  # FS operation in progress, VMs waiting. Persistent

class VMState(enum.Enum):
    """
    VM states as defined in OpenNebula documentation.
    Reference: https://docs.opennebula.io/6.10/integration_and_development/references/vm_states.html
    """
    INIT            = 0   # Internal initialization state right after VM creation
    PENDING         = 1   # Waiting for a resource to run on
    HOLD            = 2   # VM held by the owner; not scheduled until released
    ACTIVE          = 3   # The VM is active (detailed by LCM state)
    STOPPED         = 4   # VM is stopped; state saved and disks transferred back
    SUSPENDED       = 5   # VM is suspended; files remain on the host for resume
    DONE            = 6   # VM is done; kept in the database for accounting
    POWEROFF        = 8   # Like suspended but with no checkpoint file generated
    UNDEPLOYED      = 9   # VM is shut down; disks transferred to the datastore
    CLONING         = 10  # Waiting for disk images to complete the initial copy
    CLONING_FAILURE = 11  # Failure during cloning; one or more images in ERROR state

class VMLCMState(enum.Enum):
    """
    VM LCM states as defined in OpenNebula documentation. This states are only valid if the VM is in ACTIVE state.
    Reference: https://docs.opennebula.io/6.10/integration_and_development/references/vm_states.html
    """
    INIT                            = 0   # Internal initialization, not visible to end users
    PROLOG                          = 1   # Transferring VM files to the host
    BOOT                            = 2   # Waiting for the hypervisor to create the VM
    RUNNING                         = 3   # The VM is running (includes booting and shutdown phases)
    MIGRATE                         = 4   # The VM is migrating between hosts (hot migration)
    SAVE_STOP                       = 5   # Saving VM files after a stop operation
    SAVE_SUSPEND                    = 6   # Saving VM files after a suspend operation
    SAVE_MIGRATE                    = 7   # Saving VM files for a cold migration
    PROLOG_MIGRATE                  = 8   # File transfers during a cold migration
    PROLOG_RESUME                   = 9   # File transfers after a resume action (from stopped)
    EPILOG_STOP                     = 10  # File transfers from the host to the datastore
    EPILOG                          = 11  # Cleanup: host cleanup and copying disk images back
    SHUTDOWN                        = 12  # Shutdown ACPI signal sent; waiting for shutdown
    CLEANUP_RESUBMIT                = 15  # Cleanup after a delete-recreate action
    UNKNOWN                         = 16  # VM couldn’t be monitored; state is unknown
    HOTPLUG                         = 17  # A disk attach/detach operation is in progress
    SHUTDOWN_POWEROFF               = 18  # Shutdown signal sent; waiting for shutdown (poweroff)
    BOOT_UNKNOWN                    = 19  # Waiting for hypervisor creation (from UNKNOWN)
    BOOT_POWEROFF                   = 20  # Waiting for hypervisor creation (from POWEROFF)
    BOOT_SUSPENDED                  = 21  # Waiting for hypervisor creation (from SUSPENDED)
    BOOT_STOPPED                    = 22  # Waiting for hypervisor creation (from STOPPED)
    CLEANUP_DELETE                  = 23  # Cleanup after a delete action
    HOTPLUG_SNAPSHOT                = 24  # A system snapshot action is in progress
    HOTPLUG_NIC                     = 25  # A NIC attach/detach operation is in progress
    HOTPLUG_SAVEAS                  = 26  # A disk-saveas operation is in progress
    HOTPLUG_SAVEAS_POWEROFF         = 27  # Disk-saveas (from POWEROFF) in progress
    HOTPLUG_SAVEAS_SUSPENDED        = 28  # Disk-saveas (from SUSPENDED) in progress
    SHUTDOWN_UNDEPLOY               = 29  # Shutdown signal sent; waiting for undeploy shutdown
    EPILOG_UNDEPLOY                 = 30  # Cleanup: host cleanup and transferring files during undeploy
    PROLOG_UNDEPLOY                 = 31  # File transfers after resume action (from undeployed)
    BOOT_UNDEPLOY                   = 32  # Waiting for hypervisor creation (from UNDEPLOY)
    HOTPLUG_PROLOG_POWEROFF         = 33  # File transfers for disk attach from poweroff
    HOTPLUG_EPILOG_POWEROFF         = 34  # File transfers for disk detach from poweroff
    BOOT_MIGRATE                    = 35  # Waiting for hypervisor creation (cold migration)
    BOOT_FAILURE                    = 36  # Failure during BOOT
    BOOT_MIGRATE_FAILURE            = 37  # Failure during BOOT_MIGRATE
    PROLOG_MIGRATE_FAILURE          = 38  # Failure during PROLOG_MIGRATE
    PROLOG_FAILURE                  = 39  # Failure during PROLOG
    EPILOG_FAILURE                  = 40  # Failure during EPILOG
    EPILOG_STOP_FAILURE             = 41  # Failure during EPILOG_STOP
    EPILOG_UNDEPLOY_FAILURE         = 42  # Failure during EPILOG_UNDEPLOY
    PROLOG_MIGRATE_POWEROFF         = 43  # File transfers during cold migration (from POWEROFF)
    PROLOG_MIGRATE_POWEROFF_FAILURE = 44  # Failure during PROLOG_MIGRATE_POWEROFF
    PROLOG_MIGRATE_SUSPEND          = 45  # File transfers during cold migration (from SUSPEND)
    PROLOG_MIGRATE_SUSPEND_FAILURE  = 46  # Failure during PROLOG_MIGRATE_SUSPEND
    BOOT_UNDEPLOY_FAILURE           = 47  # Failure during BOOT_UNDEPLOY
    BOOT_STOPPED_FAILURE            = 48  # Failure during BOOT_STOPPED
    PROLOG_RESUME_FAILURE           = 49  # Failure during PROLOG_RESUME
    PROLOG_UNDEPLOY_FAILURE         = 50  # Failure during PROLOG_UNDEPLOY
    DISK_SNAPSHOT_POWEROFF          = 51  # Disk-snapshot-create (from POWEROFF) in progress
    DISK_SNAPSHOT_REVERT_POWEROFF   = 52  # Disk-snapshot-revert (from POWEROFF) in progress
    DISK_SNAPSHOT_DELETE_POWEROFF   = 53  # Disk-snapshot-delete (from POWEROFF) in progress
    DISK_SNAPSHOT_SUSPENDED         = 54  # Disk-snapshot-create (from SUSPENDED) in progress
    DISK_SNAPSHOT_REVERT_SUSPENDED  = 55  # Disk-snapshot-revert (from SUSPENDED) in progress
    DISK_SNAPSHOT_DELETE_SUSPENDED  = 56  # Disk-snapshot-delete (from SUSPENDED) in progress
    DISK_SNAPSHOT                   = 57  # Disk-snapshot-create (from RUNNING) in progress
    DISK_SNAPSHOT_DELETE            = 59  # Disk-snapshot-delete (from RUNNING) in progress
    PROLOG_MIGRATE_UNKNOWN          = 60  # File transfers during cold migration (from UNKNOWN)
    PROLOG_MIGRATE_UNKNOWN_FAILURE  = 61  # Failure during PROLOG_MIGRATE_UNKNOWN
    DISK_RESIZE                     = 62  # Disk resize with VM in RUNNING state
    DISK_RESIZE_POWEROFF            = 63  # Disk resize with VM in POWEROFF state
    DISK_RESIZE_UNDEPLOYED          = 64  # Disk resize with VM in UNDEPLOYED state
    HOTPLUG_NIC_POWEROFF            = 65  # NIC attach/detach (from POWEROFF) in progress
    HOTPLUG_RESIZE                  = 66  # Hotplug resize of VCPU and memory in progress
    HOTPLUG_SAVEAS_UNDEPLOYED       = 67  # Disk-saveas (from UNDEPLOYED) in progress
    HOTPLUG_SAVEAS_STOPPED          = 68  # Disk-saveas (from STOPPED) in progress
    BACKUP                          = 69  # Backup operation in progress (VM running)
    BACKUP_POWEROFF                 = 70  # Backup operation in progress (VM poweroff)
    RESTORE                         = 71  # VM disks are being restored from backup image
