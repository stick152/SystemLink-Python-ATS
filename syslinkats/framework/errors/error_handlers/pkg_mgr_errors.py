"""
pkg_mgr_errors.py
"""
import re

from syslinkats.framework.errors.error_codes.package_manager_exit_codes import retrieve_pkgmgr_error


def handle_pkgmgr_operation_errors(output=None, code_ignore_list=None,
                                   args_list=None,
                                   append_found_ret_code=False):
    """Handle errors related to Package Manager operations.

    Prints pkgmgr exit codes to the console and, if needed, raises a
    RuntimeError exception containing the pkgmgr return information.

    Args:
        output: The Popen object with the returncode to examine.
        code_ignore_list: Error codes to ignore.
        args_list: A list of arguments to use in the format string of the
        located error message.
        append_found_ret_code: Should the actual, discovered error code (the
        one that Package Manager returned) be appended to the list of args?

    Returns:
        Can return an pkgmgr_error object with structure:
            {
                'value': int,
                'code': 'string',
                'description': 'format string'
            }

    Raises:
        RuntimeError
        TypeError

    """
    if not output:
        raise TypeError('output cannot be None.')

    # Psexec can't handle PkgMgr return codes, so it returns one of its own
    # when it gets a non-zero code from PkgMgr.  So we need to parse out the
    # actual PkgMgr code and set it here.
    if output['return_code'] != 0:
        output['return_code'] = int(
            re.findall('error code ([-+]\\d+)', output['stderr'])[0]
        )

    if append_found_ret_code:
        args_list.append(output['return_code'])

    pkgmgr_error = retrieve_pkgmgr_error(output, args_list)

    if code_ignore_list:
        if pkgmgr_error['value'] in code_ignore_list:
            return

    if pkgmgr_error['value'] == -125083:
        return pkgmgr_error

    if (pkgmgr_error['code'] != 'Success' and
            pkgmgr_error['code'] != 'RebootNeeded'):
        raise RuntimeError(pkgmgr_error.values())
