---
name: pack-it-compliance
description: Enterprise IT compliance and endpoint security configuration query pack. Contains 32 queries auditing disk encryption (FileVault, BitLocker), host firewall state, system integrity protection (SIP), screen lock timeout, password policies, and admin users across macOS, Linux, and Windows.
---

# IT Compliance & Endpoint Hygiene Query Pack

The `pack-it-compliance` skill equips agents with curated queries and diagnostic procedures from `osquery_data/packs/it-compliance.conf`. This query pack focuses on it compliance & endpoint hygiene query pack.

## Threat Model & Scope
Enterprise IT compliance frameworks (SOC 2, ISO 27001, HIPAA, PCI-DSS) require verification of endpoint controls:
- Full Disk Encryption: FileVault (macOS), BitLocker (Windows), LUKS (Linux).
- Host Firewalls: Application Layer Firewall (macOS), Windows Firewall, iptables/nftables (Linux).
- Privilege Management: Enumerating local administrator accounts and sudo users.
- Patch Currency: Tracking operating system updates and security patches.

## Triage & Investigation Runbook
### Compliance Audit Runbook
1. **Encryption & Firewall Check**: Run queries for `disk_encryption`, `alf`, and Windows firewall profiles.
2. **Administrative Accounts**: Run queries against `users` and `groups` to detect unauthorized local admin accounts.
3. **Audit Report Generation**: Compile evidence logs for compliance auditors.

## Complete Query Catalog

### 1. `osquery_info`
- **Description**: Retrieves the current version of the running osquery in the target system and where the configuration was loaded from.
- **Context / Value**: Identify if your infrastructure is running the correct osquery version and which hosts may have drifted
- **Interval**: 86400 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select * from time, osquery_info;
```

### 2. `ad_config`
- **Description**: Retrieves the Active Directory configuration for the target machine, attached to the domain (requires sudo).
- **Context / Value**: Helps you debug domain binding / Active Directory issues in your environment.
- **Interval**: 86400 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select * from ad_config;
```

### 3. `kernel_info`
- **Description**: Retrieves information from the current kernel in the target system.
- **Context / Value**: Identify out of date kernels or version drift across your infrastructure
- **Interval**: 86400 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select * from kernel_info;
```

### 4. `os_version`
- **Description**: Retrieves information from the Operative System where osquery is currently running.
- **Context / Value**: Identify out of date operating systems or version drift across your infrastructure
- **Interval**: 86400 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select * from os_version;
```

### 5. `alf`
- **Description**: Retrieves the configuration values for the Application Layer Firewall for OSX.
- **Context / Value**: Verify firewall settings are as expected
- **Interval**: 86400 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select * from alf;
```

### 6. `alf_exceptions`
- **Description**: Retrieves the exceptions for the Application Layer Firewall in OSX.
- **Context / Value**: Verify firewall settings are as expected
- **Interval**: 86400 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select * from alf_exceptions;
```

### 7. `alf_services`
- **Description**: Retrieves the services for the Application Layer Firewall in OSX.
- **Context / Value**: Verify firewall settings are as expected
- **Interval**: 86400 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select * from alf_services;
```

### 8. `alf_explicit_auths`
- **Description**: Retrieves the list of processes with explicit authorization for the Application Layer Firewall.
- **Context / Value**: Verify firewall settings are as expected
- **Interval**: 86400 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select * from alf_explicit_auths;
```

### 9. `mounts`
- **Description**: Retrieves the current list of mounted drives in the target system.
- **Context / Value**: Verify if mounts are accessible to those who need it
- **Interval**: 86400 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select * from mounts;
```

### 10. `nfs_shares`
- **Description**: Retrieves the current list of Network File System mounted shares.
- **Context / Value**: Verify if shares are accessible to those who need it
- **Interval**: 86400 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select * from nfs_shares;
```

### 11. `windows_shared_resources`
- **Description**: Retrieves the list of shared resources in the target Windows system.
- **Context / Value**: General security posture.
- **Interval**: 86400 seconds
- **Minimum Osquery Version**: 2.0.0
- **SQL Query**:
```sql
select * from shared_resources;
```

### 12. `browser_plugins`
- **Description**: Retrieves the list of C/NPAPI browser plugins in the target system.
- **Context / Value**: General security posture.
- **Interval**: 86400 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select * from users join browser_plugins using (uid);
```

### 13. `safari_extensions`
- **Description**: Retrieves the list of extensions for Safari in the target system.
- **Context / Value**: General security posture.
- **Interval**: 86400 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select * from users join safari_extensions using (uid);
```

