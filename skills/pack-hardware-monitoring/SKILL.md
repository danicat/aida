---
name: pack-hardware-monitoring
description: Hardware and peripheral device monitoring query pack. Features 17 queries inspecting PCI devices, USB devices, CPU topology, ACPI/SMBIOS tables, fan speeds, temperature sensors, and firmware health. Use to track peripheral connectivity, detect unauthorized USB devices, and monitor thermal telemetry.
---

# Hardware & Peripheral Monitoring Query Pack

The `pack-hardware-monitoring` skill equips agents with curated queries and diagnostic procedures from `osquery_data/packs/hardware-monitoring.conf`. This query pack focuses on hardware & peripheral monitoring query pack.

## Threat Model & Scope
Hardware auditing and peripheral monitoring address physical attack vectors and hardware degradation:
- Rogue peripheral insertion: BadUSB, Rubber Ducky, or unauthorized mass storage devices.
- PCI device anomalies: DMA attack hardware or unauthorized expansion cards.
- System thermal and fan telemetry: Overheating or thermal throttling.
- Firmware & BIOS validation: ACPI tables, SMBIOS details, and NVRAM variables.

## Triage & Investigation Runbook
### Hardware Triage Runbook
1. **Peripheral Audit**: Query `usb_devices` and `pci_devices` to detect newly attached hardware.
2. **Thermal & Sensor Check**: Run `temperature_sensors` and `fan_speed_sensors` to diagnose thermal health.
3. **Firmware Integrity**: Query `smbios_tables` and `nvram` to audit BIOS vendor and boot parameters.

## Complete Query Catalog

### 1. `acpi_tables`
- **Description**: General reporting and heuristics monitoring.
- **Interval**: 86400 seconds
- **Minimum Osquery Version**: 1.3.0
- **SQL Query**:
```sql
select * from acpi_tables;
```

### 2. `cpuid`
- **Description**: General reporting and heuristics monitoring.
- **Interval**: 86400 seconds
- **Minimum Osquery Version**: 1.0.4
- **SQL Query**:
```sql
select feature, value, output_register, output_bit, input_eax from cpuid;
```

### 3. `smbios_tables`
- **Description**: General reporting and heuristics monitoring.
- **Interval**: 86400 seconds
- **Minimum Osquery Version**: 1.3.0
- **SQL Query**:
```sql
select * from smbios_tables;
```

### 4. `nvram`
- **Description**: Report on crashes, alternate boots, and boot arguments.
- **Interval**: 7200 seconds
- **Minimum Osquery Version**: 1.0.2
- **SQL Query**:
```sql
select * from nvram where name not in ('backlight-level', 'SystemAudioVolumeDB', 'SystemAudioVolume');
```

### 5. `kernel_info`
- **Description**: Report the booted kernel, potential arguments, and the device.
- **Interval**: 7200 seconds
- **Minimum Osquery Version**: 1.4.0
- **SQL Query**:
```sql
select * from kernel_info join hash using (path);
```

### 6. `pci_devices`
- **Description**: Report an inventory of PCI devices. Attaches and detaches will show up in hardware_events.
- **Interval**: 7200 seconds
- **Minimum Osquery Version**: 1.0.4
- **SQL Query**:
```sql
select * from pci_devices;
```

### 7. `fan_speeds`
- **Description**: Report current fan speeds in the target OSX system.
- **Interval**: 7200 seconds
- **Minimum Osquery Version**: 1.7.1
- **SQL Query**:
```sql
select * from fan_speed_sensors;
```

### 8. `temperatures`
- **Description**: Report current machine temperatures in the target OSX system.
- **Interval**: 7200 seconds
- **Minimum Osquery Version**: 1.7.1
- **SQL Query**:
```sql
select * from temperature_sensors;
```

### 9. `usb_devices`
- **Description**: Report an inventory of USB devices. Attaches and detaches will show up in hardware_events.
- **Interval**: 7200 seconds
- **Minimum Osquery Version**: 1.2.0
- **SQL Query**:
```sql
select * from usb_devices;
```

### 10. `hardware_events`
- **Description**: Retrieves all the hardware related events in the target OSX system.
- **Context / Value**: Determine if a third party device was attached to the system.
- **Interval**: 7200 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select * from hardware_events where path <> '' or model <> '';
```

### 11. `darwin_kernel_system_controls`
- **Description**: Double check the information reported in kernel_info and report the kernel signature.
- **Interval**: 7200 seconds
- **Minimum Osquery Version**: 1.4.3
- **SQL Query**:
```sql
select * from system_controls where subsystem = 'kern' and (name like '%boot%' or name like '%secure%' or name like '%single%');
```

### 12. `iokit_devicetree`
- **Description**: General inventory of IOKit's devices on OS X.
- **Interval**: 86400 seconds
- **Minimum Osquery Version**: 1.3.0
- **SQL Query**:
```sql
select * from iokit_devicetree;
```

### 13. `efi_file_hashes`
- **Description**: Hash files related to EFI platform updates and EFI bootloaders on primary boot partition. This does not hash bootloaders on the EFI/boot partition.
- **Interval**: 7200 seconds
- **Minimum Osquery Version**: 1.6.1
- **SQL Query**:
```sql
select file.path, uid, gid, mode, 0 as atime, mtime, ctime, md5, sha1, sha256 from (select * from file where path like '/System/Library/CoreServices/%.efi' union select * from file where path like '/System/Library/LaunchDaemons/com.apple%efi%') file join hash using (path);
```

### 14. `kernel_extensions`
- **Description**: Retrieves all the information about the current kernel extensions for the target OSX system.
- **Interval**: 7200 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select * from kernel_extensions;
```

