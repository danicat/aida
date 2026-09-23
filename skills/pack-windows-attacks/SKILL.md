---
name: pack-windows-attacks
description: Windows threat and persistence detection query pack. Contains 14 queries targeting accessibility backdoor replaces (StickyKeys/Utilman), malicious service installations, registry Run keys, unusual startup processes, and ransomware indicators. Use when hunting for Windows intrusions and persistence.
---

# Windows Attack & Persistence Detection Query Pack

The `pack-windows-attacks` skill equips agents with curated queries and diagnostic procedures from `osquery_data/packs/windows-attacks.conf`. This query pack focuses on windows attack & persistence detection query pack.

## Threat Model & Scope
This pack focuses on prevalent Windows post-exploitation techniques:
- Accessibility backdoor hijacks: Replacing `sethc.exe` (Sticky Keys) or `utilman.exe` with `cmd.exe` or debugger redirects.
- Malicious service creation: Services pointing to user directories, temp directories, or unquoted service paths.
- Registry autostart persistence: Suspicious binaries executed via Run/RunOnce keys.
- Known malicious hashes: Files matching known malware signatures.

## Triage & Investigation Runbook
### Windows Threat Investigation Protocol
1. **Inspect Accessibility Backdoors**: Verify if `sethc.exe` or `utilman.exe` registry entries have a `Debugger` value assigned.
2. **Audit Startup Keys**: Run queries against `HKEY_LOCAL_MACHINE\Software\Microsoft\Windows\CurrentVersion\Run`.
3. **Containment**: If an unauthorized service or autostart binary is found, stop the service via `sc.exe stop <name>`, disable startup entry, and isolate the endpoint.

## Complete Query Catalog

