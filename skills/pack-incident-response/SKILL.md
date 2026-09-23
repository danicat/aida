---
name: pack-incident-response
description: Live incident response query pack for rapid host triage and forensics. Features 35 queries covering volatile processes, open sockets, listening ports, logged-in users, shell history, crontab, SUID binaries, kernel modules, and firewall rules. Use during active incident investigations and breach triage.
---

# Live Incident Response & Host Forensics Query Pack

The `pack-incident-response` skill equips agents with curated queries and diagnostic procedures from `osquery_data/packs/incident-response.conf`. This query pack focuses on live incident response & host forensics query pack.

## Threat Model & Scope
This pack is engineered for high-priority live host triage following a security alert or suspected breach. It covers:
- Volatile state: Current interactive user logins, active network connections, and unlinked running processes.
- Attacker command history: Recent bash and zsh commands in user profiles.
- Persistence mechanisms: Startup items, crontabs, launchd daemons, and SUID/SGID binaries.
- Kernel & filesystem integrity: Loaded kernel extensions, modified hosts files, and NFS mounts.

## Triage & Investigation Runbook
### Incident Triage Execution Phases
1. **Phase 1: Volatile Host Triage**:
   - Query `logged_in_users` and `last` to identify who is or was recently logged in.
   - Run `listening_ports` and `process_open_sockets` to map out active network conduits.
2. **Phase 2: Execution & Process Forensics**:
   - Query `processes` and `process_envs` for suspicious environment variables (e.g., `LD_PRELOAD`, `DYLD_INSERT_LIBRARIES`).
   - Query `shell_history` to inspect raw operator commands.
3. **Phase 3: Persistence & Privilege Escalation Audit**:
   - Run `crontab`, `startup_items`, `launchd`, and `suid_bin` queries.
4. **Phase 4: Containment**:
   - Isolate host from the network if active C2 connections or backdoor listeners are identified.

## Complete Query Catalog

### 1. `launchd`
- **Description**: Retrieves all the daemons that will run in the start of the target OSX system.
- **Context / Value**: Identify malware that uses this persistence mechanism to launch at system boot
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select * from launchd;
```

### 2. `startup_items`
- **Description**: Retrieve all the items that will load when the target OSX system starts.
- **Context / Value**: Identify malware that uses this persistence mechanism to launch at a given interval
- **Interval**: 86400 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select * from startup_items;
```

### 3. `crontab`
- **Description**: Retrieves all the jobs scheduled in crontab in the target system.
- **Context / Value**: Identify malware that uses this persistence mechanism to launch at a given interval
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select * from crontab;
```

### 4. `loginwindow1`
- **Description**: Retrieves all the values for the loginwindow process in the target OSX system.
- **Context / Value**: Identify malware that uses this persistence mechanism to launch at system boot
- **Interval**: 86400 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select key, subkey, value from plist where path = '/Library/Preferences/com.apple.loginwindow.plist';
```

### 5. `loginwindow2`
- **Description**: Retrieves all the values for the loginwindow process in the target OSX system.
- **Context / Value**: Identify malware that uses this persistence mechanism to launch at system boot
- **Interval**: 86400 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select key, subkey, value from plist where path = '/Library/Preferences/loginwindow.plist';
```

### 6. `loginwindow3`
- **Description**: Retrieves all the values for the loginwindow process in the target OSX system.
- **Context / Value**: Identify malware that uses this persistence mechanism to launch at system boot
- **Interval**: 86400 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select username, key, subkey, value from plist p, (select * from users where directory like '/Users/%') u where p.path = u.directory || '/Library/Preferences/com.apple.loginwindow.plist';
```

### 7. `loginwindow4`
- **Description**: Retrieves all the values for the loginwindow process in the target OSX system.
- **Context / Value**: Identify malware that uses this persistence mechanism to launch at system boot
- **Interval**: 86400 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select username, key, subkey, value from plist p, (select * from users where directory like '/Users/%') u where p.path = u.directory || '/Library/Preferences/loginwindow.plist';
```

### 8. `alf`
- **Description**: Retrieves the configuration values for the Application Layer Firewall for OSX.
- **Context / Value**: Verify firewall settings are as restrictive as you need. Identify unwanted firewall holes made by malware or humans
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select * from alf;
```

