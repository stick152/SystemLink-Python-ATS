"""
process_errors.py
"""
from syslinkats.framework.errors.error_codes.installer_error_codes import retrieve_installer_error
from syslinkats.framework.errors.error_codes.system_error_codes import retrieve_system_error
from syslinkats.framework.errors.error_handlers.pkg_mgr_errors import handle_pkgmgr_operation_errors


def handle_process_errors(caller='', output=None, code_ignore_list=None,
                          args_list=None, append_found_ret_code=False):
    """Routes process error handling.

    Args:
        caller: The calling method / function.
        output: The output object with the returncode to examine.
        code_ignore_list: Error codes to ignore.
        args_list: A list of arguments to be used in the error format strings.
        append_found_ret_code: Should the actual, discovered error code (the
        one that Package Manager returned) be appended to the list of args?

    Returns:
        Can return an error object.

    Raises:
        TypeError

    """
    if not output:
        raise TypeError('output cannot be None.')

    if caller == 'run_installer_on_vm':
        error = handle_installer_process_errors(output, code_ignore_list)
        if error:
            if error['code'] == 'UNKNOWN_ERROR':
                handle_non_installer_process_errors(output, code_ignore_list)
    elif caller == 'pkgmgr_operation':
        result = handle_pkgmgr_operation_errors(
            output, code_ignore_list, args_list, append_found_ret_code
        )
        if result:
            return result
    else:
        handle_non_installer_process_errors(output, code_ignore_list)


def handle_non_installer_process_errors(output=None, code_ignore_list=None):
    """Handle system (or non-installer) errors.

    Args:
        output: The Popen object with the returncode to examine.
        code_ignore_list: Error codes to ignore.

    Raises:
        RuntimeError
        TypeError

    """
    if not output:
        raise TypeError('output cannot be None.')

    if code_ignore_list:
        if output['return_code'] in code_ignore_list:
            return

    system_error = retrieve_system_error(output)

    if system_error['value'] != 0:
        raise RuntimeError(
            'Process failed with code {0}: {1}\n{2}'.format(
                system_error['value'],
                system_error['code'],
                system_error['description']
            )
        )


def handle_installer_process_errors(output=None, code_ignore_list=None):
    """Handle errors related to installers.

    Prints installer return info to the console and, if needed, raises a
    RuntimeError exception containing the installer return information.

    Args:
        output: The Popen object with the returncode to examine.
        code_ignore_list: Error codes to ignore.

    Returns:
        Can return an installer_error object.

    Raises:
        RuntimeError
        TypeError

    """
    if not output:
        raise TypeError('output cannot be None.')

    installer_error = retrieve_installer_error(output)

    if code_ignore_list:
        if installer_error['value'] in code_ignore_list:
            return

    if (installer_error['code'] == 'ERROR_SUCCESS' or
            installer_error['code'] == 'ERROR_SUCCESS_REBOOT_INITIATED' or
            installer_error['code'] == 'ERROR_SUCCESS_REBOOT_REQUIRED' or
            installer_error['code'] == 'UNKNOWN_ERROR'):
        return installer_error
    elif installer_error['value'] != 0:
        raise RuntimeError(installer_error.values())
