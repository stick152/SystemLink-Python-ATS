"""
remote_share_operations.py

This module contains functions related to remote shares.
"""
__author__ = 'sedwards'

import os
import platform
import shutil
import stat
import sys
from pathlib import Path
from string import ascii_uppercase
from typing import Any, Callable, Dict, List, Optional, Tuple

import pytest

from syslinkats.framework.errors.error_handlers.process_errors import handle_process_errors
from syslinkats.framework.local.local_shell_commands import call_subprocess_popen
from syslinkats.framework.logging.auto_indent import AutoIndent
from syslinkats.framework.remote.remote_commands import run_aws_remote_command
from syslinkats.framework.validators.validate_args import validate_args_for_value

LOGGER = AutoIndent(sys.stdout)


# region Fixtures
@pytest.fixture(scope='package')
def remote_share_letter(get_ats_config_data: Callable[[], Dict[str, str]]) -> str:
    """Get a share letter for the worker instance.

    Args:
        get_ats_config_data (Callable[[], Dict[str, str]]): A callable to get the master data.

    Returns:
        str: A share letter string.
    """
    ats_config_data = get_ats_config_data()
    return get_remote_share_letter(ats_config_data)


@pytest.fixture(scope='package')
def remote_network_share_letter() -> Callable[[str, str, str], str]:
    """A fixture for returning a function which returns a network share letter."""
    def _remote_network_share_letter(
            network_drive_path: str,
            user_name: str,
            password: str) -> str:
        """Get a share letter for the remote drive to map.

        Args:
            network_drive_path (str): The path to the remote drive, etc. to map.
            user_name (str): The user name to use for login.
            password (str): The password to use for login.

        Returns:
            str: A share letter string.
        """
        return get_remote_network_share_letter(network_drive_path, user_name, password)
    return _remote_network_share_letter
# endregion


# region Public
def unmap_all_shares(share_ignores: List[str]) -> None:
    """A function for unmapping all shares before or after a test run."""
    for letter in ascii_uppercase:
        if letter in share_ignores:
            continue
        unmap_share(f'{letter}:')


def get_remote_share_letter(ats_config_data: Dict[str, Any]) -> str:
    """Get a share letter for the worker instance.

    Args:
        ats_config_data (Dict[str, Any]): The master data.

    Returns:
        str: A share letter string.
    """
    _share_letter, output = _map_remote_share(
        share_system_name=ats_config_data['syslink_worker_name'],
        share_user=ats_config_data['syslink_worker_system_username'],
        share_pass=ats_config_data['syslink_worker_system_password'],
        share_ignores=ats_config_data['share_ignores']
    )
    if output:
        if output['return_code'] == 0:
            LOGGER.write(output['stdout'])
        else:
            LOGGER.write(output['stderr'], 'error')
            raise Exception(output)
    return _share_letter


def get_remote_network_share_letter(network_drive_path: str, user_name: str, password: str) -> str:
    """Get a share letter for the worker instance.

    Args:
        network_drive_path (str): The path to the remote drive, etc. to map.
        user_name (str): The user name to use for login.
        password (str): The password to use for login.

    Returns:
        str: A share letter string.
    """
    _share_letter, output = _map_remote_share(
        share_system_name=network_drive_path,
        share_user=user_name,
        share_pass=password,
        is_remote_system_drive=False
    )
    if output:
        if output['return_code'] == 0:
            LOGGER.write(output['stdout'])
        else:
            LOGGER.write(output['stderr'], 'error')
            raise Exception(output)
    return _share_letter