### 9. `alf_exceptions`
- **Description**: Retrieves the exceptions for the Application Layer Firewall in OSX.
- **Context / Value**: Verify firewall settings are as restrictive as you need. Identify unwanted firewall holes made by malware or humans
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select * from alf_exceptions;
```

### 10. `alf_services`
- **Description**: Retrieves the services for the Application Layer Firewall in OSX.
- **Context / Value**: Verify firewall settings are as restrictive as you need. Identify unwanted firewall holes made by malware or humans
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select * from alf_services;
```

### 11. `alf_explicit_auths`
- **Description**: Retrieves the list of processes with explicit authorization for the Application Layer Firewall.
- **Context / Value**: Verify firewall settings are as restrictive as you need. Identify unwanted firewall holes made by malware or humans
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select * from alf_explicit_auths;
```

### 12. `etc_hosts`
- **Description**: Retrieves all the entries in the target system /etc/hosts file.
- **Context / Value**: Identify network communications that are being redirected. Example: identify if security logging has been disabled
- **Interval**: 86400 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select * from etc_hosts;
```

### 13. `kextstat`
- **Description**: Retrieves all the information about the current kernel extensions for the target OSX system.
- **Context / Value**: Identify malware that has a kernel extension component.
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select * from kernel_extensions;
```

### 14. `kernel_modules`
- **Description**: Retrieves all the information for the current kernel modules in the target Linux system.
- **Context / Value**: Identify malware that has a kernel module component.
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select * from kernel_modules;
```

### 15. `last`
- **Description**: Retrieves the list of the latest logins with PID, username and timestamp.
- **Context / Value**: Useful for intrusion detection and incident response. Verify assumptions of what accounts should be accessing what systems and identify machines accessed during a compromise.
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select * from last;
```

### 16. `installed_applications`
- **Description**: Retrieves all the currently installed applications in the target OSX system.
- **Context / Value**: Identify malware, adware, or vulnerable packages that are installed as an application.
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select * from apps;
```

### 17. `open_sockets`
- **Description**: Retrieves all the open sockets per process in the target system.
- **Context / Value**: Identify malware via connections to known bad IP addresses as well as odd local or remote port bindings
- **Interval**: 86400 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select distinct pid, family, protocol, local_address, local_port, remote_address, remote_port, path from process_open_sockets where path <> '' or remote_address <> '';
```

### 18. `open_files`
- **Description**: Retrieves all the open files per process in the target system.
- **Context / Value**: Identify processes accessing sensitive files they shouldn't
- **Interval**: 86400 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select distinct pid, path from process_open_files where path not like '/private/var/folders%' and path not like '/System/Library/%' and path not in ('/dev/null', '/dev/urandom', '/dev/random');
```

### 19. `logged_in_users`
- **Description**: Retrieves the list of all the currently logged in users in the target system.
- **Context / Value**: Useful for intrusion detection and incident response. Verify assumptions of what accounts should be accessing what systems and identify machines accessed during a compromise.
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select liu.*, p.name, p.cmdline, p.cwd, p.root from logged_in_users liu, processes p where liu.pid = p.pid;
```

### 20. `ip_forwarding`
- **Description**: Retrieves the current status of IP/IPv6 forwarding.
- **Context / Value**: Identify if a machine is being used as relay.
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select * from system_controls where oid = '4.30.41.1' union select * from system_controls where oid = '4.2.0.1';
```

### 21. `process_env`
- **Description**: Retrieves all the environment variables per process in the target system.
- **Context / Value**: Insight into the process data: Where was it started from, was it preloaded...
- **Interval**: 86400 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select * from process_envs;
```

### 22. `mounts`
- **Description**: Retrieves the current list of mounted drives in the target system.
- **Context / Value**: Scope for lateral movement. Potential exfiltration locations. Potential dormant backdoors.
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select * from mounts;
```

### 23. `nfs_shares`
- **Description**: Retrieves the current list of Network File System mounted shares.
- **Context / Value**: Scope for lateral movement. Potential exfiltration locations. Potential dormant backdoors.
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select * from nfs_shares;
```

### 24. `shell_history`
- **Description**: Retrieves the command history, per user, by parsing the shell history files.
- **Context / Value**: Identify actions taken. Useful for compromised hosts.
- **Interval**: 86400 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select * from users join shell_history using (uid);
```

