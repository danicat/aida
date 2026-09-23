---
name: pack-ossec-rootkit
description: Linux rootkit detection query pack based on OSSEC rootkit signatures. Features 60 targeted queries detecting rootkit artifacts, hidden files, trojaned system binaries (ps, netstat, login, ifconfig), and known rootkits including t0rn, Adore, Knark, Ramen, and Suckit. Use for deep Linux rootkit hunting.
---

# OSSEC Rootkit Detection Query Pack

The `pack-ossec-rootkit` skill equips agents with curated queries and diagnostic procedures from `osquery_data/packs/ossec-rootkit.conf`. This query pack focuses on ossec rootkit detection query pack.

## Threat Model & Scope
This pack ports OSSEC's rootkit signature library into high-speed osquery filesystem rules. It detects:
- Well-known historical and modern Linux rootkits: t0rn, Adore, Knark, Ramen, Suckit, Beastkit, Dica, etc.
- Trojaned core binaries: `/bin/ps`, `/bin/netstat`, `/bin/login`, `/sbin/ifconfig`, `/usr/bin/top`.
- Hidden directories and rootkit artifacts: `/dev/...`, `/dev/.ida`, `/dev/.udev`, `/usr/lib/...`, `/tmp/.rk`.

## Triage & Investigation Runbook
### Rootkit Discovery & Response Protocol
1. **Alert Verification**: If a query returns a positive hit for any rootkit path, treat host as completely compromised.
2. **Volatile Capture**: Dump memory and active network sockets before taking host offline.
3. **Quarantine & Rebuild**: Because kernel and binary integrity is compromised by rootkits, avoid in-place patching; isolate the machine, image the drive for forensics, and re-image from clean golden source.

## Complete Query Catalog

### 1. `bash_door`
- **Description**: bash_door
- **Context / Value**: Artifacts used by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: N/A
- **SQL Query**:
```sql
select * from file where path in ('/tmp/mcliZokhb', '/tmp/mclzaKmfa');
```

### 2. `slapper_installed`
- **Description**: slapper_installed
- **Context / Value**: Artifacts used by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: N/A
- **SQL Query**:
```sql
select * from file where path in ('/tmp/.bugtraq', '/tmp/.bugtraq.c', '/tmp/.cinik', '/tmp/.b', '/tmp/httpd', '/tmp./update', '/tmp/.unlock', '/tmp/.font-unix/.cinik', '/tmp/.cinik');
```

