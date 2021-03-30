#-------------------------------------------------------------------------
# Name:         system_error_codes
# Purpose:      Used to generate output for system errors.  By default, psexec
#               will return an error code, but no other information.  This file
#               contains the default return codes provided by Microsoft
#               at this location: 
# http://msdn.microsoft.com/en-us/library/windows/desktop/ms681382(v=vs.85).aspx
#
# NOTE:         This module is under development!  I will be making it more
#               like the one for installer_error_codes, and also adding ALL
#               error codes provided by Microsoft at the above location. 
#
# Author:       sedwards
#
# Created:      20/11/2013
# Copyright:    (c) NationalInstruments 2013
#-------------------------------------------------------------------------

def retrieve_system_error(process_output=None):
    """Return a dictionary with system error code information."""
    if not process_output:
        raise TypeError('process cannot be None!')

    return_code = process_output['return_code']
    stderr = process_output['stderr']
    stdout = process_output['stdout']

    system_error = {}

    # Set a ganeric error in case one comes in that we don't know how to
    # handle.
    system_error['code'] = 'UNKNOWN_ERROR'
    system_error['value'] = return_code
    system_error['description'] = 'sdtout: {0} \nstderr: {1}'.format(
        stdout, stderr)

    if return_code == 0:
        system_error['code'] = 'ERROR_SUCCESS'
        system_error['value'] = 0
        system_error['description'] = 'The operation completed successfully.'
    elif return_code == 1:
        system_error['code'] = 'ERROR_INVALID_FUNCTION'
        system_error['value'] = 1
        system_error['description'] = 'Incorrect function.'
    elif return_code == 2:
        system_error['code'] = 'ERROR_FILE_NOT_FOUND'
        system_error['value'] = 2
        system_error['description'] = '''
            The system cannot find the file specified.'''
    elif return_code == 3:
        system_error['code'] = 'ERROR_PATH_NOT_FOUND'
        system_error['value'] = 3
        system_error['description'] = '''
            TThe system cannot find the path specified.'''
    elif return_code == 5:
        system_error['code'] = 'ERROR_ACCESS_DENIED'
        system_error['value'] = 5
        system_error['description'] = 'Access is denied.'
    elif return_code == 6:
        system_error['code'] = 'ERROR_INVALID_HANDLE'
        system_error['value'] = 6
        system_error['description'] = 'The handle is invalid.'
    elif return_code == 53:
        system_error['code'] = 'ERROR_BAD_NETPATH'
        system_error['value'] = 53
        system_error['description'] = 'The network path was not found.'
    elif return_code == 54:
        system_error['code'] = 'ERROR_NETWORK_BUSY'
        system_error['value'] = 54
        system_error['description'] = 'The network is busy.'
    elif return_code == 2202:
        system_error['code'] = 'ERROR_BAD_USERNAME'
        system_error['value'] = 2202
        system_error['description'] = 'The specified username is invalid.'
    elif return_code == 2250:
        system_error['code'] = 'ERROR_NOT_CONNECTED'
        system_error['value'] = 2250
        system_error['description'] = 'This network connection does not exist.'

    return system_error
