---
name: osquery-linux
description: Linux system diagnostics and osquery schema reference. Provides tables for systemd units, deb and rpm packages, iptables, process sockets, shadow, crontab, kernel modules, syslog, and AppArmor/SELinux. Use for Linux daemon management, persistence hunting, network auditing, and privilege checks.
---

# Linux Osquery Diagnostics and Schema Reference

The `osquery-linux` skill provides comprehensive osquery table schemas, diagnostic queries, and incident investigation runbooks tailored specifically for Linux systems. Agents should load this skill when diagnosing system health, hunting for threats or persistence, inspecting system configurations, or auditing compliance on Linux hosts.

## Diagnostic Runbooks & Investigation Workflows

### Systemd Services & Timers Triage
Audit active, failed, and suspicious systemd units:
```sql
-- Find failed or unusual systemd services
SELECT id, description, load_state, active_state, sub_state, unit_file_state
FROM systemd_units
WHERE active_state = 'failed' OR id LIKE '%.timer';

-- List recently modified or non-standard systemd service paths
SELECT name, path, mtime, size FROM file 
WHERE directory IN ('/etc/systemd/system', '/lib/systemd/system') 
  AND type = 'regular';
```

### Persistence Hunting via Crontab & Shell Profiles
Check scheduled cron jobs and user shell startup scripts:
```sql
-- Check system and user crontabs
SELECT command, path, hour, minute, day_of_month, month, day_of_week 
FROM crontab;

-- Check SUID and SGID binaries
SELECT path, username, groupname, permissions 
FROM suid_bin;

-- Check user shell profiles
SELECT u.username, f.path, f.mtime 
FROM users u 
JOIN file f ON f.path = u.directory || '/.bashrc' OR f.path = u.directory || '/.profile';
```

### Network Connections & IPTables Auditing
Inspect active listening ports and iptables firewall rules:
```sql
-- Active listening ports on Linux
SELECT lp.port, lp.protocol, lp.address, p.name, p.pid, p.cmdline
FROM listening_ports lp
JOIN processes p ON lp.pid = p.pid;

-- Inspect active iptables rules
SELECT chain, policy, src_ip, dst_ip, iniface, outiface, target 
FROM iptables;

-- Check foreign connections with associated binaries
SELECT s.family, s.protocol, s.local_address, s.local_port, s.remote_address, s.remote_port, p.name, p.path
FROM process_open_sockets s
JOIN processes p ON s.pid = p.pid
WHERE s.remote_port != 0 AND s.remote_address NOT IN ('127.0.0.1', '::1');
```

### Kernel Modules & Rootkit Checks
Check loaded kernel modules and integrity:
```sql
-- List loaded kernel modules
SELECT name, size, used_by, status FROM kernel_modules;

-- Check password aging and accounts with empty passwords
SELECT username, last_change, min, max, warn FROM shadow WHERE password_status = 'empty';
```

## Query Performance & Constraints Best Practices
When querying osquery tables on this platform, heed these crucial rules:
1. **Always filter virtual and filesystem tables**: Tables like `file`, `hash`, and `plist` require path constraints (`WHERE path = '...'` or `WHERE directory = '...'`). Never execute unbounded queries (`SELECT * FROM file;`) as this triggers a full filesystem crawl.
2. **Limit process and memory scans**: When inspecting `process_memory_map` or `process_open_files`, always filter by specific process IDs (`WHERE pid = 1234`).
3. **Use indexes on system events**: Filter event subscriber tables by timestamp or event ID to prevent reading extensive historical logs in memory.


## Linux Core Table Schemas

### `apparmor_events`

Track AppArmor events.