### 3. ``mithra`s_rootkit``
- **Description**: mithra`s_rootkit
- **Context / Value**: Artifacts used by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: N/A
- **SQL Query**:
```sql
select * from file where path in ('/usr/lib/locale/uboot');
```

### 4. `omega_worm`
- **Description**: omega_worm
- **Context / Value**: Artifacts used by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: N/A
- **SQL Query**:
```sql
select * from file where path in ('/dev/chr');
```

### 5. `kenga3_rootkit`
- **Description**: kenga3_rootkit
- **Context / Value**: Artifacts used by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: N/A
- **SQL Query**:
```sql
select * from file where path in ('/usr/include/. .');
```

### 6. `sadmind/iis_worm`
- **Description**: sadmind/iis_worm
- **Context / Value**: Artifacts used by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: N/A
- **SQL Query**:
```sql
select * from file where path in ('/dev/cuc');
```

### 7. `rsha`
- **Description**: rsha
- **Context / Value**: Artifacts used by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: N/A
- **SQL Query**:
```sql
select * from file where path in ('/usr/bin/kr4p', '/usr/bin/n3tstat', '/usr/bin/chsh2', '/usr/bin/slice2', '/etc/rc.d/rsha');
```

### 8. `old_rootkits`
- **Description**: old_rootkits
- **Context / Value**: Artifacts used by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: N/A
- **SQL Query**:
```sql
select * from file where path in ('/usr/include/rpc/ ../kit', '/usr/include/rpc/ ../kit2', '/usr/doc/.sl', '/usr/doc/.sp', '/usr/doc/.statnet', '/usr/doc/.logdsys', '/usr/doc/.dpct', '/usr/doc/.gifnocfi', '/usr/doc/.dnif', '/usr/doc/.nigol');
```

### 9. `telekit_trojan`
- **Description**: telekit_trojan
- **Context / Value**: Artifacts used by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: N/A
- **SQL Query**:
```sql
select * from file where path in ('/dev/hda06', '/usr/info/libc1.so');
```

### 10. `tc2_worm`
- **Description**: tc2_worm
- **Context / Value**: Artifacts used by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: N/A
- **SQL Query**:
```sql
select * from file where path in ('/usr/info/.tc2k', '/usr/bin/util', '/usr/sbin/initcheck', '/usr/sbin/ldb');
```

### 11. `shitc`
- **Description**: shitc
- **Context / Value**: Artifacts used by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: N/A
- **SQL Query**:
```sql
select * from file where path in ('/bin/home', '/sbin/home', '/usr/sbin/in.slogind');
```

### 12. `rh_sharpe`
- **Description**: rh_sharpe
- **Context / Value**: Artifacts used by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: N/A
- **SQL Query**:
```sql
select * from file where path in ('/bin/.ps', '/usr/bin/cleaner', '/usr/bin/slice', '/usr/bin/vadim', '/usr/bin/.ps', '/bin/.lpstree', '/usr/bin/.lpstree', '/usr/bin/lnetstat', '/bin/lnetstat', '/usr/bin/ldu', '/bin/ldu', '/usr/bin/lkillall', '/bin/lkillall', '/usr/include/rpcsvc/du');
```

### 13. `showtee_/_romanian_rootkit`
- **Description**: showtee_/_romanian_rootkit
- **Context / Value**: Artifacts used by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: N/A
- **SQL Query**:
```sql
select * from file where path in ('/usr/include/addr.h', '/usr/include/file.h', '/usr/include/syslogs.h', '/usr/include/proc.h');
```

### 14. `lrk_rootkit`
- **Description**: lrk_rootkit
- **Context / Value**: Artifacts used by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: N/A
- **SQL Query**:
```sql
select * from file where path in ('/dev/ida/.inet');
```

### 15. `zk_rootkit`
- **Description**: zk_rootkit
- **Context / Value**: Artifacts used by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: N/A
- **SQL Query**:
```sql
select * from file where path in ('/usr/share/.zk', '/usr/share/.zk/zk', '/etc/1ssue.net', '/usr/X11R6/.zk', '/usr/X11R6/.zk/xfs', '/usr/X11R6/.zk/echo', '/etc/sysconfig/console/load.zk');
```

### 16. `ramen_worm`
- **Description**: ramen_worm
- **Context / Value**: Artifacts used by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: N/A
- **SQL Query**:
```sql
select * from file where path in ('/usr/lib/ldlibps.so', '/usr/lib/ldlibns.so', '/usr/lib/ldliblogin.so', '/usr/src/.poop', '/tmp/ramen.tgz', '/etc/xinetd.d/asp');
```

### 17. `maniac_rk`
- **Description**: maniac_rk
- **Context / Value**: Artifacts used by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: N/A
- **SQL Query**:
```sql
select * from file where path in ('/usr/bin/mailrc');
```

### 18. `bmbl_rootkit`
- **Description**: bmbl_rootkit
- **Context / Value**: Artifacts used by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: N/A
- **SQL Query**:
```sql
select * from file where path in ('/etc/.bmbl', '/etc/.bmbl/sk');
```

### 19. `suckit_rootkit`
- **Description**: suckit_rootkit
- **Context / Value**: Artifacts used by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: N/A
- **SQL Query**:
```sql
select * from file where path in ('/lib/.x', '/lib/sk');
```

### 20. `adore_rootkit`
- **Description**: adore_rootkit
- **Context / Value**: Artifacts used by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: N/A
- **SQL Query**:
```sql
select * from file where path in ('/etc/bin/ava', '/etc/sbin/ava');
```

### 21. `ldp_worm`
- **Description**: ldp_worm
- **Context / Value**: Artifacts used by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: N/A
- **SQL Query**:
```sql
select * from file where path in ('/dev/.kork', '/bin/.login', '/bin/.ps');
```

### 22. `romanian_rootkit`
- **Description**: romanian_rootkit
- **Context / Value**: Artifacts used by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: N/A
- **SQL Query**:
```sql
select * from file where path in ('/usr/sbin/initdl', '/usr/sbin/xntps');
```

### 23. `illogic_rootkit`
- **Description**: illogic_rootkit
- **Context / Value**: Artifacts used by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: N/A
- **SQL Query**:
```sql
select * from file where path in ('/lib/security/.config', '/usr/bin/sia', '/etc/ld.so.hash');
```

### 24. `bobkit_rootkit`
- **Description**: bobkit_rootkit
- **Context / Value**: Artifacts used by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: N/A
- **SQL Query**:
```sql
select * from file where path in ('/usr/include/.../', '/usr/lib/.../', '/usr/sbin/.../', '/usr/bin/ntpsx', '/tmp/.bkp', '/usr/lib/.bkit-');
```

### 25. `monkit`
- **Description**: monkit
- **Context / Value**: Artifacts used by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: N/A
- **SQL Query**:
```sql
select * from file where path in ('/lib/defs');
```

### 26. `override_rootkit`
- **Description**: override_rootkit
- **Context / Value**: Artifacts used by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: N/A
- **SQL Query**:
```sql
select * from file where path in ('/dev/grid-hide-pid-', '/dev/grid-unhide-pid-', '/dev/grid-show-pids', '/dev/grid-hide-port-', '/dev/grid-unhide-port-');
```

### 27. `madalin_rootkit`
- **Description**: madalin_rootkit
- **Context / Value**: Artifacts used by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: N/A
- **SQL Query**:
```sql
select * from file where path in ('/usr/include/icekey.h', '/usr/include/iceconf.h', '/usr/include/iceseed.h');
```

### 28. `solaris_worm`
- **Description**: solaris_worm
- **Context / Value**: Artifacts used by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: N/A
- **SQL Query**:
```sql
select * from file where path in ('/var/adm/.profile', '/var/spool/lp/.profile', '/var/adm/sa/.adm', '/var/spool/lp/admins/.lp');
```

### 29. `phalanx_rootkit`
- **Description**: phalanx_rootkit
- **Context / Value**: Artifacts used by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: N/A
- **SQL Query**:
```sql
select * from file where path in ('/usr/share/.home*', '/usr/share/.home*/tty', '/etc/host.ph1', '/bin/host.ph1');
```

### 30. `ark_rootkit`
- **Description**: ark_rootkit
- **Context / Value**: Artifacts used by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: N/A
- **SQL Query**:
```sql
select * from file where path in ('/dev/ptyxx');
```

### 31. `tribe_bot`
- **Description**: tribe_bot
- **Context / Value**: Artifacts used by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: N/A
- **SQL Query**:
```sql
select * from file where path in ('/dev/wd4');
```

### 32. `cback_worm`
- **Description**: cback_worm
- **Context / Value**: Artifacts used by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: N/A
- **SQL Query**:
```sql
select * from file where path in ('/tmp/cback', '/tmp/derfiq');
```

### 33. `optickit`
- **Description**: optickit
- **Context / Value**: Artifacts used by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: N/A
- **SQL Query**:
```sql
select * from file where path in ('/usr/bin/xchk', '/usr/bin/xsf', '/usr/bin/xsf', '/usr/bin/xchk');
```

### 34. `anonoiyng_rootkit`
- **Description**: anonoiyng_rootkit
- **Context / Value**: Artifacts used by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: N/A
- **SQL Query**:
```sql
select * from file where path in ('/usr/sbin/mech', '/usr/sbin/kswapd');
```

### 35. `loc_rookit`
- **Description**: loc_rookit
- **Context / Value**: Artifacts used by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: N/A
- **SQL Query**:
```sql
select * from file where path in ('/tmp/xp', '/tmp/kidd0.c', '/tmp/kidd0');
```

### 36. `showtee`
- **Description**: showtee
- **Context / Value**: Artifacts used by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: N/A
- **SQL Query**:
```sql
select * from file where path in ('/usr/lib/.egcs', '/usr/lib/.wormie', '/usr/lib/.kinetic', '/usr/lib/liblog.o', '/usr/include/cron.h', '/usr/include/chk.h');
```

### 37. `zarwt_rootkit`
- **Description**: zarwt_rootkit
- **Context / Value**: Artifacts used by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: N/A
- **SQL Query**:
```sql
select * from file where path in ('/bin/imin', '/bin/imout');
```

### 38. `lion_worm`
- **Description**: lion_worm
- **Context / Value**: Artifacts used by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: N/A
- **SQL Query**:
```sql
select * from file where path in ('/dev/.lib', '/dev/.lib/1iOn.sh', '/bin/mjy', '/bin/in.telnetd', '/usr/info/torn');
```

### 39. `suspicious_file`
- **Description**: suspicious_file
- **Context / Value**: Artifacts used by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: N/A
- **SQL Query**:
```sql
select * from file where path in ('/etc/rc.d/init.d/rc.modules', '/lib/ldd.so', '/usr/man/muie', '/usr/X11R6/include/pain', '/usr/bin/sourcemask', '/usr/bin/ras2xm', '/usr/bin/ddc', '/usr/bin/jdc', '/usr/sbin/in.telnet', '/sbin/vobiscum', '/usr/sbin/jcd', '/usr/sbin/atd2', '/usr/bin/ishit', '/usr/bin/.etc', '/usr/bin/xstat', '/var/run/.tmp', '/usr/man/man1/lib/.lib', '/usr/man/man2/.man8', '/var/run/.pid', '/lib/.so', '/lib/.fx', '/lib/lblip.tk', '/usr/lib/.fx', '/var/local/.lpd', '/dev/rd/cdb', '/dev/.rd/', '/usr/lib/pt07', '/usr/bin/atm', '/tmp/.cheese', '/dev/.arctic', '/dev/.xman', '/dev/.golf', '/dev/srd0', '/dev/ptyzx', '/dev/ptyzg', '/dev/xdf1', '/dev/ttyop', '/dev/ttyof', '/dev/hd7', '/dev/hdx1', '/dev/hdx2', '/dev/xdf2', '/dev/ptyp', '/dev/ptyr', '/sbin/pback', '/usr/man/man3/psid', '/proc/kset', '/usr/bin/gib', '/usr/bin/snick', '/usr/bin/kfl', '/tmp/.dump', '/var/.x', '/var/.x/psotnic');
```

### 40. `apa_kit`
- **Description**: apa_kit
- **Context / Value**: Artifacts used by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: N/A
- **SQL Query**:
```sql
select * from file where path in ('/usr/share/.aPa');
```

### 41. `enye_sec_rootkit`
- **Description**: enye_sec_rootkit
- **Context / Value**: Artifacts used by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: N/A
- **SQL Query**:
```sql
select * from file where path in ('/etc/.enyelkmHIDE^IT.ko');
```

### 42. `rk17`
- **Description**: rk17
- **Context / Value**: Artifacts used by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: N/A
- **SQL Query**:
```sql
select * from file where path in ('/bin/rtty', '/bin/squit', '/sbin/pback', '/proc/kset', '/usr/src/linux/modules/autod.o', '/usr/src/linux/modules/soundx.o');
```

### 43. `trk_rootkit`
- **Description**: trk_rootkit
- **Context / Value**: Artifacts used by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: N/A
- **SQL Query**:
```sql
select * from file where path in ('/usr/bin/soucemask', '/usr/bin/sourcemask');
```

### 44. `scalper_installed`
- **Description**: scalper_installed
- **Context / Value**: Artifacts used by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: N/A
- **SQL Query**:
```sql
select * from file where path in ('/tmp/.uua', '/tmp/.a');
```

### 45. `hidr00tkit`
- **Description**: hidr00tkit
- **Context / Value**: Artifacts used by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: N/A
- **SQL Query**:
```sql
select * from file where path in ('/var/lib/games/.k');
```

### 46. `beastkit_rootkit`
- **Description**: beastkit_rootkit
- **Context / Value**: Artifacts used by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: N/A
- **SQL Query**:
```sql
select * from file where path in ('/usr/local/bin/bin', '/usr/man/.man10', '/usr/sbin/arobia', '/usr/lib/elm/arobia', '/usr/local/bin/.../bktd');
```

### 47. `shv5_rootkit`
- **Description**: shv5_rootkit
- **Context / Value**: Artifacts used by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: N/A
- **SQL Query**:
```sql
select * from file where path in ('/lib/libsh.so', '/usr/lib/libsh');
```

### 48. `esrk_rootkit`
- **Description**: esrk_rootkit
- **Context / Value**: Artifacts used by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: N/A
- **SQL Query**:
```sql
select * from file where path in ('/usr/lib/tcl5.3');
```

### 49. `shkit_rootkit`
- **Description**: shkit_rootkit
- **Context / Value**: Artifacts used by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: N/A
- **SQL Query**:
```sql
select * from file where path in ('/lib/security/.config', '/etc/ld.so.hash');
```

### 50. `knark_installed`
- **Description**: knark_installed
- **Context / Value**: Artifacts used by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: N/A
- **SQL Query**:
```sql
select * from file where path in ('/proc/knark', '/dev/.pizda', '/dev/.pula', '/dev/.pula');
```

### 51. `volc_rootkit`
- **Description**: volc_rootkit
- **Context / Value**: Artifacts used by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: N/A
- **SQL Query**:
```sql
select * from file where path in ('/usr/lib/volc', '/usr/bin/volc');
```

### 52. `fu_rootkit`
- **Description**: fu_rootkit
- **Context / Value**: Artifacts used by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: N/A
- **SQL Query**:
```sql
select * from file where path in ('/sbin/xc', '/usr/include/ivtype.h', '/bin/.lib');
```

### 53. `ajakit_rootkit`
- **Description**: ajakit_rootkit
- **Context / Value**: Artifacts used by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: N/A
- **SQL Query**:
```sql
select * from file where path in ('/lib/.ligh.gh', '/lib/.libgh.gh', '/lib/.libgh-gh', '/dev/tux', '/dev/tux/.proc', '/dev/tux/.file');
```

### 54. `monkit_found`
- **Description**: monkit_found
- **Context / Value**: Artifacts used by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: N/A
- **SQL Query**:
```sql
select * from file where path in ('/usr/lib/libpikapp.a');
```

### 55. `t0rn_rootkit`
- **Description**: t0rn_rootkit
- **Context / Value**: Artifacts used by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: N/A
- **SQL Query**:
```sql
select * from file where path in ('/usr/src/.puta', '/usr/info/.t0rn', '/lib/ldlib.tk', '/etc/ttyhash', '/sbin/xlogin');
```

### 56. `adore_worm`
- **Description**: adore_worm
- **Context / Value**: Artifacts used by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: N/A
- **SQL Query**:
```sql
select * from file where path in ('/dev/.shit/red.tgz', '/usr/lib/libt', '/usr/bin/adore');
```

### 57. `55808.a_worm`
- **Description**: 55808.a_worm
- **Context / Value**: Artifacts used by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: N/A
- **SQL Query**:
```sql
select * from file where path in ('/tmp/.../a', '/tmp/.../r');
```

### 58. `tuxkit_rootkit`
- **Description**: tuxkit_rootkit
- **Context / Value**: Artifacts used by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: N/A
- **SQL Query**:
```sql
select * from file where path in ('/dev/tux', '/usr/bin/xsf', '/usr/bin/xchk');
```

### 59. `reptile_rootkit`
- **Description**: reptile_rootkit
- **Context / Value**: Artifacts used by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: N/A
- **SQL Query**:
```sql
select * from file where path in ('/reptile/reptile_cmd', '/lib/udev/reptile');
```

### 60. `beurk_rootkit`
- **Description**: beurk_rootkit
- **Context / Value**: Artifacts used by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: N/A
- **SQL Query**:
```sql
select * from file where path in ('/lib/libselinux.so');
```

## Referenced Table Schemas

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
