"""The utils.linux package functions."""
import os
import socket

from os import path


def get_file(localpath, remotepath):
    """Get file."""
    return os.get(localpath, remotepath, use_sudo=True)


def get_free_space(path="/"):
    """Get free space."""
    f_bsize, f_frsize, f_blocks, f_bfree, f_bavail, f_files, f_ffree, \
        f_favail, f_flag, f_namema = tuple(os.statvfs(path))
    free_space = f_bsize * f_bfree
    return free_space


def get_disk_size():
    """Get disk size."""
    f_bsize, f_frsize, f_blocks, f_bfree, f_bavail, f_files, f_ffree, \
        f_favail, f_flag, f_namema = tuple(os.statvfs(path))
    disk_size = f_blocks * f_bsize
    return disk_size


def get_ip():
    """Get ip address."""
    return socket.gethostbyname(socket.gethostname())


def get_hostname():
    """Get hostname."""
    return socket.gethostname()


def make_dir(path):
    """Make directory."""
    if not os.path.exists(path):
        os.makedirs(path)


def path_exists(path):
    """Ceck if path exists, either file or folder."""
    return os.path.exists(path)
