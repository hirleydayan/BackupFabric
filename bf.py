#!/usr/bin/python
"""The main script file."""
from __future__ import with_statement
from fabric.api import env, parallel, roles

import datetime
import fab.linux as fl
import fab.xen as fx
import getopt
import os
import sys
import utils
import utils.linux as ul

# CONFIG file settings ########################################################
__SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__))
__CONFIG_FILE = __SCRIPT_PATH + "/config.ini"
__CONFIG = utils.init_config(__CONFIG_FILE)

__SERVER_BKP_PATH = __CONFIG.get("server", "backup_path")
__LOG = __CONFIG.get("server", "log_file")

__XEN_BKP_PATH = __CONFIG.get("xen", "backup_mount_point")
env.roledefs['xen'] = __CONFIG.get("xen", "hosts").split(',')
###############################################################################

__VERSION = "20170310-2000"
__DATE_TIME = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')


def __make_list_of_vms(f, logger=None):
    vms = {}
    if f == "":
        vms = fx.vm_list()
    else:
        vms = fx.vm_list(other_parameters="tags:contains\=" + f)
    if len(vms) == 0 and logger is not None:
        logger.warning("No virtual machines where found to be backed-up")

    return None if not vms else vms


def __make_folder(path, logger=None):
    resp = fl.mkdir(path)

    if resp is not None and resp.return_code == 0:
        if logger is not None:
            logger.info("Mount point path on XenServer created")
    else:
        resp = fl.ls(__XEN_BKP_PATH, "-1")
        if resp is not None and resp.return_code == 0:
            if logger is not None:
                logger.info("Mount point path on XenServer already created")
        else:
            if logger is not None:
                logger.error("Could not create temporary mount point on " +
                             "XenServer")
            return False
    return True


def __delete_folder(path, logger=None):
    # rmdir <local_path>
    resp = fl.rmdir(path)
    if resp is not None and resp.return_code == 0:
        if logger is not None:
            logger.info("Mount point path removed fron XenServer")
        return True
    else:
        if logger is not None:
            logger.warning("Could not remove temporary mount point path " +
                           "from XenServer")
        return False


def __mount_folder(local_path, remote_path, logger=None):
    # mount -t <mount_type> <ip>:<path> <local_path>
    resp = fl.mount("nfs", local_path, remote_path)
    if resp is not None and resp.return_code == 0:
        if logger is not None:
            logger.info("NFS mounted on XenServer")
        return True
    else:
        if logger is not None:
            logger.warning("Could not mount NFS on XenServer ")
        return False


def __unmount_folder(path, logger=None):
    # unmount <local_path>
    resp = fl.unmount(path)
    if resp is not None and resp.return_code == 0:
        if logger is not None:
            logger.info("NFS unmounted from XenServer")
        return True
    else:
        if logger is not None:
            logger.warning("NFS could not be unmounted from XenServer")
        return False


def ___check_mountpoint(path, logger=None):
    # mountpoint -t <mount_type> <ip>:<path> <local_path>
    resp = fl.mountpoint(path, True)
    if resp is not None and resp.return_code == 0:
        if logger is not None:
            logger.info("NFS is mounted on XenServer")
        return True
    else:
        if logger is not None:
            logger.error("NFS is not mounted on XenServer")
        return False


@roles('xen')
def test():
    """Run test function."""
    print(___check_mountpoint(__XEN_BKP_PATH))