| Column | Type | Description |
| :--- | :--- | :--- |
| `type` | TEXT | Event type |
| `message` | TEXT | Raw audit message |
| `time` | BIGINT | Time of execution in UNIX time |
| `uptime` | BIGINT | Time of execution in system uptime |
| `eid` | TEXT | Event ID |
| `apparmor` | TEXT | Apparmor Status like ALLOWED, DENIED etc. |
| `operation` | TEXT | Permission requested by the process |
| `parent` | UNSIGNED_BIGINT | Parent process PID |
| `profile` | TEXT | Apparmor profile name |
| `name` | TEXT | Process name |
| `pid` | UNSIGNED_BIGINT | Process ID |
| `comm` | TEXT | Command-line name of the command that was used to invoke the analyzed process |
| `denied_mask` | TEXT | Denied permissions for the process |
| `capname` | TEXT | Capability requested by the process |
| `fsuid` | UNSIGNED_BIGINT | Filesystem user ID |
| `ouid` | UNSIGNED_BIGINT | Object owner |
| `capability` | BIGINT | Capability number |
| `requested_mask` | TEXT | Requested access mask |
| `info` | TEXT | Additional information |
| `error` | TEXT | Error information |
| `namespace` | TEXT | AppArmor namespace |
| `label` | TEXT | AppArmor label |

### `apparmor_profiles`

Track active AppArmor profiles.

| Column | Type | Description |
| :--- | :--- | :--- |
| `path` | TEXT | Unique, aa-status compatible, policy identifier. |
| `name` | TEXT | Policy name. |
| `attach` | TEXT | Which executable(s) a profile will attach to. |
| `mode` | TEXT | How the policy is applied. |
| `sha1` | TEXT | A unique hash that identifies this policy. |
| `sha256` | TEXT | A unique hash that identifies this policy. |

### `apt_sources`

Current list of APT repositories or software channels.

| Column | Type | Description |
| :--- | :--- | :--- |
| `name` | TEXT | Repository name |
| `source` | TEXT | Source file |
| `base_uri` | TEXT | Repository base URI |
| `release` | TEXT | Release name |
| `version` | TEXT | Repository source version |
| `maintainer` | TEXT | Repository maintainer |
| `components` | TEXT | Repository components |
| `architectures` | TEXT | Repository architectures |
| `pid_with_namespace` | INTEGER | Pids that contain a namespace |

### `deb_package_files`

Installed files from DEB packages that are currently installed on the system.

| Column | Type | Description |
| :--- | :--- | :--- |
| `package` | TEXT | DEB package name |
| `path` | TEXT | File path within the package |
| `admindir` | TEXT | libdpkg admindir. Defaults to /var/lib/dpkg |

### `deb_packages`

The installed DEB package database.

| Column | Type | Description |
| :--- | :--- | :--- |
| `name` | TEXT | Package name |
| `version` | TEXT | Package version |
| `source` | TEXT | Package source |
| `size` | BIGINT | Package size in bytes |
| `arch` | TEXT | Package architecture |
| `revision` | TEXT | Package revision |
| `status` | TEXT | Package status |
| `maintainer` | TEXT | Package maintainer |
| `section` | TEXT | Package section |
| `priority` | TEXT | Package priority |
| `admindir` | TEXT | libdpkg admindir. Defaults to /var/lib/dpkg |
| `pid_with_namespace` | INTEGER | Pids that contain a namespace |
| `mount_namespace_id` | TEXT | Mount namespace id |

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

### `kernel_keys`

List of security data, authentication keys and encryption keys.

| Column | Type | Description |
| :--- | :--- | :--- |
| `serial_number` | TEXT | The serial key of the key. |
| `flags` | TEXT | A set of flags describing the state of the key. |
| `usage` | BIGINT | the number of threads and open file references that |
| `timeout` | TEXT | The amount of time until the key will expire, |
| `permissions` | TEXT | The key permissions, expressed as four hexadecimal |
| `uid` | BIGINT | The user ID of the key owner. |
| `gid` | BIGINT | The group ID of the key. |
| `type` | TEXT | The key type. |
| `description` | TEXT | The key description. |

### `kernel_modules`

Linux kernel modules both loaded and within the load search path.

| Column | Type | Description |
| :--- | :--- | :--- |
| `name` | TEXT | Module name |
| `size` | BIGINT | Size of module content |
| `used_by` | TEXT | Module reverse dependencies |
| `status` | TEXT | Kernel module status |
| `address` | TEXT | Kernel module address |

### `lxd_certificates`

LXD certificates information.

| Column | Type | Description |
| :--- | :--- | :--- |
| `name` | TEXT | Name of the certificate |
| `type` | TEXT | Type of the certificate |
| `fingerprint` | TEXT | SHA256 hash of the certificate |
| `certificate` | TEXT | Certificate content |

### `lxd_cluster`

LXD cluster information.