def copy_files(ats_config_data: Dict[str, str],
               src_file_paths: Optional[List[str]],
               dest_file_paths: Optional[List[str]]) -> None:
    """Copy a list of files from source to destination paths.

    Args:
        ats_config_data (Dict[str, str]): A dict of ATS configuration data.
        src_file_paths (Optional[List[str]]): The paths to the source files.
        dest_file_paths (Optional[List[str]]): The paths to the destination files.

    Returns:
        None: None
    """
    validate_args_for_value(
        ats_config_data=ats_config_data,
        src_file_paths=src_file_paths,
        dest_file_paths=dest_file_paths
    )

    LOGGER.write('Copying files to target system.')
    for src_path, dest_path in zip(src_file_paths, dest_file_paths):
        try:
            Path(Path(dest_path).parent).mkdir(parents=True, exist_ok=True)
            shutil.copy(src_path, dest_path)
        except Exception as ex:  # pylint: disable=broad-except
            LOGGER.write(f'Error while copying {src_path} to {dest_path}: {ex}', 'exception')
            raise ex
    LOGGER.write('All files were copied successfully.')


def set_parent_folder_sharing(ats_config_data: Dict[str, str], path_chain: str,
                              parent_name: str) -> None:
    """Set a parent folder's sharing settings.

    Args:
        ats_config_data (Dict[str, str]): A dict of ATS configuration data.
        path_chain (str): A path containing the parent_name property.  The path is walked until
        parent_name is found and that parent folder has its sharing settings modified.
        parent_name (str): The name of the parent directory which needs to get its sharing
        settings set.

    Returns:
        None: None
    """
    for parent_dir in Path(path_chain).parents:
        if Path(parent_dir).exists() and Path(parent_dir).name is parent_name:
            remote_commands = [
                f'New-SmbShare -Name {parent_name} -Description "{parent_name} folder" -Path '
                f'"{parent_dir}"',
                f'Grant-SmbShareAccess -Name {parent_name} '
                f'-AccountName {ats_config_data["syslink_worker_system_username"]} '
                f'-AccessRight Full -Force'
            ]
            for remote_command in remote_commands:
                try:
                    run_aws_remote_command(
                        region_name=ats_config_data['region_name'],
                        target_public_dns_names=[ats_config_data['syslink_worker_name']],
                        instance_ids=[ats_config_data['syslink_worker_instance_id']],
                        remote_command=remote_command
                    )
                except Exception as ex:  # pylint: disable=broad-except
                    if 'already been shared' in str(ex):
                        pass


def set_parent_folder_full_permissions(
        ats_config_data: Dict[str, str], path_chain: str, parent_name: str) -> None:
    """Set parent folder--as well as children and files--permissions for Authenticated Users.

    Args:
        ats_config_data (Dict[str, str]): A dict of ATS configuration data.
        path_chain (str): A path containing the parent_name property.  The path is walked until
        parent_name is found and that parent folder has its permissions modified.
        parent_name (str): The name of the parent directory which needs to get its permissions set.

    Returns:
        None: None
    """
    for parent_dir in Path(path_chain).parents:
        if Path(parent_dir).exists() and Path(parent_dir).name is parent_name:
            remote_command = (
                f'$Acl = Get-Acl "{parent_dir}";'
                f'$Ar = New-Object system.security.accesscontrol.filesystemaccessrule'
                f'("Authenticated Users", '
                '"FullControl", "ContainerInherit, ObjectInherit", "None", "Allow"); '
                '$Acl.SetAccessRule($Ar); '
                f'Set-Acl "{parent_dir}" $Acl;'
            )
            try:
                run_aws_remote_command(
                    region_name=ats_config_data['region_name'],
                    target_public_dns_names=[ats_config_data['syslink_worker_name']],
                    instance_ids=[ats_config_data['syslink_worker_instance_id']],
                    remote_command=remote_command
                )
            except Exception as ex:
                LOGGER.write(f'An error occurred: {str(ex)}', 'exception')
                raise ex


