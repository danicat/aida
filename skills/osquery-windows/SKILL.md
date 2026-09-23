---
name: osquery-windows
description: Windows system diagnostics and osquery schema reference. Provides tables for registry keys, services, scheduled tasks, BitLocker encryption, Windows events, WMI persistence, certificates, programs, and NTFS ACLs. Use for Windows persistence analysis, security configuration audits, and event log forensics.
---

# Windows Osquery Diagnostics and Schema Reference

The `osquery-windows` skill provides comprehensive osquery table schemas, diagnostic queries, and incident investigation runbooks tailored specifically for Windows systems. Agents should load this skill when diagnosing system health, hunting for threats or persistence, inspecting system configurations, or auditing compliance on Windows hosts.

## Diagnostic Runbooks & Investigation Workflows

### Registry Persistence Hunting
Query common autostart Run and RunOnce registry keys:
```sql
-- Inspect user and system Run keys
SELECT path, name, data, type 
FROM registry 
WHERE path LIKE 'HKEY_LOCAL_MACHINE\Software\Microsoft\Windows\CurrentVersion\Run\%'
   OR path LIKE 'HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run\%';

-- Inspect Winlogon userinit and shell configurations
SELECT path, name, data 
FROM registry 
WHERE path = 'HKEY_LOCAL_MACHINE\Software\Microsoft\Windows NT\CurrentVersion\Winlogon\Userinit'
   OR path = 'HKEY_LOCAL_MACHINE\Software\Microsoft\Windows NT\CurrentVersion\Winlogon\Shell';

-- Image File Execution Options (IFEO) debugger hijacks
SELECT path, name, data 
FROM registry 
WHERE path LIKE 'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\%\Debugger';
```

### Windows Services & Scheduled Tasks
Audit non-standard services and scheduled task execution:
```sql
-- Services with non-system paths or unusual startup
SELECT name, display_name, status, start_type, path_name, user_account 
FROM services 
WHERE path_name NOT LIKE 'C:\Windows\System32\%' 
  AND path_name NOT LIKE 'C:\Windows\SysWOW64\%';

-- Scheduled tasks executing script hosts or powershell
SELECT name, action, path, enabled, state, hidden 
FROM scheduled_tasks 
WHERE action LIKE '%powershell%' 
   OR action LIKE '%cmd.exe%' 
   OR action LIKE '%wscript%' 
   OR action LIKE '%mshta%';
```

### BitLocker & Security Hardening Status
Audit BitLocker drive encryption and Windows Defender status:
```sql
-- BitLocker status across volumes
SELECT drive_letter, persistent_volume_id, conversion_status, protection_status, encryption_method 
FROM bitlocker_info;

-- Patches installed on system
SELECT hotfix_id, description, installed_by, installed_on 
FROM patches 
ORDER BY installed_on DESC LIMIT 15;
```

### WMI Event Persistence & Drivers
Inspect WMI Event Subscriptions (frequently used by APTs for fileless persistence):
```sql
-- WMI event consumers
SELECT name, command_line_template FROM wmi_cli_event_consumers;

-- WMI event filters
SELECT name, query FROM wmi_event_filters;

-- Filter to consumer bindings
SELECT consumer, filter FROM wmi_filter_consumer_bindings;

-- Unsigned or third-party drivers
SELECT description, device_name, driver_path, service, signed 
FROM drivers 
WHERE signed != 1;
```

## Query Performance & Constraints Best Practices
When querying osquery tables on this platform, heed these crucial rules:
1. **Always filter virtual and filesystem tables**: Tables like `file`, `hash`, and `plist` require path constraints (`WHERE path = '...'` or `WHERE directory = '...'`). Never execute unbounded queries (`SELECT * FROM file;`) as this triggers a full filesystem crawl.
2. **Limit process and memory scans**: When inspecting `process_memory_map` or `process_open_files`, always filter by specific process IDs (`WHERE pid = 1234`).
3. **Use indexes on system events**: Filter event subscriber tables by timestamp or event ID to prevent reading extensive historical logs in memory.


## Windows Core Table Schemas

### `appcompat_shims`

Application Compatibility shims are a way to persist malware. This table presents the AppCompat Shim information from the registry in a nice format. See http://files.brucon.org/2015/Tomczak_and_Ballenthin_Shims_for_the_Win.pdf for more details.

| Column | Type | Description |
| :--- | :--- | :--- |
| `executable` | TEXT | Name of the executable that is being shimmed. This is pulled from the registry. |
| `path` | TEXT | This is the path to the SDB database. |
| `description` | TEXT | Description of the SDB. |
| `install_time` | INTEGER | Install time of the SDB |
| `type` | TEXT | Type of the SDB database. |
| `sdb_id` | TEXT | Unique GUID of the SDB. |

### `authenticode`

File (executable, bundle, installer, disk) code signing status.

| Column | Type | Description |
| :--- | :--- | :--- |
| `path` | TEXT | Must provide a path or directory |
| `original_program_name` | TEXT | The original program name that the publisher has signed |
| `serial_number` | TEXT | The certificate serial number |
| `issuer_name` | TEXT | The certificate issuer name |
| `subject_name` | TEXT | The certificate subject name |
| `result` | TEXT | The signature check result |

### `autoexec`

| Column | Type | Description |
| :--- | :--- | :--- |
| `path` | TEXT | Path to the executable |
| `name` | TEXT | Name of the program |
| `source` | TEXT | Source table of the autoexec item |

### `background_activities_moderator`

Background Activities Moderator (BAM) tracks application execution.

| Column | Type | Description |
| :--- | :--- | :--- |
| `path` | TEXT | Application file path. |
| `last_execution_time` | BIGINT | Most recent time application was executed. |
| `sid` | TEXT | User SID. |

### `bitlocker_info`

Retrieve bitlocker status of the machine.

| Column | Type | Description |
| :--- | :--- | :--- |
| `device_id` | TEXT | ID of the encrypted drive. |
| `drive_letter` | TEXT | Drive letter of the encrypted drive. |
| `persistent_volume_id` | TEXT | Persistent ID of the drive. |
| `conversion_status` | INTEGER | The bitlocker conversion status of the drive. |
| `protection_status` | INTEGER | The bitlocker protection status of the drive. |
| `encryption_method` | TEXT | The encryption type of the device. |
| `protector_types` | TEXT | Protector types used to secure the volume |
| `version` | INTEGER | The FVE metadata version of the drive. |
| `percentage_encrypted` | INTEGER | The percentage of the drive that is encrypted. |
| `lock_status` | INTEGER | The accessibility status of the drive from Windows. |

### `chassis_info`

Display information pertaining to the chassis and its security status.