| Column | Type | Description |
| :--- | :--- | :--- |
| `server_name` | TEXT | Name of the LXD server node |
| `enabled` | INTEGER | Whether clustering enabled (1) or not (0) on this node |
| `member_config_entity` | TEXT | Type of configuration parameter for this node |
| `member_config_name` | TEXT | Name of configuration parameter |
| `member_config_key` | TEXT | Config key |
| `member_config_value` | TEXT | Config value |
| `member_config_description` | TEXT | Config description |

### `lxd_cluster_members`

LXD cluster members information.

| Column | Type | Description |
| :--- | :--- | :--- |
| `server_name` | TEXT | Name of the LXD server node |
| `url` | TEXT | URL of the node |
| `database` | INTEGER | Whether the server is a database node (1) or not (0) |
| `status` | TEXT | Status of the node (Online/Offline) |
| `message` | TEXT | Message from the node (Online/Offline) |

### `lxd_images`

LXD images information.

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | TEXT | Image ID |
| `architecture` | TEXT | Target architecture for the image |
| `os` | TEXT | OS on which image is based |
| `release` | TEXT | OS release version on which the image is based |
| `description` | TEXT | Image description |
| `aliases` | TEXT | Comma-separated list of image aliases |
| `filename` | TEXT | Filename of the image file |
| `size` | BIGINT | Size of image in bytes |
| `auto_update` | INTEGER | Whether the image auto-updates (1) or not (0) |
| `cached` | INTEGER | Whether image is cached (1) or not (0) |
| `public` | INTEGER | Whether image is public (1) or not (0) |
| `created_at` | TEXT | ISO time of image creation |
| `expires_at` | TEXT | ISO time of image expiration |
| `uploaded_at` | TEXT | ISO time of image upload |
| `last_used_at` | TEXT | ISO time for the most recent use of this image in terms of container spawn |
| `update_source_server` | TEXT | Server for image update |
| `update_source_protocol` | TEXT | Protocol used for image information update and image import from source server |
| `update_source_certificate` | TEXT | Certificate for update source server |
| `update_source_alias` | TEXT | Alias of image at update source server |

### `lxd_instance_config`

LXD instance configuration information.

| Column | Type | Description |
| :--- | :--- | :--- |
| `name` | TEXT | Instance name |
| `key` | TEXT | Configuration parameter name |
| `value` | TEXT | Configuration parameter value |

### `lxd_instance_devices`

LXD instance devices information.

| Column | Type | Description |
| :--- | :--- | :--- |
| `name` | TEXT | Instance name |
| `device` | TEXT | Name of the device |
| `device_type` | TEXT | Device type |
| `key` | TEXT | Device info param name |
| `value` | TEXT | Device info param value |

### `lxd_instances`

LXD instances information.

| Column | Type | Description |
| :--- | :--- | :--- |
| `name` | TEXT | Instance name |
| `status` | TEXT | Instance state (running, stopped, etc.) |
| `stateful` | INTEGER | Whether the instance is stateful(1) or not(0) |
| `ephemeral` | INTEGER | Whether the instance is ephemeral(1) or not(0) |
| `created_at` | TEXT | ISO time of creation |
| `base_image` | TEXT | ID of image used to launch this instance |
| `architecture` | TEXT | Instance architecture |
| `os` | TEXT | The OS of this instance |
| `description` | TEXT | Instance description |
| `pid` | INTEGER | Instance |
| `processes` | INTEGER | Number of processes running inside this instance |

### `lxd_networks`

LXD network information.

| Column | Type | Description |
| :--- | :--- | :--- |
| `name` | TEXT | Name of the network |
| `type` | TEXT | Type of network |
| `managed` | INTEGER | 1 if network created by LXD, 0 otherwise |
| `ipv4_address` | TEXT | IPv4 address |
| `ipv6_address` | TEXT | IPv6 address |
| `used_by` | TEXT | URLs for containers using this network |
| `bytes_received` | BIGINT | Number of bytes received on this network |
| `bytes_sent` | BIGINT | Number of bytes sent on this network |
| `packets_received` | BIGINT | Number of packets received on this network |
| `packets_sent` | BIGINT | Number of packets sent on this network |
| `hwaddr` | TEXT | Hardware address for this network |
| `state` | TEXT | Network status |
| `mtu` | INTEGER | MTU size |

