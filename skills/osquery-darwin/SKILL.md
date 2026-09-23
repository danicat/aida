---
name: osquery-darwin
description: macOS system diagnostics and osquery schema reference. Provides tables for launchd, plists, keychain items, certificates, Gatekeeper, SIP, ALF firewall, crash logs, NVRAM, and processes. Use for macOS persistence analysis, security posture auditing, and runtime diagnostics.
---

# macOS (Darwin) Osquery Diagnostics and Schema Reference

The `osquery-darwin` skill provides comprehensive osquery table schemas, diagnostic queries, and incident investigation runbooks tailored specifically for macOS (Darwin) systems. Agents should load this skill when diagnosing system health, hunting for threats or persistence, inspecting system configurations, or auditing compliance on macOS (Darwin) hosts.

## Diagnostic Runbooks & Investigation Workflows

### macOS Persistence Analysis
Investigate persistence across all LaunchDaemons, LaunchAgents, and Startup Items:
```sql
-- Enumerate third-party LaunchAgents and LaunchDaemons
SELECT name, path, program, program_arguments, run_at_load, keep_alive 
FROM launchd 
WHERE path NOT LIKE '/System/Library/%' AND disabled = '0';

-- Enumerate Legacy Startup Items
SELECT name, path, type, status FROM startup_items;

-- Inspect Login Items per user
SELECT username, path, name FROM login_items;
```
Verify whether any binary referenced in `program` or `program_arguments` lacks an Apple code signature using the `signature` table:
```sql
SELECT path, signed, identifier, authority 
FROM signature 
WHERE path = '/Library/Application Support/Suspicious/agent';
```

### macOS Security Posture & Gatekeeper / SIP
Audit System Integrity Protection (SIP), Gatekeeper, and Application Layer Firewall (ALF):
```sql
-- Check System Integrity Protection
SELECT config_flag, enabled FROM sip_config;

-- Check Gatekeeper configuration
SELECT assessments_enabled, dev_id_enabled FROM gatekeeper;

-- Check ALF firewall state
SELECT global_state, stealth_enabled, logging_enabled FROM alf;

-- Check FileVault encryption status
SELECT * FROM disk_encryption WHERE encrypted = 1;
```

### Process & Network Socket Diagnostics
Correlate active processes with open listening ports and external connections:
```sql
-- Active listening ports on macOS with process attribution
SELECT l.port, l.address, l.protocol, p.name, p.pid, p.path, p.cmdline
FROM listening_ports l
JOIN processes p ON l.pid = p.pid
WHERE l.address NOT IN ('127.0.0.1', '::1');

-- Processes running from temporary or writable paths
SELECT pid, name, path, cmdline, cwd, uid
FROM processes
WHERE path LIKE '/tmp/%' 
   OR path LIKE '/var/tmp/%' 
   OR path LIKE '/Users/%/Downloads/%';
```

### Keychain & Certificate Auditing
Inspect system keychain and root certificates for unauthorized trust roots:
```sql
-- Inspect untrusted or custom root certificates
SELECT common_name, issuer, not_valid_after, self_signed, ca
FROM certificates
WHERE path = '/Library/Keychains/System.keychain' AND ca = 1;
```

## Query Performance & Constraints Best Practices
When querying osquery tables on this platform, heed these crucial rules:
1. **Always filter virtual and filesystem tables**: Tables like `file`, `hash`, and `plist` require path constraints (`WHERE path = '...'` or `WHERE directory = '...'`). Never execute unbounded queries (`SELECT * FROM file;`) as this triggers a full filesystem crawl.
2. **Limit process and memory scans**: When inspecting `process_memory_map` or `process_open_files`, always filter by specific process IDs (`WHERE pid = 1234`).
3. **Use indexes on system events**: Filter event subscriber tables by timestamp or event ID to prevent reading extensive historical logs in memory.


## macOS (Darwin) Core Table Schemas

### `account_policy_data`

Additional macOS user account data from the AccountPolicy section of OpenDirectory.

| Column | Type | Description |
| :--- | :--- | :--- |
| `uid` | BIGINT | User ID |
| `creation_time` | DOUBLE | When the account was first created |
| `failed_login_count` | BIGINT | The number of failed login attempts using an incorrect password. Count resets after a correct password is entered. |
| `failed_login_timestamp` | DOUBLE | The time of the last failed login attempt. Resets after a correct password is entered |
| `password_last_set_time` | DOUBLE | The time the password was last changed |

### `ad_config`

macOS Active Directory configuration.

| Column | Type | Description |
| :--- | :--- | :--- |
| `name` | TEXT | The macOS-specific configuration name |
| `domain` | TEXT | Active Directory trust domain |
| `option` | TEXT | Canonical name of option |
| `value` | TEXT | Variable typed option value |

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

### `asl`

Queries the Apple System Log data structure for system events.

| Column | Type | Description |
| :--- | :--- | :--- |
| `time` | INTEGER | Unix timestamp.  Set automatically |
| `time_nano_sec` | INTEGER | Nanosecond time. |
| `host` | TEXT | Sender |
| `sender` | TEXT | Sender |
| `facility` | TEXT | Sender |
| `pid` | INTEGER | Sending process ID encoded as a string.  Set automatically. |
| `gid` | BIGINT | GID that sent the log message (set by the server). |
| `uid` | BIGINT | UID that sent the log message (set by the server). |
| `level` | INTEGER | Log level number.  See levels in asl.h. |
| `message` | TEXT | Message text. |
| `ref_pid` | INTEGER | Reference PID for messages proxied by launchd |
| `ref_proc` | TEXT | Reference process for messages proxied by launchd |
| `extra` | TEXT | Extra columns, in JSON format. Queries against this column are performed entirely in SQLite, so do not benefit from efficient querying via asl.h. |