### 25. `recent_items`
- **Description**: Retrieves the list of recent items opened in OSX by parsing the plist per user.
- **Context / Value**: Identify recently accessed items. Useful for compromised hosts.
- **Interval**: 86400 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select username, key, value from plist p, (select * from users where directory like '/Users/%') u where p.path = u.directory || '/Library/Preferences/com.apple.recentitems.plist';
```

### 26. `ramdisk`
- **Description**: Retrieves all the ramdisk currently mounted in the target system.
- **Context / Value**: Identify if an attacker is using temporary, memory storage to avoid touching disk for anti-forensics purposes
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select * from block_devices where type = 'Virtual Interface';
```

### 27. `listening_ports`
- **Description**: Retrieves all the listening ports in the target system.
- **Context / Value**: Detect if a listening port iis not mapped to a known process. Find backdoors.
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select * from listening_ports;
```

### 28. `suid_bin`
- **Description**: Retrieves all the files in the target system that are setuid enabled.
- **Context / Value**: Detect backdoor binaries (attacker may drop a copy of /bin/sh). Find potential elevation points / vulnerabilities in the standard build.
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select * from suid_bin;
```

### 29. `process_memory`
- **Description**: Retrieves the memory map per process in the target Linux or macOS system.
- **Context / Value**: Ability to compare with known good. Identify mapped regions corresponding with or containing injected code.
- **Interval**: 86400 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select * from process_memory_map;
```

### 30. `arp_cache`
- **Description**: Retrieves the ARP cache values in the target system.
- **Context / Value**: Determine if MITM in progress.
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select * from arp_cache;
```

### 31. `wireless_networks`
- **Description**: Retrieves all the remembered wireless network that the target machine has connected to.
- **Context / Value**: Identifies connections to rogue access points.
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: 1.6.0
- **SQL Query**:
```sql
select ssid, network_name, security_type, last_connected, captive_portal, possibly_hidden, roaming, roaming_profile from wifi_networks;
```

### 32. `disk_encryption`
- **Description**: Retrieves the current disk encryption status for the target system.
- **Context / Value**: Identifies a system potentially vulnerable to disk cloning.
- **Interval**: 86400 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select * from disk_encryption;
```

### 33. `iptables`
- **Description**: Retrieves the current filters and chains per filter in the target system.
- **Context / Value**: Verify firewall settings are as restrictive as you need. Identify unwanted firewall holes made by malware or humans
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select * from iptables;
```

### 34. `app_schemes`
- **Description**: Retrieves the list of application scheme/protocol-based IPC handlers.
- **Context / Value**: Post-priori hijack detection, detect potential sensitive information leakage.
- **Interval**: 86400 seconds
- **Minimum Osquery Version**: 1.4.7
- **SQL Query**:
```sql
select * from app_schemes;
```

### 35. `sandboxes`
- **Description**: Lists the application bundle that owns a sandbox label.
- **Context / Value**: Post-priori hijack detection, detect potential sensitive information leakage.
- **Interval**: 86400 seconds
- **Minimum Osquery Version**: 1.4.7
- **SQL Query**:
```sql
select * from sandboxes;
```

## Referenced Table Schemas

### `alf`

macOS application layer firewall (ALF) service details.

| Column | Type | Description |
| :--- | :--- | :--- |
| `allow_signed_enabled` | INTEGER | 1 If allow signed mode is enabled else 0 (not supported on macOS 15+) |
| `firewall_unload` | INTEGER | 1 If firewall unloading enabled else 0 (not supported on macOS 15+) |
| `global_state` | INTEGER | 1 If the firewall is enabled with exceptions, 2 if the firewall is configured to block all incoming connections, else 0 |
| `logging_enabled` | INTEGER | 1 If logging mode is enabled else 0 |
| `logging_option` | INTEGER | Firewall logging option (not supported on macOS 15+) |
| `stealth_enabled` | INTEGER | 1 If stealth mode is enabled else 0 |
| `version` | TEXT | Application Layer Firewall version |

### `alf_exceptions`

macOS application layer firewall (ALF) service exceptions.

| Column | Type | Description |
| :--- | :--- | :--- |
| `path` | TEXT | Path to the executable that is excepted. On macOS 15+ this can also be a bundle identifier |
| `state` | INTEGER | Firewall exception state. 0 if the application is configured to allow incoming connections, 2 if the application is configured to block incoming connections and 3 if the application is configuted to allow incoming connections but with additional restrictions. |