### `lxd_storage_pools`

LXD storage pool information.

| Column | Type | Description |
| :--- | :--- | :--- |
| `name` | TEXT | Name of the storage pool |
| `driver` | TEXT | Storage driver |
| `source` | TEXT | Storage pool source |
| `size` | TEXT | Size of the storage pool |
| `space_used` | BIGINT | Storage space used in bytes |
| `space_total` | BIGINT | Total available storage space in bytes for this storage pool |
| `inodes_used` | BIGINT | Number of inodes used |
| `inodes_total` | BIGINT | Total number of inodes available in this storage pool |

### `md_devices`

Software RAID array settings.

| Column | Type | Description |
| :--- | :--- | :--- |
| `device_name` | TEXT | md device name |
| `status` | TEXT | Current state of the array |
| `raid_level` | INTEGER | Current raid level of the array |
| `size` | BIGINT | size of the array in blocks |
| `chunk_size` | BIGINT | chunk size in bytes |
| `raid_disks` | INTEGER | Number of configured RAID disks in array |
| `nr_raid_disks` | INTEGER | Number of partitions or disk devices to comprise the array |
| `working_disks` | INTEGER | Number of working disks in array |
| `active_disks` | INTEGER | Number of active disks in array |
| `failed_disks` | INTEGER | Number of failed disks in array |
| `spare_disks` | INTEGER | Number of idle disks in array |
| `superblock_state` | TEXT | State of the superblock |
| `superblock_version` | TEXT | Version of the superblock |
| `superblock_update_time` | BIGINT | Unix timestamp of last update |
| `bitmap_on_mem` | TEXT | Pages allocated in in-memory bitmap, if enabled |
| `bitmap_chunk_size` | TEXT | Bitmap chunk size |
| `bitmap_external_file` | TEXT | External referenced bitmap file |
| `recovery_progress` | TEXT | Progress of the recovery activity |
| `recovery_finish` | TEXT | Estimated duration of recovery activity |
| `recovery_speed` | TEXT | Speed of recovery activity |
| `resync_progress` | TEXT | Progress of the resync activity |
| `resync_finish` | TEXT | Estimated duration of resync activity |
| `resync_speed` | TEXT | Speed of resync activity |
| `reshape_progress` | TEXT | Progress of the reshape activity |
| `reshape_finish` | TEXT | Estimated duration of reshape activity |
| `reshape_speed` | TEXT | Speed of reshape activity |
| `check_array_progress` | TEXT | Progress of the check array activity |
| `check_array_finish` | TEXT | Estimated duration of the check array activity |
| `check_array_speed` | TEXT | Speed of the check array activity |
| `unused_devices` | TEXT | Unused devices |
| `other` | TEXT | Other information associated with array from /proc/mdstat |

### `md_drives`

Drive devices used for Software RAID.

| Column | Type | Description |
| :--- | :--- | :--- |
| `md_device_name` | TEXT | md device name |
| `drive_name` | TEXT | Drive device name |
| `slot` | INTEGER | Slot position of disk |
| `state` | TEXT | State of the drive |

### `md_personalities`

Software RAID setting supported by the kernel.

| Column | Type | Description |
| :--- | :--- | :--- |
| `name` | TEXT | Name of personality supported by kernel |

### `memory_info`

Main memory information in bytes.

| Column | Type | Description |
| :--- | :--- | :--- |
| `memory_total` | BIGINT | Total amount of physical RAM, in bytes |
| `memory_free` | BIGINT | The amount of physical RAM, in bytes, left unused by the system |
| `memory_available` | BIGINT | The amount of physical RAM, in bytes, available for starting new applications, without swapping |
| `buffers` | BIGINT | The amount of physical RAM, in bytes, used for file buffers |
| `cached` | BIGINT | The amount of physical RAM, in bytes, used as cache memory |
| `swap_cached` | BIGINT | The amount of swap, in bytes, used as cache memory |
| `active` | BIGINT | The total amount of buffer or page cache memory, in bytes, that is in active use |
| `inactive` | BIGINT | The total amount of buffer or page cache memory, in bytes, that are free and available |
| `swap_total` | BIGINT | The total amount of swap available, in bytes |
| `swap_free` | BIGINT | The total amount of swap free, in bytes |