### `authorization_mechanisms`

macOS Authorization mechanisms database.

| Column | Type | Description |
| :--- | :--- | :--- |
| `label` | TEXT | Label of the authorization right |
| `plugin` | TEXT | Authorization plugin name |
| `mechanism` | TEXT | Name of the mechanism that will be called |
| `privileged` | TEXT | If privileged it will run as root, else as an anonymous user |
| `entry` | TEXT | The whole string entry |

### `authorizations`

macOS Authorization rights database.

| Column | Type | Description |
| :--- | :--- | :--- |
| `label` | TEXT | Item name, usually in reverse domain format |
| `modified` | TEXT | Label top-level key |
| `allow_root` | TEXT | Label top-level key |
| `timeout` | TEXT | Label top-level key |
| `version` | TEXT | Label top-level key |
| `tries` | TEXT | Label top-level key |
| `authenticate_user` | TEXT | Label top-level key |
| `shared` | TEXT | Label top-level key |
| `comment` | TEXT | Label top-level key |
| `created` | TEXT | Label top-level key |
| `class` | TEXT | Label top-level key |
| `session_owner` | TEXT | Label top-level key |

### `browser_plugins`

All C/NPAPI browser plugin details for all users. C/NPAPI has been deprecated on all major browsers. To query for plugins on modern browsers, try: `chrome_extensions` `firefox_addons` `safari_extensions`.

| Column | Type | Description |
| :--- | :--- | :--- |
| `uid` | BIGINT | The local user that owns the plugin |
| `name` | TEXT | Plugin display name |
| `identifier` | TEXT | Plugin identifier |
| `version` | TEXT | Plugin short version |
| `sdk` | TEXT | Build SDK used to compile plugin |
| `description` | TEXT | Plugin description text |
| `development_region` | TEXT | Plugin language-localization |
| `native` | INTEGER | Plugin requires native execution |
| `path` | TEXT | Path to plugin bundle |
| `disabled` | INTEGER | Is the plugin disabled. 1 = Disabled |

### `certificate_trust_settings`

Certificate Authorities trust settings installed in Keychains/ca-bundles.

| Column | Type | Description |
| :--- | :--- | :--- |
| `common_name` | TEXT | Certificate common name |
| `serial` | TEXT | Certificate serial number |
| `trust_domain` | TEXT | Certificate trust settings domain |
| `trust_policy_name` | TEXT | Certificate trust policy name |
| `trust_policy_data` | TEXT | Certificate trust policy data |
| `trust_allowed_error` | TEXT | Certificate trust allowed error |
| `trust_key_usage` | TEXT | Certificate trust key usage |
| `trust_result` | TEXT | Certificate trust result |

### `connected_displays`

Provides information about the connected displays of the machine.

| Column | Type | Description |
| :--- | :--- | :--- |
| `name` | TEXT | The name of the display. |
| `product_id` | TEXT | The product ID of the display. |
| `serial_number` | TEXT | The serial number of the display. (may not be unique) |
| `vendor_id` | TEXT | The vendor ID of the display. |
| `manufactured_week` | INTEGER | The manufacture week of the display. This field is 0 if not supported |
| `manufactured_year` | INTEGER | The manufacture year of the display. This field is 0 if not supported |
| `display_id` | TEXT | The display ID. |
| `pixels` | TEXT | The number of pixels of the display. |
| `resolution` | TEXT | The resolution of the display. |
| `ambient_brightness_enabled` | TEXT | The ambient brightness setting associated with the display. This will be 1 if enabled and is 0 if disabled or not supported. |
| `connection_type` | TEXT | The connection type associated with the display. |
| `display_type` | TEXT | The type of display. |
| `main` | INTEGER | If the display is the main display. |
| `mirror` | INTEGER | If the display is mirrored or not. This field is 1 if mirrored and 0 if not mirrored. |
| `online` | INTEGER | The online status of the display. This field is 1 if the display is online and 0 if it is offline. |
| `rotation` | TEXT | The rotation of the display (0, 90, 180, or 270 degrees). This field is -1 if display rotation is not supported. |

### `crashes`

Application, System, and Mobile App crash logs.

| Column | Type | Description |
| :--- | :--- | :--- |
| `type` | TEXT | Type of crash log |
| `pid` | BIGINT | Process (or thread) ID of the crashed process |
| `path` | TEXT | Path to the crashed process |
| `crash_path` | TEXT | Location of log file |
| `identifier` | TEXT | Identifier of the crashed process |
| `version` | TEXT | Version info of the crashed process |
| `parent` | BIGINT | Parent PID of the crashed process |
| `responsible` | TEXT | Process responsible for the crashed process |
| `uid` | INTEGER | User ID of the crashed process |
| `datetime` | TEXT | Date/Time at which the crash occurred |
| `crashed_thread` | BIGINT | Thread ID which crashed |
| `stack_trace` | TEXT | Most recent frame from the stack trace |
| `exception_type` | TEXT | Exception type of the crash |
| `exception_codes` | TEXT | Exception codes from the crash |
| `exception_notes` | TEXT | Exception notes from the crash |
| `registers` | TEXT | The value of the system registers |

