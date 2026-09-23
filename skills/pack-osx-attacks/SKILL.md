---
name: pack-osx-attacks
description: macOS malware and attack detection query pack. Contains 74 detection queries identifying threats including WireLurker, Eleanor, Keydnap, OceanLotus, iWorm, Flashback, Keranger, Ventir, and unauthorized persistence. Use when investigating macOS compromises, suspicious launch agents, and malware artifacts.
---

# macOS Attack & Threat Detection Query Pack

The `pack-osx-attacks` skill equips agents with curated queries and diagnostic procedures from `osquery_data/packs/osx-attacks.conf`. This query pack focuses on macos attack & threat detection query pack.

## Threat Model & Scope
This pack provides detection rules for prominent macOS malware families and threat actors. It focuses on identifying:
- Persistence vectors: Malicious LaunchAgents and LaunchDaemons in `/Library/LaunchDaemons`, `~/Library/LaunchAgents`, and `/Library/LaunchAgents`.
- Trojanized binaries and dropped artifacts in `/Users/Shared/`, `/tmp/`, `/var/root/`, and application bundles.
- Malicious Safari and Chrome browser extensions used for credential harvesting and adware injection.
- Unsigned or self-signed certificates installed into the System keychain.
- Network listeners established by backdoor agents (e.g. Eleanor Tor daemon, Keydnap C2 channels).

## Triage & Investigation Runbook
### Alert Triage & Remediation Workflow
1. **Positive Match Verification**: If any query returns rows, immediately record the returned metadata (`name`, `path`, `label`, `pid`).
2. **Process Containment**: Check whether the malicious binary is running via `SELECT pid, name, path, cmdline FROM processes WHERE path = '<matched_path>';`. Suspend or terminate immediately if unauthorized.
3. **Persistence Neutralization**: Unload the daemon using `launchctl bootout` or `launchctl unload -w <path>` and quarantine the plist file.
4. **File Forensics & Hash Attribution**: Query `SELECT md5, sha256 FROM hash WHERE path = '<matched_path>';` to cross-reference with threat intelligence feeds.
5. **System Cleanliness Audit**: Run remaining OS X attack pack queries to discover multi-stage secondary payloads.

## Complete Query Catalog