### `memory_map`

OS memory region map.

| Column | Type | Description |
| :--- | :--- | :--- |
| `name` | TEXT | Region name |
| `start` | TEXT | Start address of memory region |
| `end` | TEXT | End address of memory region |

### `msr`

| Column | Type | Description |
| :--- | :--- | :--- |
| `processor_number` | BIGINT | The processor number as reported in /proc/cpuinfo |
| `turbo_disabled` | BIGINT | Whether the turbo feature is disabled. |
| `turbo_ratio_limit` | BIGINT | The turbo feature ratio limit. |
| `platform_info` | BIGINT | Platform information. |
| `perf_ctl` | BIGINT | Performance setting for the processor. |
| `perf_status` | BIGINT | Performance status for the processor. |
| `feature_control` | BIGINT | Bitfield controlling enabled features. |
| `rapl_power_limit` | BIGINT | Run Time Average Power Limiting power limit. |
| `rapl_energy_status` | BIGINT | Run Time Average Power Limiting energy status. |
| `rapl_power_units` | BIGINT | Run Time Average Power Limiting power units. |

### `portage_keywords`

A summary about portage configurations like keywords, mask and unmask.

| Column | Type | Description |
| :--- | :--- | :--- |
| `package` | TEXT | Package name |
| `version` | TEXT | The version which are affected by the use flags, empty means all |
| `keyword` | TEXT | The keyword applied to the package |
| `mask` | INTEGER | If the package is masked |
| `unmask` | INTEGER | If the package is unmasked |

### `portage_packages`

List of currently installed packages.

| Column | Type | Description |
| :--- | :--- | :--- |
| `package` | TEXT | Package name |
| `version` | TEXT | The version which are affected by the use flags, empty means all |
| `slot` | TEXT | The slot used by package |
| `build_time` | BIGINT | Unix time when package was built |
| `repository` | TEXT | From which repository the ebuild was used |
| `eapi` | BIGINT | The eapi for the ebuild |
| `size` | BIGINT | The size of the package |
| `world` | INTEGER | If package is in the world file |

### `portage_use`

List of enabled portage USE values for specific package.

| Column | Type | Description |
| :--- | :--- | :--- |
| `package` | TEXT | Package name |
| `version` | TEXT | The version of the installed package |
| `use` | TEXT | USE flag which has been enabled for package |

### `process_file_events`

A File Integrity Monitor implementation using the audit service.

| Column | Type | Description |
| :--- | :--- | :--- |
| `operation` | TEXT | Operation type |
| `pid` | BIGINT | Process ID |
| `ppid` | BIGINT | Parent process ID |
| `time` | BIGINT | Time of execution in UNIX time |
| `executable` | TEXT | The executable path |
| `partial` | TEXT | True if this is a partial event (i.e.: this process existed before we started osquery) |
| `cwd` | TEXT | The current working directory of the process |
| `path` | TEXT | The path associated with the event |
| `dest_path` | TEXT | The canonical path associated with the event |
| `uid` | TEXT | The uid of the process performing the action |
| `gid` | TEXT | The gid of the process performing the action |
| `auid` | TEXT | Audit user ID of the process using the file |
| `euid` | TEXT | Effective user ID of the process using the file |
| `egid` | TEXT | Effective group ID of the process using the file |
| `fsuid` | TEXT | Filesystem user ID of the process using the file |
| `fsgid` | TEXT | Filesystem group ID of the process using the file |
| `suid` | TEXT | Saved user ID of the process using the file |
| `sgid` | TEXT | Saved group ID of the process using the file |
| `uptime` | BIGINT | Time of execution in system uptime |
| `eid` | TEXT | Event ID |

### `process_namespaces`

Linux namespaces for processes running on the host system.

| Column | Type | Description |
| :--- | :--- | :--- |
| `pid` | INTEGER | Process (or thread) ID |
| `cgroup_namespace` | TEXT | cgroup namespace inode |
| `ipc_namespace` | TEXT | ipc namespace inode |
| `mnt_namespace` | TEXT | mnt namespace inode |
| `net_namespace` | TEXT | net namespace inode |
| `pid_namespace` | TEXT | pid namespace inode |
| `user_namespace` | TEXT | user namespace inode |
| `uts_namespace` | TEXT | uts namespace inode |