### `cups_destinations`

Returns all configured printers.

| Column | Type | Description |
| :--- | :--- | :--- |
| `name` | TEXT | Name of the printer |
| `option_name` | TEXT | Option name |
| `option_value` | TEXT | Option value |

### `cups_jobs`

Returns all completed print jobs from cups.

| Column | Type | Description |
| :--- | :--- | :--- |
| `title` | TEXT | Title of the printed job |
| `destination` | TEXT | The printer the job was sent to |
| `user` | TEXT | The user who printed the job |
| `format` | TEXT | The format of the print job |
| `size` | INTEGER | The size of the print job |
| `completed_time` | INTEGER | When the job completed printing |
| `processing_time` | INTEGER | How long the job took to process |
| `creation_time` | INTEGER | When the print request was initiated |

### `device_firmware`

A best-effort list of discovered firmware versions.

| Column | Type | Description |
| :--- | :--- | :--- |
| `type` | TEXT | Type of device |
| `device` | TEXT | The device name |
| `version` | TEXT | Firmware version |

### `disk_events`

Track DMG disk image events (appearance/disappearance) when opened.

| Column | Type | Description |
| :--- | :--- | :--- |
| `action` | TEXT | Appear or disappear |
| `path` | TEXT | Path of the DMG file accessed |
| `name` | TEXT | Disk event name |
| `device` | TEXT | Disk event BSD name |
| `uuid` | TEXT | UUID of the volume inside DMG if available |
| `size` | BIGINT | Size of partition in bytes |
| `ejectable` | INTEGER | 1 if ejectable, 0 if not |
| `mountable` | INTEGER | 1 if mountable, 0 if not |
| `writable` | INTEGER | 1 if writable, 0 if not |
| `content` | TEXT | Disk event content |
| `media_name` | TEXT | Disk event media name string |
| `vendor` | TEXT | Disk event vendor string |
| `filesystem` | TEXT | Filesystem if available |
| `checksum` | TEXT | UDIF Master checksum if available (CRC32) |
| `time` | BIGINT | Time of appearance/disappearance in UNIX time |
| `eid` | TEXT | Event ID |

### `es_process_events`

Process execution events from EndpointSecurity.

| Column | Type | Description |
| :--- | :--- | :--- |
| `version` | INTEGER | Version of EndpointSecurity event |
| `seq_num` | BIGINT | Per event sequence number |
| `global_seq_num` | BIGINT | Global sequence number |
| `pid` | BIGINT | Process (or thread) ID |
| `pidversion` | BIGINT | Process ID version |
| `path` | TEXT | Path of executed file |
| `parent` | BIGINT | Parent process ID |
| `original_parent` | BIGINT | Original parent process ID in case of reparenting |
| `session_id` | BIGINT | The identifier of the session that contains the process group. |
| `responsible_pid` | BIGINT | The pid of the process responsible for this process. |
| `responsible_pidversion` | BIGINT | The pidversion of the process responsible for this process. |
| `parent_pidversion` | BIGINT | The pidversion of the parent process. |
| `cmdline` | TEXT | Command line arguments (argv) |
| `cmdline_count` | BIGINT | Number of command line arguments |
| `env` | TEXT | Environment variables delimited by spaces |
| `env_count` | BIGINT | Number of environment variables |
| `cwd` | TEXT | The process current working directory |
| `uid` | BIGINT | User ID of the process |
| `euid` | BIGINT | Effective User ID of the process |
| `gid` | BIGINT | Group ID of the process |
| `egid` | BIGINT | Effective Group ID of the process |
| `username` | TEXT | Username |
| `signing_id` | TEXT | Signature identifier of the process |
| `team_id` | TEXT | Team identifier of the process |
| `cdhash` | TEXT | Codesigning hash of the process |
| `platform_binary` | INTEGER | Indicates if the binary is Apple signed binary (1) or not (0) |
| `exit_code` | INTEGER | Exit code of a process in case of an exit event |
| `child_pid` | BIGINT | Process ID of a child process in case of a fork event |
| `time` | BIGINT | Time of execution in UNIX time |
| `event_type` | TEXT | Type of EndpointSecurity event |
| `eid` | TEXT | Event ID |
| `codesigning_flags` | TEXT | Codesigning flags matching one of these options, in a comma separated list: NOT_VALID, ADHOC, NOT_RUNTIME, INSTALLER. See kern/cs_blobs.h in XNU for descriptions. |

### `es_process_file_events`

File integrity monitoring events from EndpointSecurity including process context.

| Column | Type | Description |
| :--- | :--- | :--- |
| `version` | INTEGER | Version of EndpointSecurity event |
| `seq_num` | BIGINT | Per event sequence number |
| `global_seq_num` | BIGINT | Global sequence number |
| `pid` | BIGINT | Process (or thread) ID |
| `parent` | BIGINT | Parent process ID |
| `path` | TEXT | Path of executed file |
| `filename` | TEXT | The source or target filename for the event |
| `dest_filename` | TEXT | Destination filename for the event |
| `event_type` | TEXT | Type of EndpointSecurity event |
| `time` | BIGINT | Time of execution in UNIX time |
| `eid` | TEXT | Event ID |