### 15. `kernel_modules`
- **Description**: Retrieves all the information for the current kernel modules in the target Linux system.
- **Interval**: 7200 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select * from kernel_modules;
```

### 16. `windows_drivers`
- **Description**: Retrieves all the information for the current windows drivers in the target Windows system.
- **Interval**: 7200 seconds
- **Minimum Osquery Version**: 2.2.0
- **SQL Query**:
```sql
select * from drivers;
```

### 17. `device_nodes`
- **Description**: Inventory all 'device' nodes in /dev/.
- **Interval**: 7200 seconds
- **Minimum Osquery Version**: 1.6.0
- **SQL Query**:
```sql
select file.path, uid, gid, mode, 0 as atime, mtime, ctime, block_size, type from file where directory = '/dev/';
```

## Referenced Table Schemas

### `acpi_tables`

Firmware ACPI functional table common metadata and content.

| Column | Type | Description |
| :--- | :--- | :--- |
| `name` | TEXT | ACPI table name |
| `size` | INTEGER | Size of compiled table data |
| `md5` | TEXT | MD5 hash of table content |

### `cpuid`

Useful CPU features from the cpuid ASM call.

| Column | Type | Description |
| :--- | :--- | :--- |
| `feature` | TEXT | Present feature flags |
| `value` | TEXT | Bit value or string |
| `output_register` | TEXT | Register used to for feature value |
| `output_bit` | INTEGER | Bit in register value for feature value |
| `input_eax` | TEXT | Value of EAX used |

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

### `hardware_events`

Hardware (PCI/USB/HID) events from UDEV or IOKit.

| Column | Type | Description |
| :--- | :--- | :--- |
| `action` | TEXT | Remove, insert, change properties, etc |
| `path` | TEXT | Local device path assigned (optional) |
| `type` | TEXT | Type of hardware and hardware event |
| `driver` | TEXT | Driver claiming the device |
| `vendor` | TEXT | Hardware device vendor |
| `vendor_id` | TEXT | Hex encoded Hardware vendor identifier |
| `model` | TEXT | Hardware device model |
| `model_id` | TEXT | Hex encoded Hardware model identifier |
| `serial` | TEXT | Device serial (optional) |
| `revision` | TEXT | Device revision (optional) |
| `time` | BIGINT | Time of hardware event |
| `eid` | TEXT | Event ID |

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

### `nvram`

Apple NVRAM variable listing.

| Column | Type | Description |
| :--- | :--- | :--- |
| `name` | TEXT | Variable name |
| `type` | TEXT | Data type (CFData, CFString, etc) |
| `value` | TEXT | Raw variable data |

### `pci_devices`

PCI devices active on the host system.

| Column | Type | Description |
| :--- | :--- | :--- |
| `pci_slot` | TEXT | PCI Device used slot |
| `pci_class` | TEXT | PCI Device class |
| `driver` | TEXT | PCI Device used driver |
| `vendor` | TEXT | PCI Device vendor |
| `vendor_id` | TEXT | Hex encoded PCI Device vendor identifier |
| `model` | TEXT | PCI Device model |
| `model_id` | TEXT | Hex encoded PCI Device model identifier |
| `subsystem` | TEXT | PCI Device subsystem |
| `express` | INTEGER | 1 If PCI device is express else 0 |
| `thunderbolt` | INTEGER | 1 If PCI device is thunderbolt else 0 |
| `removable` | INTEGER | 1 If PCI device is removable else 0 |
| `pci_class_id` | TEXT | PCI Device class ID in hex format |
| `pci_subclass_id` | TEXT | PCI Device  subclass in hex format |
| `pci_subclass` | TEXT | PCI Device subclass |
| `subsystem_vendor_id` | TEXT | Vendor ID of PCI device subsystem |
| `subsystem_vendor` | TEXT | Vendor of PCI device subsystem |
| `subsystem_model_id` | TEXT | Model ID of PCI device subsystem |
| `subsystem_model` | TEXT | Device description of PCI device subsystem |

### `smbios_tables`

BIOS (DMI) structure common details and content.

| Column | Type | Description |
| :--- | :--- | :--- |
| `number` | INTEGER | Table entry number |
| `type` | INTEGER | Table entry type |
| `description` | TEXT | Table entry description |
| `handle` | INTEGER | Table entry handle |
| `header_size` | INTEGER | Header size in bytes |
| `size` | INTEGER | Table entry size in bytes |
| `md5` | TEXT | MD5 hash of table entry |

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

### `temperature_sensors`

| Column | Type | Description |
| :--- | :--- | :--- |
| `key` | TEXT | The SMC key on macOS |
| `name` | TEXT | Name of temperature source |
| `celsius` | DOUBLE | Temperature in Celsius |
| `fahrenheit` | DOUBLE | Temperature in Fahrenheit |

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
