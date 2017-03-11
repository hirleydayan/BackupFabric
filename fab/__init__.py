"""The fab package functions."""
from fabric.api import run, settings, cd, hide
from utils import cleanup_text

import logging
import logging.handlers
import re


def run_cmd(cmd, work_dir="/tmp", logger=None):
    """Run remote command."""
    logger = logging.getLogger("fabric")
    r = None
    with settings(abort_exception=Exception), cd(work_dir), \
        hide('output', 'running', 'warnings'), \
            settings(warn_only=True):
        try:
            if logger:
                logger.info(cmd)
            r = run(cmd)
            if logger:
                for line in r.splitlines():
                    # Skip empty lines
                    if re.match(r"^$", line):
                        continue
                    logger.info(cleanup_text(line))
        except Exception as e:
            if logger:
                logger.error(e)
    return r