### `event_taps`

Returns information about installed event taps.

| Column | Type | Description |
| :--- | :--- | :--- |
| `enabled` | INTEGER | Is the Event Tap enabled |
| `event_tap_id` | INTEGER | Unique ID for the Tap |
| `event_tapped` | TEXT | The mask that identifies the set of events to be observed. |
| `process_being_tapped` | INTEGER | The process ID of the target application |
| `tapping_process` | INTEGER | The process ID of the application that created the event tap. |

### `fan_speed_sensors`

Fan speeds.

| Column | Type | Description |
| :--- | :--- | :--- |
| `fan` | TEXT | Fan number |
| `name` | TEXT | Fan name |
| `actual` | INTEGER | Actual speed |
| `min` | INTEGER | Minimum speed |
| `max` | INTEGER | Maximum speed |
| `target` | INTEGER | Target speed |

### `gatekeeper`

macOS Gatekeeper Details.

| Column | Type | Description |
| :--- | :--- | :--- |
| `assessments_enabled` | INTEGER | 1 If a Gatekeeper is enabled else 0 |
| `dev_id_enabled` | INTEGER | 1 If a Gatekeeper allows execution from identified developers else 0 |
| `version` | TEXT | Version of Gatekeeper |
| `opaque_version` | TEXT | Version of Gatekeeper |

### `gatekeeper_approved_apps`

Gatekeeper apps a user has allowed to run.

| Column | Type | Description |
| :--- | :--- | :--- |
| `path` | TEXT | Path of executable allowed to run |
| `requirement` | TEXT | Code signing requirement language |
| `ctime` | DOUBLE | Last change time |
| `mtime` | DOUBLE | Last modification time |

### `homebrew_packages`

The installed homebrew package database.