### `process_open_pipes`

Pipes and partner processes for each process.

| Column | Type | Description |
| :--- | :--- | :--- |
| `pid` | BIGINT | Process ID |
| `fd` | BIGINT | File descriptor |
| `mode` | TEXT | Pipe open mode (r/w) |
| `inode` | BIGINT | Pipe inode number |
| `type` | TEXT | Pipe Type: named vs unnamed/anonymous |
| `partner_pid` | BIGINT | Process ID of partner process sharing a particular pipe |
| `partner_fd` | BIGINT | File descriptor of shared pipe at partner |
| `partner_mode` | TEXT | Mode of shared pipe at partner |

### `rpm_package_files`

Installed files from RPM packages that are currently installed on the system.

| Column | Type | Description |
| :--- | :--- | :--- |
| `package` | TEXT | RPM package name |
| `path` | TEXT | File path within the package |
| `username` | TEXT | File default username from info DB |
| `groupname` | TEXT | File default groupname from info DB |
| `mode` | TEXT | File permissions mode from info DB |
| `size` | BIGINT | Expected file size in bytes from RPM info DB |
| `sha256` | TEXT | SHA256 file digest from RPM info DB |

### `rpm_packages`

RPM packages that are currently installed on the host system.

| Column | Type | Description |
| :--- | :--- | :--- |
| `name` | TEXT | RPM package name |
| `version` | TEXT | Package version |
| `release` | TEXT | Package release |
| `source` | TEXT | Source RPM package name (optional) |
| `size` | BIGINT | Package size in bytes |
| `sha1` | TEXT | SHA1 hash of the package contents |
| `arch` | TEXT | Architecture(s) supported |
| `epoch` | INTEGER | Package epoch value |
| `install_time` | INTEGER | When the package was installed |
| `vendor` | TEXT | Package vendor |
| `package_group` | TEXT | Package group |
| `pid_with_namespace` | INTEGER | Pids that contain a namespace |
| `mount_namespace_id` | TEXT | Mount namespace id |

### `seccomp_events`

A virtual table that tracks seccomp events.

| Column | Type | Description |
| :--- | :--- | :--- |
| `time` | BIGINT | Time of execution in UNIX time |
| `uptime` | BIGINT | Time of execution in system uptime |
| `auid` | UNSIGNED_BIGINT | Audit user ID (loginuid) of the user who started the analyzed process |
| `uid` | UNSIGNED_BIGINT | User ID of the user who started the analyzed process |
| `gid` | UNSIGNED_BIGINT | Group ID of the user who started the analyzed process |
| `ses` | UNSIGNED_BIGINT | Session ID of the session from which the analyzed process was invoked |
| `pid` | UNSIGNED_BIGINT | Process ID |
| `comm` | TEXT | Command-line name of the command that was used to invoke the analyzed process |
| `exe` | TEXT | The path to the executable that was used to invoke the analyzed process |
| `sig` | BIGINT | Signal value sent to process by seccomp |
| `arch` | TEXT | Information about the CPU architecture |
| `syscall` | TEXT | Type of the system call |
| `compat` | BIGINT | Is system call in compatibility mode |
| `ip` | TEXT | Instruction pointer value |
| `code` | TEXT | The seccomp action |

### `secureboot_certificates`

X.509 certificates from UEFI Secure Boot signature databases (db and dbx EFI variables). Useful for monitoring CA expiry and adoption of updated certificates (e.g. Microsoft UEFI CA 2023).

| Column | Type | Description |
| :--- | :--- | :--- |
| `common_name` | TEXT | Certificate CommonName |
| `subject` | TEXT | Certificate subject distinguished name |
| `issuer` | TEXT | Certificate issuer distinguished name |
| `not_valid_before` | DATETIME | Lower bound of valid date |
| `not_valid_after` | DATETIME | Certificate expiration date |
| `sha1` | TEXT | SHA1 hash of the raw certificate contents |
| `serial` | TEXT | Certificate serial number |
| `revoked` | INTEGER | 1 if the certificate is in the dbx revocation list, 0 if it is in the db allowlist |
| `path` | TEXT | Path to the EFI variable file |
| `is_ca` | INTEGER | 1 if the certificate is a CA, 0 otherwise |
| `self_signed` | INTEGER | 1 if the certificate is self-signed, 0 otherwise |
| `key_usage` | TEXT | Certificate key usage extension string |
| `authority_key_id` | TEXT | Authority Key Identifier (AKI) |
| `subject_key_id` | TEXT | Subject Key Identifier (SKI) |
| `signing_algorithm` | TEXT | Algorithm used to sign the certificate |
| `key_algorithm` | TEXT | Public key algorithm |
| `key_strength` | TEXT | Public key size in bits |

