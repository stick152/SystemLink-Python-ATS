#-------------------------------------------------------------------------
# Name:        installer_error_codes
# Purpose:     Used to generate output for installer errors.  By default, psexec
#              will return an error code, but no other information.  This file
#              contains the default .msi return codes provided by Microsoft
#              at this location: http://support.microsoft.com/kb/290158
#
# NOTE:         This file was auto-generated, so the error strings are not
#               wrapped.  If I have time, I might look into that.
#
# Author:      sedwards
#
# Created:     18/11/2013
# Copyright:   (c) National Instruments 2013
#-------------------------------------------------------------------------


def retrieve_installer_error(process_output=None):
    """Return a dictionary with installer error code information."""
    if not process_output:
        raise TypeError('output cannot be None!')

    return_code = process_output['return_code']
    stderr = process_output['stderr']
    stdout = process_output['stdout']

    installer_error = {}

    # Set a ganeric error in case one comes in that we don't know how to
    # handle.
    installer_error['code'] = 'UNKNOWN_ERROR'
    installer_error['value'] = return_code
    installer_error['description'] = 'sdtout: {0} \nstderr: {1}'.format(
        stdout, stderr)

    error_vals = [
        {'value': 0, 'code': 'ERROR_SUCCESS', 'description':
         'The action completed successfully.'},
        {'value': 13, 'code': 'ERROR_INVALID_DATA',
         'description': 'The data is invalid.'},
        {'value': 87, 'code': 'ERROR_INVALID_PARAMETER',
         'description': 'One of the parameters was invalid.'},
        {'value': 120, 'code': 'ERROR_CALL_NOT_IMPLEMENTED', 'description':
         'This value is returned when a custom action attempts to call a function that cannot be called from custom actions. The function returns the value ERROR_CALL_NOT_IMPLEMENTED.   Available beginning with Windows Installer version 3.0.'},
        {'value': 1259, 'code': 'ERROR_APPHELP_BLOCK', 'description':
         'If Windows Installer determines a product may be incompatible with the current operating system, it displays a dialog box informing the user and asking whether to try to install anyway. This error code is returned if the user chooses not to try the installation.'},
        {'value': 1601, 'code': 'ERROR_INSTALL_SERVICE_FAILURE', 'description':
         'The Windows Installer service could not be accessed. Contact your support personnel to verify that the Windows Installer service is properly registered.'},
        {'value': 1602, 'code': 'ERROR_INSTALL_USEREXIT',
         'description': 'The user cancels installation.'},
        {'value': 1603, 'code': 'ERROR_INSTALL_FAILURE', 'description':
         'A fatal error occurred during installation.'},
        {'value': 1604, 'code': 'ERROR_INSTALL_SUSPEND',
         'description': 'Installation suspended, incomplete.'},
        {'value': 1605, 'code': 'ERROR_UNKNOWN_PRODUCT', 'description':
         'This action is only valid for products that are currently installed.'},
        {'value': 1606, 'code': 'ERROR_UNKNOWN_FEATURE', 'description':
         'The feature identifier is not registered.'},
        {'value': 1607, 'code': 'ERROR_UNKNOWN_COMPONENT', 'description':
         'The component identifier is not registered.'},
        {'value': 1608, 'code': 'ERROR_UNKNOWN_PROPERTY',
         'description': 'This is an unknown property.'},
        {'value': 1609, 'code': 'ERROR_INVALID_HANDLE_STATE',
         'description': 'The handle is in an invalid state.'},
        {'value': 1610, 'code': 'ERROR_BAD_CONFIGURATION', 'description':
         'The configuration data for this product is corrupt. Contact your support personnel.'},
        {'value': 1611, 'code': 'ERROR_INDEX_ABSENT',
         'description': 'The component qualifier not present.'},
        {'value': 1612, 'code': 'ERROR_INSTALL_SOURCE_ABSENT', 'description':
         'The installation source for this product is not available. Verify that the source exists and that you can access it.'},
        {'value': 1613, 'code': 'ERROR_INSTALL_PACKAGE_VERSION', 'description':
         'This installation package cannot be installed by the Windows Installer service. You must install a Windows service pack that contains a newer version of the Windows Installer service.'},
        {'value': 1614, 'code': 'ERROR_PRODUCT_UNINSTALLED',
         'description': 'The product is uninstalled.'},
        {'value': 1615, 'code': 'ERROR_BAD_QUERY_SYNTAX', 'description':
         'The SQL query syntax is invalid or unsupported.'},
        {'value': 1616, 'code': 'ERROR_INVALID_FIELD',
         'description': 'The record field does not exist.'},
        {'value': 1618, 'code': 'ERROR_INSTALL_ALREADY_RUNNING', 'description':
         'Another installation is already in progress. Complete that installation before proceeding with this install.For information about the mutex, see_MSIExecute Mutex.'},
        {'value': 1619, 'code': 'ERROR_INSTALL_PACKAGE_OPEN_FAILED', 'description':
         'This installation package could not be opened. Verify that the package exists and is accessible, or contact the application vendor to verify that this is a valid Windows Installer package.'},
        {'value': 1620, 'code': 'ERROR_INSTALL_PACKAGE_INVALID', 'description':
         'This installation package could not be opened. Contact the application vendor to verify that this is a valid Windows Installer package.'},
        {'value': 1621, 'code': 'ERROR_INSTALL_UI_FAILURE', 'description':
         'There was an error starting the Windows Installer service user interface. Contact your support personnel.'},
        {'value': 1622, 'code': 'ERROR_INSTALL_LOG_FAILURE', 'description':
         'There was an error opening installation log file. Verify that the specified log file location exists and is writable.'},
        {'value': 1623, 'code': 'ERROR_INSTALL_LANGUAGE_UNSUPPORTED', 'description':
         'This language of this installation package is not supported by your system.'},
        {'value': 1624, 'code': 'ERROR_INSTALL_TRANSFORM_FAILURE', 'description':
         'There was an error applying transforms. Verify that the specified transform paths are valid.'},
        {'value': 1625, 'code': 'ERROR_INSTALL_PACKAGE_REJECTED', 'description':
         'This installation is forbidden by system policy. Contact your system administrator.'},
        {'value': 1626, 'code': 'ERROR_FUNCTION_NOT_CALLED',
         'description': 'The function could not be executed.'},
        {'value': 1627, 'code': 'ERROR_FUNCTION_FAILED',
         'description': 'The function failed during execution.'},
        {'value': 1628, 'code': 'ERROR_INVALID_TABLE', 'description':
         'An invalid or unknown table was specified.'},
        {'value': 1629, 'code': 'ERROR_DATATYPE_MISMATCH',
         'description': 'The data supplied is the wrong type.'},
        {'value': 1630, 'code': 'ERROR_UNSUPPORTED_TYPE',
         'description': 'Data of this type is not supported.'},
        {'value': 1631, 'code': 'ERROR_CREATE_FAILED', 'description':
         'The Windows Installer service failed to start. Contact your support personnel.'},
        {'value': 1632, 'code': 'ERROR_INSTALL_TEMP_UNWRITABLE', 'description':
         'The Temp folder is either full or inaccessible. Verify that the Temp folder exists and that you can write to it.'},
        {'value': 1633, 'code': 'ERROR_INSTALL_PLATFORM_UNSUPPORTED', 'description':
         'This installation package is not supported on this platform. Contact your application vendor.'},
        {'value': 1634, 'code': 'ERROR_INSTALL_NOTUSED',
         'description': 'Component is not used on this machine.'},
        {'value': 1635, 'code': 'ERROR_PATCH_PACKAGE_OPEN_FAILED', 'description':
         'This patch package could not be opened. Verify that the patch package exists and is accessible, or contact the application vendor to verify that this is a valid Windows Installer patch package.'},
        {'value': 1636, 'code': 'ERROR_PATCH_PACKAGE_INVALID', 'description':
         'This patch package could not be opened. Contact the application vendor to verify that this is a valid Windows Installer patch package.'},
        {'value': 1637, 'code': 'ERROR_PATCH_PACKAGE_UNSUPPORTED', 'description':
         'This patch package cannot be processed by the Windows Installer service. You must install a Windows service pack that contains a newer version of the Windows Installer service.'},
        {'value': 1638, 'code': 'ERROR_PRODUCT_VERSION', 'description':
         'Another version of this product is already installed. Installation of this version cannot continue. To configure or remove the existing version of this product, useAdd/Remove Programs in Control Panel.'},
        {'value': 1639, 'code': 'ERROR_INVALID_COMMAND_LINE', 'description':
         'Invalid command line argument. Consult the Windows Installer SDK for detailed command-line help.'},
        {'value': 1640, 'code': 'ERROR_INSTALL_REMOTE_DISALLOWED', 'description':
         'The current user is not permitted to perform installations from a client session of a server running the Terminal Server role service.'},
        {'value': 1641, 'code': 'ERROR_SUCCESS_REBOOT_INITIATED', 'description':
         'The installer has initiated a restart. This message is indicative of a success.'},
        {'value': 1642, 'code': 'ERROR_PATCH_TARGET_NOT_FOUND', 'description':
         'The installer cannot install the upgrade patch because the program being upgraded may be missing or the upgrade patch updates a different version of the program. Verify that the program to be upgraded exists on your computer and that you have the correct upgrade patch.'},
        {'value': 1643, 'code': 'ERROR_PATCH_PACKAGE_REJECTED', 'description':
         'The patch package is not permitted by system policy.'},
        {'value': 1644, 'code': 'ERROR_INSTALL_TRANSFORM_REJECTED', 'description':
         'One or more customizations are not permitted by system policy.'},
        {'value': 1645, 'code': 'ERROR_INSTALL_REMOTE_PROHIBITED', 'description':
         'Windows Installer does not permit installation from a Remote Desktop Connection.'},
        {'value': 1646, 'code': 'ERROR_PATCH_REMOVAL_UNSUPPORTED', 'description':
         'The patch package is not a removable patch package. Available beginning with Windows Installer version 3.0.'},
        {'value': 1647, 'code': 'ERROR_UNKNOWN_PATCH', 'description':
         'The patch is not applied to this product. Available beginning with Windows Installer version 3.0.'},
        {'value': 1648, 'code': 'ERROR_PATCH_NO_SEQUENCE', 'description':
         'No valid sequence could be found for the set of patches. Available beginning with Windows Installer version 3.0.'},
        {'value': 1649, 'code': 'ERROR_PATCH_REMOVAL_DISALLOWED', 'description':
         'Patch removal was disallowed by policy. Available beginning with Windows Installer version 3.0.'},
        {'value': 1650, 'code': 'ERROR_INVALID_PATCH_XML', 'description':
         'The XML patch data is invalid. Available beginning with Windows Installer version 3.0.'},
        {'value': 1651, 'code': 'ERROR_PATCH_MANAGED_ADVERTISED_PRODUCT', 'description':
         'Administrative user failed to apply patch for a per-user managed or a per-machine application that is in advertise state.  Available beginning with Windows Installer version 3.0.'},
        {'value': 1652, 'code': 'ERROR_INSTALL_SERVICE_SAFEBOOT', 'description':
         'Windows Installer is not accessible when the computer is in  Safe Mode.  Exit Safe Mode and try again or try usingSystem Restore to return your computer  to a previous state. Available beginning with Windows Installer version 4.0.'},
        {'value': 1653, 'code': 'ERROR_ROLLBACK_DISABLED', 'description':
         'Could not perform a  multiple-package transaction because rollback has been disabled.Multiple-Package Installations cannot run if rollback is disabled. Available beginning with Windows Installer version 4.5.'},
        {'value': 1654, 'code': 'ERROR_INSTALL_REJECTED', 'description':
         'The app that you are trying to run is not supported on this version of Windows.    A Windows Installer package, patch, or transform that has not been signed by Microsoft cannot be installed on an ARM computer.'},
        {'value': 3010, 'code': 'ERROR_SUCCESS_REBOOT_REQUIRED', 'description':
         'A restart is required to complete the install. This message is indicative of a success. This does not include installs where theForceReboot action is run.'}
    ]

    try:
       installer_error = next((item for item in error_vals if item['value'] == 
                          process_output['return_code']), installer_error)
    except GeneratorExit:
        pass

    return installer_error