### `alf_explicit_auths`

ALF services explicitly allowed to perform networking. Not supported on macOS 15+ (returns no results).

| Column | Type | Description |
| :--- | :--- | :--- |
| `process` | TEXT | Process name that is explicitly allowed |

### `app_schemes`

macOS application schemes and handlers (e.g., http, file, mailto).

| Column | Type | Description |
| :--- | :--- | :--- |
| `scheme` | TEXT | Name of the scheme/protocol |
| `handler` | TEXT | Application label for the handler |
| `enabled` | INTEGER | 1 if this handler is the OS default, else 0 |
| `external` | INTEGER | 1 if this handler does NOT exist on macOS by default, else 0 |
| `protected` | INTEGER | 1 if this handler is protected (reserved) by macOS, else 0 |

### `apps`

macOS applications installed in known search paths (e.g., /Applications).

| Column | Type | Description |
| :--- | :--- | :--- |
| `name` | TEXT | Name of the Name.app folder |
| `path` | TEXT | Absolute and full Name.app path |
| `bundle_executable` | TEXT | Info properties CFBundleExecutable label |
| `bundle_identifier` | TEXT | Info properties CFBundleIdentifier label |
| `bundle_name` | TEXT | Info properties CFBundleName label |
| `bundle_short_version` | TEXT | Info properties CFBundleShortVersionString label |
| `bundle_version` | TEXT | Info properties CFBundleVersion label |
| `bundle_package_type` | TEXT | Info properties CFBundlePackageType label |
| `environment` | TEXT | Application-set environment variables |
| `element` | TEXT | Does the app identify as a background agent |
| `compiler` | TEXT | Info properties DTCompiler label |
| `development_region` | TEXT | Info properties CFBundleDevelopmentRegion label |
| `display_name` | TEXT | Info properties CFBundleDisplayName label |
| `info_string` | TEXT | Info properties CFBundleGetInfoString label |
| `minimum_system_version` | TEXT | Minimum version of macOS required for the app to run |
| `category` | TEXT | The UTI that categorizes the app for the App Store |
| `applescript_enabled` | TEXT | Info properties NSAppleScriptEnabled label |
| `copyright` | TEXT | Info properties NSHumanReadableCopyright label |
| `last_opened_time` | DOUBLE | The time that the app was last used |

### `arp_cache`

Address resolution cache, both static and dynamic (from ARP, NDP).

| Column | Type | Description |
| :--- | :--- | :--- |
| `address` | TEXT | IPv4 address target |
| `mac` | TEXT | MAC address of broadcasted address |
| `interface` | TEXT | Interface of the network for the MAC |
| `permanent` | TEXT | 1 for true, 0 for false |

### `block_devices`

Block (buffered access) device file nodes: disks, ramdisks, and DMG containers.

| Column | Type | Description |
| :--- | :--- | :--- |
| `name` | TEXT | Block device name |
| `parent` | TEXT | Block device parent name |
| `vendor` | TEXT | Block device vendor string |
| `model` | TEXT | Block device model string identifier |
| `serial` | TEXT | Disk serial number |
| `size` | BIGINT | Block device size in blocks |
| `block_size` | INTEGER | Block size in bytes |
| `uuid` | TEXT | Block device Universally Unique Identifier |
| `type` | TEXT | Block device type string |
| `label` | TEXT | Block device label string |

### `crontab`

Line parsed values from system and user cron/tab.

| Column | Type | Description |
| :--- | :--- | :--- |
| `event` | TEXT | The job @event name (rare) |
| `minute` | TEXT | The exact minute for the job |
| `hour` | TEXT | The hour of the day for the job |
| `day_of_month` | TEXT | The day of the month for the job |
| `month` | TEXT | The month of the year for the job |
| `day_of_week` | TEXT | The day of the week for the job |
| `command` | TEXT | Raw command string |
| `path` | TEXT | File parsed |
| `pid_with_namespace` | INTEGER | Pids that contain a namespace |

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

### `etc_hosts`

Line-parsed /etc/hosts.