@parallel
@roles('xen')
def xen_backup(f=""):
    """Run xen backup on XenServers defined in config file."""
    client_ip = str(env.host_string)
    log_path, _ = os.path.split(__LOG)
    ul.make_dir(log_path)

    logger = utils.init_logger_with_rotate(__LOG, client_ip.ljust(15))

    logger.info("XenServer backup service started.")
    logger.info("Version: " + __VERSION)

    # Print XenServer hostname
    fl.hostname()

    # Make a list of VMs to backup
    vms = __make_list_of_vms(f, logger)

    if vms is None:
        logger.error("Aborting backup on XenServer.")
        return

    # Make mount point path for NFS
    if not __make_folder(__XEN_BKP_PATH, logger):
        logger.error("Aborting backup on XenServer.")
        return

    # Mount backup NFS
    __mount_folder(ul.get_ip() + ":" + __SERVER_BKP_PATH, __XEN_BKP_PATH,
                   logger)

    # Check if NFS has been mounted
    if not ___check_mountpoint(__XEN_BKP_PATH, logger):
        logger.error("Aborting backup on XenServer.")
        return

    # Make a snapshot of the VMs
    for vm_uuid in vms:
        vm_uuid_bk = vm_uuid
        vm_name = str(vms[vm_uuid][fx.VALUE_NAMELABEL])
        vm_power_state = str(vms[vm_uuid][fx.VALUE_POWERSTATE])
        if not vm_name:
            logger.error("Could not get the name of a candidate" +
                         "virtual machine to be backed-up.")
            logger.error("Skipping virtual machine")
            continue

        logger.info("Virtual machine is " + vm_power_state.lower())

        if vm_power_state == fx.VALUE_RUNNING:
            logger.info("Taking snapshot from virtual machine on XenServer.")
            vm_uuid_bk = fx.vm_snapshot(vm_uuid, "\"" + vm_name + " " +
                                        __DATE_TIME + " backup\"")

            if vm_uuid_bk is None or vm_uuid_bk.return_code != 0:
                logger.error("Could not create a snapshot of the running " +
                             "virtual machine on XenServer")
                logger.error("Skipping virtual machine")
                continue

            resp = fx.template_param_set(vm_uuid_bk)
            if resp is None or resp.return_code != 0:
                logger.error("Could not adjust a snapshot parameter of " +
                             "the running virtual machine on XenServer")
                logger.error("Skipping virtual machine")
                continue

        # Creating path for saving backup on remote mounted backup server
        # if it does not exist
        resp = fl.mkdir(__XEN_BKP_PATH + "/" + client_ip)

        file_name = __XEN_BKP_PATH + "/" + client_ip + "/" + \
            utils.cleanup_text(vm_name, True) + "_" + __DATE_TIME

        logger.info("Exporting virtual machine on XenServer to NFS")
        resp = fx.vm_export(vm_uuid_bk, file_name)

        if resp is None or resp.return_code != 0:
            logger.error("Could not export virtual machine on XenServer")
            logger.error("Virtual machine backup aborted")
            continue

        if vm_power_state == fx.VALUE_RUNNING:
            resp = fx.vm_uninstall(vm_uuid_bk, force="true")
            if resp is None or resp.return_code != 0:
                logger.warning("Could not uninstall virtual machine " +
                               "snapshot on XenServer")
                logger.warning("Server needs to be cleaned up manually")

    # Unmount backup NFS
    logger.info("Unmounting NSF fron XenServer")
    if not __unmount_folder(__XEN_BKP_PATH, logger):
        return

    # Delete mount point
    logger.info("Deleting temporary mount point path fron XenServer")
    if not __delete_folder(__XEN_BKP_PATH, logger):
        return

    logger.info("Backup finished for XenServer at " + client_ip)


def main(argv):
    """Main function."""
    filter_string = ""
    try:
        opts, args = getopt.getopt(argv, "hf:", ["filter="])
    except getopt.GetoptError:
        print('bf.py -f <filter_string>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('bf.py -f <filter_string>')
            sys.exit()
        elif opt in ("-f", "--filter"):
            filter_string = arg

    fab_name = os.path.basename(sys.argv[0]).split(".")[0]
    print(fab_name)
    os.system('fab -f ' + __SCRIPT_PATH + "/" + fab_name +
              ' xen_backup:f=\"' + filter_string + "\"")


if __name__ == "__main__":
    main(sys.argv[1:])
