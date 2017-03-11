"""The fab.linux package functions."""
import fab

__CMD_DF = "df -k {path}"
__CMD_DU = "du -s {path}"
__CMD_HOSTNAME = "hostname"
__CMD_LS = "ls {options} {path}"
__CMD_MKDIR = "mkdir {parent} {path}"
__CMD_MOUNT = "mount -vvv -t {type} {remote_target} {mount_point}"
__CMD_MOUNTPOINT = "mountpoint {options} {path}"
__CMD_RMDIR = "rmdir {path}"
__CMD_STAT = " stat {options} {path}"
__CMD_UNMOUNT = "umount -vvv {mount_point}"


def hostname():
    """Run hostname command."""
    return fab.run_cmd(cmd=__CMD_HOSTNAME)


def df(path=""):
    """Run df command."""
    return fab.run_cmd(cmd=__CMD_DF.format(**locals()))


def du(path=""):
    """Run du command."""
    resp = fab.run_cmd(cmd=__CMD_DU.format(**locals()))
    resp = resp.strip().split()
    return resp[0] if len(resp) > 1 else None


def mountpoint(path="/", quiet=False):
    """Run mountpoint command."""
    options = "-q" if quiet else ""
    return fab.run_cmd(cmd=__CMD_MOUNTPOINT.format(**locals()))


def mount(type, remote_target, mount_point):
    """Run mount command."""
    return fab.run_cmd(cmd=__CMD_MOUNT.format(**locals()))


def unmount(mount_point):
    """Run unmount command."""
    return fab.run_cmd(cmd=__CMD_UNMOUNT.format(**locals()))


def mkdir(path, make_parent=True):
    """Run mkdir command."""
    parent = "-p" if make_parent else ""
    return fab.run_cmd(cmd=__CMD_MKDIR.format(**locals()))


def rmdir(path):
    """Run rmdir command."""
    return fab.run_cmd(cmd=__CMD_RMDIR.format(**locals()))


def ls(path=".", options=""):
    """Run ls command."""
    return fab.run_cmd(cmd=__CMD_RMDIR.format(**locals()))


def stat(path=".", options=""):
    """Run stat command."""
    return fab.run_cmd(cmd=__CMD_STAT.format(**locals()))