def copy_new_folders(src_folder_paths: List[str] = None, dest_folder_paths: List[str] = None,
                     copy_ignores: Optional[List[str]] = None,
                     retry_count: int = 3) -> None:
    """Copy over new versions of the LV ATS folders.

    Args:
        src_folder_paths (list): List of local source folders to copy.
        dest_folder_paths (list): List of destination folder paths.
        copy_ignores (Optional[List[str]]): Optional list of str file extensions to ignore
        during the file copy.
        retry_count (int): The number of times to retry copying files.

    Raises:
        Exception: Any and all exceptions.
    """
    validate_args_for_value(src_folder_paths=src_folder_paths, dest_folder_paths=dest_folder_paths)
    if not copy_ignores:
        copy_ignores: List[str] = []

    LOGGER.write('Copying folders to target system.')
    for src_path, dest_path in zip(src_folder_paths, dest_folder_paths):
        for try_count in range(retry_count):
            try:
                copy_tree(src_path, dest_path, ignore=shutil.ignore_patterns(*copy_ignores))
                LOGGER.write(f'Copy to {dest_path} was successful.')
                break
            except Exception as ex:
                if try_count < retry_count - 1:
                    LOGGER.write(
                        f'Error while copying to {dest_path}: {ex}.  Retrying...',
                        log_method='warning'
                    )
                else:
                    LOGGER.write(
                        f'Error while copying to {dest_path}: {ex}', log_method='exception'
                    )
                    raise ex
    LOGGER.write('All folders were copied successfully.')


def copy_tree(src, dst, symlinks=False, ignore=None):
    """This is a fixed version of shutil.copytree.

    When retrying copies, the test for the existing dir keeps it from choking when the directory
    is already there.
    """
    names = os.listdir(src)
    if ignore is not None:
        ignored_names = ignore(src, names)
    else:
        ignored_names = set()

    if not os.path.isdir(dst):
        os.makedirs(dst)
    errors = []
    for name in names:
        if name in ignored_names:
            continue
        src_name = os.path.join(src, name)
        dst_name = os.path.join(dst, name)
        try:
            if symlinks and os.path.islink(src_name):
                link_to = os.readlink(src_name)
                os.symlink(link_to, dst_name)
            elif os.path.isdir(src_name):
                copy_tree(src_name, dst_name, symlinks, ignore)
            else:
                # Will raise a SpecialFileError for unsupported file types
                shutil.copy2(src_name, dst_name)
        # catch the Error from the recursive copytree so that we can
        # continue with other files
        except shutil.Error as err:
            errors.extend(err.args[0])
        except EnvironmentError as why:
            errors.append((src_name, dst_name, str(why)))
    try:
        shutil.copystat(src, dst)
    except OSError as why:
        if WindowsError is not None and isinstance(why, WindowsError):
            # Copying file access times may fail on Windows
            pass
        else:
            errors.extend((src, dst, str(why)))
    if errors:
        raise shutil.Error(errors)


def remove_files(file_paths: List[str] = None) -> None:
    """Remove all files in the list of file paths.

    Args:
        file_paths (List[str]): A list of file paths to be deleted.

    Returns:
        None: None
    """
    if not file_paths:
        LOGGER.write('file_paths was None or empty, so not removing files.')
        return

    LOGGER.write('Removing files from the target system.')
    for file_path in file_paths:
        if Path(file_path).exists():
            try:
                os.remove(file_path)
            except Exception as ex:
                LOGGER.write(f'Failed to remove {file_path} with error: {str(ex)}')
                raise ex
            LOGGER.write(f'Removal of {file_path} was successful.')
    LOGGER.write('All files were successfully removed.')


def remove_old_folders(folder_paths: List[str] = None) -> None:
    """Remove old versions of the LV ATS folders.

    Args:
        folder_paths (Optional[List[str]]): The list of folders to remove.

    Raises:
        Exception: Any and all exceptions.
    """
    if not folder_paths:
        LOGGER.write('folder_paths was None or empty, so not removing folders.')
        return

    LOGGER.write('Removing folders from target system.')
    for folder in folder_paths:
        if Path(folder).exists():
            try:
                shutil.rmtree(folder, False, onerror=_on_error)
            except Exception as ex:
                LOGGER.write(str(ex), 'exception')
                raise ex
            LOGGER.write(f'Removal of {folder} was successful.')
    LOGGER.write('All folders were successfully removed.')