### 1. `CCleaner_Trojan.Floxif`
- **Description**: (https://sensorstechforum.com/ccleaner-trojan-floxif-malware-how-to-remove/)
- **Context / Value**: Artifact used by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: 2.2.1
- **SQL Query**:
```sql
select * from registry where path like 'HKEY_LOCAL_MACHINE\SOFTWARE\Piriform\Agomo%';
```

### 2. `CCleaner_Trojan_stage2.Floxif`
- **Description**: (https://sensorstechforum.com/ccleaner-trojan-floxif-malware-how-to-remove/)
- **Context / Value**: Artifact used by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: 2.1.0
- **SQL Query**:
```sql
select h.md5, h.sha1, h.sha256, s.name, s.service_type, s.display_name, s.module_path, s.user_account from services s, hash h where h.path = s.module_path and ((s.module_path like '%GeeSetup_x86%' and h.sha256 = 'dc9b5e8aa6ec86db8af0a7aa897ca61db3e5f3d2e0942e319074db1aaccfdc83') or (s.module_path like '%EFACli64%' and h.sha256 = '128aca58be325174f0220bd7ca6030e4e206b4378796e82da460055733bb6f4f') or (s.module_path like '%TSMSISrv%' and h.sha256 = '07fb252d2e853a9b1b32f30ede411f2efbb9f01e4a7782db5eacf3f55cf34902'));
```

### 3. `Winsecurity_info_1`
- **Description**: (https://sensorstechforum.com/windows-infected-2-viruses-scam-remove/)
- **Context / Value**: Artifact used by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: 2.2.1
- **SQL Query**:
```sql
select * from programs where name = 'Winsecurity.info';
```

### 4. `Winsecurity_info_2`
- **Description**: (https://sensorstechforum.com/windows-infected-2-viruses-scam-remove/)
- **Context / Value**: Artifact used by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: 2.2.1
- **SQL Query**:
```sql
select * from chrome_extensions join users using (uid) where name = 'Winsecurity.info';
```

### 5. `unTabs_1`
- **Description**: (https://sensorstechforum.com/untabs-browser-extension-virus-remove-completely/)
- **Context / Value**: Artifact used by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: 2.2.1
- **SQL Query**:
```sql
select * from programs where name like 'unTabs%';
```

### 6. `unTabs_2`
- **Description**: (https://sensorstechforum.com/untabs-browser-extension-virus-remove-completely/)
- **Context / Value**: Artifact used by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: 2.2.1
- **SQL Query**:
```sql
select * from chrome_extensions join users using (uid) where name like 'unTabs%';
```

### 7. `StickyKeys_File_Replace_Backdoor`
- **Description**: Checks the hashes of accessibility tools to ensure they don't match the hashes of cmd.exe, powershell.exe, or explorer.exe. More info: (https://github.com/TrullJ/sticky-keys-scanner/blob/master/TestFor-StickyKey.ps1)
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: 2.2.1
- **SQL Query**:
```sql
SELECT * FROM hash WHERE (path='c:\windows\system32\osk.exe' OR path='c:\windows\system32\sethc.exe' OR path='c:\windows\system32\narrator.exe' OR path='c:\windows\system32\magnify.exe' OR path='c:\windows\system32\displayswitch.exe') AND sha256 IN (SELECT sha256 FROM hash WHERE path='c:\windows\system32\cmd.exe' OR path='c:\windows\system32\WindowsPowerShell\v1.0\powershell.exe' OR path='c:\windows\system32\explorer.exe') AND sha256!='e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855';
```

### 8. `StickyKeys_Registry_Backdoor`
- **Description**: Searches for the presence of the 'Debugger' registry key for common Windows accessibility tools. More info: (https://blogs.technet.microsoft.com/jonathantrull/2016/10/03/detecting-sticky-key-backdoors/)
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: 2.2.1
- **SQL Query**:
```sql
SELECT * FROM registry WHERE key LIKE 'HKEY_LOCAL_MACHINE\Software\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\%%' and name='Debugger';
```

### 9. `conhost.exe_incorrect_path`
- **Description**: Detect processes masquerading as legitimate Windows processes
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: 2.2.1
- **SQL Query**:
```sql
SELECT * FROM processes WHERE LOWER(name)='conhost.exe' AND LOWER(path)!='c:\windows\system32\conhost.exe' AND path!='';
```

### 10. `dllhost.exe_incorrect_path`
- **Description**: Detect processes masquerading as legitimate Windows processes
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: 2.2.1
- **SQL Query**:
```sql
SELECT * FROM processes WHERE LOWER(name)='dllhost.exe' AND LOWER(path)!='c:\windows\system32\dllhost.exe' AND LOWER(path)!='c:\windows\syswow64\dllhost.exe' AND path!='';
```

### 11. `lsass.exe_incorrect_path`
- **Description**: Detect processes masquerading as legitimate Windows processes
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: 2.2.1
- **SQL Query**:
```sql
SELECT * FROM processes WHERE LOWER(name)='lsass.exe' AND LOWER(path)!='c:\windows\system32\lsass.exe' AND path!='';
```

### 12. `services.exe_incorrect_parent_process`
- **Description**: Detect processes masquerading as legitimate Windows processes
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: 2.2.1
- **SQL Query**:
```sql
SELECT name FROM processes WHERE pid=(SELECT parent FROM processes WHERE LOWER(name)='services.exe') AND LOWER(name)!='wininit.exe';
```

### 13. `svchost.exe_incorrect_path`
- **Description**: Detect processes masquerading as legitimate Windows processes
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: 2.2.1
- **SQL Query**:
```sql
SELECT * FROM processes WHERE LOWER(name)='svchost.exe' AND LOWER(path)!='c:\windows\system32\svchost.exe' AND LOWER(path)!='c:\windows\syswow64\svchost.exe' AND path!='';
```

### 14. `svchost.exe_incorrect_parent_process`
- **Description**: Detect processes masquerading as legitimate Windows processes
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: 2.2.1
- **SQL Query**:
```sql
SELECT name FROM processes WHERE pid=(SELECT parent FROM processes WHERE LOWER(name)='svchost.exe') AND LOWER(name)!='services.exe';
```

## Referenced Table Schemas

### `chrome_extensions`

Chrome-based browser extensions.

| Column | Type | Description |
| :--- | :--- | :--- |
| `browser_type` | TEXT | The browser type (Valid values: chrome, chromium, opera, yandex, brave, edge, edge_beta) |
| `uid` | BIGINT | The local user that owns the extension |
| `name` | TEXT | Extension display name |
| `profile` | TEXT | The name of the Chrome profile that contains this extension |
| `profile_path` | TEXT | The profile path |
| `referenced_identifier` | TEXT | Extension identifier, as specified by the preferences file. Empty if the extension is not in the profile. |
| `identifier` | TEXT | Extension identifier, computed from its manifest. Empty in case of error. |
| `version` | TEXT | Extension-supplied version |
| `description` | TEXT | Extension-optional description |
| `default_locale` | TEXT | Default locale supported by extension |
| `current_locale` | TEXT | Current locale supported by extension |
| `update_url` | TEXT | Extension-supplied update URI |
| `author` | TEXT | Optional extension author |
| `persistent` | INTEGER | 1 If extension is persistent across all tabs else 0 |
| `path` | TEXT | Path to extension folder |
| `permissions` | TEXT | The permissions required by the extension |
| `permissions_json` | TEXT | The JSON-encoded permissions required by the extension |
| `optional_permissions` | TEXT | The permissions optionally required by the extensions |
| `optional_permissions_json` | TEXT | The JSON-encoded permissions optionally required by the extensions |
| `manifest_hash` | TEXT | The SHA256 hash of the manifest.json file |
| `referenced` | BIGINT | 1 if this extension is referenced by the Preferences file of the profile |
| `from_webstore` | TEXT | True if this extension was installed from the web store |
| `state` | TEXT | 1 if this extension is enabled |
| `install_time` | TEXT | Extension install time, in its original Webkit format |
| `install_timestamp` | BIGINT | Extension install time, converted to unix time |
| `manifest_json` | TEXT | The manifest file of the extension |
| `key` | TEXT | The extension key, from the manifest file |

### `hash`

Filesystem hash data.

| Column | Type | Description |
| :--- | :--- | :--- |
| `path` | TEXT | Must provide a path or directory |
| `directory` | TEXT | Must provide a path or directory |
| `md5` | TEXT | MD5 hash of provided filesystem data |
| `sha1` | TEXT | SHA1 hash of provided filesystem data |
| `sha256` | TEXT | SHA256 hash of provided filesystem data |
| `pid_with_namespace` | INTEGER | Pids that contain a namespace |
| `mount_namespace_id` | TEXT | Mount namespace id |

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