| Column | Type | Description |
| :--- | :--- | :--- |
| `address` | TEXT | IP address mapping |
| `hostnames` | TEXT | Raw hosts mapping |
| `pid_with_namespace` | INTEGER | Pids that contain a namespace |

### `iptables`

Linux IP packet filtering and NAT tool.

| Column | Type | Description |
| :--- | :--- | :--- |
| `filter_name` | TEXT | Packet matching filter table name. |
| `chain` | TEXT | Size of module content. |
| `policy` | TEXT | Policy that applies for this rule. |
| `target` | TEXT | Target that applies for this rule. |
| `protocol` | INTEGER | Protocol number identification. |
| `src_port` | TEXT | Protocol source port(s). |
| `dst_port` | TEXT | Protocol destination port(s). |
| `src_ip` | TEXT | Source IP address. |
| `src_mask` | TEXT | Source IP address mask. |
| `iniface` | TEXT | Input interface for the rule. |
| `iniface_mask` | TEXT | Input interface mask for the rule. |
| `dst_ip` | TEXT | Destination IP address. |
| `dst_mask` | TEXT | Destination IP address mask. |
| `outiface` | TEXT | Output interface for the rule. |
| `outiface_mask` | TEXT | Output interface mask for the rule. |
| `match` | TEXT | Matching rule that applies. |
| `packets` | INTEGER | Number of matching packets for this rule. |
| `bytes` | INTEGER | Number of matching bytes for this rule. |

### `kernel_extensions`

| Column | Type | Description |
| :--- | :--- | :--- |
| `idx` | INTEGER | Extension load tag or index |
| `refs` | INTEGER | Reference count |
| `size` | BIGINT | Bytes of wired memory used by extension |
| `name` | TEXT | Extension label |
| `version` | TEXT | Extension version |
| `linked_against` | TEXT | Indexes of extensions this extension is linked against |
| `path` | TEXT | Optional path to extension bundle |

### `kernel_modules`

Linux kernel modules both loaded and within the load search path.

| Column | Type | Description |
| :--- | :--- | :--- |
| `name` | TEXT | Module name |
| `size` | BIGINT | Size of module content |
| `used_by` | TEXT | Module reverse dependencies |
| `status` | TEXT | Kernel module status |
| `address` | TEXT | Kernel module address |

### `last`

System logins and logouts.

| Column | Type | Description |
| :--- | :--- | :--- |
| `username` | TEXT | Entry username |
| `tty` | TEXT | Entry terminal |
| `pid` | INTEGER | Process (or thread) ID |
| `type` | INTEGER | Entry type, according to ut_type types (utmp.h) |
| `type_name` | TEXT | Entry type name, according to ut_type types (utmp.h) |
| `time` | INTEGER | Entry timestamp |
| `host` | TEXT | Entry hostname |

### `launchd`

LaunchAgents and LaunchDaemons from default search paths.

| Column | Type | Description |
| :--- | :--- | :--- |
| `path` | TEXT | Path to daemon or agent plist |
| `name` | TEXT | File name of plist (used by launchd) |
| `label` | TEXT | Daemon or agent service name |
| `program` | TEXT | Path to target program |
| `run_at_load` | TEXT | Should the program run on launch load |
| `keep_alive` | TEXT | Should the process be restarted if killed |
| `on_demand` | TEXT | Deprecated key, replaced by keep_alive |
| `disabled` | TEXT | Skip loading this daemon or agent on boot |
| `username` | TEXT | Run this daemon or agent as this username |
| `groupname` | TEXT | Run this daemon or agent as this group |
| `stdout_path` | TEXT | Pipe stdout to a target path |
| `stderr_path` | TEXT | Pipe stderr to a target path |
| `start_interval` | TEXT | Frequency to run in seconds |
| `program_arguments` | TEXT | Command line arguments passed to program |
| `watch_paths` | TEXT | Key that launches daemon or agent if path is modified |
| `queue_directories` | TEXT | Similar to watch_paths but only with non-empty directories |
| `inetd_compatibility` | TEXT | Run this daemon or agent as it was launched from inetd |
| `start_on_mount` | TEXT | Run daemon or agent every time a filesystem is mounted |
| `root_directory` | TEXT | Key used to specify a directory to chroot to before launch |
| `working_directory` | TEXT | Key used to specify a directory to chdir to before launch |
| `process_type` | TEXT | Key describes the intended purpose of the job |

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