def unmap_share(drive_letter: str = None):
    """Unmaps an existing share.

    Args:
        drive_letter (str): The share's drive letter value (i.e., z:).
    """
    validate_args_for_value(share_letter=drive_letter)
    output = _unmap_remote_share(drive_letter)
    if output:
        if output['return_code'] == 0:
            LOGGER.write(output['stdout'])
        elif output['return_code'] == 2:
            LOGGER.write('The network share was not found.  Continuing...')
        else:
            LOGGER.write(output['stderr'], 'error')
            raise Exception(output)
# endregion


# region Private
def _build_map_share_command(share_letter: str = None, share_location: str = None,
                             share_user: str = None, share_pass: str = None,
                             map_args: str = None) -> str:
    """Build a net use map share command.

    Args:
        share_letter (Optional[str]): Letter to map to (if any).
        share_location (Optional[str]): Network location of the share.
        share_user (Optional[str]): Username for the share.
        share_pass (Optional[str]): Password for the share.
        map_args (Optional[str]): Arguments for net use.

    Returns:
        str: A command string for mapping a remote share.

    Raises:
        TypeError
    """
    validate_args_for_value(share_letter=share_letter, share_location=share_location,
                            share_user=share_user, share_pass=share_pass)

    map_cmd = rf'net use /persistent:no {share_letter} {share_location} /user:{share_user} ' \
              f'{share_pass} {map_args or ""}'

    return map_cmd


def _build_unmap_share_command(drive_letter: str = None) -> str:
    """Build a net use unmap command.

    Args:
        drive_letter (Optional[str]): Letter to unmap.

    Returns:
        str: A command string.
    """
    validate_args_for_value(drive_letter=drive_letter)
    return rf'net use {drive_letter} /delete'


def _check_if_share_already_mapped(share_name: str = None) -> Optional[str]:
    """Check to see if a share has been mapped.

    If a share has already been mapped, return the share drive letter.
    Otherwise, return None.

    Args:
        share_name (Optional[str]): The share name to look for in the drive mappings.

    Returns:
        Optional[str, None]: Either a drive letter (i.e., 'Z:') or None.
    """
    validate_args_for_value(share_name=share_name)

    LOGGER.write('Checking for drive mapping...')
    drive_mapping = _get_current_drive_mapping()

    drive_mapping = drive_mapping.splitlines()
    tmp_share_name = share_name.lower().strip()
    tmp_share_name = tmp_share_name.replace('"', '')
    for line in drive_mapping:
        line = line.lower().strip()
        if tmp_share_name not in line:
            continue

        share_name_index = line.find(tmp_share_name)
        if share_name_index > 0:
            colon_index = line.find(':')
            if colon_index > 0:
                drive_letter = line[colon_index - 1:colon_index + 1]
                return drive_letter

    return None


def _find_available_share_drive_letter(share_ignores: List[str] = None) -> str:
    """Find an available drive letter for a share.

    This function iterates backwards through the ASCII uppercase letters trying
    and checks them against the current net use drive mappings.  Once it finds
    an available drive letter, it passes that back to the caller.  If an
    available drive letter is not found, a RuntimeError is raised.

    Args:
        share_ignores (List[str]): A list of share letters to ignore.

    Returns:
        str: An available drive letter (i.e., 'Z:') for a network share.

    Raises:
        RuntimeError
    """
    LOGGER.write('Looking for an available share letter.')
    drive_mapping = _get_current_drive_mapping()

    # Iterate backwards through letters to see if they've already been used.
    available_letter = ''
    for letter in reversed(ascii_uppercase):
        if letter in share_ignores:
            continue

        letter = f'{letter}:'
        if letter not in drive_mapping:
            available_letter = letter
            break

    if not available_letter:
        raise RuntimeError('Unable to find a free drive letter to map to!')

    return available_letter