| Column | Type | Description |
| :--- | :--- | :--- |
| `audible_alarm` | TEXT | If TRUE, the frame is equipped with an audible alarm. |
| `breach_description` | TEXT | If provided, gives a more detailed description of a detected security breach. |
| `chassis_types` | TEXT | A comma-separated list of chassis types, such as Desktop or Laptop. |
| `description` | TEXT | An extended description of the chassis if available. |
| `lock` | TEXT | If TRUE, the frame is equipped with a lock. |
| `manufacturer` | TEXT | The manufacturer of the chassis. |
| `model` | TEXT | The model of the chassis. |
| `security_breach` | TEXT | The physical status of the chassis such as Breach Successful, Breach Attempted, etc. |
| `serial` | TEXT | The serial number of the chassis. |
| `smbios_tag` | TEXT | The assigned asset tag number of the chassis. |
| `sku` | TEXT | The Stock Keeping Unit number if available. |
| `status` | TEXT | If available, gives various operational or nonoperational statuses such as OK, Degraded, and Pred Fail. |
| `visible_alarm` | TEXT | If TRUE, the frame is equipped with a visual alarm. |

### `chocolatey_packages`

Chocolatey packages installed in a system.

| Column | Type | Description |
| :--- | :--- | :--- |
| `name` | TEXT | Package display name |
| `version` | TEXT | Package-supplied version |
| `summary` | TEXT | Package-supplied summary |
| `author` | TEXT | Optional package author |
| `license` | TEXT | License under which package is launched |
| `path` | TEXT | Path at which this package resides |

### `connectivity`

| Column | Type | Description |
| :--- | :--- | :--- |
| `disconnected` | INTEGER | True if the all interfaces are not connected to any network |
| `ipv4_no_traffic` | INTEGER | True if any interface is connected via IPv4, but has seen no traffic |
| `ipv6_no_traffic` | INTEGER | True if any interface is connected via IPv6, but has seen no traffic |
| `ipv4_subnet` | INTEGER | True if any interface is connected to the local subnet via IPv4 |
| `ipv4_local_network` | INTEGER | True if any interface is connected to a routed network via IPv4 |
| `ipv4_internet` | INTEGER | True if any interface is connected to the Internet via IPv4 |
| `ipv6_subnet` | INTEGER | True if any interface is connected to the local subnet via IPv6 |
| `ipv6_local_network` | INTEGER | True if any interface is connected to a routed network via IPv6 |
| `ipv6_internet` | INTEGER | True if any interface is connected to the Internet via IPv6 |

### `default_environment`

Default environment variables and values.

| Column | Type | Description |
| :--- | :--- | :--- |
| `variable` | TEXT | Name of the environment variable |
| `value` | TEXT | Value of the environment variable |
| `expand` | INTEGER | 1 if the variable needs expanding, 0 otherwise |

### `deviceguard_status`

Retrieve DeviceGuard info of the machine.

| Column | Type | Description |
| :--- | :--- | :--- |
| `version` | TEXT | The version number of the Device Guard build. |
| `instance_identifier` | TEXT | The instance ID of Device Guard. |
| `vbs_status` | TEXT | The status of the virtualization based security settings. Returns UNKNOWN if an error is encountered. |
| `code_integrity_policy_enforcement_status` | TEXT | The status of the code integrity policy enforcement settings. Returns UNKNOWN if an error is encountered. |
| `configured_security_services` | TEXT | The list of configured Device Guard services. Returns UNKNOWN if an error is encountered. |
| `running_security_services` | TEXT | The list of running Device Guard services. Returns UNKNOWN if an error is encountered. |
| `umci_policy_status` | TEXT | The status of the User Mode Code Integrity security settings. Returns UNKNOWN if an error is encountered. |

### `disk_info`

Retrieve basic information about the physical disks of a system.

| Column | Type | Description |
| :--- | :--- | :--- |
| `partitions` | INTEGER | Number of detected partitions on disk. |
| `disk_index` | INTEGER | Physical drive number of the disk. |
| `type` | TEXT | The interface type of the disk. |
| `id` | TEXT | The unique identifier of the drive on the system. |
| `pnp_device_id` | TEXT | The unique identifier of the drive on the system. |
| `disk_size` | BIGINT | Size of the disk. |
| `manufacturer` | TEXT | The manufacturer of the disk. |
| `hardware_model` | TEXT | Hard drive model. |
| `name` | TEXT | The label of the disk object. |
| `serial` | TEXT | The serial number of the disk. |
| `description` | TEXT | The OS |

### `dns_cache`

Enumerate the DNS cache using the undocumented DnsGetCacheDataTable function in dnsapi.dll.

| Column | Type | Description |
| :--- | :--- | :--- |
| `name` | TEXT | DNS record name |
| `type` | TEXT | DNS record type |
| `flags` | INTEGER | DNS record flags |

### `dns_lookup_events`

DNS lookups performed through the Windows DNS stack.

| Column | Type | Description |
| :--- | :--- | :--- |
| `eid` | INTEGER | Event ID |
| `time` | BIGINT | Event timestamp in Unix format |
| `time_windows` | BIGINT | Event timestamp in Windows format |
| `datetime` | DATETIME | Event timestamp in DATETIME format |
| `pid` | BIGINT | Process ID of process making the lookup |
| `path` | TEXT | Path to binary of process making the lookup (sometimes unavailable for very short-lived processes) |
| `username` | TEXT | User rights - primary token username |
| `name` | TEXT | Name being queried in lookup |
| `type` | TEXT | DNS record type of lookup as string |
| `type_id` | INTEGER | Integer type ID for record type |
| `status` | INTEGER | Response status code |
| `response` | TEXT | Results returned by lookup |

### `drivers`

Details for in-use Windows device drivers. This does not display installed but unused drivers.

| Column | Type | Description |
| :--- | :--- | :--- |
| `device_id` | TEXT | Device ID |
| `device_name` | TEXT | Device name |
| `image` | TEXT | Path to driver image file |
| `description` | TEXT | Driver description |
| `service` | TEXT | Driver service name, if one exists |
| `service_key` | TEXT | Driver service registry key |
| `version` | TEXT | Driver version |
| `inf` | TEXT | Associated inf file |
| `class` | TEXT | Device/driver class name |
| `provider` | TEXT | Driver provider |
| `manufacturer` | TEXT | Device manufacturer |
| `driver_key` | TEXT | Driver key |
| `date` | BIGINT | Driver date |
| `signed` | INTEGER | Whether the driver is signed or not |

### `ie_extensions`

Internet Explorer browser extensions.

| Column | Type | Description |
| :--- | :--- | :--- |
| `name` | TEXT | Extension display name |
| `registry_path` | TEXT | Extension identifier |
| `version` | TEXT | Version of the executable |
| `path` | TEXT | Path to executable |

### `kva_speculative_info`

Display kernel virtual address and speculative execution information for the system.