| Column | Type | Description |
| :--- | :--- | :--- |
| `name` | TEXT | Package name |
| `path` | TEXT | Package install path |
| `version` | TEXT | Current |
| `type` | TEXT | Package type ( |
| `auto_updates` | INTEGER | 1 if the cask auto-updates otherwise 0 |
| `app_name` | TEXT | Name of the installed App (for Casks) |
| `prefix` | TEXT | Homebrew install prefix |

### `ibridge_info`

Information about the Apple iBridge hardware controller.

| Column | Type | Description |
| :--- | :--- | :--- |
| `boot_uuid` | TEXT | Boot UUID of the iBridge controller |
| `coprocessor_version` | TEXT | The manufacturer and chip version |
| `firmware_version` | TEXT | The build version of the firmware |
| `unique_chip_id` | TEXT | Unique id of the iBridge controller |

### `iokit_devicetree`

The IOKit registry matching the DeviceTree plane.

| Column | Type | Description |
| :--- | :--- | :--- |
| `name` | TEXT | Device node name |
| `class` | TEXT | Best matching device class (most-specific category) |
| `id` | BIGINT | IOKit internal registry ID |
| `parent` | BIGINT | Parent device registry ID |
| `device_path` | TEXT | Device tree path |
| `service` | INTEGER | 1 if the device conforms to IOService else 0 |
| `busy_state` | INTEGER | 1 if the device is in a busy state else 0 |
| `retain_count` | INTEGER | The device reference count |
| `depth` | INTEGER | Device nested depth |

### `iokit_registry`

The full IOKit registry without selecting a plane.

| Column | Type | Description |
| :--- | :--- | :--- |
| `name` | TEXT | Default name of the node |
| `class` | TEXT | Best matching device class (most-specific category) |
| `id` | BIGINT | IOKit internal registry ID |
| `parent` | BIGINT | Parent registry ID |
| `busy_state` | INTEGER | 1 if the node is in a busy state else 0 |
| `retain_count` | INTEGER | The node reference count |
| `depth` | INTEGER | Node nested depth |

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

### `kernel_panics`

System kernel panic logs.

| Column | Type | Description |
| :--- | :--- | :--- |
| `path` | TEXT | Location of log file |
| `time` | TEXT | Formatted time of the event |
| `registers` | TEXT | A space delimited line of register:value pairs |
| `frame_backtrace` | TEXT | Backtrace of the crashed module |
| `module_backtrace` | TEXT | Modules appearing in the crashed module |
| `dependencies` | TEXT | Module dependencies existing in crashed module |
| `name` | TEXT | Process name corresponding to crashed thread |
| `os_version` | TEXT | Version of the operating system |
| `kernel_version` | TEXT | Version of the system kernel |
| `system_model` | TEXT | Physical system model, for example |
| `uptime` | BIGINT | System uptime at kernel panic in nanoseconds |
| `last_loaded` | TEXT | Last loaded module before panic |
| `last_unloaded` | TEXT | Last unloaded module before panic |

### `keychain_acls`

Applications that have ACL entries in the keychain. NOTE: osquery limits frequent access to keychain files. This limit is controlled by keychain_access_interval flag.

| Column | Type | Description |
| :--- | :--- | :--- |
| `keychain_path` | TEXT | The path of the keychain |
| `authorizations` | TEXT | A space delimited set of authorization attributes |
| `path` | TEXT | The path of the authorized application |
| `description` | TEXT | The description included with the ACL entry |
| `label` | TEXT | An optional label tag that may be included with the keychain entry |

### `keychain_items`

Generic details about keychain items. NOTE: osquery limits frequent access to keychain files. This limit is controlled by keychain_access_interval flag.

| Column | Type | Description |
| :--- | :--- | :--- |
| `label` | TEXT | Generic item name |
| `description` | TEXT | Optional item description |
| `comment` | TEXT | Optional keychain comment |
| `account` | TEXT | Optional item account |
| `created` | TEXT | Date item was created |
| `modified` | TEXT | Date of last modification |
| `type` | TEXT | Keychain item type (class) |
| `pk_hash` | TEXT | Hash of associated public key (SHA1 of subjectPublicKey, see RFC 8520 4.2.1.2) |
| `path` | TEXT | Path to keychain containing item |

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

### `launchd_overrides`

Override keys, per user, for LaunchDaemons and Agents.

| Column | Type | Description |
| :--- | :--- | :--- |
| `label` | TEXT | Daemon or agent service name |
| `key` | TEXT | Name of the override key |
| `value` | TEXT | Overridden value |
| `uid` | BIGINT | User ID applied to the override, 0 applies to all |
| `path` | TEXT | Path to daemon or agent plist |

### `location_services`

Reports the status of the Location Services feature of the OS.

| Column | Type | Description |
| :--- | :--- | :--- |
| `enabled` | INTEGER | 1 if Location Services are enabled, else 0 |

### `managed_policies`

The managed configuration policies from AD, MDM, MCX, etc.

| Column | Type | Description |
| :--- | :--- | :--- |
| `domain` | TEXT | System or manager-chosen domain key |
| `uuid` | TEXT | Optional UUID assigned to policy set |
| `name` | TEXT | Policy key name |
| `value` | TEXT | Policy value |
| `username` | TEXT | Policy applies only this user |
| `manual` | INTEGER | 1 if policy was loaded manually, otherwise 0 |

### `mdfind`

Run searches against the spotlight database.

| Column | Type | Description |
| :--- | :--- | :--- |
| `path` | TEXT | Path of the file returned from spotlight |
| `query` | TEXT | The query that was run to find the file |

### `mdls`

Query file metadata in the Spotlight database.

| Column | Type | Description |
| :--- | :--- | :--- |
| `path` | TEXT | Path of the file |
| `key` | TEXT | Name of the metadata key |
| `value` | TEXT | Value stored in the metadata key |
| `valuetype` | TEXT | CoreFoundation type of data stored in value |

### `nfs_shares`

NFS shares exported by the host.

| Column | Type | Description |
| :--- | :--- | :--- |
| `share` | TEXT | Filesystem path to the share |
| `options` | TEXT | Options string set on the export share |
| `readonly` | INTEGER | 1 if the share is exported readonly else 0 |

### `nvram`

Apple NVRAM variable listing.

| Column | Type | Description |
| :--- | :--- | :--- |
| `name` | TEXT | Variable name |
| `type` | TEXT | Data type (CFData, CFString, etc) |
| `value` | TEXT | Raw variable data |

### `package_bom`

macOS package bill of materials (BOM) file list.

| Column | Type | Description |
| :--- | :--- | :--- |
| `filepath` | TEXT | Package file or directory |
| `uid` | INTEGER | Expected user of file or directory |
| `gid` | INTEGER | Expected group of file or directory |
| `mode` | INTEGER | Expected permissions |
| `size` | BIGINT | Expected file size |
| `modified_time` | INTEGER | Timestamp the file was installed |
| `path` | TEXT | Path of package bom |

### `package_install_history`

macOS package install history.

| Column | Type | Description |
| :--- | :--- | :--- |
| `package_id` | TEXT | Label packageIdentifiers |
| `time` | INTEGER | Label date as UNIX timestamp |
| `name` | TEXT | Package display name |
| `version` | TEXT | Package display version |
| `source` | TEXT | Install source: usually the installer process name |
| `content_type` | TEXT | Package content_type (optional) |

### `package_receipts`

macOS package receipt details.

| Column | Type | Description |
| :--- | :--- | :--- |
| `package_id` | TEXT | Package domain identifier |
| `package_filename` | TEXT | Filename of original .pkg file |
| `version` | TEXT | Installed package version |
| `location` | TEXT | Optional relative install path on volume |
| `install_time` | DOUBLE | Timestamp of install time |
| `installer_name` | TEXT | Name of installer process |
| `path` | TEXT | Path of receipt plist |

### `password_policy`

OpenDirectory account policies for macOS including password content, authentication, and password change policies.

| Column | Type | Description |
| :--- | :--- | :--- |
| `uid` | BIGINT | User ID for the policy, -1 for policies that are global |
| `policy_identifier` | TEXT | Policy Identifier |
| `policy_content` | TEXT | Policy content |
| `policy_description` | TEXT | Policy description |
| `policy_category` | TEXT | Policy category: passwordPolicyAuthentication, passwordPolicyPasswordChange, or passwordPolicyPasswordContent |
| `policy_parameters` | TEXT | Policy parameters serialized as JSON |

### `plist`

Read and parse a plist file.

| Column | Type | Description |
| :--- | :--- | :--- |
| `key` | TEXT | Preference top-level key |
| `subkey` | TEXT | Intermediate key path, includes lists/dicts |
| `value` | TEXT | String value of most CF types |
| `path` | TEXT | (required) read preferences from a plist |

### `power_sensors`

Machine power (currents, voltages, wattages, etc) sensors.

| Column | Type | Description |
| :--- | :--- | :--- |
| `key` | TEXT | The SMC key on macOS |
| `category` | TEXT | The sensor category: currents, voltage, wattage |
| `name` | TEXT | Name of power source |
| `value` | TEXT | Power in Watts |

### `preferences`

macOS defaults and managed preferences.

| Column | Type | Description |
| :--- | :--- | :--- |
| `domain` | TEXT | Application ID usually in com.name.product format |
| `key` | TEXT | Preference top-level key |
| `subkey` | TEXT | Intemediate key path, includes lists/dicts |
| `value` | TEXT | String value of most CF types |
| `forced` | INTEGER | 1 if the value is forced/managed, else 0 |
| `username` | TEXT | (optional) read preferences for a specific user |
| `host` | TEXT |  |

### `quicklook_cache`

| Column | Type | Description |
| :--- | :--- | :--- |
| `path` | TEXT | Path of file |
| `rowid` | INTEGER | Quicklook file rowid key |
| `fs_id` | TEXT | Quicklook file fs_id key |
| `volume_id` | INTEGER | Parsed volume ID from fs_id |
| `inode` | INTEGER | Parsed file ID (inode) from fs_id |
| `mtime` | INTEGER | Parsed version date field |
| `size` | BIGINT | Parsed version size field |
| `label` | TEXT | Parsed version |
| `last_hit_date` | INTEGER | Apple date format for last thumbnail cache hit |
| `hit_count` | TEXT | Number of cache hits on thumbnail |
| `icon_mode` | BIGINT | Thumbnail icon mode |
| `cache_path` | TEXT | Path to cache data |

### `running_apps`

macOS applications currently running on the host system.

| Column | Type | Description |
| :--- | :--- | :--- |
| `pid` | INTEGER | The pid of the application |
| `bundle_identifier` | TEXT | The bundle identifier of the application |
| `is_active` | INTEGER | (DEPRECATED) |

### `safari_extensions`

Safari browser extension details for all users. This table requires Full Disk Access (FDA) permission.

| Column | Type | Description |
| :--- | :--- | :--- |
| `uid` | BIGINT | The local user that owns the extension |
| `name` | TEXT | Extension display name |
| `identifier` | TEXT | Extension identifier |
| `version` | TEXT | Extension long version |
| `sdk` | TEXT | Bundle SDK used to compile extension |
| `description` | TEXT | Optional extension description text |
| `path` | TEXT | Path to the Info.plist describing the extension |
| `bundle_version` | TEXT | The version of the build that identifies an iteration of the bundle |
| `copyright` | TEXT | A human-readable copyright notice for the bundle |

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

### `screenlock`

| Column | Type | Description |
| :--- | :--- | :--- |
| `enabled` | INTEGER | 1 If a password is required after sleep or the screensaver begins; else 0 |
| `grace_period` | INTEGER | The amount of time in seconds the screen must be asleep or the screensaver on before a password is required on-wake. 0 = immediately; -1 = no password is required on-wake |

### `shared_folders`

Folders available to others via SMB or AFP.

| Column | Type | Description |
| :--- | :--- | :--- |
| `name` | TEXT | The shared name of the folder as it appears to other users |
| `path` | TEXT | Absolute path of shared folder on the local system |

### `sharing_preferences`

macOS Sharing preferences.

| Column | Type | Description |
| :--- | :--- | :--- |
| `screen_sharing` | INTEGER | 1 If screen sharing is enabled else 0 |
| `file_sharing` | INTEGER | 1 If file sharing is enabled else 0 |
| `printer_sharing` | INTEGER | 1 If printer sharing is enabled else 0 |
| `remote_login` | INTEGER | 1 If remote login is enabled else 0 |
| `remote_management` | INTEGER | 1 If remote management is enabled else 0 |
| `remote_apple_events` | INTEGER | 1 If remote apple events are enabled else 0 |
| `internet_sharing` | INTEGER | 1 If internet sharing is enabled else 0 |
| `bluetooth_sharing` | INTEGER | 1 If bluetooth sharing is enabled for any user else 0 |
| `disc_sharing` | INTEGER | 1 If CD or DVD sharing is enabled else 0 |
| `content_caching` | INTEGER | 1 If content caching is enabled else 0 |

### `signature`

File (executable, bundle, installer, disk) code signing status.

| Column | Type | Description |
| :--- | :--- | :--- |
| `path` | TEXT | Must provide a path or directory |
| `hash_resources` | INTEGER | Set to 1 to also hash resources, or 0 otherwise. Default is 1 |
| `hash_executable` | INTEGER | Set to 1 to also hash the executable, or 0 otherwise. Default is 1 |
| `arch` | TEXT | If applicable, the arch of the signed code |
| `signed` | INTEGER | 1 If the file is signed else 0 |
| `identifier` | TEXT | The signing identifier sealed into the signature |
| `cdhash` | TEXT | Hash of the application Code Directory |
| `team_identifier` | TEXT | The team signing identifier sealed into the signature |
| `authority` | TEXT | Certificate Common Name |
| `entitlements` | TEXT | JSON representation of the code signing entitlements |

### `sip_config`

| Column | Type | Description |
| :--- | :--- | :--- |
| `config_flag` | TEXT | The System Integrity Protection config flag |
| `enabled` | INTEGER | 1 if this configuration is enabled, otherwise 0 |
| `enabled_nvram` | INTEGER | 1 if this configuration is enabled, otherwise 0 |

### `smc_keys`

| Column | Type | Description |
| :--- | :--- | :--- |
| `key` | TEXT | 4-character key |
| `type` | TEXT | SMC-reported type literal type |
| `size` | INTEGER | Reported size of data in bytes |
| `value` | TEXT | A type-encoded representation of the key value |
| `hidden` | INTEGER | 1 if this key is normally hidden, otherwise 0 |

### `system_extensions`

macOS (>= 10.15) system extension table.

| Column | Type | Description |
| :--- | :--- | :--- |
| `path` | TEXT | Original path of system extension |
| `UUID` | TEXT | Extension unique id |
| `state` | TEXT | System extension state |
| `identifier` | TEXT | Identifier name |
| `version` | TEXT | System extension version |
| `category` | TEXT | System extension category |
| `bundle_path` | TEXT | System extension bundle path |
| `team` | TEXT | Signing team ID |
| `mdm_managed` | INTEGER | 1 if managed by MDM system extension payload configuration, 0 otherwise |

### `system_profiler`

Query system_profiler data types and return the full result as JSON. Returns only the data types specified in the constraints. See available data types with `system_profiler -listDataTypes`.

| Column | Type | Description |
| :--- | :--- | :--- |
| `data_type` | TEXT | The system profiler data type (e.g., SPHardwareDataType) |
| `value` | TEXT | A JSON representation of the full result dictionary for the data type |

### `temperature_sensors`

| Column | Type | Description |
| :--- | :--- | :--- |
| `key` | TEXT | The SMC key on macOS |
| `name` | TEXT | Name of temperature source |
| `celsius` | DOUBLE | Temperature in Celsius |
| `fahrenheit` | DOUBLE | Temperature in Fahrenheit |

### `time_machine_backups`

Backups to drives using TimeMachine. This table requires Full Disk Access (FDA) permission.

| Column | Type | Description |
| :--- | :--- | :--- |
| `destination_id` | TEXT | Time Machine destination ID |
| `backup_date` | INTEGER | Backup Date |

### `time_machine_destinations`

Locations backed up to using Time Machine. This table requires Full Disk Access (FDA) permission.

| Column | Type | Description |
| :--- | :--- | :--- |
| `alias` | TEXT | Human readable name of drive |
| `destination_id` | TEXT | Time Machine destination ID |
| `consistency_scan_date` | INTEGER | Consistency scan date |
| `root_volume_uuid` | TEXT | Root UUID of backup volume |
| `bytes_available` | INTEGER | Bytes available on volume |
| `bytes_used` | INTEGER | Bytes used on volume |
| `encryption` | TEXT | Last known encrypted state |

### `unified_log`

| Column | Type | Description |
| :--- | :--- | :--- |
| `timestamp` | BIGINT | unix timestamp associated with the entry |
| `timestamp_double` | TEXT | floating point timestamp associated with the entry |
| `storage` | INTEGER | the storage category for the entry |
| `message` | TEXT | composed message |
| `activity` | BIGINT | the activity ID associate with the entry |
| `process` | TEXT | the name of the process that made the entry |
| `pid` | BIGINT | the pid of the process that made the entry |
| `sender` | TEXT | the name of the binary image that made the entry |
| `tid` | BIGINT | the tid of the thread that made the entry |
| `category` | TEXT | the category of the os_log_t used |
| `subsystem` | TEXT | the subsystem of the os_log_t used |
| `level` | TEXT | the severity level of the entry (undefined, debug, info, default, error, fault) |
| `max_rows` | INTEGER | the max number of rows returned (defaults to 100) |
| `predicate` | TEXT | predicate to search (see `log help predicates`), note that this is merged into the predicate created from the column constraints |

### `user_interaction_events`

| Column | Type | Description |
| :--- | :--- | :--- |
| `time` | BIGINT | Time |

### `virtual_memory_info`

Darwin Virtual Memory statistics.

| Column | Type | Description |
| :--- | :--- | :--- |
| `free` | BIGINT | Total number of free pages. |
| `active` | BIGINT | Total number of active pages. |
| `inactive` | BIGINT | Total number of inactive pages. |
| `speculative` | BIGINT | Total number of speculative pages. |
| `throttled` | BIGINT | Total number of throttled pages. |
| `wired` | BIGINT | Total number of wired down pages. |
| `purgeable` | BIGINT | Total number of purgeable pages. |
| `faults` | BIGINT | Total number of calls to vm_faults. |
| `copy` | BIGINT | Total number of copy-on-write pages. |
| `zero_fill` | BIGINT | Total number of zero filled pages. |
| `reactivated` | BIGINT | Total number of reactivated pages. |
| `purged` | BIGINT | Total number of purged pages. |
| `file_backed` | BIGINT | Total number of file backed pages. |
| `anonymous` | BIGINT | Total number of anonymous pages. |
| `uncompressed` | BIGINT | Total number of uncompressed pages. |
| `compressor` | BIGINT | The number of pages used to store compressed VM pages. |
| `decompressed` | BIGINT | The total number of pages that have been decompressed by the VM compressor. |
| `compressed` | BIGINT | The total number of pages that have been compressed by the VM compressor. |
| `page_ins` | BIGINT | The total number of requests for pages from a pager. |
| `page_outs` | BIGINT | Total number of pages paged out. |
| `swap_ins` | BIGINT | The total number of compressed pages that have been swapped out to disk. |
| `swap_outs` | BIGINT | The total number of compressed pages that have been swapped back in from disk. |

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

### `wifi_status`

macOS current WiFi status. This table requires Full Disk Access (FDA) permission to retrieve network_name.

| Column | Type | Description |
| :--- | :--- | :--- |
| `interface` | TEXT | Name of the interface |
| `ssid` | TEXT | SSID octets of the network |
| `bssid` | TEXT | The current basic service set identifier |
| `network_name` | TEXT | Name of the network |
| `country_code` | TEXT | The country code (ISO/IEC 3166-1:1997) for the network |
| `security_type` | TEXT | Type of security on this network |
| `rssi` | INTEGER | The current received signal strength indication (dbm) |
| `noise` | INTEGER | The current noise measurement (dBm) |
| `channel` | INTEGER | Channel number |
| `channel_width` | INTEGER | Channel width |
| `channel_band` | INTEGER | Channel band |
| `transmit_rate` | TEXT | The current transmit rate |
| `mode` | TEXT | The current operating mode for the Wi-Fi interface |

### `wifi_survey`

Scan for nearby WiFi networks.

| Column | Type | Description |
| :--- | :--- | :--- |
| `interface` | TEXT | Name of the interface |
| `ssid` | TEXT | SSID octets of the network |
| `bssid` | TEXT | The current basic service set identifier |
| `network_name` | TEXT | Name of the network |
| `country_code` | TEXT | The country code (ISO/IEC 3166-1:1997) for the network |
| `rssi` | INTEGER | The current received signal strength indication (dbm) |
| `noise` | INTEGER | The current noise measurement (dBm) |
| `channel` | INTEGER | Channel number |
| `channel_width` | INTEGER | Channel width |
| `channel_band` | INTEGER | Channel band |

### `xprotect_entries`

| Column | Type | Description |
| :--- | :--- | :--- |
| `name` | TEXT | Description of XProtected malware |
| `launch_type` | TEXT | Launch services content type |
| `identity` | TEXT | XProtect identity (SHA1) of content |
| `filename` | TEXT | Use this file name to match |
| `filetype` | TEXT | Use this file type to match |
| `optional` | INTEGER | Match any of the identities/patterns for this XProtect name |
| `uses_pattern` | INTEGER | Uses a match pattern instead of identity |

### `xprotect_meta`

| Column | Type | Description |
| :--- | :--- | :--- |
| `identifier` | TEXT | Browser plugin or extension identifier |
| `type` | TEXT | Either plugin or extension |
| `developer_id` | TEXT | Developer identity (SHA1) of extension |
| `min_version` | TEXT | The minimum allowed plugin version. |

### `xprotect_reports`

Database of XProtect matches (if user generated/sent an XProtect report).

| Column | Type | Description |
| :--- | :--- | :--- |
| `name` | TEXT | Description of XProtected malware |
| `user_action` | TEXT | Action taken by user after prompted |
| `time` | TEXT | Quarantine alert time |

## Additional Shared & POSIX Tables

### `certificates`

| Column | Type | Description |
| :--- | :--- | :--- |
| `common_name` | TEXT | Certificate CommonName |
| `subject` | TEXT | Certificate distinguished name (deprecated, use subject2) |
| `subject2` | TEXT | Certificate distinguished name |
| `issuer` | TEXT | Certificate issuer distinguished name (deprecated, use issuer2) |
| `issuer2` | TEXT | Certificate issuer distinguished name |
| `ca` | INTEGER | 1 if CA: true (certificate is an authority) else 0 |
| `self_signed` | INTEGER | 1 if self-signed, else 0 |
| `not_valid_before` | DATETIME | Lower bound of valid date |
| `not_valid_after` | DATETIME | Certificate expiration data |
| `signing_algorithm` | TEXT | Signing algorithm used |
| `key_algorithm` | TEXT | Key algorithm used |
| `key_strength` | TEXT | Key size used for RSA/DSA, or curve name |
| `key_usage` | TEXT | Certificate key usage and extended key usage |
| `subject_key_id` | TEXT | SKID an optionally included SHA1 |
| `authority_key_id` | TEXT | AKID an optionally included SHA1 |
| `sha1` | TEXT | SHA1 hash of the raw certificate contents |
| `path` | TEXT | Path to Keychain or PEM bundle |
| `serial` | TEXT | Certificate serial number |
| `sid` | TEXT | SID |
| `store_location` | TEXT | Certificate system store location |
| `store` | TEXT | Certificate system store |
| `username` | TEXT | Username |
| `store_id` | TEXT | Exists for service/user stores. Contains raw store id provided by WinAPI. |

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

### `shell_history`

A line-delimited (command) table of per-user .*_history data.

| Column | Type | Description |
| :--- | :--- | :--- |
| `uid` | BIGINT | Shell history owner |
| `time` | INTEGER | Entry timestamp. It could be absent, default value is 0. |
| `command` | TEXT | Unparsed date/line/command history line |
| `history_file` | TEXT | Path to the .*_history for this user |

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