def _get_current_drive_mapping() -> str:
    """Gets the output from net use as a string.

    Returns:
        str: Output from net use.
    """
    LOGGER.write('Getting the current drive mapping.')
    output = call_subprocess_popen('net use')
    handle_process_errors('get_current_drive_mapping', output)

    current_mapping = output['stdout']

    return current_mapping


def _map_remote_share(share_system_name: str = None, share_user: str = None,
                      share_pass: str = None, share_location_format_str: str = None,
                      share_ignores: List[str] = None,
                      is_remote_system_drive: bool = True) \
        -> Tuple[str, Optional[Dict[str, Any]]]:
    """Map a remote share directory.

    Args:
        share_system_name (Optional[str]): The share letter or name to check for.
        share_user (Optional[str]): The user name of the remote account with permissions for
        mapping a share.
        share_pass (Optional[str]): The password for the specified user account.
        share_location_format_str (Optional[str]): An optional format string that specifies the
        way that the drive / folder was configured in the share settings on the remote system.
        (i.e., '\\\\{0}\\c' or '\\\\{0}\\my_share', etc.).
        share_ignores (List[str]): A list of share letters to ignore.
        is_remote_system_drive (bool): Determines the method of share location formatting.

    Returns:
        Tuple[str, Optional[Dict[str, Any]]: Share letter and a process instance for
        validation (etc.)

    Raises:
        TypeError
    """
    validate_args_for_value(
        share_system_name=share_system_name, share_user=share_user, share_pass=share_pass)

    if 'localhost' in share_system_name or platform.node() in share_system_name:
        # If the user is using their local system for testing, then default the share letter to
        # their 'c' drive.
        return 'C:', None

    if not share_ignores:
        share_ignores = []

    if not share_location_format_str:
        if is_remote_system_drive:
            share_location_format_str = r'\\{0}\c'
        else:
            share_location_format_str = '{}'

    share_letter = _check_if_share_already_mapped(
        share_name=share_system_name
    )
    process = None

    if not share_letter:
        # Map the share to a drive.
        share_letter = _find_available_share_drive_letter(share_ignores)
        map_share_command = _build_map_share_command(
            share_letter=share_letter,
            share_location=share_location_format_str.format(share_system_name),
            share_user=share_user,
            share_pass=share_pass
        )
        # Store the process var in case we want to do any validation later.
        process = call_subprocess_popen(
            command_to_run=map_share_command
        )

    return share_letter, process


def _on_error(func: Callable, path: str, exc_info: Exception):
    """
      Error handler for ``shutil.rmtree``.

      If the error is due to an access error (read only file)
      it attempts to add write permission and then retries.

      If the error is for another reason it re-raises the error.

      Usage : ``shutil.rmtree(path, onerror=onerror)``

    Args:
        func (Callable): The function which failed and must be re-run.
        path (str): The path to the file to set permissions for.
        exc_info (Exception): An exception to re-raise.

    Raises:
        Exception: The passed-in exception to re-raise (if needed).
    """
    if not os.access(path, os.W_OK):
        # Is the error an access error ?
        os.chmod(path, stat.S_IWUSR)
        func(path)
    else:
        LOGGER.write(
            f'An exception occurred while deleting old ATS folders: {exc_info}',
            log_method='exception'
        )
        raise exc_info


def _unmap_remote_share(drive_letter: str = None) -> Dict[str, Any]:
    validate_args_for_value(drive_letter=drive_letter)
    unmap_share_command = _build_unmap_share_command(drive_letter)

    # Store the process var in case we want to do any validation later.
    process = call_subprocess_popen(
        command_to_run=unmap_share_command
    )

    return process
# endregion