### `selinux_events`

Track SELinux events.

| Column | Type | Description |
| :--- | :--- | :--- |
| `type` | TEXT | Event type |
| `message` | TEXT | Message |
| `time` | BIGINT | Time of execution in UNIX time |
| `uptime` | BIGINT | Time of execution in system uptime |
| `eid` | TEXT | Event ID |

### `selinux_settings`

Track active SELinux settings.

| Column | Type | Description |
| :--- | :--- | :--- |
| `scope` | TEXT | Where the key is located inside the SELinuxFS mount point. |
| `key` | TEXT | Key or class name. |
| `value` | TEXT | Active value. |

### `shadow`

Local system users encrypted passwords and related information. Please note, that you usually need superuser rights to access `/etc/shadow`.

| Column | Type | Description |
| :--- | :--- | :--- |
| `password_status` | TEXT | Password status |
| `hash_alg` | TEXT | Password hashing algorithm |
| `last_change` | BIGINT | Date of last password change (starting from UNIX epoch date) |
| `min` | BIGINT | Minimal number of days between password changes |
| `max` | BIGINT | Maximum number of days between password changes |
| `warning` | BIGINT | Number of days before password expires to warn user about it |
| `inactive` | BIGINT | Number of days after password expires until account is blocked |
| `expire` | BIGINT | Number of days since UNIX epoch date until account is disabled |
| `flag` | BIGINT | Reserved |
| `username` | TEXT | Username |

### `shared_memory`

OS shared memory regions.

| Column | Type | Description |
| :--- | :--- | :--- |
| `shmid` | INTEGER | Shared memory segment ID |
| `owner_uid` | BIGINT | User ID of owning process |
| `creator_uid` | BIGINT | User ID of creator process |
| `pid` | BIGINT | Process ID to last use the segment |
| `creator_pid` | BIGINT | Process ID that created the segment |
| `atime` | BIGINT | Attached time |
| `dtime` | BIGINT | Detached time |
| `ctime` | BIGINT | Changed time |
| `permissions` | TEXT | Memory segment permissions |
| `size` | BIGINT | Size in bytes |
| `attached` | INTEGER | Number of attached processes |
| `status` | TEXT | Destination/attach status |
| `locked` | INTEGER | 1 if segment is locked else 0 |

### `syslog_events`

| Column | Type | Description |
| :--- | :--- | :--- |
| `time` | BIGINT | Current unix epoch time |
| `datetime` | TEXT | Time known to syslog |
| `host` | TEXT | Hostname configured for syslog |
| `severity` | INTEGER | Syslog severity |
| `facility` | TEXT | Syslog facility |
| `tag` | TEXT | The syslog tag |
| `message` | TEXT | The syslog message |
| `eid` | TEXT | Event ID |

### `systemd_units`

Track systemd units.

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | TEXT | Unique unit identifier |
| `description` | TEXT | Unit description |
| `load_state` | TEXT | Reflects whether the unit definition was properly loaded |
| `active_state` | TEXT | The high-level unit activation state, i.e. generalization of SUB |
| `sub_state` | TEXT | The low-level unit activation state, values depend on unit type |
| `unit_file_state` | TEXT | Whether the unit file is enabled, e.g. `enabled`, `masked`, `disabled`, etc |
| `following` | TEXT | The name of another unit that this unit follows in state |
| `object_path` | TEXT | The object path for this unit |
| `job_id` | BIGINT | Next queued job id |
| `job_type` | TEXT | Job type |
| `job_path` | TEXT | The object path for the job |
| `fragment_path` | TEXT | The unit file path this unit was read from, if there is any |
| `user` | TEXT | The configured user, if any |
| `source_path` | TEXT | Path to the (possibly generated) unit configuration file |

### `yum_sources`