| Column | Type | Description |
| :--- | :--- | :--- |
| `kva_shadow_enabled` | INTEGER | Kernel Virtual Address shadowing is enabled. |
| `kva_shadow_user_global` | INTEGER | User pages are marked as global. |
| `kva_shadow_pcid` | INTEGER | Kernel VA PCID flushing optimization is enabled. |
| `kva_shadow_inv_pcid` | INTEGER | Kernel VA INVPCID is enabled. |
| `bp_mitigations` | INTEGER | Branch Prediction mitigations are enabled. |
| `bp_system_pol_disabled` | INTEGER | Branch Predictions are disabled via system policy. |
| `bp_microcode_disabled` | INTEGER | Branch Predictions are disabled due to lack of microcode update. |
| `cpu_spec_ctrl_supported` | INTEGER | SPEC_CTRL MSR supported by CPU Microcode. |
| `ibrs_support_enabled` | INTEGER | Windows uses IBRS. |
| `stibp_support_enabled` | INTEGER | Windows uses STIBP. |
| `cpu_pred_cmd_supported` | INTEGER | PRED_CMD MSR supported by CPU Microcode. |

### `logical_drives`

Details for logical drives on the system. A logical drive generally represents a single partition.

| Column | Type | Description |
| :--- | :--- | :--- |
| `device_id` | TEXT | The drive id, usually the drive name, e.g., |
| `type` | TEXT | Deprecated (always |
| `description` | TEXT | The canonical description of the drive, e.g. |
| `free_space` | BIGINT | The amount of free space, in bytes, of the drive (-1 on failure). |
| `size` | BIGINT | The total amount of space, in bytes, of the drive (-1 on failure). |
| `file_system` | TEXT | The file system of the drive. |
| `boot_partition` | INTEGER | True if Windows booted from this drive. |

### `logon_sessions`

Windows Logon Session.

| Column | Type | Description |
| :--- | :--- | :--- |
| `logon_id` | INTEGER | A locally unique identifier (LUID) that identifies a logon session. |
| `user` | TEXT | The account name of the security principal that owns the logon session. |
| `logon_domain` | TEXT | The name of the domain used to authenticate the owner of the logon session. |
| `authentication_package` | TEXT | The authentication package used to authenticate the owner of the logon session. |
| `logon_type` | TEXT | The logon method. |
| `session_id` | INTEGER | The Terminal Services session identifier. |
| `logon_sid` | TEXT | The user |
| `logon_time` | BIGINT | The time the session owner logged on. |
| `logon_server` | TEXT | The name of the server used to authenticate the owner of the logon session. |
| `dns_domain_name` | TEXT | The DNS name for the owner of the logon session. |
| `upn` | TEXT | The user principal name (UPN) for the owner of the logon session. |
| `logon_script` | TEXT | The script used for logging on. |
| `profile_path` | TEXT | The home directory for the logon session. |
| `home_directory` | TEXT | The home directory for the logon session. |
| `home_directory_drive` | TEXT | The drive location of the home directory of the logon session. |

### `ntdomains`

Display basic NT domain information of a Windows machine.

| Column | Type | Description |
| :--- | :--- | :--- |
| `name` | TEXT | The label by which the object is known. |
| `client_site_name` | TEXT | The name of the site where the domain controller is configured. |
| `dc_site_name` | TEXT | The name of the site where the domain controller is located. |
| `dns_forest_name` | TEXT | The name of the root of the DNS tree. |
| `domain_controller_address` | TEXT | The IP Address of the discovered domain controller.. |
| `domain_controller_name` | TEXT | The name of the discovered domain controller. |
| `domain_name` | TEXT | The name of the domain. |
| `status` | TEXT | The current status of the domain object. |

### `ntfs_acl_permissions`

Retrieve NTFS ACL permission information for files and directories.

| Column | Type | Description |
| :--- | :--- | :--- |
| `path` | TEXT | Path to the file or directory. |
| `type` | TEXT | Type of access mode for the access control entry. |
| `principal` | TEXT | User or group to which the ACE applies. |
| `access` | TEXT | Specific permissions that indicate the rights described by the ACE. |
| `inherited_from` | TEXT | The inheritance policy of the ACE. |

### `ntfs_journal_events`

Track time/action changes to files specified in configuration data.

| Column | Type | Description |
| :--- | :--- | :--- |
| `action` | TEXT | Change action (Write, Delete, etc) |
| `category` | TEXT | The category that the event originated from |
| `old_path` | TEXT | Old path (renames only) |
| `path` | TEXT | Path |
| `record_timestamp` | TEXT | Journal record timestamp |
| `record_usn` | TEXT | The update sequence number that identifies the journal record |
| `node_ref_number` | TEXT | The ordinal that associates a journal record with a filename |
| `parent_ref_number` | TEXT | The ordinal that associates a journal record with a filename |
| `drive_letter` | TEXT | The drive letter identifying the source journal |
| `file_attributes` | TEXT | File attributes |
| `partial` | BIGINT | Set to 1 if either path or old_path only contains the file or folder name |
| `time` | BIGINT | Time of file event |
| `eid` | TEXT | Event ID |

### `office_mru`

View recently opened Office documents.

| Column | Type | Description |
| :--- | :--- | :--- |
| `application` | TEXT | Associated Office application |
| `version` | TEXT | Office application version number |
| `path` | TEXT | File path |
| `last_opened_time` | BIGINT | Most recent opened time file was opened |
| `sid` | TEXT | User SID |

### `patches`

Lists all the patches applied. Note: This does not include patches applied via MSI or downloaded from Windows Update (e.g. Service Packs).

| Column | Type | Description |
| :--- | :--- | :--- |
| `csname` | TEXT | The name of the host the patch is installed on. |
| `hotfix_id` | TEXT | The KB ID of the patch. |
| `caption` | TEXT | Short description of the patch. |
| `description` | TEXT | Fuller description of the patch. |
| `fix_comments` | TEXT | Additional comments about the patch. |
| `installed_by` | TEXT | The system context in which the patch as installed. |
| `install_date` | TEXT | Indicates when the patch was installed. Lack of a value does not indicate that the patch was not installed. |
| `installed_on` | TEXT | The date when the patch was installed. |

### `physical_disk_performance`

Provides provides raw data from performance counters that monitor hard or fixed disk drives on the system.

| Column | Type | Description |
| :--- | :--- | :--- |
| `name` | TEXT | Name of the physical disk |
| `avg_disk_bytes_per_read` | BIGINT | Average number of bytes transferred from the disk during read operations |
| `avg_disk_bytes_per_write` | BIGINT | Average number of bytes transferred to the disk during write operations |
| `avg_disk_read_queue_length` | BIGINT | Average number of read requests that were queued for the selected disk during the sample interval |
| `avg_disk_write_queue_length` | BIGINT | Average number of write requests that were queued for the selected disk during the sample interval |
| `avg_disk_sec_per_read` | INTEGER | Average time, in seconds, of a read operation of data from the disk |
| `avg_disk_sec_per_write` | INTEGER | Average time, in seconds, of a write operation of data to the disk |
| `current_disk_queue_length` | INTEGER | Number of requests outstanding on the disk at the time the performance data is collected |
| `percent_disk_read_time` | BIGINT | Percentage of elapsed time that the selected disk drive is busy servicing read requests |
| `percent_disk_write_time` | BIGINT | Percentage of elapsed time that the selected disk drive is busy servicing write requests |
| `percent_disk_time` | BIGINT | Percentage of elapsed time that the selected disk drive is busy servicing read or write requests |
| `percent_idle_time` | BIGINT | Percentage of time during the sample interval that the disk was idle |

### `pipes`

Named and Anonymous pipes.

| Column | Type | Description |
| :--- | :--- | :--- |
| `pid` | BIGINT | Process ID of the process to which the pipe belongs |
| `name` | TEXT | Name of the pipe |
| `instances` | INTEGER | Number of instances of the named pipe |
| `max_instances` | INTEGER | The maximum number of instances creatable for this pipe |
| `flags` | TEXT | The flags indicating whether this pipe connection is a server or client end, and if the pipe for sending messages or bytes |

### `powershell_events`

Powershell script blocks reconstructed to their full script content, this table requires script block logging to be enabled.

| Column | Type | Description |
| :--- | :--- | :--- |
| `time` | BIGINT | Timestamp the event was received by the osquery event publisher |
| `datetime` | TEXT | System time at which the Powershell script event occurred |
| `script_block_id` | TEXT | The unique GUID of the powershell script to which this block belongs |
| `script_block_count` | INTEGER | The total number of script blocks for this script |
| `script_text` | TEXT | The text content of the Powershell script |
| `script_name` | TEXT | The name of the Powershell script |
| `script_path` | TEXT | The path for the Powershell script |
| `cosine_similarity` | DOUBLE | How similar the Powershell script is to a provided |

### `prefetch`

Prefetch files show metadata related to file execution.

| Column | Type | Description |
| :--- | :--- | :--- |
| `path` | TEXT | Prefetch file path. |
| `filename` | TEXT | Executable filename. |
| `hash` | TEXT | Prefetch CRC hash. |
| `last_run_time` | INTEGER | Most recent time application was run. |
| `other_run_times` | TEXT | Other execution times in prefetch file. |
| `run_count` | INTEGER | Number of times the application has been run. |
| `size` | INTEGER | Application file size. |
| `volume_serial` | TEXT | Volume serial number. |
| `volume_creation` | TEXT | Volume creation time. |
| `accessed_files_count` | INTEGER | Number of files accessed. |
| `accessed_directories_count` | INTEGER | Number of directories accessed. |
| `accessed_files` | TEXT | Files accessed by application within ten seconds of launch. |
| `accessed_directories` | TEXT | Directories accessed by application within ten seconds of launch. |
| `executable_path` | TEXT | Full path of the executable. |

### `process_etw_events`

Windows process execution events.

| Column | Type | Description |
| :--- | :--- | :--- |
| `type` | TEXT | Event Type (ProcessStart, ProcessStop) |
| `pid` | BIGINT | Process ID |
| `ppid` | BIGINT | Parent Process ID |
| `session_id` | INTEGER | Session ID |
| `flags` | INTEGER | Process Flags |
| `exit_code` | INTEGER | Exit Code - Present only on ProcessStop events |
| `path` | TEXT | Path of executed binary |
| `cmdline` | TEXT | Command Line |
| `username` | TEXT | User rights - primary token username |
| `token_elevation_type` | TEXT | Primary token elevation type - Present only on ProcessStart events |
| `token_elevation_status` | INTEGER | Primary token elevation status - Present only on ProcessStart events |
| `mandatory_label` | TEXT | Primary token mandatory label sid - Present only on ProcessStart events |
| `datetime` | DATETIME | Event timestamp in DATETIME format |
| `time_windows` | BIGINT | Event timestamp in Windows format |
| `time` | BIGINT | Event timestamp in Unix format |
| `eid` | INTEGER | Event ID |
| `header_pid` | BIGINT | Process ID of the process reporting the event |
| `process_sequence_number` | BIGINT | Process Sequence Number - Present only on ProcessStart events |
| `parent_process_sequence_number` | BIGINT | Parent Process Sequence Number - Present only on ProcessStart events |

### `process_open_handles`

Enumerate open handles for a specified process.

| Column | Type | Description |
| :--- | :--- | :--- |
| `pid` | BIGINT | The process identifier that owns the handle. |
| `value` | BIGINT | The handle value |
| `type` | TEXT | The type of object referenced by the handle. |
| `access` | TEXT | The access permissions of the object referenced by the handle. |
| `name` | TEXT | The value of the object referenced by the handle. |
| `attributes` | TEXT | Object handle attributes. |
| `count` | BIGINT | Handle Count. |
| `raw_pointer_count` | BIGINT | Raw Pointer/Reference Count. Meaning varies, consult Windows docs. |
| `error_stage` | TEXT | Error Stage. |
| `error_code` | BIGINT | Error Code. |

### `programs`

Represents products as they are installed by Windows Installer. A product generally correlates to one installation package on Windows. Some fields may be blank as Windows installation details are left to the discretion of the product author.

| Column | Type | Description |
| :--- | :--- | :--- |
| `name` | TEXT | Commonly used product name. |
| `version` | TEXT | Product version information. |
| `install_location` | TEXT | The installation location directory of the product. |
| `install_source` | TEXT | The installation source of the product. |
| `language` | TEXT | The language of the product. |
| `publisher` | TEXT | Name of the product supplier. |
| `uninstall_string` | TEXT | Path and filename of the uninstaller. |
| `install_date` | TEXT | Date that this product was installed on the system. |
| `identifying_number` | TEXT | Product identification such as a serial number on software, or a die number on a hardware chip. |
| `package_family_name` | TEXT | A combination of PackageName and PublisherHash that is used to uniquely identify applications across versions and architectures. |
| `upgrade_code` | TEXT | Specific to MSI applications, a GUID used to identify a product suite across multiple versions. |

### `recent_files`

Recently files (as displayed in Start Menu or File Explorer).

| Column | Type | Description |
| :--- | :--- | :--- |
| `uid` | BIGINT | The local user ID |
| `filename` | TEXT | The name of the file |
| `path` | TEXT | The full path of the file |
| `type` | TEXT | Display type for the file |
| `mtime` | BIGINT | Last modification time of the shortcut (usually corresponds to last opened time for the file) |
| `shortcut_path` | TEXT | Path to the shortcut where Windows stores the recent file data |

### `registry`

All of the Windows registry hives.

| Column | Type | Description |
| :--- | :--- | :--- |
| `key` | TEXT | Name of the key to search for |
| `path` | TEXT | Full path to the value |
| `name` | TEXT | Name of the registry value entry |
| `type` | TEXT | Type of the registry value, or |
| `data` | TEXT | Data content of registry value |
| `mtime` | BIGINT | timestamp of the most recent registry write |

### `scheduled_tasks`

Lists all of the tasks in the Windows task scheduler.

| Column | Type | Description |
| :--- | :--- | :--- |
| `name` | TEXT | Name of the scheduled task |
| `action` | TEXT | Actions executed by the scheduled task |
| `path` | TEXT | Path to the executable to be run |
| `enabled` | INTEGER | Whether or not the scheduled task is enabled |
| `state` | TEXT | State of the scheduled task |
| `hidden` | INTEGER | Whether or not the task is visible in the UI |
| `last_run_time` | BIGINT | Timestamp the task last ran |
| `next_run_time` | BIGINT | Timestamp the task is scheduled to run next |
| `last_run_message` | TEXT | Exit status message of the last task run |
| `last_run_code` | TEXT | Exit status code of the last task run |

### `security_profile_info`

Information on the security profile of a given system by listing the system Account and Audit Policies. This table mimics the exported securitypolicy output from the secedit tool.

| Column | Type | Description |
| :--- | :--- | :--- |
| `minimum_password_age` | INTEGER | Determines the minimum number of days that a password must be used before the user can change it |
| `maximum_password_age` | INTEGER | Determines the maximum number of days that a password can be used before the client requires the user to change it |
| `minimum_password_length` | INTEGER | Determines the least number of characters that can make up a password for a user account |
| `password_complexity` | INTEGER | Determines whether passwords must meet a series of strong-password guidelines |
| `password_history_size` | INTEGER | Number of unique new passwords that must be associated with a user account before an old password can be reused |
| `lockout_bad_count` | INTEGER | Number of failed logon attempts after which a user account MUST be locked out |
| `logon_to_change_password` | INTEGER | Determines if logon session is required to change the password |
| `force_logoff_when_expire` | INTEGER | Determines whether SMB client sessions with the SMB server will be forcibly disconnected when the client |
| `new_administrator_name` | TEXT | Determines the name of the Administrator account on the local computer |
| `new_guest_name` | TEXT | Determines the name of the Guest account on the local computer |
| `clear_text_password` | INTEGER | Determines whether passwords MUST be stored by using reversible encryption |
| `lsa_anonymous_name_lookup` | INTEGER | Determines if an anonymous user is allowed to query the local LSA policy |
| `enable_admin_account` | INTEGER | Determines whether the Administrator account on the local computer is enabled |
| `enable_guest_account` | INTEGER | Determines whether the Guest account on the local computer is enabled |
| `audit_system_events` | INTEGER | Determines whether the operating system MUST audit System Change, System Startup, System Shutdown, Authentication Component Load, and Loss or Excess of Security events |
| `audit_logon_events` | INTEGER | Determines whether the operating system MUST audit each instance of a user attempt to log on or log off this computer |
| `audit_object_access` | INTEGER | Determines whether the operating system MUST audit each instance of user attempts to access a non-Active Directory object that has its own SACL specified |
| `audit_privilege_use` | INTEGER | Determines whether the operating system MUST audit each instance of user attempts to exercise a user right |
| `audit_policy_change` | INTEGER | Determines whether the operating system MUST audit each instance of user attempts to change user rights assignment policy, audit policy, account policy, or trust policy |
| `audit_account_manage` | INTEGER | Determines whether the operating system MUST audit each event of account management on a computer |
| `audit_process_tracking` | INTEGER | Determines whether the operating system MUST audit process-related events |
| `audit_ds_access` | INTEGER | Determines whether the operating system MUST audit each instance of user attempts to access an Active Directory object that has its own system access control list (SACL) specified |
| `audit_account_logon` | INTEGER | Determines whether the operating system MUST audit each time this computer validates the credentials of an account |

### `services`

Lists all installed Windows services and their relevant data.

| Column | Type | Description |
| :--- | :--- | :--- |
| `name` | TEXT | Service name |
| `service_type` | TEXT | Service Type: OWN_PROCESS, SHARE_PROCESS and maybe Interactive (can interact with the desktop) |
| `display_name` | TEXT | Service Display name |
| `status` | TEXT | Service Current status: STOPPED, START_PENDING, STOP_PENDING, RUNNING, CONTINUE_PENDING, PAUSE_PENDING, PAUSED |
| `pid` | INTEGER | the Process ID of the service |
| `start_type` | TEXT | Service start type: BOOT_START, SYSTEM_START, AUTO_START, DEMAND_START, DISABLED |
| `win32_exit_code` | INTEGER | The error code that the service uses to report an error that occurs when it is starting or stopping |
| `service_exit_code` | INTEGER | The service-specific error code that the service returns when an error occurs while the service is starting or stopping |
| `path` | TEXT | Path to Service Executable |
| `module_path` | TEXT | Path to ServiceDll |
| `description` | TEXT | Service Description |
| `user_account` | TEXT | The name of the account that the service process will be logged on as when it runs. This name can be of the form Domain\\UserName. If the account belongs to the built-in domain, the name can be of the form .\\UserName. |

### `shared_resources`

Displays shared resources on a computer system running Windows. This may be a disk drive, printer, interprocess communication, or other sharable device.

| Column | Type | Description |
| :--- | :--- | :--- |
| `description` | TEXT | A textual description of the object |
| `install_date` | TEXT | Indicates when the object was installed. Lack of a value does not indicate that the object is not installed. |
| `status` | TEXT | String that indicates the current status of the object. |
| `allow_maximum` | INTEGER | Number of concurrent users for this resource has been limited. If True, the value in the MaximumAllowed property is ignored. |
| `maximum_allowed` | BIGINT | Limit on the maximum number of users allowed to use this resource concurrently. The value is only valid if the AllowMaximum property is set to FALSE. |
| `name` | TEXT | Alias given to a path set up as a share on a computer system running Windows. |
| `path` | TEXT | Local path of the Windows share. |
| `type` | BIGINT | Type of resource being shared. Types include: disk drives, print queues, interprocess communications (IPC), and general devices. |
| `type_name` | TEXT | Human readable value for the |

### `shellbags`

Shows directories accessed via Windows Explorer.

| Column | Type | Description |
| :--- | :--- | :--- |
| `sid` | TEXT | User SID |
| `source` | TEXT | Shellbags source Registry file |
| `path` | TEXT | Directory name. |
| `modified_time` | BIGINT | Directory Modified time. |
| `created_time` | BIGINT | Directory Created time. |
| `accessed_time` | BIGINT | Directory Accessed time. |
| `mft_entry` | BIGINT | Directory master file table entry. |
| `mft_sequence` | INTEGER | Directory master file table sequence. |

### `shimcache`

Application Compatibility Cache, contains artifacts of execution.

| Column | Type | Description |
| :--- | :--- | :--- |
| `entry` | INTEGER | Execution order. |
| `path` | TEXT | This is the path to the executed file. |
| `modified_time` | INTEGER | File Modified time. |
| `execution_flag` | INTEGER | Boolean Execution flag, 1 for execution, 0 for no execution, -1 for missing (this flag does not exist on Windows 10 and higher). |

### `tpm_info`

A table that lists the TPM related information.

| Column | Type | Description |
| :--- | :--- | :--- |
| `activated` | INTEGER | TPM is activated |
| `enabled` | INTEGER | TPM is enabled |
| `owned` | INTEGER | TPM is owned |
| `manufacturer_version` | TEXT | TPM version |
| `manufacturer_id` | INTEGER | TPM manufacturers ID |
| `manufacturer_name` | TEXT | TPM manufacturers name |
| `product_name` | TEXT | Product name of the TPM |
| `physical_presence_version` | TEXT | Version of the Physical Presence Interface |
| `spec_version` | TEXT | Trusted Computing Group specification that the TPM supports |

### `userassist`

UserAssist Registry Key tracks when a user executes an application from Windows Explorer.

| Column | Type | Description |
| :--- | :--- | :--- |
| `path` | TEXT | Application file path. |
| `last_execution_time` | BIGINT | Most recent time application was executed. |
| `count` | INTEGER | Number of times the application has been executed. |
| `sid` | TEXT | User SID. |

### `video_info`

Retrieve video card information of the machine.

| Column | Type | Description |
| :--- | :--- | :--- |
| `color_depth` | INTEGER | The amount of bits per pixel to represent color. |
| `driver` | TEXT | The driver of the device. |
| `driver_date` | BIGINT | The date listed on the installed driver. |
| `driver_version` | TEXT | The version of the installed driver. |
| `manufacturer` | TEXT | The manufacturer of the gpu. |
| `model` | TEXT | The model of the gpu. |
| `series` | TEXT | The series of the gpu. |
| `video_mode` | TEXT | The current resolution of the display. |

### `winbaseobj`

Lists named Windows objects in the default object directories, across all terminal services sessions.  Example Windows object types include Mutexes, Events, Jobs and Semaphors.

| Column | Type | Description |
| :--- | :--- | :--- |
| `session_id` | INTEGER | Terminal Services Session Id |
| `object_name` | TEXT | Object Name |
| `object_type` | TEXT | Object Type |

### `windows_crashes`

Extracted information from Windows crash logs (Minidumps).

| Column | Type | Description |
| :--- | :--- | :--- |
| `datetime` | TEXT | Timestamp (log format) of the crash |
| `module` | TEXT | Path of the crashed module within the process |
| `path` | TEXT | Path of the executable file for the crashed process |
| `pid` | BIGINT | Process ID of the crashed process |
| `tid` | BIGINT | Thread ID of the crashed thread |
| `version` | TEXT | File version info of the crashed process |
| `process_uptime` | BIGINT | Uptime of the process in seconds |
| `stack_trace` | TEXT | Multiple stack frames from the stack trace |
| `exception_code` | TEXT | The Windows exception code |
| `exception_message` | TEXT | The NTSTATUS error message associated with the exception code |
| `exception_address` | TEXT | Address (in hex) where the exception occurred |
| `registers` | TEXT | The values of the system registers |
| `command_line` | TEXT | Command-line string passed to the crashed process |
| `current_directory` | TEXT | Current working directory of the crashed process |
| `username` | TEXT | Username of the user who ran the crashed process |
| `machine_name` | TEXT | Name of the machine where the crash happened |
| `major_version` | INTEGER | Windows major version of the machine |
| `minor_version` | INTEGER | Windows minor version of the machine |
| `build_number` | INTEGER | Windows build number of the crashing machine |
| `type` | TEXT | Type of crash log |
| `crash_path` | TEXT | Path of the log file |

### `windows_eventlog`

Table for querying all recorded Windows event logs.

| Column | Type | Description |
| :--- | :--- | :--- |
| `channel` | TEXT | Source or channel of the event |
| `datetime` | TEXT | System time at which the event occurred |
| `task` | INTEGER | Task value associated with the event |
| `level` | INTEGER | Severity level associated with the event |
| `provider_name` | TEXT | Provider name of the event |
| `provider_guid` | TEXT | Provider guid of the event |
| `computer_name` | TEXT | Hostname of system where event was generated |
| `eventid` | INTEGER | Event ID of the event |
| `keywords` | TEXT | A bitmask of the keywords defined in the event |
| `data` | TEXT | Data associated with the event |
| `pid` | INTEGER | Process ID which emitted the event record |
| `tid` | INTEGER | Thread ID which emitted the event record |
| `time_range` | TEXT | System time to selectively filter the events |
| `timestamp` | TEXT | Timestamp to selectively filter the events |
| `xpath` | TEXT | The custom query to filter events |

### `windows_events`

Windows Event logs.

| Column | Type | Description |
| :--- | :--- | :--- |
| `time` | BIGINT | Timestamp the event was received |
| `datetime` | TEXT | System time at which the event occurred |
| `source` | TEXT | Source or channel of the event |
| `provider_name` | TEXT | Provider name of the event |
| `provider_guid` | TEXT | Provider guid of the event |
| `computer_name` | TEXT | Hostname of system where event was generated |
| `eventid` | INTEGER | Event ID of the event |
| `task` | INTEGER | Task value associated with the event |
| `level` | INTEGER | The severity level associated with the event |
| `keywords` | TEXT | A bitmask of the keywords defined in the event |
| `data` | TEXT | Data associated with the event |
| `eid` | TEXT | Event ID |

### `windows_firewall_rules`

Provides the list of Windows firewall rules.

| Column | Type | Description |
| :--- | :--- | :--- |
| `name` | TEXT | Friendly name of the rule |
| `app_name` | TEXT | Friendly name of the application to which the rule applies |
| `action` | TEXT | Action for the rule or default setting |
| `enabled` | INTEGER | 1 if the rule is enabled |
| `grouping` | TEXT | Group to which an individual rule belongs |
| `direction` | TEXT | Direction of traffic for which the rule applies |
| `protocol` | TEXT | IP protocol of the rule |
| `local_addresses` | TEXT | Local addresses for the rule |
| `remote_addresses` | TEXT | Remote addresses for the rule |
| `local_ports` | TEXT | Local ports for the rule |
| `remote_ports` | TEXT | Remote ports for the rule |
| `icmp_types_codes` | TEXT | ICMP types and codes for the rule |
| `profile_domain` | INTEGER | 1 if the rule profile type is domain |
| `profile_private` | INTEGER | 1 if the rule profile type is private |
| `profile_public` | INTEGER | 1 if the rule profile type is public |
| `service_name` | TEXT | Service name property of the application |

### `windows_optional_features`

Lists names and installation states of windows features. Maps to Win32_OptionalFeature WMI class.

| Column | Type | Description |
| :--- | :--- | :--- |
| `name` | TEXT | Name of the feature |
| `caption` | TEXT | Caption of feature in settings UI |
| `state` | INTEGER | Installation state value. 1 == Enabled, 2 == Disabled, 3 == Absent |
| `statename` | TEXT | Installation state name. |

### `windows_search`

Run searches against the Windows system index database using Advanced Query Syntax. See https://learn.microsoft.com/en-us/windows/win32/search/-search-3x-advancedquerysyntax for details.

| Column | Type | Description |
| :--- | :--- | :--- |
| `name` | TEXT | The name of the item |
| `path` | TEXT | The full path of the item. |
| `size` | BIGINT | The item size in bytes. |
| `date_created` | INTEGER | The unix timestamp of when the item was created. |
| `date_modified` | INTEGER | The unix timestamp of when the item was last modified |
| `owner` | TEXT | The owner of the item |
| `type` | TEXT | The item type |
| `properties` | TEXT | Additional property values JSON |
| `query` | TEXT | Windows search query |
| `sort` | TEXT | Sort for windows api |
| `max_results` | INTEGER | Maximum number of results returned by windows api, set to -1 for unlimited |
| `additional_properties` | TEXT | Comma separated list of columns to include in properties JSON |

### `windows_security_center`

| Column | Type | Description |
| :--- | :--- | :--- |
| `firewall` | TEXT | The health of the monitored Firewall (see windows_security_products) |
| `autoupdate` | TEXT | The health of the Windows Autoupdate feature |
| `antivirus` | TEXT | The health of the monitored Antivirus solution (see windows_security_products) |
| `antispyware` | TEXT | Deprecated (always |
| `internet_settings` | TEXT | The health of the Internet Settings |
| `windows_security_center_service` | TEXT | The health of the Windows Security Center Service |
| `user_account_control` | TEXT | The health of the User Account Control (UAC) capability in Windows |

### `windows_security_products`

Enumeration of registered Windows security products. Note: Not compatible with Windows Server.

| Column | Type | Description |
| :--- | :--- | :--- |
| `type` | TEXT | Type of security product |
| `name` | TEXT | Name of product |
| `state` | TEXT | State of protection |
| `state_timestamp` | TEXT | Timestamp for the product state |
| `remediation_path` | TEXT | Remediation path |
| `signatures_up_to_date` | INTEGER | 1 if product signatures are up to date, else 0 |

### `windows_update_history`

Provides the history of the windows update events.

| Column | Type | Description |
| :--- | :--- | :--- |
| `client_app_id` | TEXT | Identifier of the client application that processed an update |
| `date` | BIGINT | Date and the time an update was applied |
| `description` | TEXT | Description of an update |
| `hresult` | BIGINT | HRESULT value that is returned from the operation on an update |
| `operation` | TEXT | Operation on an update |
| `result_code` | TEXT | Result of an operation on an update |
| `server_selection` | TEXT | Value that indicates which server provided an update |
| `service_id` | TEXT | Service identifier of an update service that is not a Windows update |
| `support_url` | TEXT | Hyperlink to the language-specific support information for an update |
| `title` | TEXT | Title of an update |
| `update_id` | TEXT | Revision-independent identifier of an update |
| `update_revision` | BIGINT | Revision number of an update |

### `wmi_bios_info`

Lists important information from the system bios.

| Column | Type | Description |
| :--- | :--- | :--- |
| `name` | TEXT | Name of the Bios setting |
| `value` | TEXT | Value of the Bios setting |

### `wmi_cli_event_consumers`

WMI CommandLineEventConsumer, which can be used for persistence on Windows. See https://www.blackhat.com/docs/us-15/materials/us-15-Graeber-Abusing-Windows-Management-Instrumentation-WMI-To-Build-A-Persistent%20Asynchronous-And-Fileless-Backdoor-wp.pdf for more details.

| Column | Type | Description |
| :--- | :--- | :--- |
| `namespace` | TEXT | The WMI namespace where the consumer was found. |
| `name` | TEXT | Unique name of a consumer. |
| `command_line_template` | TEXT | Standard string template that specifies the process to be started. This property can be NULL, and the ExecutablePath property is used as the command line. |
| `executable_path` | TEXT | Module to execute. The string can specify the full path and file name of the module to execute, or it can specify a partial name. If a partial name is specified, the current drive and current directory are assumed. |
| `class` | TEXT | The name of the class. |
| `relative_path` | TEXT | Relative path to the class or instance. |

### `wmi_event_filters`

Lists WMI event filters.

| Column | Type | Description |
| :--- | :--- | :--- |
| `namespace` | TEXT | The WMI namespace where the filter was found. |
| `name` | TEXT | Unique identifier of an event filter. |
| `query` | TEXT | Windows Management Instrumentation Query Language (WQL) event query that specifies the set of events for consumer notification, and the specific conditions for notification. |
| `query_language` | TEXT | Query language that the query is written in. |
| `class` | TEXT | The name of the class. |
| `relative_path` | TEXT | Relative path to the class or instance. |

### `wmi_filter_consumer_binding`

Lists the relationship between event consumers and filters.

| Column | Type | Description |
| :--- | :--- | :--- |
| `namespace` | TEXT | The WMI namespace where the binding was found. |
| `consumer` | TEXT | Reference to an instance of __EventConsumer that represents the object path to a logical consumer, the recipient of an event. |
| `filter` | TEXT | Reference to an instance of __EventFilter that represents the object path to an event filter which is a query that specifies the type of event to be received. |
| `class` | TEXT | The name of the class. |
| `relative_path` | TEXT | Relative path to the class or instance. |

### `wmi_script_event_consumers`

WMI ActiveScriptEventConsumer, which can be used for persistence on Windows. See https://www.blackhat.com/docs/us-15/materials/us-15-Graeber-Abusing-Windows-Management-Instrumentation-WMI-To-Build-A-Persistent%20Asynchronous-And-Fileless-Backdoor-wp.pdf for more details.

| Column | Type | Description |
| :--- | :--- | :--- |
| `namespace` | TEXT | The WMI namespace where the consumer was found. |
| `name` | TEXT | Unique identifier for the event consumer. |
| `scripting_engine` | TEXT | Name of the scripting engine to use, for example, |
| `script_file_name` | TEXT | Name of the file from which the script text is read, intended as an alternative to specifying the text of the script in the ScriptText property. |
| `script_text` | TEXT | Text of the script that is expressed in a language known to the scripting engine. This property must be NULL if the ScriptFileName property is not NULL. |
| `class` | TEXT | The name of the class. |
| `relative_path` | TEXT | Relative path to the class or instance. |

## Additional Shared & POSIX Tables

### `disk_encryption`

Disk encryption status and information.

| Column | Type | Description |
| :--- | :--- | :--- |
| `name` | TEXT | Disk name |
| `uuid` | TEXT | Disk Universally Unique Identifier |
| `encrypted` | INTEGER | 1 If encrypted: true (disk is encrypted), else 0 |
| `type` | TEXT | Description of cipher type and mode if available |
| `encryption_status` | TEXT | Disk encryption status with one of following values: encrypted \| not encrypted \| undefined |
| `uid` | TEXT | Currently authenticated user if available |
| `user_uuid` | TEXT | UUID of authenticated user if available |
| `filevault_status` | TEXT | FileVault status with one of following values: on \| off \| unknown |

### `groups`

Local system groups.

| Column | Type | Description |
| :--- | :--- | :--- |
| `gid` | BIGINT | Unsigned int64 group ID |
| `gid_signed` | BIGINT | A signed int64 version of gid |
| `groupname` | TEXT | Canonical local group name |
| `group_sid` | TEXT | Unique group ID |
| `comment` | TEXT | Remarks or comments associated with the group |
| `is_hidden` | INTEGER | IsHidden attribute set in OpenDirectory |
| `pid_with_namespace` | INTEGER | Pids that contain a namespace |

### `listening_ports`

Processes with listening (bound) network sockets/ports.

| Column | Type | Description |
| :--- | :--- | :--- |
| `pid` | INTEGER | Process (or thread) ID |
| `port` | INTEGER | Transport layer port |
| `protocol` | INTEGER | Transport protocol (TCP/UDP) |
| `family` | INTEGER | Network protocol (IPv4, IPv6) |
| `address` | TEXT | Specific address for bind |
| `fd` | BIGINT | Socket file descriptor number |
| `socket` | BIGINT | Socket handle or inode number |
| `path` | TEXT | Path for UNIX domain sockets |
| `net_namespace` | TEXT | The inode number of the network namespace |

### `processes`

All running processes on the host system.

| Column | Type | Description |
| :--- | :--- | :--- |
| `pid` | BIGINT | Process (or thread) ID |
| `name` | TEXT | The process path or shorthand argv[0] |
| `path` | TEXT | Path to executed binary |
| `cmdline` | TEXT | Complete argv |
| `state` | TEXT | Process state |
| `cwd` | TEXT | Process current working directory |
| `root` | TEXT | Process virtual root directory |
| `uid` | BIGINT | Unsigned user ID |
| `gid` | BIGINT | Unsigned group ID |
| `euid` | BIGINT | Unsigned effective user ID |
| `egid` | BIGINT | Unsigned effective group ID |
| `suid` | BIGINT | Unsigned saved user ID |
| `sgid` | BIGINT | Unsigned saved group ID |
| `on_disk` | INTEGER | The process path exists yes=1, no=0, unknown=-1 |
| `wired_size` | BIGINT | Bytes of unpageable memory used by process |
| `resident_size` | BIGINT | Bytes of private memory used by process |
| `total_size` | BIGINT | Total virtual memory size (Linux, Windows) or |
| `user_time` | BIGINT | CPU time in milliseconds spent in user space |
| `system_time` | BIGINT | CPU time in milliseconds spent in kernel space |
| `disk_bytes_read` | BIGINT | Bytes read from disk |
| `disk_bytes_written` | BIGINT | Bytes written to disk |
| `start_time` | BIGINT | Process start time in seconds since Epoch, in case of error -1 |
| `parent` | BIGINT | Process parent |
| `pgroup` | BIGINT | Process group |
| `threads` | INTEGER | Number of threads used by process |
| `nice` | INTEGER | Process nice level (-20 to 20, default 0) |
| `elevated_token` | INTEGER | Process uses elevated token yes=1, no=0 |
| `secure_process` | INTEGER | Process is secure (IUM) yes=1, no=0 |
| `protection_type` | TEXT | The protection type of the process |
| `virtual_process` | INTEGER | Process is virtual (e.g. System, Registry, vmmem) yes=1, no=0 |
| `elapsed_time` | BIGINT | Elapsed time in seconds this process has been running. |
| `handle_count` | BIGINT | Total number of handles that the process has open. This number is the sum of the handles currently opened by each thread in the process. |
| `percent_processor_time` | BIGINT | Returns elapsed time that all of the threads of this process used the processor to execute instructions in 100 nanoseconds ticks. |
| `upid` | BIGINT | A 64bit pid that is never reused. Returns -1 if we couldn |
| `uppid` | BIGINT | The 64bit parent pid that is never reused. Returns -1 if we couldn |
| `cpu_type` | INTEGER | Indicates the specific processor designed for installation. |
| `cpu_subtype` | INTEGER | Indicates the specific processor on which an entry may be used. |
| `translated` | INTEGER | Indicates whether the process is running under the Rosetta Translation Environment, yes=1, no=0, error=-1. |
| `cgroup_path` | TEXT | The full hierarchical path of the process |

### `system_info`

System information for identification.

| Column | Type | Description |
| :--- | :--- | :--- |
| `hostname` | TEXT | Network hostname including domain |
| `uuid` | TEXT | Unique ID provided by the system |
| `cpu_type` | TEXT | CPU type |
| `cpu_subtype` | TEXT | CPU subtype |
| `cpu_brand` | TEXT | CPU brand string, contains vendor and model |
| `cpu_physical_cores` | INTEGER | Number of physical CPU cores in to the system |
| `cpu_logical_cores` | INTEGER | Number of logical CPU cores available to the system |
| `cpu_sockets` | INTEGER | Number of processor sockets in the system |
| `cpu_microcode` | TEXT | Microcode version |
| `physical_memory` | BIGINT | Total physical memory in bytes |
| `hardware_vendor` | TEXT | Hardware vendor |
| `hardware_model` | TEXT | Hardware model |
| `hardware_version` | TEXT | Hardware version |
| `hardware_serial` | TEXT | Device serial number |
| `board_vendor` | TEXT | Board vendor |
| `board_model` | TEXT | Board model |
| `board_version` | TEXT | Board version |
| `board_serial` | TEXT | Board serial number |
| `computer_name` | TEXT | Friendly computer name (optional) |
| `local_hostname` | TEXT | Local hostname (optional) |
| `emulated_cpu_type` | TEXT | Emulated CPU type |

### `uptime`

Track time passed since last boot. Some systems track this as calendar time, some as runtime.

| Column | Type | Description |
| :--- | :--- | :--- |
| `days` | INTEGER | Days of uptime |
| `hours` | INTEGER | Hours of uptime |
| `minutes` | INTEGER | Minutes of uptime |
| `seconds` | INTEGER | Seconds of uptime |
| `total_seconds` | BIGINT | Total uptime seconds |

### `users`

Local user accounts (including domain accounts that have logged on locally (Windows)).

| Column | Type | Description |
| :--- | :--- | :--- |
| `uid` | BIGINT | User ID |
| `gid` | BIGINT | Group ID (unsigned) |
| `uid_signed` | BIGINT | User ID as int64 signed (Apple) |
| `gid_signed` | BIGINT | Default group ID as int64 signed (Apple) |
| `username` | TEXT | Username |
| `description` | TEXT | Optional user description |
| `directory` | TEXT | User |
| `shell` | TEXT | User |
| `uuid` | TEXT | User |
| `type` | TEXT | Whether the account is roaming (domain), local, or a system profile |
| `is_hidden` | INTEGER | IsHidden attribute set in OpenDirectory |
| `pid_with_namespace` | INTEGER | Pids that contain a namespace |
| `include_remote` | INTEGER | 1 to include remote (LDAP/AD) accounts (default 0). Warning: without any uid/username filtering it may list whole LDAP directories |