### 1. `WireLurker`
- **Description**: (https://github.com/PaloAltoNetworks-BD/WireLurkerDetector)
- **Context / Value**: Artifact used by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select * from launchd where          name = 'com.apple.machook_damon.plist' OR          name = 'com.apple.globalupdate.plist' OR          name = 'com.apple.appstore.plughelper.plist' OR          name = 'com.apple.MailServiceAgentHelper.plist' OR          name = 'com.apple.systemkeychain-helper.plist' OR          name = 'com.apple.periodic-dd-mm-yy.plist';
```

### 2. `Leverage-A_1`
- **Description**: (http://www.intego.com/mac-security-blog/new-mac-trojan-discovered-related-to-syria/)
- **Context / Value**: Artifact used by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select * from launchd where path like '%UserEvent.System.plist';
```

### 3. `Leverage-A_2`
- **Description**: (http://www.intego.com/mac-security-blog/new-mac-trojan-discovered-related-to-syria/)
- **Context / Value**: Artifact used by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select * from file where path = '/Users/Shared/UserEvent.app';
```

### 4. `Leverage-A_3`
- **Description**: (https://www.volexity.com/blog/2017/07/24/real-news-fake-flash-mac-os-x-users-targeted/)
- **Context / Value**: Artifact used by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select * from launchd where name = 'com.GetFlashPlayer.plist';
```

### 5. `Tibet.D`
- **Description**: (http://www.intego.com/mac-security-blog/os-x-malware-tibet-variant-found/)
- **Context / Value**: Artifact used by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select * from launchd where path like '%com.apple.AudioService.plist';
```

### 6. `DevilRobber`
- **Description**: (https://www.f-secure.com/v-descs/backdoor_osx_devilrobber_a.shtml)
- **Context / Value**: Artifact used by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select * from launchd where name = 'com.apple.legion.plist' or name = 'com.apple.pixel.plist';
```

### 7. `XSLCmd`
- **Description**: (https://www.fireeye.com/blog/threat-research/2014/09/forced-to-adapt-xslcmd-backdoor-now-on-os-x.html)
- **Context / Value**: Artifact used by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select * from launchd where name = 'com.apple.service.clipboardd.plist';
```

### 8. `Olyx`
- **Description**: (https://www.f-secure.com/v-descs/backdoor_osx_olyx_c.shtml)
- **Context / Value**: Artifact used by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select * from launchd where name = 'com.apple.DockActions.plist' or name like '%www. google.com.tstart.plist%';
```

### 9. `Imuler`
- **Description**: (https://www.f-secure.com/v-descs/backdoor_osx_imuler_a.shtml)
- **Context / Value**: Artifact used by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select * from launchd where name = 'checkflr.plist';
```

### 10. `iWorkServ`
- **Description**: (https://www.f-secure.com/v-descs/backdoor_osx_iworkserv_a.shtml)
- **Context / Value**: Artifact used by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select * from startup_items where path like '%iWorkServices%';
```

### 11. `Morcut`
- **Description**: (http://www.trendmicro.com/vinfo/us/threat-encyclopedia/malware/osx_morcut.a)
- **Context / Value**: Artifact used by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select * from launchd where name = 'com.apple.mdworker.plist';
```

### 12. `BlazingKeylogger`
- **Description**: (http://www.blazingtools.com/mac_keylogger.html)
- **Context / Value**: Artifact used by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select * from launchd where name = 'com.BT.BPK.plist';
```

### 13. `Icefog`
- **Description**: (http://securelist.com/blog/research/57331/the-icefog-apt-a-tale-of-cloak-and-three-daggers/)
- **Context / Value**: Artifact used by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select * from launchd where name = 'apple.launchd.plist' or name = 'com.apple.launchport.plist';
```

### 14. `Careto`
- **Description**: (http://blog.kaspersky.com/the-mask-unveiling-the-worlds-most-sophisticated-apt-campaign/)
- **Context / Value**: Artifact used by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select * from launchd where path like '%com.apple.launchport.plist';
```

### 15. `Inqtana`
- **Description**: (https://www.f-secure.com/v-descs/inqtana_a.shtml)
- **Context / Value**: Artifact used by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select * from launchd where name = 'com.pwned.plist' or name = 'com.openbundle.plist' or name = 'com.adobe.reader.plist';
```

### 16. `MacKontrol`
- **Description**: (https://www.f-secure.com/v-descs/backdoor_osx_mackontrol_a.shtml)
- **Context / Value**: Artifact used by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select * from launchd where name = 'com.apple.FolderActionsxl.plist';
```

### 17. `PubSab`
- **Description**: (https://www.f-secure.com/v-descs/backdoor_osx_sabpab_a.shtml)
- **Context / Value**: Artifact used by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select * from launchd where name = 'com.apple.PubSabAgent.plist';
```

### 18. `Dockster`
- **Description**: (http://www.trendmicro.com/vinfo/us/threat-encyclopedia/malware/osx_dockster.a)
- **Context / Value**: Artifact used by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select * from launchd where name = 'mac.Dockset.deman.plist';
```

### 19. `CallMe`
- **Description**: (https://www.f-secure.com/weblog/archives/00002546.html)
- **Context / Value**: Artifact used by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select * from launchd where name = 'realPlayerUpdate.plist';
```

### 20. `Whitesmoke`
- **Description**: (http://www.thesafemac.com/osxfkcodec-a-in-action/ )
- **Context / Value**: Artifact used by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select * from launchd where name = 'com.whitesmoke.uploader.plist';
```

### 21. `Codecm`
- **Description**: (http://www.thesafemac.com/osxfkcodec-a-in-action/)
- **Context / Value**: Artifact used by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select * from launchd where name = 'com.codecm.uploader.plist';
```

### 22. `iWorm`
- **Description**: (https://www.virusbtn.com/virusbulletin/archive/2014/10/vb201410-iWorm)
- **Context / Value**: Artifact used by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select * from launchd where name = 'com.JavaW.plist';
```

### 23. `iWorm_1`
- **Description**: (https://www.virusbtn.com/virusbulletin/archive/2014/10/vb201410-iWorm)
- **Context / Value**: Artifact used by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select * from file where path like '/Library/Application Support/JavaW%';
```

### 24. `SniperSpy`
- **Description**: (http://www.symantec.com/security_response/writeup.jsp?docid=2010-081606-4034-99&tabid=2)
- **Context / Value**: Artifact used by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select * from launchd where name = 'com.rxs.syslogagent.plist';
```

### 25. `Vsearch`
- **Description**: (http://www.thesafemac.com/arg-downlite/)
- **Context / Value**: Artifact used by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select * from launchd where          name = 'com.vsearch.agent.plist' OR          name = 'com.vsearch.daemon.plist' OR          name = 'com.vsearch.helper.plist' OR          name = 'Jack.plist' OR          program_arguments = '/etc/run_upd.sh' OR          program_arguments LIKE '/Library/Application Support/%/Agent/agent.app/Contents/MacOS/agent%';
```

### 26. `Buca`
- **Description**: (http://www.thesafemac.com/arg-buca-apps/)
- **Context / Value**: Artifact used by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select * from launchd where name = 'com.webhelper.plist' or name = 'com.webtools.update.agent.plist' or name = 'com.webtools.uninstaller.plist';
```

### 27. `Conduit`
- **Description**: (http://www.thesafemac.com/arg-conduit/)
- **Context / Value**: Artifact used by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select * from launchd where path like '%com.conduit.loader.agent.plist' or name = 'com.conduit.loader.agent.plist' or path like '%com.perion.searchprotectd.plist' or name = 'com.perion.searchprotectd.plist';
```

### 28. `Genieo`
- **Description**: (http://www.thesafemac.com/arg-genieo/)
- **Context / Value**: Artifact used by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select * from launchd where          name = 'com.genieo.completer.download.plist' OR          name = 'com.genieo.completer.update.plist' OR          name = 'com.genieo.completer.ltvbit.plist' OR          name = 'com.installer.completer.download.plist' OR          name = 'com.installer.completer.update.plist' OR          name = 'com.installer.completer.ltvbit.plist' OR          name = 'com.genieoinnovation.macextension.plist' OR          name = 'com.genieoinnovation.macextension.client.plist' OR          name = 'com.genieo.engine.plist';
```

### 29. `GenieoPart2`
- **Description**: New version of Genieo
- **Context / Value**: Artifact used by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select * from launchd where program_arguments like '/Users/%/Library/Application Support/%/%.app/Contents/MacOS/App% -trigger download -isDev % -installVersion % -firstAppId % -identity %';
```

### 30. `HackingTeam_Mac_RAT1`
- **Description**: Detect RAT used by Hacking Team
- **Context / Value**: Artifact used by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select * from file where path = '/dev/ptmx0';
```

### 31. `HackingTeam_Mac_RAT2`
- **Description**: Detect RAT used by Hacking Team
- **Context / Value**: Artifact used by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select * from apps where bundle_identifier = 'com.ht.RCSMac';
```

### 32. `HackingTeam_Mac_RAT3`
- **Description**: Detect RAT used by Hacking Team
- **Context / Value**: Artifact used by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select * from launchd where          label = 'com.ht.RCSMac' OR          name = 'com.apple.loginStoreagent.plist' OR          name = 'com.apple.mdworker.plist' OR          name = 'com.apple.UIServerLogin.plist';
```

### 33. `HackingTeam_Mac_Persistence`
- **Description**: Detection persistency by Hacking Team
- **Context / Value**: Artifact used by Hacking Team
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select * from file where directory like '/Users/%/Library/Preferences/8pHbqThW%';
```

### 34. `xprotect_reports`
- **Description**: Report on Apple/OS X XProtect 'report' generation. Reports are generated when OS X matches an item in xprotect_entries.
- **Context / Value**: Although XProtect reports are rare, they may be worth collecting and aggregating internally.
- **Interval**: 1200 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select * from xprotect_reports;
```

### 35. `Keranger_1`
- **Description**: http://researchcenter.paloaltonetworks.com/2016/03/new-os-x-ransomware-keranger-infected-transmission-bittorrent-client-installer/
- **Context / Value**: Artifact used by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select * from processes where name = 'kernel_service';
```

### 36. `Keranger_2`
- **Description**: http://researchcenter.paloaltonetworks.com/2016/03/new-os-x-ransomware-keranger-infected-transmission-bittorrent-client-installer/
- **Context / Value**: Artifact used by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select * from file where          path LIKE '/Users/%/Library/.kernel_%' OR          path LIKE '/Users/%/Library/kernel_service';
```

### 37. `PremierOpinion`
- **Description**: (http://www.thesafemac.com/arg-premier-opinion/)
- **Context / Value**: Artifact used by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select * from launchd where name = 'PremierOpinion.plist' or name = 'PremierOpinionAgent.plist';
```

### 38. `Bundlore`
- **Description**: (http://www.thesafemac.com/arg-bundlore/)
- **Context / Value**: Artifact used by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select * from launchd where name like 'com.WebShoppy.%.plist' or name like 'com.SoftwareUpdater.%.plist' or name like 'cinema-plus%.plist' or name like 'com.WebTools.%.plist' or name like 'com.crossrider.%.plist' or name like 'shopy-mate_%.plist' or name like 'com.WebShopper.%.plist';
```

### 39. `Spigot`
- **Description**: (http://www.thesafemac.com/arg-spigot/)
- **Context / Value**: Artifact used by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select * from launchd where name like 'com.spigot.%.plist';
```

### 40. `SearchInstUpdater`
- **Description**: (https://www.virustotal.com/en/file/9530d481f7bb07aac98a46357bfcff96e2936a90571b4629ae865a2ce63e5c8e/analysis/)
- **Context / Value**: Artifact used by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select * from launchd where name like 'com.updater.mc%.plist' or name like 'com.updater.watch.mc%.plist';
```

### 41. `OSX_Pirrit`
- **Description**: (https://threatpost.com/mac-adware-osx-pirrit-unleashes-ad-overload-for-now/117273/)
- **Context / Value**: Artifact used by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select * from plist where path = '/Library/Preferences/com.common.plist' and key = 'net_pref';
```

### 42. `Backdoor_MAC_Eleanor`
- **Description**: (https://blog.malwarebytes.com/cybercrime/2016/07/new-mac-backdoor-malware-eleanor/)
- **Context / Value**: Artifact used by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
SELECT * FROM launchd WHERE name IN ('com.getdropbox.dropbox.integritycheck.plist','com.getdropbox.dropbox.timegrabber.plist','com.getdropbox.dropbox.usercontent.plist');
```

### 43. `EliteKeylogger`
- **Description**: (https://www.elitekeyloggers.com/elite-keylogger-mac)
- **Context / Value**: Artifact used by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select * from launchd where name = 'com.apple.fonts.plist' and label = 'unknown';
```

### 44. `Aobo_Keylogger`
- **Description**: (http://aobo.cc/aobo-mac-os-x-keylogger.html)
- **Context / Value**: Artifact used by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select * from launchd where name like 'com.ab.kl%.plist';
```

### 45. `OSX_Keydnap`
- **Description**: (http://www.welivesecurity.com/2016/07/06/new-osxkeydnap-malware-hungry-credentials)
- **Context / Value**: Artifact used by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select * from launchd where name IN ('com.apple.iCloud.sync.daemon', 'com.geticloud.icloud.photo');
```

### 46. `Java_Adwind_Trojan`
- **Description**: (https://blog.malwarebytes.com/threat-analysis/2016/07/cross-platform-malware-adwind-infects-mac/)
- **Context / Value**: Artifact used by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select * from launchd where name like 'org.%.plist' and program_arguments like '/Library/Internet Plug-Ins/JavaAppletPlugin.plugin/Contents/Home/bin/java -Dapple.awt.UIElement=true -jar /Users/%/.%';
```

### 47. `OSX_Backdoor_Mokes`
- **Description**: (https://securelist.com/blog/research/75990/the-missing-piece-sophisticated-os-x-backdoor-discovered/)
- **Context / Value**: Artifact used by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select * from file where          path LIKE '/Users/%/Library/App Store/storeuserd' OR          path LIKE '/Users/%/Library/com.apple.spotlight/SpotlightHelper' OR          path LIKE '/Users/%/Library/Dock/com.apple.dock.cache' OR          path LIKE '/Users/%/Library/Dropbox/DropboxCache' OR          path LIKE '/Users/%/Library/Skype/SkypeHelper' OR          path LIKE '/Users/%/Library/Google/Chrome/nacld' OR          path LIKE '/Users/%/Library/Firefox/Profiles/profiled';
```

### 48. `OSX_Komplex`
- **Description**: (http://researchcenter.paloaltonetworks.com/2016/09/unit42-sofacys-komplex-os-x-trojan/)
- **Context / Value**: Artifact used by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select * from file where path = '/Users/Shared/.local/kext' or path = '/Users/Shared/com.apple.updates.plist' or path = '/Users/Shared/start.sh';
```

### 49. `OceanLotus_launchagent`
- **Description**: OceanLotus Launch Agent (https://www.alienvault.com/blogs/labs-research/oceanlotus-for-os-x-an-application-bundle-pretending-to-be-an-adobe-flash-update)
- **Context / Value**: Artifact used by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select * from launchd where name = 'com.google.plugins.plist';
```

### 50. `OceanLotus_dropped_file_1`
- **Description**: OceanLotus dropped file (https://www.alienvault.com/blogs/labs-research/oceanlotus-for-os-x-an-application-bundle-pretending-to-be-an-adobe-flash-update)
- **Context / Value**: Artifact used by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select * from file, (          select '/Library/Logs/.Logs/corevideosd' ioc union          select '/Library/.SystemPreferences/.prev/.ver.txt' ioc union          select '/Library/Parallels/.cfg' ioc union          select '/Library/Preferences/.fDTYuRs' ioc union          select '/Library/Hash/.Hashtag/.hash' ioc union          select '/Library/Hash/.hash' ioc        ) iocs where          file.path LIKE '/Users/%/' || ioc OR          file.path = iocs.ioc OR          file.path LIKE '/tmp/crunzip.temp.%';
```

### 51. `XcodeGhost`
- **Description**: Xcode Ghost dropped files (http://researchcenter.paloaltonetworks.com/2015/09/novel-malware-xcodeghost-modifies-xcode-infects-apple-ios-apps-and-hits-app-store/)
- **Context / Value**: Artifact used by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select * from (          select apps.bundle_short_version as xcode_version,            apps.path as xcode_path,            file.path,            file.type as file_type          from apps, file          where apps.bundle_name='Xcode' and            file.path like (apps.path || '/Contents/Developer/Platforms/%/Developer/SDKs/Library/%%')        ) join hash using (path) where file_type = 'regular';
```

### 52. `Quimitchin_Backdoor`
- **Description**: Quimitchin Launch Agent (https://blog.malwarebytes.com/threat-analysis/2017/01/new-mac-backdoor-using-antiquated-code/)
- **Context / Value**: Artifact used by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select * from launchd where name = 'com.client.client.plist';
```

### 53. `Pronto`
- **Description**: ProntoApp Launch Agents (https://malwarefixes.com/remove-pronto-video-converter/)
- **Context / Value**: Artifact used by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select * from launchd where name = 'pronto.notification.plist' or name = 'pronto.update.plist';
```

### 54. `OSX_DOK_1`
- **Description**: DOK Launch Agents (http://blog.checkpoint.com/2017/04/27/osx-malware-catching-wants-read-https-traffic/)
- **Context / Value**: Artifact used by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select * from launchd where name = 'com.apple.Safari.proxy.plist' or name = 'com.apple.Safari.proxy.pac';
```

### 55. `OSX_DOK_2`
- **Description**: DOK certificate (http://blog.checkpoint.com/2017/04/27/osx-malware-catching-wants-read-https-traffic/)
- **Context / Value**: Artifact used by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select common_name, sha1, subject_key_id from certificates where subject_key_id = 'e637d656f9f088ddca3b3b55c4fe698d8c97a552';
```

### 56. `OSX_DOK_3`
- **Description**: DOK dropped file (http://blog.checkpoint.com/2017/04/27/osx-malware-catching-wants-read-https-traffic/)
- **Context / Value**: Artifact used by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select * from file where path = '/Users/Shared/AppStore.app';
```

### 57. `OSX_DOK_4`
- **Description**: DOK malicious app (http://blog.checkpoint.com/2017/04/27/osx-malware-catching-wants-read-https-traffic/)
- **Context / Value**: Artifact used by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select * from apps where bundle_name = 'Truesteer.AppStore';
```

### 58. `OSX_Snake`
- **Description**: OS X port of Snake malware discovered by Fox-IT (https://blog.fox-it.com/2017/05/03/snake-coming-soon-in-mac-os-x-flavour/)
- **Context / Value**: Artifacts created by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select * from file           where path = '/Library/LaunchDaemons/com.adobe.update.plist' OR             path = '/Library/Scripts/installd.sh' OR             path = '/Library/Scripts/queue' OR             path = '/tmp/.gdm-socket' OR             path = '/tmp/.gdm-selinux' OR             path LIKE '/var/tmp/.ur-%%';
```

### 59. `OSX_Proton_Files`
- **Description**: OSX/Proton bundled with a tampered version of Handbrake and Elmedia Player: (https://objective-see.com/blog/blog_0x1D.html and https://www.welivesecurity.com/2017/10/20/osx-proton-supply-chain-attack-elmedia/)
- **Context / Value**: Artifacts created by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select * from file          where path like '/Users/%/Library/RenderFiles/activity_agent.app/' OR          path like '/Users/%/Library/LaunchAgents/fr.handbrake.activity_agent.plist' OR          path='/tmp/Updater.app' OR path='/Library/.rand/updateragent.app' OR          path='/Library/LaunchAgents/com.apple.xpcd.plist' OR          path='/Library/.cachedir' OR          path='/Library/.random';
```

### 60. `OSX_Proton_Launchd`
- **Description**: OSX/Proton bundled with a tampered version of Elmedia Player or Fake Symantec Blog: (https://www.welivesecurity.com/2017/10/20/osx-proton-supply-chain-attack-elmedia/) and (https://blog.malwarebytes.com/threat-analysis/mac-threat-analysis/2017/11/osx-proton-spreading-through-fake-symantec-blog/)
- **Context / Value**: Artifacts created by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select * from launchd where name='com.Eltima.UpdaterAgent.plist' OR name='com.apple.xpcd.plist';
```

### 61. `OSX_Proton_Process`
- **Description**: OSX/Proton bundled with a tampered version of Handbrake and Elmedia Player: (https://objective-see.com/blog/blog_0x1D.html and https://www.welivesecurity.com/2017/10/20/osx-proton-supply-chain-attack-elmedia/)
- **Context / Value**: Artifacts created by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select * from processes          where path like '/Users/%/Library/RenderFiles/activity_agent.app/Contents/MacOS/activity_agent' OR          path='/Library/.rand/updateragent.app/Contents/MacOS/updateragent' OR          path='/Library/.random/xpcd.app/Contents/MacOS/xpcd';
```

### 62. `EmPyre_Agent`
- **Description**: EmPyre post exploitation agent (https://github.com/EmpireProject/EmPyre/blob/master/lib/modules/persistence/osx/launchdaemonexecutable.py)
- **Context / Value**: Artifacts created by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select * from launchd where name = 'com.proxy.initialize.plist';
```

### 63. `OSX_FruitFly`
- **Description**: FruitFly OSX Malware (https://blog.malwarebytes.com/threat-analysis/2017/01/new-mac-backdoor-using-antiquated-code/)
- **Context / Value**: Artifacts created by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select * from launchd where name = 'com.client.client.plist';
```

### 64. `OSX_Mughthesec`
- **Description**: Mughthesec OSX Malware (https://objective-see.com/blog/blog_0x20.html)
- **Context / Value**: Artifacts created by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select * from launchd where name = 'com.Mughthesec.plist';
```

### 65. `OSX_HiddenLotus`
- **Description**: Apple added XProtect rules for this sample: (https://www.virustotal.com/en/file/f261815905e77eebdb5c4ec06a7acdda7b68644b1f5155049f133be866d8b179/analysis/1509567775/)
- **Context / Value**: Artifacts created by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select * from launchd where name = 'com.apple.hidd.shared.plist';
```

### 66. `OSX_MaMi_DNS_Servers`
- **Description**: MaMi OSX Malware 2017-01-12 (https://objective-see.com/blog/blog_0x26.html)
- **Context / Value**: DNS Servers set by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: 2.8.0
- **SQL Query**:
```sql
select * from dns_resolvers where type = 'nameserver' and address in ('82.163.143.135', '82.163.142.137');
```

### 67. `OSX_MaMi_Certificate`
- **Description**: MaMi OSX Malware 2017-01-12 (https://objective-see.com/blog/blog_0x26.html)
- **Context / Value**: bogus certificate added to key store by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: 2.8.0
- **SQL Query**:
```sql
select * from certificates where common_name like '%cloudguard.me%' and not_valid_after = '2352216315';
```

### 68. `Behavioral_Reverse_Shell`
- **Description**: Find shell processes that have open sockets and no open files or TTY (https://clo.ng/blog/osquery_reverse_shell/)
- **Context / Value**: Behavioral detection for potential reverse shells
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: 2.8.0
- **SQL Query**:
```sql
SELECT DISTINCT(processes.pid), processes.parent, processes.name, processes.path,          processes.cmdline, processes.cwd, processes.root, processes.uid, processes.gid,          processes.start_time, process_open_sockets.remote_address, process_open_sockets.remote_port,          (SELECT cmdline FROM processes AS parent_cmdline WHERE pid=processes.parent) AS parent_cmdline          FROM processes JOIN process_open_sockets USING (pid)          LEFT OUTER JOIN process_open_files          ON processes.pid = process_open_files.pid          WHERE (name='sh' OR name='bash')          AND process_open_files.pid IS NULL          AND process_open_sockets.remote_port > 0;
```

### 69. `OSX_ColdRoot_RAT_Launchd`
- **Description**: ColdRoot OSX Malware (https://objective-see.com/blog/blog_0x2A.html)
- **Context / Value**: Artifacts created by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select * from launchd where name = 'com.apple.audio.driver.plist';
```

### 70. `OSX_ColdRoot_RAT_Files`
- **Description**: ColdRoot OSX Malware (https://objective-see.com/blog/blog_0x2A.html)
- **Context / Value**: Artifacts created by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
select * from file          where path in ('/private/var/tmp/com.apple.audio.driver.app/',          '/private/var/tmp/com.apple.audio.driver.app/Contents/MacOS/conx.wol');
```

### 71. `MacSearch_Adware`
- **Description**: MacSearch OSX Adware (https://www.virustotal.com/latest-scan/15966224C4E25C9787A4A8C984A863E9)
- **Context / Value**: Artifacts created by this adware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
SELECT * FROM launchd WHERE path='/Library/LaunchAgents/tapufind.plist';
```

### 72. `OSX_Dummy_Launchd`
- **Description**: OSX Dummy Malware (https://objective-see.com/blog/blog_0x32.html and https://isc.sans.edu/diary/23816)
- **Context / Value**: Artifacts created by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
SELECT * FROM launchd WHERE name = 'com.startup.plist';
```

### 73. `OSX_Dummy_Files`
- **Description**: OSX Dummy Malware (https://objective-see.com/blog/blog_0x32.html and https://isc.sans.edu/diary/23816)
- **Context / Value**: Artifacts created by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
SELECT * FROM file           WHERE path = '/Library/LaunchDaemons/com.startup.plist' OR             path = '/var/root/script.sh' OR             path = '/Users/Shared/dumpdummy' OR             path = '/tmp/script.sh' OR             path = '/tmp/com.startup.plist' OR             path = '/tmp/dumpdummy';
```

### 74. `OSX_SearchAwesome`
- **Description**: OSX SearchAwesome Malware (https://blog.malwarebytes.com/threat-analysis/2018/10/mac-malware-intercepts-encrypted-web-traffic-for-ad-injection/)
- **Context / Value**: Artifacts created by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: 1.4.5
- **SQL Query**:
```sql
SELECT * FROM file           WHERE path = '/Applications/spi.app' OR             path = '/Users/%/Library/LaunchAgents/spid-uninstall.plist' OR             path = '/Users/%/Library/LaunchAgents/spid.plist' OR             path = '/Users/%/Library/SPI';
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

### `dns_resolvers`

Resolvers used by this host. Note: On Windows this data is available in the interface_details table.

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | INTEGER | Address type index or order |
| `type` | TEXT | Address type: sortlist, nameserver, search |
| `address` | TEXT | Resolver IP/IPv6 address |
| `netmask` | TEXT | Address (sortlist) netmask length |
| `options` | BIGINT | Resolver options |
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

### `plist`

Read and parse a plist file.

| Column | Type | Description |
| :--- | :--- | :--- |
| `key` | TEXT | Preference top-level key |
| `subkey` | TEXT | Intermediate key path, includes lists/dicts |
| `value` | TEXT | String value of most CF types |
| `path` | TEXT | (required) read preferences from a plist |

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

### `xprotect_reports`

Database of XProtect matches (if user generated/sent an XProtect report).

| Column | Type | Description |
| :--- | :--- | :--- |
| `name` | TEXT | Description of XProtected malware |
| `user_action` | TEXT | Action taken by user after prompted |
| `time` | TEXT | Quarantine alert time |