### 14. `chrome_extensions`
- **Description**: Retrieves the list of extensions for Chrome in the target system.
- **Context / Value**: General security posture.
- **Interval**: 86400 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select * from users join chrome_extensions using (uid);
```

### 15. `firefox_addons`
- **Description**: Retrieves the list of addons for Firefox in the target system.
- **Context / Value**: General security posture.
- **Interval**: 86400 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select * from users join firefox_addons using (uid);
```

### 16. `homebrew_packages`
- **Description**: Retrieves the list of brew packages installed in the target OSX system.
- **Context / Value**: General security posture.
- **Interval**: 86400 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select * from homebrew_packages;
```

### 17. `windows_programs`
- **Description**: Retrieves the list of products as they are installed by Windows Installer in the target Windows system.
- **Context / Value**: General security posture.
- **Interval**: 86400 seconds
- **Minimum Osquery Version**: 2.0.0
- **SQL Query**:
```sql
select * from programs;
```

### 18. `windows_patches`
- **Description**: Retrieves all the information for the current windows drivers in the target Windows system.
- **Interval**: 86400 seconds
- **Minimum Osquery Version**: 2.2.0
- **SQL Query**:
```sql
select * from patches;
```

### 19. `package_receipts`
- **Description**: Retrieves all the PKG related information stored in OSX.
- **Context / Value**: General security posture.
- **Interval**: 86400 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select * from package_receipts;
```

### 20. `usb_devices`
- **Description**: Retrieves the current list of USB devices in the target system.
- **Context / Value**: General security posture.
- **Interval**: 86400 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select * from usb_devices;
```

### 21. `keychain_items`
- **Description**: Retrieves all the items contained in the keychain in the target OSX system.
- **Context / Value**: General security posture.
- **Interval**: 86400 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select * from keychain_items;
```

### 22. `deb_packages`
- **Description**: Retrieves all the installed DEB packages in the target Linux system.
- **Context / Value**: General security posture.
- **Interval**: 86400 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select * from deb_packages;
```

### 23. `apt_sources`
- **Description**: Retrieves all the APT sources to install packages from in the target Linux system.
- **Context / Value**: General security posture.
- **Interval**: 86400 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select * from apt_sources;
```

### 24. `portage_packages`
- **Description**: Retrieves all the packages installed with portage from the target Linux system.
- **Context / Value**: General security posture.
- **Interval**: 86400 seconds
- **Minimum Osquery Version**: 2.0.0
- **SQL Query**:
```sql
select * from portage_use;
```

### 25. `kernel_modules`
- **Description**: Retrieves the current list of loaded kernel modules in the target Linux system.
- **Context / Value**: General security posture.
- **Interval**: 86400 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select * from kernel_modules;
```

### 26. `windows_drivers`
- **Description**: Retrieves all the information for the current windows drivers in the target Windows system.
- **Interval**: 86400 seconds
- **Minimum Osquery Version**: 2.2.0
- **SQL Query**:
```sql
select * from drivers;
```

### 27. `rpm_packages`
- **Description**: Retrieves all the installed RPM packages in the target Linux system.
- **Context / Value**: General security posture.
- **Interval**: 86400 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select * from rpm_packages;
```

### 28. `installed_applications`
- **Description**: Retrieves all the currently installed applications in the target OSX system.
- **Context / Value**: Find currently installed applications and versions of each.
- **Interval**: 86400 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select * from apps;
```

### 29. `disk_encryption`
- **Description**: Retrieves the current disk encryption status for the target system.
- **Context / Value**: Identifies a system potentially vulnerable to disk cloning.
- **Interval**: 86400 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select * from disk_encryption;
```

### 30. `launchd`
- **Description**: Retrieves all the daemons that will run in the start of the target OSX system.
- **Context / Value**: Visibility on what starts in the system.
- **Interval**: 86400 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select * from launchd;
```

### 31. `iptables`
- **Description**: Retrieves the current filters and chains per filter in the target system.
- **Context / Value**: General security posture.
- **Interval**: 86400 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select * from iptables;
```

### 32. `sip_config`
- **Description**: Retrieves the current System Integrity Protection configuration in the target system.
- **Context / Value**: General security posture.
- **Interval**: 86400 seconds
- **Minimum Osquery Version**: 1.7.0
- **SQL Query**:
```sql
select * from sip_config;
```

## Referenced Table Schemas

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

### `firefox_addons`

Firefox browser extensions, webapps, and addons.

