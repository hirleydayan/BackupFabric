"""The fab.xen package functions."""
import fab
import re

__CMD_VM_LIST = "xe vm-list is-control-domain={is_control_domain} " + \
              "is-a-snapshot={is_snapshot} {other_parameters}"
__CMD_VM_SNAPSHOT = "xe vm-snapshot uuid={uuid} " + \
                   "new-name-label={new_name_label}"
__CMD_TEMPLATE_PARAM_SET = "xe template-param-set " + \
                         "is-a-template={is_a_template} " + \
                         "ha-always-run={ha_always_run} uuid={uuid}"
__CMD_VM_EXPORT = "xe vm-export compress={compress} " + \
                "vm={uuid} filename={filename}"
__CMD_VM_UNINSTALL = "xe vm-uninstall uuid={uuid} force={force}"

VALUE_FALSE = "false"
VALUE_TRUE = "true"
VALUE_UUID = "uuid"
VALUE_POWERSTATE = "power-state"
VALUE_NAMELABEL = "name-label"
VALUE_DATA = "data"
VALUE_HALTED = "halted"
VALUE_RUNNING = "running"


def vm_list(is_control_domain=VALUE_FALSE, is_snapshot=VALUE_FALSE,
            other_parameters="", work_dir="/tmp"):
    """Run xen vm list command."""
    resp = fab.run_cmd(cmd=__CMD_VM_LIST.format(**locals()))

    vm = {}
    vm_list = {}
    lines = resp.splitlines()
    n_lines = len(lines)
    for index in range(n_lines):
        line = fab.cleanup_text(lines[index])

        # Skip empty lines
        if re.match(r"^$", line):
            continue

        obj = line.split(":")
        if len(obj) > 1:
            key = re.search(re.compile(r"^[^ ]*"), obj[0]).group(0)

            if key in vm:
                # Start over new VM parameters
                uuid = vm[VALUE_UUID]
                del vm[VALUE_UUID]
                vm_list[uuid] = vm
                vm = {}

            if key not in vm:
                # Parameter belongs to same vm
                vm[key] = obj[1].strip()

            if index == n_lines - 1:
                # Last line reached
                uuid = vm[VALUE_UUID]
                del vm[VALUE_UUID]
                vm_list[uuid] = vm

    return vm_list


def vm_snapshot(uuid, new_name_label):
    """Run xen template-param-set command."""
    resp = fab.run_cmd(cmd=__CMD_VM_SNAPSHOT.format(**locals()))
    return resp


def template_param_set(uuid, is_a_template=VALUE_FALSE,
                       ha_always_run=VALUE_FALSE):
    """Run xen template-param-set command."""
    return fab.run_cmd(cmd=__CMD_TEMPLATE_PARAM_SET.format(**locals()))


def vm_export(uuid, filename, compress=VALUE_TRUE):
    """Run xen vm export command."""
    # xe vm-export vm={uuid} filename={filename}"
    extension = ".xva.gz" if compress else ".xva"
    filename = filename + extension
    return fab.run_cmd(cmd=__CMD_VM_EXPORT.format(**locals()))


def vm_uninstall(uuid, force=VALUE_FALSE):
    """Run xen vm uninstall command."""
    return fab.run_cmd(cmd=__CMD_VM_UNINSTALL.format(**locals()))
