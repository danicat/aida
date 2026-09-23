---
name: pack-vuln-management
description: Vulnerability management and software inventory query pack. Contains 18 queries auditing OS versions, kernel releases, installed packages (deb, rpm, Homebrew, Portage, Python pip), browser extensions, and outdated software. Use for asset inventory, patch verification, and vulnerability scanning.
---

# Vulnerability Management & Software Inventory Query Pack

The `pack-vuln-management` skill equips agents with curated queries and diagnostic procedures from `osquery_data/packs/vuln-management.conf`. This query pack focuses on vulnerability management & software inventory query pack.

## Threat Model & Scope
Vulnerability management relies on comprehensive software inventory and fast discovery of vulnerable dependencies. This pack tracks:
- System & Kernel versions across Linux, macOS, and Windows.
- Operating system package managers: `deb_packages`, `rpm_packages`, `portage_packages`, and `homebrew_packages`.
- Language runtimes and application dependencies: `python_packages`.
- Browser extensions and plugins across Chrome, Firefox, Safari, and Opera.

## Triage & Investigation Runbook
### Vulnerability Assessment Workflow
1. **Asset Identification**: Run `os_version` and `kernel_info` to establish operating system and kernel patch levels.
2. **Package Inventory Scan**: Execute package queries (`deb_packages`, `rpm_packages`, or `homebrew_packages`) matching target CVE software identifiers.
3. **Browser & Application Audit**: Enumerate browser extensions and third-party application bundles (`apps`).
4. **Remediation Tracking**: After applying security updates, re-run package queries to confirm version bump.

## Complete Query Catalog

### 1. `kernel_info`
- **Description**: Retrieves information from the current kernel in the target system.
- **Context / Value**: Kernel version can tell you vulnerabilities based on the version
- **Interval**: 86400 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select * from kernel_info;
```

### 2. `os_version`
- **Description**: Retrieves the current version of the running osquery in the target system and where the configuration was loaded from.
- **Context / Value**: OS version will tell which distribution the OS is running on, allowing to detect the main distribution
- **Interval**: 86400 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select * from os_version;
```

### 3. `kextstat`
- **Description**: Retrieves all the information about the current kernel extensions for the target OSX system.
- **Context / Value**: Only for OS X.  It may pinpoint inserted modules that can carry malicious payloads.
- **Interval**: 86400 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select * from kernel_extensions;
```

### 4. `kernel_modules`
- **Description**: Retrieves all the information for the current kernel modules in the target Linux system.
- **Context / Value**: Only for Linux.  It may pinpoint inserted modules that can carry malicious payloads.
- **Interval**: 86400 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select * from kernel_modules;
```

### 5. `installed_applications`
- **Description**: Retrieves all the currently installed applications in the target OSX system.
- **Context / Value**: This, with the help of a vulnerability feed, can help tell if a vulnerable application is installed.
- **Interval**: 86400 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select * from apps;
```

### 6. `browser_plugins`
- **Description**: Retrieves the list of C/NPAPI browser plugins in the target system.
- **Context / Value**: General security posture.
- **Interval**: 86400 seconds
- **Minimum Osquery Version**: 1.6.1
- **SQL Query**:
```sql
select browser_plugins.* from users join browser_plugins using (uid);
```

### 7. `safari_extensions`
- **Description**: Retrieves the list of extensions for Safari in the target system.
- **Context / Value**: General security posture.
- **Interval**: 86400 seconds
- **Minimum Osquery Version**: 1.6.1
- **SQL Query**:
```sql
select safari_extensions.* from users join safari_extensions using (uid);
```

### 8. `opera_extensions`
- **Description**: Retrieves the list of extensions for Opera in the target system.
- **Context / Value**: General security posture.
- **Interval**: 86400 seconds
- **Minimum Osquery Version**: 1.6.1
- **SQL Query**:
```sql
select opera_extensions.* from users join opera_extensions using (uid);
```

### 9. `chrome_extensions`
- **Description**: Retrieves the list of extensions for Chrome in the target system.
- **Context / Value**: General security posture.
- **Interval**: 86400 seconds
- **Minimum Osquery Version**: 1.6.1
- **SQL Query**:
```sql
select chrome_extensions.* from users join chrome_extensions using (uid);
```

### 10. `firefox_addons`
- **Description**: Retrieves the list of addons for Firefox in the target system.
- **Context / Value**: General security posture.
- **Interval**: 86400 seconds
- **Minimum Osquery Version**: 1.6.1
- **SQL Query**:
```sql
select firefox_addons.* from users join firefox_addons using (uid);
```

### 11. `homebrew_packages`
- **Description**: Retrieves the list of brew packages installed in the target OSX system.
- **Context / Value**: This, with the help of a vulnerability feed, can help tell if a vulnerable application is installed.
- **Interval**: 86400 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select * from homebrew_packages;
```