### `logged_in_users`

Users with an active shell on the system.

| Column | Type | Description |
| :--- | :--- | :--- |
| `type` | TEXT | Login type |
| `user` | TEXT | User login name |
| `tty` | TEXT | Device name |
| `host` | TEXT | Remote hostname |
| `time` | BIGINT | Time entry was made |
| `pid` | INTEGER | Process (or thread) ID |
| `sid` | TEXT | The user |
| `registry_hive` | TEXT | HKEY_USERS registry hive |

### `mounts`

System mounted devices and filesystems (not process specific).

| Column | Type | Description |
| :--- | :--- | :--- |
| `device` | TEXT | Mounted device |
| `device_alias` | TEXT | Mounted device alias |
| `path` | TEXT | Mounted device path |
| `type` | TEXT | Mounted device type |
| `blocks_size` | BIGINT | Block size in bytes |
| `blocks` | BIGINT | Mounted device used blocks |
| `blocks_free` | BIGINT | Mounted device blocks available to root users, a superset of blocks_available |
| `blocks_available` | BIGINT | Mounted device blocks available to non-root users |
| `inodes` | BIGINT | Mounted device used inodes |
| `inodes_free` | BIGINT | Mounted device free inodes |
| `flags` | TEXT | Mounted device flags |

### `nfs_shares`

NFS shares exported by the host.

| Column | Type | Description |
| :--- | :--- | :--- |
| `share` | TEXT | Filesystem path to the share |
| `options` | TEXT | Options string set on the export share |
| `readonly` | INTEGER | 1 if the share is exported readonly else 0 |

### `plist`

Read and parse a plist file.

| Column | Type | Description |
| :--- | :--- | :--- |
| `key` | TEXT | Preference top-level key |
| `subkey` | TEXT | Intermediate key path, includes lists/dicts |
| `value` | TEXT | String value of most CF types |
| `path` | TEXT | (required) read preferences from a plist |

### `process_envs`

A key/value table of environment variables for each process.

| Column | Type | Description |
| :--- | :--- | :--- |
| `pid` | INTEGER | Process (or thread) ID |
| `key` | TEXT | Environment variable name |
| `value` | TEXT | Environment variable value |

### `process_memory_map`

Process memory mapped files and pseudo device/regions.

| Column | Type | Description |
| :--- | :--- | :--- |
| `pid` | INTEGER | Process (or thread) ID |
| `start` | TEXT | Virtual start address (hex) |
| `end` | TEXT | Virtual end address (hex) |
| `permissions` | TEXT | r=read, w=write, x=execute, p=private (cow) |
| `offset` | BIGINT | Offset into mapped path |
| `device` | TEXT | MA:MI Major/minor device ID |
| `inode` | INTEGER | Mapped path inode, 0 means uninitialized (BSS) |
| `path` | TEXT | Path to mapped file or mapped type |
| `pseudo` | INTEGER | 1 If path is a pseudo path, else 0 |

### `process_open_files`

File descriptors for each process.

| Column | Type | Description |
| :--- | :--- | :--- |
| `pid` | BIGINT | Process (or thread) ID |
| `fd` | BIGINT | Process-specific file descriptor number |
| `path` | TEXT | Filesystem path of descriptor |

### `process_open_sockets`

Processes which have open network sockets on the system.

| Column | Type | Description |
| :--- | :--- | :--- |
| `pid` | INTEGER | Process (or thread) ID |
| `fd` | BIGINT | Socket file descriptor number |
| `socket` | BIGINT | Socket handle or inode number |
| `family` | INTEGER | Network protocol (IPv4, IPv6) |
| `protocol` | INTEGER | Transport protocol (TCP/UDP) |
| `local_address` | TEXT | Socket local address |
| `remote_address` | TEXT | Socket remote address |
| `local_port` | INTEGER | Socket local port |
| `remote_port` | INTEGER | Socket remote port |
| `path` | TEXT | For UNIX sockets (family=AF_UNIX), the domain path |
| `state` | TEXT | TCP socket state |
| `net_namespace` | TEXT | The inode number of the network namespace |

### `sandboxes`

macOS application sandboxes container details.

