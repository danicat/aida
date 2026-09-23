---
name: pack-unwanted-chrome-extensions
description: Google Chrome extension auditing and unwanted extension detection pack. Contains 14 queries identifying malicious, suspicious, or policy-violating browser extensions, adware, excessive permissions, and browser hijackers across all user profiles. Use for browser hygiene and adware eradication.
---

# Unwanted Chrome Extensions Query Pack

The `pack-unwanted-chrome-extensions` skill equips agents with curated queries and diagnostic procedures from `osquery_data/packs/unwanted-chrome-extensions.conf`. This query pack focuses on unwanted chrome extensions query pack.

## Threat Model & Scope
Browser extensions represent a pervasive attack vector for session hijacking, ad injection, and credential theft:
- Adware and search hijackers overriding user search defaults.
- Extensions requesting dangerous permissions (`<all_urls>`, `webRequest`, `cookies`).
- Sideloaded extensions bypassing the Chrome Web Store security vetting.

## Triage & Investigation Runbook
### Browser Extension Triage Runbook
1. **Identify Malicious Extension IDs**: Compare installed extensions with known malicious extension identifier lists.
2. **Inspect Extension Permissions**: Run queries on `chrome_extensions` inspecting `permissions` and `manifest_hash`.
3. **Remediation**: Remove corresponding extension folder from user profile directory (`~/Library/Application Support/Google/Chrome/Default/Extensions/<id>` or `%LOCALAPPDATA%\Google\Chrome\User Data\Default\Extensions\<id>`).

## Complete Query Catalog

### 1. `BetternetVPN`
- **Description**: (https://www.bleepingcomputer.com/news/security/eight-chrome-extensions-hijacked-to-deliver-malicious-code-to-4-8-million-users/)
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: N/A
- **SQL Query**:
```sql
SELECT * FROM users CROSS JOIN chrome_extensions USING (uid) WHERE identifier='gjknjjomckknofjidppipffbpoekiipm';
```

### 2. `Chrometana`
- **Description**: (https://www.bleepingcomputer.com/news/security/eight-chrome-extensions-hijacked-to-deliver-malicious-code-to-4-8-million-users/)
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: N/A
- **SQL Query**:
```sql
SELECT * FROM users CROSS JOIN chrome_extensions USING (uid) WHERE identifier='kaicbfmipfpfpjmlbpejaoaflfdnabnc';
```

### 3. `CopyFish`
- **Description**: (https://www.bleepingcomputer.com/news/security/copyfish-chrome-extension-hijacked-to-show-adware/)
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: N/A
- **SQL Query**:
```sql
SELECT * FROM users CROSS JOIN chrome_extensions USING (uid) WHERE identifier='eenjdnjldapjajjofmldgmkjaienebbj';
```

### 4. `HolaVPN`
- **Description**: (http://adios-hola.org)
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: N/A
- **SQL Query**:
```sql
SELECT * FROM users CROSS JOIN chrome_extensions USING (uid) WHERE identifier='gkojfkhlekighikafcpjkiklfbnlmeio';
```

### 5. `InfinityNewTab`
- **Description**: (https://www.bleepingcomputer.com/news/security/eight-chrome-extensions-hijacked-to-deliver-malicious-code-to-4-8-million-users/)
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: N/A
- **SQL Query**:
```sql
SELECT * FROM users CROSS JOIN chrome_extensions USING (uid) WHERE identifier='dbfmnekepjoapopniengjbcpnbljalfg';
```

### 6. `SocialFixer`
- **Description**: (https://www.bleepingcomputer.com/news/security/eight-chrome-extensions-hijacked-to-deliver-malicious-code-to-4-8-million-users/)
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: N/A
- **SQL Query**:
```sql
SELECT * FROM users CROSS JOIN chrome_extensions USING (uid) WHERE identifier='ifmhoabcaeehkljcfclfiieohkohdgbb';
```

### 7. `TouchVPN`
- **Description**: (https://www.bleepingcomputer.com/news/security/eight-chrome-extensions-hijacked-to-deliver-malicious-code-to-4-8-million-users/)
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: N/A
- **SQL Query**:
```sql
SELECT * FROM users CROSS JOIN chrome_extensions USING (uid) WHERE identifier='bihmplhobchoageeokmgbdihknkjbknd';
```

### 8. `WebDeveloper`
- **Description**: (https://www.bleepingcomputer.com/news/security/chrome-extension-with-over-one-million-users-hijacked-to-serve-adware/)
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: N/A
- **SQL Query**:
```sql
SELECT * FROM users CROSS JOIN chrome_extensions USING (uid) WHERE identifier='bfbameneiokkgbdmiekhjnmfkcnldhhm';
```

### 9. `WebPaint`
- **Description**: (https://www.bleepingcomputer.com/news/security/eight-chrome-extensions-hijacked-to-deliver-malicious-code-to-4-8-million-users/)
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: N/A
- **SQL Query**:
```sql
SELECT * FROM users CROSS JOIN chrome_extensions USING (uid) WHERE identifier='emeokgokialpjadjaoeiplmnkjoaegng';
```

### 10. `MacOSInstallCore`
- **Description**: (https://www.virustotal.com/#/file/5cab0821f597100dc1170bfef704d8cebaf67743e9d509e83b0b208eb630d992/detection)
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: N/A
- **SQL Query**:
```sql
SELECT * FROM users CROSS JOIN chrome_extensions USING (uid) WHERE identifier='hinehnlkkmckjblijjpbpamhljokoohh';
```

### 11. `User-Agent Switcher`
- **Description**: (https://chris.partridge.tech/2020/extensions-the-next-generation-of-malware/help-for-users/)
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: N/A
- **SQL Query**:
```sql
SELECT * FROM users CROSS JOIN chrome_extensions USING (uid) WHERE identifier='clddifkhlkcojbojppdojfeeikdkgiae';
```

### 12. `Nano Adblocker`
- **Description**: (https://chris.partridge.tech/2020/extensions-the-next-generation-of-malware/help-for-users/)
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: N/A
- **SQL Query**:
```sql
SELECT * FROM users CROSS JOIN chrome_extensions USING (uid) WHERE identifier='gabbbocakeomblphkmmnoamkioajlkfo';
```

### 13. `Nano Defender `
- **Description**: (https://chris.partridge.tech/2020/extensions-the-next-generation-of-malware/help-for-users/)
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: N/A
- **SQL Query**:
```sql
SELECT * FROM users CROSS JOIN chrome_extensions USING (uid) WHERE identifier='ggolfgbegefeeoocgjbmkembbncoadlb';
```

### 14. `Forcepoint Endpoint Chrome Extension`
- **Description**: (https://www.bleepingcomputer.com/news/security/malicious-extension-abuses-chrome-sync-to-steal-users-data/)
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: N/A
- **SQL Query**:
```sql
SELECT * FROM users CROSS JOIN chrome_extensions USING (uid) WHERE identifier='fmfjhicbjecfchfmpelfnifijeigelme';
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