### 12. `package_receipts`
- **Description**: Retrieves all the PKG related information stored in OSX.
- **Context / Value**: It could give you a trail of installed/deleted packages
- **Interval**: 86400 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select * from package_receipts;
```

### 13. `deb_packages`
- **Description**: Retrieves all the installed DEB packages in the target Linux system.
- **Context / Value**: This, with the help of vulnerability feed, can help tell if a vulnerable application is installed.
- **Interval**: 86400 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select * from deb_packages;
```

### 14. `apt_sources`
- **Description**: Retrieves all the APT sources to install packages from in the target Linux system.
- **Context / Value**: In the future this may not have a lot of value as we expect to have installed only signed packages
- **Interval**: 86400 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select * from apt_sources;
```

### 15. `portage_packages`
- **Description**: Retrieves all the installed packages on the target Linux system.
- **Context / Value**: This, with the help of vulnerability feed, can help tell if a vulnerable application is installed.
- **Interval**: 86400 seconds
- **Minimum Osquery Version**: 2.0.0
- **SQL Query**:
```sql
select * from portage_packages;
```

### 16. `rpm_packages`
- **Description**: Retrieves all the installed RPM packages in the target Linux system.
- **Context / Value**: This, with the help of vulnerability feed, can help tell if a vulnerable application is installed.
- **Interval**: 86400 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select * from rpm_packages;
```

### 17. `unauthenticated_sparkle_feeds`
- **Description**: Retrieves all application bundles using unauthenticated Sparkle update feeds. See (https://vulnsec.com/2016/osx-apps-vulnerabilities/) for details.
- **Context / Value**: Tracking vulnerable applications updates may allow blocking of DNS or removal by BundleID.
- **Interval**: 86400 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select feeds.*, p2.value as sparkle_version from (select a.name as app_name, a.path as app_path, a.bundle_identifier as bundle_id, p.value as feed_url from (select name, path, bundle_identifier from apps) a, plist p where p.path = a.path || '/Contents/Info.plist' and p.key = 'SUFeedURL' and feed_url like 'http://%') feeds left outer join plist p2 on p2.path = app_path || '/Contents/Frameworks/Sparkle.framework/Resources/Info.plist' where (p2.key = 'CFBundleShortVersionString' OR coalesce(p2.key, '') = '');
```

### 18. `backdoored_python_packages`
- **Description**: Watches for the backdoored Python packages installed on system. See (http://www.nbu.gov.sk/skcsirt-sa-20170909-pypi/index.html)
- **Context / Value**: Gives some assurances that no bad Python packages are installed on the system.
- **Interval**: 86400 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select name as package_name, version as package_version, path as package_path from python_packages where package_name = 'acqusition' or package_name = 'apidev-coop' or package_name = 'bzip' or package_name = 'crypt' or package_name = 'django-server' or package_name = 'pwd' or package_name = 'setup-tools' or package_name = 'telnet' or package_name = 'urlib3' or package_name = 'urllib';
```

## Referenced Table Schemas

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

### `plist`

Read and parse a plist file.

| Column | Type | Description |
| :--- | :--- | :--- |
| `key` | TEXT | Preference top-level key |
| `subkey` | TEXT | Intermediate key path, includes lists/dicts |
| `value` | TEXT | String value of most CF types |
| `path` | TEXT | (required) read preferences from a plist |

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

### `python_packages`

Python packages installed in a system. NOTE: when querying on windows, even without a users cross join, all user installed python packages will be returned. This special behavior is to not break original functionality.

| Column | Type | Description |
| :--- | :--- | :--- |
| `name` | TEXT | Package display name |
| `uid` | BIGINT | The local user that owns the python package |
| `version` | TEXT | Package-supplied version |
| `summary` | TEXT | Package-supplied summary |
| `author` | TEXT | Optional package author |
| `license` | TEXT | License under which package is launched |
| `path` | TEXT | Path at which this module resides |
| `directory` | TEXT | Directory where Python modules are located |
| `pid_with_namespace` | INTEGER | Pids that contain a namespace |

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