| Column | Type | Description |
| :--- | :--- | :--- |
| `label` | TEXT | UTI-format bundle or label ID |
| `user` | TEXT | Sandbox owner |
| `enabled` | INTEGER | Application sandboxings enabled on container |
| `build_id` | TEXT | Sandbox-specific identifier |
| `bundle_path` | TEXT | Application bundle used by the sandbox |
| `path` | TEXT | Path to sandbox container directory |

### `shell_history`

A line-delimited (command) table of per-user .*_history data.

| Column | Type | Description |
| :--- | :--- | :--- |
| `uid` | BIGINT | Shell history owner |
| `time` | INTEGER | Entry timestamp. It could be absent, default value is 0. |
| `command` | TEXT | Unparsed date/line/command history line |
| `history_file` | TEXT | Path to the .*_history for this user |

### `startup_items`

Applications and binaries set as startup items.

| Column | Type | Description |
| :--- | :--- | :--- |
| `name` | TEXT | Name of startup item |
| `path` | TEXT | Path of startup item |
| `args` | TEXT | Arguments provided to startup executable |
| `type` | TEXT | Type of startup item. On macOS this can be app, agent (LaunchAgent), daemon (LaunchDaemon), login item, or user item. |
| `source` | TEXT | Directory containing startup item (on macOS, the subsystem providing it) |
| `status` | TEXT | Startup status. On Linux: enabled or disabled. On macOS: Combination of enabled, allowed, notified, and hidden. Apple does not seem to document these status values, but allowed seems to indicate whether it is enabled in System Settings. |
| `username` | TEXT | The user associated with the startup item |

### `suid_bin`

suid binaries in common locations.

| Column | Type | Description |
| :--- | :--- | :--- |
| `path` | TEXT | Binary path |
| `username` | TEXT | Binary owner username |
| `groupname` | TEXT | Binary owner group |
| `permissions` | TEXT | Binary permissions |
| `pid_with_namespace` | INTEGER | Pids that contain a namespace |

### `system_controls`

sysctl names, values, and settings information.

| Column | Type | Description |
| :--- | :--- | :--- |
| `name` | TEXT | Full sysctl MIB name |
| `oid` | TEXT | Control MIB |
| `subsystem` | TEXT | Subsystem ID, control type |
| `current_value` | TEXT | Value of setting |
| `config_value` | TEXT | The MIB value set in /etc/sysctl.conf |
| `type` | TEXT | Data type |
| `field_name` | TEXT | Specific attribute of opaque type |

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

### `wifi_networks`

macOS known/remembered Wi-Fi networks list.

| Column | Type | Description |
| :--- | :--- | :--- |
| `ssid` | TEXT | SSID octets of the network |
| `network_name` | TEXT | Name of the network |
| `security_type` | TEXT | Type of security on this network |
| `last_connected` | INTEGER | Last time this network was connected to as a unix_time (max of last_connected_automatic and last_connected_manual, if available) |
| `last_connected_automatic` | INTEGER | Last time this network was automatically connected to by the system as a unix_time |
| `last_connected_manual` | INTEGER | Last time this network was manually connected to by the user as a unix_time |
| `passpoint` | INTEGER | 1 if Passpoint is supported, 0 otherwise |
| `possibly_hidden` | INTEGER | 1 if network is possibly a hidden network, 0 otherwise |
| `roaming` | INTEGER | 1 if roaming is supported, 0 otherwise |
| `roaming_profile` | TEXT | Describe the roaming profile, usually one of Single, Dual  or Multi |
| `auto_login` | INTEGER | 1 if auto login is enabled, 0 otherwise |
| `temporarily_disabled` | INTEGER | 1 if this network is temporarily disabled, 0 otherwise |
| `disabled` | INTEGER | 1 if this network is disabled, 0 otherwise |
| `add_reason` | TEXT | Shows why this network was added, via menubar or command line or something else |
| `added_at` | INTEGER | Time this network was added as a unix_time |
| `captive_portal` | INTEGER | 1 if this network has a captive portal, 0 otherwise |
| `captive_login_date` | INTEGER | Time this network logged in to a captive portal as unix_time |
| `was_captive_network` | INTEGER | 1 if this network was previously a captive network, 0 otherwise |
| `auto_join` | INTEGER | 1 if this network set to join automatically, 0 otherwise |
| `personal_hotspot` | INTEGER | 1 if this network is a personal hotspot, 0 otherwise |