| Column | Type | Description |
| :--- | :--- | :--- |
| `uid` | BIGINT | The local user that owns the addon |
| `name` | TEXT | Addon display name |
| `identifier` | TEXT | Addon identifier |
| `creator` | TEXT | Addon-supported creator string |
| `type` | TEXT | Extension, addon, webapp |
| `version` | TEXT | Addon-supplied version string |
| `description` | TEXT | Addon-supplied description string |
| `source_url` | TEXT | URL that installed the addon |
| `visible` | INTEGER | 1 If the addon is shown in browser else 0 |
| `active` | INTEGER | 1 If the addon is active else 0 |
| `disabled` | INTEGER | 1 If the addon is application-disabled else 0 |
| `autoupdate` | INTEGER | 1 If the addon applies background updates else 0 |
| `location` | TEXT | Global, profile location |
| `path` | TEXT | Path to plugin bundle |

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

### `kernel_info`

Basic active kernel information.

| Column | Type | Description |
| :--- | :--- | :--- |
| `version` | TEXT | Kernel version |
| `arguments` | TEXT | Kernel arguments |
| `path` | TEXT | Kernel path |
| `device` | TEXT | Kernel device identifier |

### `kernel_modules`

Linux kernel modules both loaded and within the load search path.

| Column | Type | Description |
| :--- | :--- | :--- |
| `name` | TEXT | Module name |
| `size` | BIGINT | Size of module content |
| `used_by` | TEXT | Module reverse dependencies |
| `status` | TEXT | Kernel module status |
| `address` | TEXT | Kernel module address |

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

### `os_version`

A single row containing the operating system name and version.

| Column | Type | Description |
| :--- | :--- | :--- |
| `name` | TEXT | Distribution or product name |
| `version` | TEXT | Pretty, suitable for presentation, OS version |
| `major` | INTEGER | Major release version |
| `minor` | INTEGER | Minor release version |
| `patch` | INTEGER | Optional patch release |
| `build` | TEXT | Optional build-specific or variant string |
| `platform` | TEXT | OS Platform or ID |
| `platform_like` | TEXT | Closely related platforms |
| `codename` | TEXT | OS version codename |
| `arch` | TEXT | OS Architecture |
| `extra` | TEXT | Optional extra release specification |
| `install_date` | BIGINT | The install date of the OS. |
| `revision` | INTEGER | Update Build Revision, refers to the specific revision number of a Windows update |
| `pid_with_namespace` | INTEGER | Pids that contain a namespace |
| `mount_namespace_id` | TEXT | Mount namespace id |

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

### `portage_use`

List of enabled portage USE values for specific package.

| Column | Type | Description |
| :--- | :--- | :--- |
| `package` | TEXT | Package name |
| `version` | TEXT | The version of the installed package |
| `use` | TEXT | USE flag which has been enabled for package |

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

### `sip_config`

| Column | Type | Description |
| :--- | :--- | :--- |
| `config_flag` | TEXT | The System Integrity Protection config flag |
| `enabled` | INTEGER | 1 if this configuration is enabled, otherwise 0 |
| `enabled_nvram` | INTEGER | 1 if this configuration is enabled, otherwise 0 |

### `time`

Track current date and time in UTC.

| Column | Type | Description |
| :--- | :--- | :--- |
| `weekday` | TEXT | Current weekday in UTC |
| `year` | INTEGER | Current year in UTC |
| `month` | INTEGER | Current month in UTC |
| `day` | INTEGER | Current day in UTC |
| `hour` | INTEGER | Current hour in UTC |
| `minutes` | INTEGER | Current minutes in UTC |
| `seconds` | INTEGER | Current seconds in UTC |
| `timezone` | TEXT | Timezone for reported time (hardcoded to UTC) |
| `local_timezone` | TEXT | Current local timezone in of the system |
| `unix_time` | INTEGER | Current UNIX time in UTC |
| `timestamp` | TEXT | Current timestamp (log format) in UTC |
| `datetime` | TEXT | Current date and time (ISO format) in UTC |
| `iso_8601` | TEXT | Current time (ISO format) in UTC |
| `win_timestamp` | BIGINT | Timestamp value in 100 nanosecond units |

### `usb_devices`

USB devices that are actively plugged into the host system.

| Column | Type | Description |
| :--- | :--- | :--- |
| `usb_address` | INTEGER | USB Device used address |
| `usb_port` | INTEGER | USB Device used port |
| `vendor` | TEXT | USB Device vendor string |
| `vendor_id` | TEXT | Hex encoded USB Device vendor identifier |
| `version` | TEXT | USB Device version number |
| `model` | TEXT | USB Device model string |
| `model_id` | TEXT | Hex encoded USB Device model identifier |
| `serial` | TEXT | USB Device serial connection |
| `class` | TEXT | USB Device class |
| `subclass` | TEXT | USB Device subclass |
| `protocol` | TEXT | USB Device protocol |
| `removable` | INTEGER | 1 If USB device is removable else 0 |

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