Current list of Yum repositories or software channels.

| Column | Type | Description |
| :--- | :--- | :--- |
| `name` | TEXT | Repository name |
| `source` | TEXT | Source file |
| `baseurl` | TEXT | Repository base URL |
| `mirrorlist` | TEXT | Mirrorlist URL |
| `metalink` | TEXT | Metalink URL |
| `enabled` | TEXT | Whether the repository is used |
| `gpgcheck` | TEXT | Whether packages are GPG checked |
| `gpgkey` | TEXT | URL to GPG key |
| `pid_with_namespace` | INTEGER | Pids that contain a namespace |

## Additional Shared & POSIX Tables

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

### `etc_hosts`

Line-parsed /etc/hosts.

| Column | Type | Description |
| :--- | :--- | :--- |
| `address` | TEXT | IP address mapping |
| `hostnames` | TEXT | Raw hosts mapping |
| `pid_with_namespace` | INTEGER | Pids that contain a namespace |

### `file`

Interactive filesystem attributes and metadata.

| Column | Type | Description |
| :--- | :--- | :--- |
| `path` | TEXT | Absolute file path |
| `directory` | TEXT | Directory of file(s) |
| `filename` | TEXT | Name portion of file path |
| `inode` | BIGINT | Filesystem inode number |
| `uid` | BIGINT | Owning user ID |
| `gid` | BIGINT | Owning group ID |
| `mode` | TEXT | Permission bits |
| `device` | BIGINT | Device ID (optional) |
| `size` | BIGINT | Size of file in bytes |
| `block_size` | INTEGER | Block size of filesystem |
| `atime` | BIGINT | Last access time |
| `mtime` | BIGINT | Last modification time |
| `ctime` | BIGINT | Last status change time |
| `btime` | BIGINT | (B)irth or (cr)eate time |
| `hard_links` | INTEGER | Number of hard links |
| `symlink` | INTEGER | 1 if the path is a symlink, otherwise 0 |
| `type` | TEXT | File status |
| `symlink_target_path` | TEXT | Full path of the symlink target if any |
| `attributes` | TEXT | File attrib string. See: https://ss64.com/nt/attrib.html |
| `volume_serial` | TEXT | Volume serial number |
| `file_id` | TEXT | file ID |
| `file_version` | TEXT | File version |
| `product_version` | TEXT | File product version |
| `original_filename` | TEXT | (Executable files only) Original filename |
| `shortcut_target_path` | TEXT | Full path to the file the shortcut points to |
| `shortcut_target_type` | TEXT | Display name for the target type |
| `shortcut_target_location` | TEXT | Folder name where the shortcut target resides |
| `shortcut_start_in` | TEXT | Full path to the working directory to use when executing the shortcut target |
| `shortcut_run` | TEXT | Window mode the target of the shortcut should be run in |
| `shortcut_comment` | TEXT | Comment on the shortcut |
| `bsd_flags` | TEXT | The BSD file flags (chflags). Possible values: NODUMP, UF_IMMUTABLE, UF_APPEND, OPAQUE, HIDDEN, ARCHIVED, SF_IMMUTABLE, SF_APPEND |
| `pid_with_namespace` | INTEGER | Pids that contain a namespace |
| `mount_namespace_id` | TEXT | Mount namespace id |

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

### `routes`

The active route table for the host system.

| Column | Type | Description |
| :--- | :--- | :--- |
| `destination` | TEXT | Destination IP address |
| `netmask` | INTEGER | Netmask length |
| `gateway` | TEXT | Route gateway |
| `source` | TEXT | Route source |
| `flags` | INTEGER | Flags to describe route |
| `interface` | TEXT | Route local interface |
| `mtu` | INTEGER | Maximum Transmission Unit for the route |
| `metric` | INTEGER | Cost of route. Lowest is preferred |
| `type` | TEXT | Type of route |
| `hopcount` | INTEGER | Max hops expected |

### `suid_bin`

suid binaries in common locations.

| Column | Type | Description |
| :--- | :--- | :--- |
| `path` | TEXT | Binary path |
| `username` | TEXT | Binary owner username |
| `groupname` | TEXT | Binary owner group |
| `permissions` | TEXT | Binary permissions |
| `pid_with_namespace` | INTEGER | Pids that contain a namespace |

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
