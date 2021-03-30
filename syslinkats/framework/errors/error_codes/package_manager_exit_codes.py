#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
package_manager_exit_codes.py
"""
import time
import re
from textwrap import TextWrapper

__author__ = 'sedwards'


def retrieve_pkgmgr_error(process_output=None, args_list=None):
    """Return a dictionary with package manager error code information.

    Args:
        process_output:
        args_list:

    Returns:

    """
    if not process_output:
        raise TypeError('output cannot be None!')
    if args_list and type(args_list) != list:
        raise TypeError('args_list must be a list or None.')

    return_code = process_output['return_code']
    stderr = process_output['stderr']
    stdout = process_output['stdout']

    # Set a generic error in case one comes in that we don't know how to
    # handle.
    installer_error = dict(
        code='UNKNOWN_ERROR',
        value=return_code,
        description='stdout: {0} \nstderr: {1}'.format(stdout, stderr)
    )

    error_values = [
        {
            'value': 0,
            'code': 'Success',
            'description': "No errors occurred"
        },
        {
            'value': -125000,
            'code': 'ClientInsufficientResources',
            'description': "Client produced an error due to a lack of "
                           "resources."
        },
        {
            'value': -125001,
            'code': 'ServerInsufficientResources',
            'description': "Server produced an error due to a lack of "
                           "resources."
        },
        {
            'value': -125002,
            'code': 'InvalidRequestHandle',
            'description': "Invalid request handle."
        },
        {
            'value': -125003,
            'code': 'InvalidRepositoryName',
            'description': "The feed name '{0}' is invalid. Be sure "
                           "the feed name begins with an alphabetical "
                           "character and only contains alphanumeric "
                           "characters, spaces, underscores, and "
                           "hyphens."
        },
        {
            'value': -125004,
            'code': 'InvalidRepositoryType',
            'description': "The feed type '{0}' is invalid or is no "
                           "longer supported."
        },
        {
            'value': -125005,
            'code': 'RepositoryAlreadyExistsAtUri',
            'description': "A feed already exists at the specified URI "
                           "'{0}'. Choose a different location for the "
                           "feed."
        },
        {
            'value': -125006,
            'code': 'RepositoryNameAlreadyTaken',
            'description': "The feed name '{0}' is already in use.  "
                           "Choose a different name for the feed."
        },
        {
            'value': -125007,
            'code': 'RepositoryUriAlreadyTaken',
            'description': "The feed URI '{0}' is already in use.  "
                           "Choose a different URI for the feed."
        },
        {
            'value': -125008,
            'code': 'InvalidRepositoryUri',
            'description': "The feed URI '{0}' is invalid."
        },
        {
            'value': -125009,
            'code': 'MissingRepositoryType',
            'description': "Corrupt feed configuration. Missing a "
                           "required feed type."
        },
        {
            'value': -125010,
            'code': 'UnsupportedRepositoryType',
            'description': "The feed type is not supported."
        },
        {
            'value': -125011,
            'code': 'RepoUriNotAvailable',
            'description': "The feed URL you are trying to reach is "
                           "not available. Check to make sure the URL "
                           "is correct, and that the server is running "
                           "and configured to accept remote requests "
                           "({0})."
        },
        {
            'value': -125012,
            'code': 'CouldNotOpenRepository',
            'description': "Could not open feed file."
        },
        {
            'value': -125013,
            'code': 'Md5ChecksumFailed',
            'description': "Error in {0} MD5 checksum. {1} is "
                           "different from {2}."
        },
        {
            'value': -125014,
            'code': 'UnknownErrorOccuredInCallback',
            'description': "An unknown error occured during a user "
                           "callback."
        },
        {
            'value': -125015,
            'code': 'PregexInvalidPattern',
            'description': "Invalid Regex Pattern."
        },
        {
            'value': -125016,
            'code': 'InvalidVersionString',
            'description': "Invalid version string."
        },
        {
            'value': -125017,
            'code': 'InvalidConfigurationAttribute',
            'description': "The Configuration Attribute is invalid or "
                           "does not exist."
        },
        {
            'value': -125018,
            'code': 'InvalidArchitectureProcessor',
            'description': "Architecture string specified an invalid "
                           "or unsupported processor string."
        },
        {
            'value': -125019,
            'code': 'InvalidArchitectureOs',
            'description': "Architecture string specified an invalid "
                           "or unsupported operating system."
        },
        {
            'value': -125020,
            'code': 'NoPackagesToInstall',
            'description': "No package name(s) specified for "
                           "installation. Please specify one or more "
                           "packages to install."
        },
        {
            'value': -125021,
            'code': 'NoPackagesToRemove',
            'description': "No package name(s) specified for removal.  "
                           "Please specify one or more packages to "
                           "remove."
        },
        {
            'value': -125022,
            'code': 'PackageDoesNotExist',
            'description': "The specified package name '{0}' is "
                           "unknown or does not exist."
        },
        {
            'value': -125023,
            'code': 'InvalidPkgAttributeReturnType',
            'description': "The requested package attribute does not "
                           "match the requested return type."
        },
        {
            'value': -125024,
            'code': 'FailedToOpenFile',
            'description': "Cannot open file '{0}'({1})."
        },
        {
            'value': -125025,
            'code': 'InvalidPath',
            'description': "The specified path '{0}' is invalid. {1}"
        },
        {
            'value': -125026,
            'code': 'InvalidArchive',
            'description': "An error occurred while trying to extract "
                           "the contents of the file archive."
        },
        {
            'value': -125027,
            'code': 'InvalidIpkPackage',
            'description': "The ipk/nipkg package '{0}' is invalid."
        },
        {
            'value': -125028,
            'code': 'FailedToCopyFile',
            'description': "Cannot copy file"
        },
        {
            'value': -125029,
            'code': 'UserCancelledRequest',
            'description': "Request could not be completed because the "
                           "user cancelled the request."
        },
        {
            'value': -125030,
            'code': 'CouldNotCreateRepoCacheDirectory',
            'description': "An error occurred while trying to create "
                           "the feed cache directory: '{0}'."
        },
        {
            'value': -125031,
            'code': 'CouldNotDownloadRepository',
            'description': "An error occurred while trying to download "
                           "the feed: {0}"
        },
        {
            'value': -125032,
            'code': 'InvalidPackageStructure',
            'description': "Invalid package structure. The package is "
                           "missing mandatory files or directories."
        },
        {
            'value': -125033,
            'code': 'FailedCreatingTempDir',
            'description': "An error ocurred while trying to create a "
                           "temp directory path."
        },
        {
            'value': -125034,
            'code': 'InvalidSystemArchitecture',
            'description': "Invalid or unsupported system architecture "
                           "specified in the configuration."
        },
        {
            'value': -125035,
            'code': 'AttributeValueNotValidBoolean',
            'description': "Attribute '{0}' has a value '{1}' that is "
                           "not a valid boolean."
        },
        {
            'value': -125036,
            'code': 'AttributeValueNotValidNumber',
            'description': "Attribute '{0}' has a value '{1}' that is "
                           "not a valid number."
        },
        {
            'value': -125037,
            'code': 'AttributeValueNotValidString',
            'description': "Attribute '{0}' has a value '{1}' that is "
                           "not a valid string."
        },
        {
            'value': -125038,
            'code': 'RequiredAttributeValueCannotBeEmpty',
            'description': "Required attribute '{0}' value cannot be "
                           "empty."
        },
        {
            'value': -125039,
            'code': 'MissingAttributeColonSeparator',
            'description': "Missing attribute colon separator on line "
                           "'{0}'."
        },
        {
            'value': -125040,
            'code': 'InvalidPackageAttributeValue',
            'description': "Package attribute '{0}' has a value '{1}' "
                           "that is invalid or empty."
        },
        {
            'value': -125041,
            'code': 'EmptyPackageAttributeName',
            'description': "Package attribute name cannot be empty."
        },
        {
            'value': -125042,
            'code': 'InvalidPackageNameAttribute',
            'description': "Package name '{0}' is invalid. Be sure the "
                           "package name contains no whitespace "
                           "characters and begins with an alphabetical "
                           "character."
        },
        {
            'value': -125043,
            'code': 'PackageAttributeNameDoesNotExist',
            'description': "Attribute name '{0}' does not exist."
        },
        {
            'value': -125044,
            'code': 'RepositoryNotLoaded',
            'description': "A feed must be loaded in order to perform "
                           "this operation."
        },
        {
            'value': -125045,
            'code': 'EmptyConfigAttributeName',
            'description': "Configuration attribute name cannot be "
                           "empty."
        },
        {
            'value': -125046,
            'code': 'InvalidConfigAttribute',
            'description': "Configuration attribute name '{0}' is "
                           "invalid. Be sure the configuration "
                           "attribute names contain no whitespace "
                           "characters and begins with an alphabetical "
                           "character."
        },
        {
            'value': -125047,
            'code': 'GenericListAvailablePackagesError',
            'description': "An error occurred when listing the "
                           "available package."
        },
        {
            'value': -125048,
            'code': 'CannotLoadRepository',
            'description': "The feed file located at '{0}' contains an "
                           "invalid entry on line {1}."
        },
        {
            'value': -125049,
            'code': 'NoWriteAccess',
            'description': "Access denied. Make sure you have "
                           "permission to write to the destination "
                           "file or folder '{0}'."
        },
        {
            'value': -125050,
            'code': 'CouldNotDownloadPackage',
            'description': "An error occurred while trying to download "
                           "the package '{0}' from URI '{1}'."
        },
        {
            'value': -125051,
            'code': 'CouldNotCreatePackageCacheDirectory',
            'description': "An error occurred while trying to create "
                           "the package cache directory."
        },
        {
            'value': -125052,
            'code': 'PackageSignatureValidationFailed',
            'description': "Package signature validation failed. The "
                           "package may be corrupted."
        },
        {
            'value': -125053,
            'code': 'IncorrectServerResponse',
            'description': "The server returned an unexpected status "
                           "code ({0}) while trying to access URL "
                           "'{1}'. Check your Internet connection and "
                           "try again. If this error persists, the "
                           "server may be down."
        },
        {
            'value': -125054,
            'code': 'CannotAcquireAdminLock',
            'description': "Unable to acquire an administrative lock.  "
                           "Is another application modifying the "
                           "system?"
        },
        {
            'value': -125055,
            'code': 'CompareVersionsInvalidOperator',
            'description': "Invalid comparison operator."
        },
        {
            'value': -125056,
            'code': 'NoPackagesToDownload',
            'description': "No package name(s) specified for download.  "
                           "Please specify one or more packages to "
                           "download."
        },
        {
            'value': -125057,
            'code': 'PackMissingRequiredAttributeInControlFile',
            'description': "Cannot create the specified package.  "
                           "Missing a required attribute key-value "
                           "pair '{0}: {1}' in the control file."
        },
        {
            'value': -125058,
            'code': 'NoPackageSpecified',
            'description': "No package name(s) specified. Please "
                           "specify a package."
        },
        {
            'value': -125059,
            'code': 'EmptyRepositoryDirectory',
            'description': "The feed directory cannot be empty."
        },
        {
            'value': -125060,
            'code': 'InvalidRepositoryDirectory',
            'description': "Invalid feed directory specified."
        },
        {
            'value': -125061,
            'code': 'PathToFileListCannotBeEmpty',
            'description': "No path to a filelist specified. Please "
                           "specify a path to a file with a .filelist "
                           "extension containing paths to packages."
        },
        {
            'value': -125062,
            'code': 'PackageDirectoryCannotBeEmpty',
            'description': "No package directory specified. Please "
                           "specify a path containing packages."
        },
        {
            'value': -125063,
            'code': 'PackagePathCannotBeEmpty',
            'description': "No path to package specified. Please "
                           "specify one or more paths to packages."
        },
        {
            'value': -125064,
            'code': 'CouldNotOpenFileList',
            'description': "Could not open filelist file containing a "
                           "list of packages to include in the feed."
        },
        {
            'value': -125065,
            'code': 'ConvertionToRelativePathFailed',
            'description': "Cannot convert path '{0}' to a relative "
                           "path from '{1}'."
        },
        {
            'value': -125066,
            'code': 'ConvertionToAbsoluteUrlFailed',
            'description': "The relative url cannot be represented as "
                           "an absolute-path url."
        },
        {
            'value': -125067,
            'code': 'UnsolvableTransaction',
            'description': "The requested transaction cannot be "
                           "solved, {0} problems were found."
        },
        {
            'value': -125068,
            'code': 'EulasNotAccepted',
            'description': "The required license agreements were not "
                           "accepted. Please accept all license "
                           "agreements for the packages being "
                           "installed by passing the '--accept-eulas' "
                           "flag."
        },
        {
            'value': -125069,
            'code': 'SettingNotConfigurable',
            'description': "The specified setting is not configurable "
                           "({0})"
        },
        {
            'value': -125070,
            'code': 'SettingsDirectoryError',
            'description': "An error occurred reading from the "
                           "settings directory ({0})"
        },
        {
            'value': -125071,
            'code': 'RebootNeeded',
            'description': "A system reboot is needed to complete the "
                           "transaction."
        },
        {
            'value': -125072,
            'code': 'EmptyRepositoryName',
            'description': "No feed name(s) specified. Please specify "
                           "a feed name."
        },
        {
            'value': -125073,
            'code': 'EmptyRepositoryUri',
            'description': "No feed URI(s) specified. Please specify a "
                           "feed URI."
        },
        {
            'value': -125074,
            'code': 'RequiredRepositoryUri',
            'description': "The feed '{0}' cannot specify an empty "
                           "URI. Please specify a feed URI."
        },
        {
            'value': -125075,
            'code': 'EulaDisplayPackagePayloadDirMissing',
            'description': "EULA information could not be processed "
                           "for EULA display package '{0}'. The EULA "
                           "package payload directory does not exist: "
                           "'{1}'."
        },
        {
            'value': -125076,
            'code': 'EulaDisplayPackagePayloadDirIterationError',
            'description': "EULA information could not be processed "
                           "for EULA display package '{0}'. Could not "
                           "iterate the contents of the EULA package "
                           "payload directory '{1}'. Error details: "
                           "{2}"
        },
        {
            'value': -125077,
            'code': 'EulaDisplayPackageMissingRtfFile',
            'description': "EULA information could not be processed "
                           "for EULA display package '{0}'. Did not "
                           "find a '.rtf' file in the payload of the "
                           "package: '{1}'."
        },
        {
            'value': -125078,
            'code': 'AttributeValueNotValidUnsignedLongLong',
            'description': "Attribute '{0}' has a value '{1}' that is "
                           "not a valid unsigned number."
        },
        {
            'value': -125079,
            'code': 'RepositoryDoesNotExist',
            'description': "The feed '{0}' does not exist."
        },
        {
            'value': -125080,
            'code': 'EulaDisplayPackagesNotFound',
            'description': "One or more license agreement packages "
                           "were not found in any feeds: {0}."
        },
        {
            'value': -125081,
            'code': 'CompatibilityVersionError',
            'description': "This version of Package Manager is too "
                           "outdated to install package '{0}'. You "
                           "must first upgrade to a newer version of "
                           "Package Manager, then install this package "
                           "again. (Package Manager compatibility "
                           "value '{1}' is less than the package "
                           "compatibility value of '{2}')"
        },
        {
            'value': -125082,
            'code': 'GetInstalledPackagesPluginError',
            'description': "An error occurred while getting the list "
                           "of installed packages."
        },
        {
            'value': -125083,
            'code': 'PackageOperationPluginInstallError',
            'description': "An error occurred while installing the "
                           "package '{0} ({1})'."
        },
        {
            'value': -125084,
            'code': 'PackageOperationPluginRemoveError',
            'description': "An error occurred while removing the "
                           "package '{0} ({1})'."
        },
        {
            'value': -125085,
            'code': 'PackageOperationPluginReinstallError',
            'description': "An error occurred while reinstalling the "
                           "package '{0} ({1})'."
        },
        {
            'value': -125086,
            'code': 'PackageOperationPluginUpgradeError',
            'description': "An error occurred while upgrading from "
                           "package '{0} ({1})' to '{2} ({3})'."
        },
        {
            'value': -125087,
            'code': 'PackageOperationPluginDowngradeError',
            'description': "An error occurred while downgrading from "
                           "package '{0} ({1})' to '{2} ({3})'."
        },
        {
            'value': -125088,
            'code': 'ForEachInstalledPackagePluginError',
            'description': "An error occurred while processing the "
                           "installed packages."
        },
        {
            'value': -125089,
            'code': 'CreatePackagePluginError',
            'description': "A plugin returned one or more errors while "
                           "creating the package at '{0}."
        },
        {
            'value': -125090,
            'code': 'BeginTransactionPluginError',
            'description': "A plugin returned one or more errors at "
                           "the beginning of the transaction."
        },
        {
            'value': -125091,
            'code': 'EndTransactionPluginError',
            'description': "A plugin returned one or more errors at "
                           "the end of the transaction."
        },
        {
            'value': -125092,
            'code': 'ProxyAuthenticationRequired',
            'description': "Proxy credentials are required for this "
                           "request."
        },
        {
            'value': -125093,
            'code': 'InvalidPathEmpty',
            'description': "The specified path is empty."
        },
        {
            'value': -125094,
            'code': 'FeedUpdateFailed',
            'description': "Failed to update feed '{0}'."
        },
        {
            'value': -125095,
            'code': 'FeedUpdateAllFailed',
            'description': "Failed to update all feeds."
        },
        {
            'value': -125200,
            'code': 'InternalBadArgument',
            'description': "An error occurred due to a bad input "
                           "parameter."
        },
        {
            'value': -125201,
            'code': 'InternalNotImplemented',
            'description': "The function or method is not implemented."
        },
        {
            'value': -125202,
            'code': 'InternalUndefinedError',
            'description': "An unknown error occurred."
        },
        {
            'value': -125203,
            'code': 'InternalMissingAttrNameInNameValueMap',
            'description': "A required attribute name was missing from "
                           "a key-value pair map."
        },
        {
            'value': -125204,
            'code': 'InternalArrayMustBeEmpty',
            'description': "An error occurred due an attempt to add "
                           "into an array multiple times."
        },
        {
            'value': -125205,
            'code': 'InternalFailedToFreeArchive',
            'description': "Cannot free archive when using libarchive."
        },
        {
            'value': -125206,
            'code': 'InternalFailedToReadFile',
            'description': "Cannot read the file: '{0}'."
        },
        {
            'value': -125207,
            'code': 'InternalNotConnectedToRepository',
            'description': "Cannot perform the operation on a "
                           "disconnected feed."
        },
        {
            'value': -125208,
            'code': 'InternalInvalidObjectState',
            'description': "Cannot perform the operation because a "
                           "critical object is in an invalid state."
        },
        {
            'value': -125209,
            'code': 'InternalFailedGettingConfiguration',
            'description': "Cannot get a configuration from the data "
                           "storage."
        },
        {
            'value': -125210,
            'code': 'InternalFailedSettingConfiguration',
            'description': "Cannot set a configuration in the data "
                           "storage."
        },
        {
            'value': -125211,
            'code': 'InternalMissingInstalledSoftwareCfg',
            'description': "Cannot load the installed software feed."
                           "Be sure to include the installed software "
                           "feed in the configuration file."
        },
        {
            'value': -125212,
            'code': 'InternalInvalidPackageAttributeId',
            'description': "Invalid package attribute id."
        },
        {
            'value': -125213,
            'code': 'InternalUnexpectedLibArchiveError',
            'description': "An unexpected error occurred while calling "
                           "libarchive '{0}'."
        },
        {
            'value': -125214,
            'code': 'InternalInvalidPluginName',
            'description': "The specified plugin is invalid or does "
                           "not exist."
        },
        {
            'value': -125215,
            'code': 'InternalFailedCreatingCurlHandle',
            'description': "An error ocurred while trying to create a "
                           "CURL handle."
        },
        {
            'value': -125216,
            'code': 'InternalUndefinedNipkgAttribute',
            'description': "An error ocurred when performing an "
                           "operation on an undefined internal "
                           "attribute."
        },
        {
            'value': -125217,
            'code': 'InternalBadProblemRuleType',
            'description': "An error occurred due to a bad solver "
                           "problem rule."
        },
        {
            'value': -125218,
            'code': 'InternalTransactionNotAvailable',
            'description': "The requested operation cannot be "
                           "performed because no transaction is in "
                           "progress."
        },
        {
            'value': -125219,
            'code': 'InternalCannotConvertTransactionOptionValue',
            'description': "Cannot convert the transaction option "
                           "value to the specified data type."
        },
        {
            'value': -125220,
            'code': 'InternalCannotGetSettingsDirectory',
            'description': "Cannot get the path to the settings "
                           "directory."
        },
        {
            'value': -125221,
            'code': 'InternalAddRepositoryExists',
            'description': "The feed to add already exists."
        },
        {
            'value': -125222,
            'code': 'InternalGettingUnfilledEulaInfoStruct',
            'description': "Cannot get EULA info because the struct "
                           "has not been filled."
        },
        {
            'value': -125223,
            'code': 'InternalSettingFilledEulaInfoStruct',
            'description': "Cannot set EULA info because the struct "
                           "has already been filled."
        },
        {
            'value': -125227,
            'code': 'FailedToWriteToConfiguration',
            'description': "Unable to write to the configuration at: "
                           "'{0};. Do you have access to this "
                           "location?"
        },
        {
            'value': -125228,
            'code': 'FailedToOpenFeed',
            'description': "One or more errors occurred while trying "
                           "to open the feed named '{0}' at URI '{1}'."
        },
        {
            'value': -125401,
            'code': 'PluginUnknownError',
            'description': "An unknown error has occurred in the "
                           "plugin ({0})."
        },
        {
            'value': -125402,
            'code': 'PluginFeatureNotImplemented',
            'description': "The feature is not implemented ({0})."
        },
        {
            'value': -125403,
            'code': 'PluginFeatureUnavailableError',
            'description': "The feature cannot be used because a "
                           "required object or function is missing "
                           "({0})."
        },
        {
            'value': -125404,
            'code': 'PluginInvalidArgumentError',
            'description': "An invalid argument was passed to a "
                           "function."
        },
        {
            'value': -125405,
            'code': 'ErrorWhileThrowingException',
            'description': "An error occurred while another exception "
                           "was already being thrown."
        },
        {
            'value': -125406,
            'code': 'PluginFunctionDescriptionMissingError',
            'description': "Function description message missing for "
                           "'{0}'."
        },
        {
            'value': -125407,
            'code': 'RemoveFileError',
            'description': "An error occurred while removing the file "
                           "or directory '{0}'."
        },
        {
            'value': -125408,
            'code': 'UnsupportedPackageActionError',
            'description': "The package '{0}' does not support the "
                           "specified action '{1}'."
        },
        {
            'value': -125409,
            'code': 'FileDoesNotExistError',
            'description': "A file does not exist at the path '{0}'."
        },
        {
            'value': -125410,
            'code': 'AgentInterfaceOnTransactionBeginError',
            'description': "An error occurred in OnTransactionBegin."
        },
        {
            'value': -125411,
            'code': 'AgentInterfaceOnTransactionEndError',
            'description': "An error occurred in OnTransactionEnd."
        },
        {
            'value': -125412,
            'code': 'AgentInterfaceOnTransactionStepError',
            'description': "An error occurred in OnTransactionStep for "
                           "transaction type '{0}'."
        },
        {
            'value': -125413,
            'code': 'AgentInterfaceOnTransactionListInstalledError',
            'description': "An error occurred in "
                           "OnTransactionListInstalled with "
                           "verbose={0}."
        },
        {
            'value': -125414,
            'code': 'AgentInterfaceOnTransactionCreatePackageError',
            'description': "An error occurred in "
                           "OnTransactionCreatePackage fror output "
                           "path '{0}'."
        },
        {
            'value': -125420,
            'code': 'PathResolverRootNameError',
            'description': "There was an error getting the path for "
                           "root name '{0}' ({1})."
        },
        {
            'value': -125421,
            'code': 'PathResolverUserError',
            'description': "The user was not specified for a root path "
                           "that requires it."
        },
        {
            'value': -125422,
            'code': 'PathResolverBitnessError',
            'description': "The bitness was not specified for a root "
                           "path that requires it."
        },
        {
            'value': -125423,
            'code': 'PathResolverUnknownRootName',
            'description': "Unknown root name '{0}'."
        },
        {
            'value': -125424,
            'code': 'PathResolverGetKnownFolderPathError',
            'description': "An error occurred getting the known folder "
                           "for a system path."
        },
        {
            'value': -125425,
            'code': 'PathResolverGetEnvironmentVariableError',
            'description': "An error occurred getting the environment "
                           "variable for a system path."
        },
        {
            'value': -125426,
            'code': 'PathResolverUnsupportedRootNameSuffixError',
            'description': "Suffix '{0}' is not supported for root "
                           "name Id '{1}'."
        },
        {
            'value': -125430,
            'code': 'Win32Disable64bitRedirectionError',
            'description': "An error occurred when attempting to "
                           "disable 64-bit folder redirection."
        },
        {
            'value': -125431,
            'code': 'Win32Enable64bitRedirectionError',
            'description': "An error occurred when attempting to "
                           "reenable 64-bit folder redirection."
        },
        {
            'value': -125432,
            'code': 'CreateProcessError',
            'description': "An error occurred creating a process to "
                           "run command '{0}'."
        },
        {
            'value': -125433,
            'code': 'WaitForProcessError',
            'description': "An error occurred waiting for a process "
                           "when attempting to run command '{0}'."
        },
        {
            'value': -125434,
            'code': 'GetProcessExitCodeError',
            'description': "An error occurred getting the exit code of "
                           "a process run using command '{0}'."
        },
        {
            'value': -125435,
            'code': 'RegistryQueryError',
            'description': "An error occurred querying the registry "
                           "value '{0}'."
        },
        {
            'value': -125436,
            'code': 'WindowsFastStartupOverrideError',
            'description': "Windows Fast Startup could not be "
                           "disabled. Fast Startup my cause problems "
                           "with NI hardware and software."
        },
        {
            'value': -125437,
            'code': 'WindowsFastStartupSetByGroupPolicyError',
            'description': "Windows Fast Startup is Force Enabled by a "
                           "Group Policy. Fast Startup my cause "
                           "problems with NI hardware and software. "
                           "Contact your Administrator to disable Fast "
                           "Startup."
        },
        {
            'value': -125438,
            'code': 'FileSystemMoveFileSecurityError',
            'description': "An error occurred when resetting security "
                           "permissions after moving a file from '{0}' "
                           "to '{1}'."
        },
        {
            'value': -125439,
            'code': 'RegistrySetError',
            'description': "An error occurred setting the registry "
                           "value '{0}'."
        },
        {
            'value': -125440,
            'code': 'CustomActionExecutorRunQueueError',
            'description': "An error occurred running the custom "
                           "action queue '{0}'."
        },
        {
            'value': -125441,
            'code': 'CustomActionExecutorReturnCodeError',
            'description': "The executable returned error {0} after "
                           "running the custom action command '{1}'."
        },
        {
            'value': -125442,
            'code': 'CustomActionExecutorRootPathNotSetError',
            'description': "The custom action cannot be called because "
                           "the root path has not been set for "
                           "executable '{0}' with arguments '{1}'."
        },
        {
            'value': -125443,
            'code': 'CustomActionExecutorRunCustomActionError',
            'description': "The custom action at '{0}' with arguments "
                           "'{1}', failed to launch."
        },
        {
            'value': -125444,
            'code': 'CustomActionExecutorFileNotInPackageError',
            'description': "The custom action, '{0}', was not found in "
                           "the package."
        },
        {
            'value': -125445,
            'code': 'CustomActionExecutorFileNotSpecifiedError',
            'description': "No executable was specified for an "
                           "'inPackage' custom action."
        },
        {
            'value': -125446,
            'code': 'CustomActionExecutorInpackageNotAllowedToRunError',
            'description': "An 'inPackage' custom action is not "
                           "allowed to run at this time."
        },
        {
            'value': -125450,
            'code': 'InstallationTrackerBackupError',
            'description': "An error occurred while backing up the "
                           "installation database ({0})."
        },
        {
            'value': -125451,
            'code': 'InstallationTrackerPackageError',
            'description': "There was a problem getting package "
                           "information from the database ({0})."
        },
        {
            'value': -125452,
            'code': 'InstallationTrackerRootPathError',
            'description': "There was a problem getting root path "
                           "information from the database ({0})."
        },
        {
            'value': -125453,
            'code': 'InstallationTrackerFilePathError',
            'description': "There was a problem getting file "
                           "information from the database ({0})."
        },
        {
            'value': -125454,
            'code': 'InstallationTrackerFileRootError',
            'description': "There was a problem getting root path and "
                           "file information from the database ({0})."
        },
        {
            'value': -125455,
            'code': 'InstallationTrackerInternalDatabaseUsageError',
            'description': "An internal error occurred due to "
                           "incorrect usage of the database ({0})."
        },
        {
            'value': -125456,
            'code': 'InstallationTrackerInputDataError',
            'description': "There was a problem in the package "
                           "information being saved to the database "
                           "({0})."
        },
        {
            'value': -125457,
            'code': 'InstallationTrackerCustomActionError',
            'description': "There was a problem getting custom action "
                           "information from the database ({0})."
        },
        {
            'value': -125458,
            'code': 'InstallationTrackerBackupCleanError',
            'description': "An error occurred while removing the "
                           "installation database backup ({0})."
        },
        {
            'value': -125460,
            'code': 'InstallerFileNotFoundError',
            'description': "The file to install was not found at "
                           "'{0}'."
        },
        {
            'value': -125461,
            'code': 'InstallerCreateDirectoriesError',
            'description': "An error occurred in the installer while "
                           "creating the directories '{0}'"
        },
        {
            'value': -125462,
            'code': 'InstallerErrorForRootName',
            'description': "An error occured while installing files in "
                           "root '{0}' ({1})."
        },
        {
            'value': -125463,
            'code': 'InstallerGetTempDirectoryError',
            'description': "An error occurred getting the temp "
                           "directory path."
        },
        {
            'value': -125464,
            'code': 'InstallerMoveToTempError',
            'description': "An error occurred moving the file '{0}' to "
                           "the temp directory path '{1}'."
        },
        {
            'value': -125465,
            'code': 'InstallerScheduleMoveError',
            'description': "An error occurred while scheduling the "
                           "file to be moved on reboot from '{0}' to "
                           "'{1}'."
        },
        {
            'value': -125466,
            'code': 'InstallerScheduleFilesElevationError',
            'description': "Files cannot be scheduled to install "
                           "because the process is not elevated."
        },
        {
            'value': -125470,
            'code': 'ContextGetCurrentUserError',
            'description': "An error occurred while getting the "
                           "current user."
        },
        {
            'value': -125471,
            'code': 'ContextGetCurrentUserWin32Error',
            'description': "An error occurred making a system call to "
                           "get the current user ({0})."
        },
        {
            'value': -125480,
            'code': 'MediatorPackageVersionError',
            'description': "Unable to return information abou t"
                           "installed package '{0}' version '{1}' - "
                           "its version does not match the format "
                           "expected by NI Package Manager."
        },
        {
            'value': -125481,
            'code': 'MediatorTaskMediatorCannotBeSet',
            'description': "The task mediator cannot be set because "
                           "there is already a task mediator for the "
                           "current thread."
        },
        {
            'value': -125482,
            'code': 'MediatorRemoveTempError',
            'description': "An error occurred removing the NI Package "
                           "Manager temp directory path '{0}'."
        },
        {
            'value': -125483,
            'code': 'MediatorLogFileDirectoryCreationError',
            'description': "Could not create log file directory path, "
                           "'{0}'."
        },
        {
            'value': -125484,
            'code': 'MediatorLogFileCreationError',
            'description': "Could not create log file, '{0}'."
        },
        {
            'value': -125485,
            'code': 'MediatorLogFileWriteError',
            'description': "Could not write to log file, '{0}'."
        },
        {
            'value': -125490,
            'code': 'PackageReaderReadError',
            'description': "An error occurred while reading the "
                           "package '{0}'."
        },
        {
            'value': -125491,
            'code': 'PackageReaderIteratorError',
            'description': "An error occurred while creating an "
                           "iterator to read the files in the package "
                           "'{0}'."
        },
        {
            'value': -125492,
            'code': 'PackageReaderLoadInstructionsError',
            'description': "An error occurred reading the instructions "
                           "file located at '{0}'."
        },
        {
            'value': -125493,
            'code': 'PackageReaderBadValueError',
            'description': "The attribute '{0}' in the package's "
                           "instructions file has an invalid value "
                           "'{1}'."
        },
        {
            'value': -125494,
            'code': 'PackageReaderMissingAttributeError',
            'description': "An element in the package's instructions "
                           "file is missing the required attribute "
                           "'{0}'."
        },
        {
            'value': -125495,
            'code': 'MsiDatabaseOpenFailed',
            'description': "Could not open MSI at '{0}'. ({1})"
        },
        {
            'value': -125496,
            'code': 'MsiFileNotFound',
            'description': "Could not find MSI at '{0}'."
        },
        {
            'value': -125497,
            'code': 'PackageReaderMissingCustomActionExecutable',
            'description': "The custom action executable path or file "
                           "of a custom action element in the "
                           "instructions file is missing or invalid."
        },
        {
            'value': -125498,
            'code': 'PackageReaderInvalidInPackageAttribute',
            'description': "The inPackage attribute, or one of its "
                           "associated attributes, of a custom action "
                           "element in the instructions file is "
                           "invalid."
        },
        {
            'value': -125499,
            'code': 'CreateCompareLastWriteTimesError',
            'description': "Error occured while comparing the last "
                           "write times of two files. '{0}'."
        },
        {
            'value': -125500,
            'code': 'FileAgentConsoleError',
            'description': "An exception occurred in a"
                           "FileAgentConsole test function '{0}'."
        },
        {
            'value': -125510,
            'code': 'UninstallerErrorForRootName',
            'description': "Uninstalling files in root '{0}' returned "
                           "an unknown error ({1})."
        },
        {
            'value': -125511,
            'code': 'UninstallerFileNotFoundWarning',
            'description': "The file to uninstall was not found at "
                           "'{0}'."
        },
        {
            'value': -125512,
            'code': 'UninstallerScheduleDeleteError',
            'description': "An error occurred scheduling the file to "
                           "be deleted on reboot from '{0}'."
        },
        {
            'value': -125513,
            'code': 'UninstallerScheduleFilesElevationError',
            'description': "Files cannot be scheduled for deletion "
                           "because the process is not elevated."
        },
        {
            'value': -125514,
            'code': 'UninstallerEmptyFilePathError',
            'description': "The file path to remove is an empty value."
        },
        {
            'value': -125520,
            'code': 'SqliteStatementError',
            'description': "An error occurred while preparing or "
                           "running this SQL statement ({0})."
        },
        {
            'value': -125521,
            'code': 'SqliteNoDatabaseError',
            'description': "Attempting to pass a NULL database pointer "
                           "to SQLite call '{0}'."
        },
        {
            'value': -125522,
            'code': 'SqliteDatabaseError',
            'description': "There was a problem calling to the "
                           "database of installed packages ({0})."
        },
        {
            'value': -125523,
            'code': 'SqliteInternalDatabaseUsageError',
            'description': "An internal error occurred due to "
                           "incorrect usage of the database ({0})."
        },
        {
            'value': -125530,
            'code': 'MsiInstallationError',
            'description': "An error occurred while installing the MSI "
                           "at '{0}'. {1}"
        },
        {
            'value': -125531,
            'code': 'MsiUninstallationError',
            'description': "An error occurred while uninstalling the "
                           "MSI at '{0}'. {1}"
        },
        {
            'value': -125532,
            'code': 'InstallerUnexpectedError',
            'description': "An unexpected error occurred while "
                           "Installer was processing a package: '{0}'."
        },
        {
            'value': -125540,
            'code': 'WinInstallAgentConsoleError',
            'description': "An exception occurred in a "
                           "WinInstallAgentConsole test function "
                           "'{0}'."
        },
        {
            'value': -125541,
            'code': 'UpgradeError',
            'description': "An error occurred while upgrading the "
                           "package '{0}'. The package upgrade type is "
                           "'{1}'."
        },
        {
            'value': -125542,
            'code': 'UpgradeSourceNoLongerInstalledWarning',
            'description': "The source package is no longer installed "
                           "on the system. Skipping an attempt to "
                           "uninstall this package during Upgrade.  "
                           "package name: '{0}' package version '{1}'."
        },
        {
            'value': -125550,
            'code': 'NiPathsUnableToLoadMifsystemutilityDllError',
            'description': "Unable to load MIFSystemUtility.dll from "
                           "the path: '{0}'. Ensure your package "
                           "depends on the NI-Paths package and that "
                           "the NI-Paths package has already been "
                           "installed on the system."
        },
        {
            'value': -125551,
            'code': 'NiPathsInvalidParameter',
            'description': "The function '{0}' has been passed the "
                           "following invalid parameter: '{1}'."
        },
        {
            'value': -125552,
            'code': 'NiPathsUnexpectedError',
            'description': "An unexpected error occurred when calling "
                           "the following function: '{0}'."
        },
        {
            'value': -125553,
            'code': 'NiPathsWindowsFunctionError',
            'description': "An unexpected windows error occurred. The "
                           "following function call failed: '{0}'."
        },
        {
            'value': -125560,
            'code': 'WinMifRecorderError',
            'description': "There was a problem processing products "
                           "installed or uninstalled outside NI "
                           "Package Manager."
        },
        {
            'value': -125561,
            'code': 'AgentForwardIncompatibility',
            'description': "This version of Package Manager is too old "
                           "to handle newer installed software. Please "
                           "upgrade Package Manager."
        },
        {
            'value': -125570,
            'code': 'CacherError',
            'description': "There was an error while caching or "
                           "uncaching the product for deployment "
                           "'{0}'."
        },
        {
            'value': -125600,
            'code': 'PathNotAbsoluteError',
            'description': "The path, '{0}', is not absolute."
        },
        {
            'value': -125620,
            'code': 'PackageValidationError',
            'description': "This package failed validation. See log "
                           "file at the following path for detailed "
                           "error information '{0}'."
        },
        {
            'value': -125800,
            'code': 'GuiUnknownCommand',
            'description': "Unknown command: '{0}'"
        },
        {
            'value': -125801,
            'code': 'GuiUnknownFlag',
            'description': "Unknown flag: '{0}'"
        },
        {
            'value': -125802,
            'code': 'GuiInstanceAlreadyRunning',
            'description': "An instance is already running."
        },
        {
            'value': -125804,
            'code': 'GuiRebooting',
            'description': "The transaction finished successfully, a "
                           "system reboot was triggered."
        },
        {
            'value': -125805,
            'code': 'GuiInvalidCommandCombination',
            'description': "Cannot use the command: '{0}', with the "
                           "arguments: {0}."
        },
        {
            'value': -125806,
            'code': 'GuiInvalidFlagCombination',
            'description': "Cannot use the flag: '{0}', with the "
                           "arguments: {0}"
        },
        {
            'value': -125807,
            'code': 'GuiNoCommandSpecified',
            'description': "The flag: '{0}', requires a command. (e.g. "
                           "install)"
        },
        {
            'value': -125808,
            'code': 'GuiDuplicatedFlag',
            'description': "The flag: '{0}', cannot be specified more "
                           "than once."
        },
        {
            'value': -125900,
            'code': 'CliUnknownCommand',
            'description': "Unknown '{0}' command.  Try 'nipkg help' "
                           "for info."
        },
        {
            'value': -125901,
            'code': 'CliNoHelpForSpecifiedCommand',
            'description': "No help for '{0}'."
        },
        {
            'value': -125902,
            'code': 'CliUtf8LocaleRequired',
            'description': "Unknown system locale '{0}' (the command "
                           "line interface requires on a "
                           "UTF8-configured locale)."
        },
        {
            'value': -125903,
            'code': 'CliCouldNotSetConsoleCtrlHandler',
            'description': "Could not set the console control handler."
        },
        {
            'value': -125904,
            'code': 'CliCompareVersionsIncorrectArgumentCount',
            'description': "Compare versions needs to have at three "
                           "arguments (ver1 <op> ver2)."
        },
        {
            'value': -125950,
            'code': 'CliInternalInvalidCallbackUserdata',
            'description': "The callback user data is invalid or null."
        },
        {
            'value': -125951,
            'code': 'CliRepoUpdateFailed',
            'description': "Failed to update one or more feeds:{0}"
        },
        {
            'value': -126000,
            'code': 'CurlSslNotConfiguredOrSupportedOnOs',
            'description': "Can not use SSL on this operating system "
                           "because it is either not configured, not "
                           "installed, or not supported."
        },
        {
            'value': -126001,
            'code': 'CurlTimeoutOccurred',
            'description': "The network operation exceeded the user- "
                           "specified or system time limit. ({0})"
        },
        {
            'value': -126002,
            'code': 'CurlCouldNotConnectToHost',
            'description': "The network connection was refused by the "
                           "server."
        },
        {
            'value': -126003,
            'code': 'CurlServerNotResponding',
            'description': "The network is down, unreachable, or has "
                           "been reset. ({0})"
        },
        {
            'value': -126004,
            'code': 'CurlProtocolNotSupported',
            'description': "The network function is not supported by "
                           "the system. ({0})"
        },
        {
            'value': -126005,
            'code': 'CurlMalformedUrl',
            'description': "The network address is ill-formed. Make "
                           "sure the address is in a valid format. For "
                           "TCP/IP, the address can be either a "
                           "machine name or an IP address in the form "
                           "xxx.xxx.xxx.xxx. If this error occurs when "
                           "specifying a machine name, make sure the "
                           "machine name is valid. Try to ping the "
                           "machine name. Check that you have a DNS "
                           "server properly configured. ({0})"
        },
        {
            'value': -126006,
            'code': 'CurlCouldNotConnect',
            'description': "Failed to connect to the specified "
                           "hostname.  Be sure the specified hostname "
                           "is correct, the server is running and "
                           "configured to accept remote requests.  "
                           "({0})"
        },
        {
            'value': -126007,
            'code': 'CurlCannotAccessOrOpenFile',
            'description': "Cannot access or open the specified "
                           "filename.  Be sure the path is correct, "
                           "the file exists, and that it is not locked "
                           "by another user."
        },
        {
            'value': -126008,
            'code': 'CurlInvalidFileName',
            'description': "The specified file name is invalid or does "
                           "not exist."
        },
        {
            'value': -126009,
            'code': 'CurlLibraryNotLoaded',
            'description': "The HTTP client-side libraries (or one of "
                           "its dependencies) failed to load. ({0})"
        },
        {
            'value': -126010,
            'code': 'CurlUnAuthorized',
            'description': "Invalid username or password combination.  "
                           "({0})"
        },
        {
            'value': -126011,
            'code': 'CurlCannotConvertFilestreamToBuffer',
            'description': "An error occured while converting a file "
                           "stream to a fixed buffer."
        },
        {
            'value': -126012,
            'code': 'CurlCouldNotUseCaCert',
            'description': "The certificate path or CA information of "
                           "the local host is invalid. ({0})"
        },
        {
            'value': -126013,
            'code': 'CurlCouldNotVerifyServerAuthenticity',
            'description': "LabVIEW could not verify the authenticity "
                           "of the server. ({0})"
        },
        {
            'value': -126014,
            'code': 'CurlAbortedByCallback',
            'description': "The request was aborted by the caller.  "
                           "({0})"
        },
        {
            'value': -126015,
            'code': 'CurlCouldNotReadFile',
            'description': "LabVIEW could not read the specified "
                           "filename. ({0})"
        },
        {
            'value': -126016,
            'code': 'CurlGenericWriteError',
            'description': "An error occurred while writing to the "
                           "socket. ({0})"
        },
        {
            'value': -126017,
            'code': 'CurlGenericReadError',
            'description': "An error occurred while reading from the "
                           "socket. ({0})"
        },
        {
            'value': -126018,
            'code': 'CurlGenericUploadFailed',
            'description': "An error occurred while uploading a file.  "
                           "({0})"
        },
        {
            'value': -126019,
            'code': 'CurlGenericSendError',
            'description': "An error occurred while sending data on "
                           "the network. ({0})"
        },
        {
            'value': -126020,
            'code': 'CurlGenericReceiveError',
            'description': "An error occurred while receiving data "
                           "from the network. ({0})"
        },
        {
            'value': -126021,
            'code': 'CurlFileSizeLimitExceeded',
            'description': "The file exceeds the size limit on the "
                           "server. ({0})"
        },
        {
            'value': -126022,
            'code': 'CurlAccessForbidden',
            'description': "Client does not have access to the"
                           "specified resource (access is forbidden).  "
                           "({0})"
        },
        {
            'value': -126023,
            'code': 'CurlRemoteFileNotFound',
            'description': "Cannot find the remote file. ({0})"
        },
        {
            'value': -126024,
            'code': 'CurlRemoteFileAlreadyExists',
            'description': "The remote file already exists. ({0})"
        },
        {
            'value': -126025,
            'code': 'CurlUnsufficientStorageSpace',
            'description': "Storage space limits on the server "
                           "exceeded. ({0})"
        },
        {
            'value': -126026,
            'code': 'CurlUnrecognizedTransferEncoding',
            'description': "The server does not recognize the transfer "
                           "encoding. ({0})"
        },
        {
            'value': -126027,
            'code': 'CurlRedirectsLimitExceeded',
            'description': "Number of redirects to other resources "
                           "exceeded. ({0})"
        },
        {
            'value': -126028,
            'code': 'CurlSocketNotReady',
            'description': "The network communication socket is not "
                           "ready. ({0})"
        },
        {
            'value': -126029,
            'code': 'CurlUnknownCurlError',
            'description': "An unknown error occurred in the curl "
                           "libraries. ({0})"
        },
        {
            'value': -126030,
            'code': 'CurlInvalidOrUnsupportedProtocol',
            'description': "The specified protocol is invalid or "
                           "unsupported."
        },
        {
            'value': -126031,
            'code': 'CurlUndefinedServerKey',
            'description': "Failed to negotiate an encryption key from "
                           "the server."
        },
        {
            'value': -126032,
            'code': 'CurlGenericEncryptionError',
            'description': "An error occurred when trying to encrypt "
                           "the user data. Ensure the specified "
                           "hostname is correct, the server is running "
                           "and is configured to accept remote "
                           "requests, and the server is a National "
                           "Instruments web server."
        },
        {
            'value': -126033,
            'code': 'CurlGenericDecryptionError',
            'description': "An error occurred when trying to decrypt "
                           "the user data. Ensure the specified "
                           "hostname is correct, the server is running "
                           "and is configured to accept remote "
                           "requests, and the server is a National "
                           "Instruments web server."
        },
        {
            'value': -126034,
            'code': 'CurlRequestHeaderDoesNotExist',
            'description': "The specified request header does not "
                           "exist."
        },
        {
            'value': -126035,
            'code': 'CurlServerClosedConnectionPrematurely',
            'description': "The server closed the connection "
                           "prematurely. ({0})"
        },
        {
            'value': -126036,
            'code': 'CurlRedirectForbidden',
            'description': "Redirection to another URL was forbidden."
        },
        {
            'value': -126096,
            'code': 'CurlInternalErrorSettingCurlOption',
            'description': "CURL returned result {0} when setting CURL "
                           "option {1} with value '{2}'."
        },
        {
            'value': -126097,
            'code': 'CurlInternalErrorSettingCurlFormOption',
            'description': "CURL returned result {0} when setting CURL "
                           "form option {1} with value '{2}' (content "
                           "type: '{3}')."
        },
        {
            'value': -126098,
            'code': 'CurlInternalErrorGettingCurlOption',
            'description': "CURL returned result {0} when getting CURL "
                           "option {1}."
        },
        {
            'value': -126099,
            'code': 'CurlInternalUndefinedError',
            'description': "The HTTP client produced an unknown error."
        },
        {
            'value': -126100,
            'code': 'SolverProblemDistUpgrade',
            'description': "'{0}' does not belong to a distupgrade "
                           "feed."
        },
        {
            'value': -126101,
            'code': 'SolverProblemInferiorArch',
            'description': "'{0}' has inferior architecture."
        },
        {
            'value': -126102,
            'code': 'SolverProblemUpdate',
            'description': "Problem with installed package '{0}'."
        },
        {
            'value': -126103,
            'code': 'SolverProblemJobConflictingRequests',
            'description': "Conflicting requests."
        },
        {
            'value': -126104,
            'code': 'SolverProblemJobUnsupportedRequest',
            'description': "Unsupported requests."
        },
        {
            'value': -126105,
            'code': 'SolverProblemJobNothingProvidesDep',
            'description': "Nothing provides requested '{0}'."
        },
        {
            'value': -126106,
            'code': 'SolverProblemJobUnknownPackage',
            'description': "Unable to locate package '{0}'."
        },
        {
            'value': -126107,
            'code': 'SolverProblemJobDepProvidedBySystem',
            'description': "Dependency '{0}' is provided by the "
                           "system."
        },
        {
            'value': -126108,
            'code': 'SolverProblemDependencyProblem',
            'description': "Dependency problem."
        },
        {
            'value': -126109,
            'code': 'SolverProblemPackageNotInstallable',
            'description': "The package '{0}' is not installable."
        },
        {
            'value': -126110,
            'code': 'SolverProblemNothingProvidesDependency',
            'description': "Nothing provides '{0}' needed by '{1}'."
        },
        {
            'value': -126111,
            'code': 'SolverProblemSameName',
            'description': "Cannot install both '{0}' and '{1}'."
        },
        {
            'value': -126112,
            'code': 'SolverProblemPackageConflict',
            'description': "Package '{0}' conflicts with '{1}' "
                           "provided by '{2}'."
        },
        {
            'value': -126113,
            'code': 'SolverProblemPackageObsoletes',
            'description': "Package '{0}' obsoletes '{1}' provided by "
                           "'{2}'."
        },
        {
            'value': -126114,
            'code': 'SolverProblemInstalledPackageObsoletes',
            'description': "Installed package '{0}' obsoletes '{1}' "
                           "provided by '{2}'."
        },
        {
            'value': -126115,
            'code': 'SolverProblemPackageImplicitlyObsoletes',
            'description': "Package '{0}' implicitly obsoletes '{1}' "
                           "provided by '{2}'."
        },
        {
            'value': -126116,
            'code': 'SolverProblemPackageRequires',
            'description': "Package '{0}' requires '{1}', but none of "
                           "the providers can be installed."
        },
        {
            'value': -126117,
            'code': 'SolverProblemPackageSelfConflict',
            'description': "Package '{0}' conflicts with '{1}' "
                           "provided by itself."
        },
        {
            'value': -126200,
            'code': 'AdminCannotFindDepotDirectory',
            'description': "The depot directory containing"
                           "'.nipkgadmin' cannot be found at '{0}' or "
                           "in any of its parent directories."
        },
        {
            'value': -126201,
            'code': 'AdminPackageMissingRequiredAttribute',
            'description': "Required attribute '{0}' does not exist in "
                           "the package's control file."
        },
        {
            'value': -126202,
            'code': 'AdminInvalidPoolStoragePolicy',
            'description': "Pool storage policy '{0}' is not valid."
        },
        {
            'value': -126203,
            'code': 'AdminConfigurationDoesNotExist',
            'description': "Cannot open configuration settings because "
                           "the specified path '{0}' is invalid does "
                           "not exist."
        },
        {
            'value': -126204,
            'code': 'AdminCannotFindSpecifiedPackageRepository',
            'description': "The package '{0}' with release '{1}' is "
                           "not registered with the depot."
        },
        {
            'value': -126205,
            'code': 'AdminPackageRepositoryAlreadyRegistered',
            'description': "A package feed '{0}' with release '{1}' is "
                           "already registered in the depot."
        },
        {
            'value': -126206,
            'code': 'AdminPackageWithVersionNotFoundInPool',
            'description': "The package '{0}' with version '{1}' does "
                           "not exist in the pool."
        },
        {
            'value': -126207,
            'code': 'AdminCannotDoOperationOnAClosedDepot',
            'description': "Cannot perform the operation on a closed "
                           "depot."
        },
        {
            'value': -126208,
            'code': 'AdminUnsupportedStoragePolicy',
            'description': "Unsupported storage policy '{0}'."
        },
        {
            'value': -126209,
            'code': 'AdminInvalidStoragePolicy',
            'description': "Invalid storage policy '{0}'."
        },
        {
            'value': -126210,
            'code': 'AdminInvalidConfigTokenValue',
            'description': "The configuration token '{0}' has a value "
                           "'{1}' that is not valid."
        },
        {
            'value': -126211,
            'code': 'AdminMissingLocationForUserDefinedPoolStoragePolicy',
            'description': "Missing required 'location' specification "
                           "for user-defined pool storage strategy."
        },
        {
            'value': -126212,
            'code': 'AdminNoPackageFoundForPackageRepository',
            'description': "No package found in pool for package '{0}' "
                           "with release '{1}'."
        },
        {
            'value': -126213,
            'code': 'AdminMapfileCorrupt',
            'description': "Corrupt mapfile at '{0}."
        },
        {
            'value': -126214,
            'code': 'AdminInvalidPackageName',
            'description': "Invalid package name '{0}'. Package names "
                           "must consist only of lower case letters "
                           "(a-z), digits (0-9), plus (+) and minus "
                           "(-) signs, and periods (.), they must be "
                           "at least two characters long and start "
                           "with an alphanumeric character."
        },
        {
            'value': -126215,
            'code': 'AdminInvalidPackageRepositoryInBuildlist',
            'description': "Invalid or unregistered package '{0}' with "
                           "release '{1}' inside '{2}'."
        },
        {
            'value': -126216,
            'code': 'AdminInvalidPackageRepositoryStagenameInBuildlist',
            'description': "Unknown stage name '{0}' for package '{1}' "
                           "inside '{2}'."
        },
        {
            'value': -126217,
            'code': 'AdminBuildPackagePathDoesNotExistInPool',
            'description': "Dependency package '{0}' with filelist "
                           "'{1}' specifies package '{2}' that does "
                           "not exist in the pool. Either update your "
                           "dependency on this package or have the "
                           "author of that package fix their filelist."
        },
        {
            'value': -126218,
            'code': 'AdminAddToPoolRenameNotSupported',
            'description': "Cannot rename the package file '{0}' when "
                           "adding it into the pool at location '{1}'."
        },
        {
            'value': -126219,
            'code': 'AdminCorruptBuildlistFile',
            'description': "The buildlist file '{0}' contains an "
                           "unparsable line '{1}' (be sure the line "
                           "has three space-delimited/tab-delimited "
                           "fields and that each space/tab character "
                           "is valid)."
        },
        {
            'value': -126220,
            'code': 'AdminCannotWriteToDepotConfigurationFile',
            'description': "An unknown error occurred ({0}) when "
                           "attempting to write to the depot "
                           "configuration file '{1}'."
        },
        {
            'value': -126295,
            'code': 'InternalAdminPackageRepositoryNotInitialized',
            'description': "The package feed is not initialized."
        },
        {
            'value': -126296,
            'code': 'InternalAdminPackageRepositoryNotOpened',
            'description': "The package feed for package '{0}' with "
                           "release version '{1}' is not opened."
        },
        {
            'value': -126297,
            'code': 'InternalAdminDepotDirectoryNotSpecified',
            'description': "The depot directory was not specified."
        },
        {
            'value': -126298,
            'code': 'InternalAdminDepotNotOpened',
            'description': "Cannot do an operation on a closed depot."
        },
        {
            'value': -126299,
            'code': 'InternalAdminUndefinedError',
            'description': "An unknown error occurred."
        },
        {
            'value': -126300,
            'code': 'DotnetRequiresReboot',
            'description': "The system requires a reboot. You will "
                           "need to resume installation of NI Package "
                           "Manager once the reboot is complete. Click "
                           "OK to reboot now."
        },
        {
            'value': -126301,
            'code': 'DotnetCouldNotBeInstalled',
            'description': "An error occured during .NET installation.  "
                           "Please try again."
        },
        {
            'value': -126302,
            'code': 'OsNotX64',
            'description': "You are trying to execute a Windows 64 "
                           "-bit-only application."
        },
        {
            'value': -126303,
            'code': 'OsNotWindows7Sp1OrGreater',
            'description': "You need at least Windows 7 Service Pack 1 "
                           "to install NI Package Manager."
        },
        {
            'value': -126304,
            'code': 'ProblemWhenLaunchingRequiredFile',
            'description': "A problem occurred while launching a "
                           "required file. The installer might be "
                           "corrupted. Try redownloading or getting a "
                           "new media distribution."
        },
        {
            'value': -126305,
            'code': 'AutomaticRebootFailed',
            'description': "Automatic reboot failed. Please reboot "
                           "your system manually and then resume "
                           "installation of NI Package Manager. "
        },
        {
            'value': -126306,
            'code': 'ElevatedPrivilegesRequired',
            'description': "Elevated privileges are required to "
                           "install NI Package Manager."
        }
    ]

    try:
        installer_error = next(
            (item for item in error_values if item['value'] == return_code),
            installer_error
        )
    except GeneratorExit:
        pass

    if args_list:
        installer_error['description'] = installer_error['description'].format(
            *args_list
        )

    return installer_error


if __name__ == '__main__':
    '''
    If you want to re-scrape the Package Manager exit codes from the document, 
    just set the parse_code_source flag to True, run the script, select the 
    dictionary values and paste them over the contents of the error_vals list.
    
    If you're getting errors about not finding the 'code' or 'container' 
    elements, try increasing page_load_wait_s.
    '''
    parse_code_source = True
    page_load_wait_s = 5
    if parse_code_source:
        from selenium import webdriver

        page_address = 'http://niweb.natinst.com/confluence/display/ss/' \
                       'NI+Package+Management+-+GUI+Exit+Codes'
        driver = webdriver.Chrome(
            '../../testing_considerations/chromedriver.exe')
        driver.get(page_address)

        # Sleep for a bit to give the page time to load.
        time.sleep(page_load_wait_s)

        data_list = list()
        desc_regex = re.compile('%([0-9])%')
        try:
            td = driver.find_element_by_class_name('code')
            data_container = td.find_element_by_class_name('container')

            for row in data_container.find_elements_by_tag_name('div'):
                if row.text.lstrip().startswith(
                        ('namespace', '{', 'public', '//', '}')
                ):
                    continue

                data = dict()

                # Extract the value and code.
                split_text = row.text.split()
                data['value'] = split_text[2][:-1] if \
                    ',' in split_text[2] else split_text[2]
                data['code'] = split_text[0]

                # Select the description text, replacing %1%, %2%, etc. with
                # {1}, {2}, etc.
                desc_line = row.text.split('//')[-1].strip()
                data['description'] = re.sub(desc_regex, r'{\g<1>}', desc_line)

                data_list.append(data)

        finally:
            driver.close()

        # print(data_list)
        for index, row in enumerate(data_list):
            brace_leading_spaces = 8
            leading_spaces = 12
            # max_line_len = 79 - leading_spaces
            # heading_len = len("'description': \"\"")
            # num_rows = int(
            #     (heading_len + len(row['description'])) / max_line_len
            # )

            print(' ' * brace_leading_spaces + '{')
            print(' ' * leading_spaces + "'value': {},".format(row['value']))
            print(' ' * leading_spaces + "'code': '{}',".format(row['code']))

            wrapper = TextWrapper(
                initial_indent=' ' * leading_spaces + "'description': \"",
                subsequent_indent=' ' *
                                  (leading_spaces + len("'description': ")) +
                                  '"'
            )

            wrapped_text = wrapper.wrap(row['description'])
            for line in wrapped_text:
                print(line + '"')

            # offset = 0
            # for index in range(num_rows + 1):
            #     if index == 0:
            #         print(
            #             ' ' * leading_spaces + "'description': \"{}\"".format(
            #                 row['description']
            #                 [offset:max_line_len - heading_len]
            #             )
            #         )
            #         offset += max_line_len - heading_len
            #     else:
            #         print(
            #             ' ' * leading_spaces + "\"{}\"".format(
            #                 row['description']
            #                 [offset:offset+max_line_len]
            #             )
            #         )
            #         offset += max_line_len

            print(
                ' ' * brace_leading_spaces +
                ('},' if index < len(data_list) - 1 else '}')
            )
