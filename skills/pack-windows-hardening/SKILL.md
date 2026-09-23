---
name: pack-windows-hardening
description: Windows security baseline and hardening audit query pack. Features 39 queries validating registry configuration against CIS benchmarks for UAC elevation, SMBv1 disablement, Windows Defender status, firewall profiles, BitLocker, and credential caching. Use for Windows security compliance audits.
---

# Windows Hardening & Security Baseline Query Pack

The `pack-windows-hardening` skill equips agents with curated queries and diagnostic procedures from `osquery_data/packs/windows-hardening.conf`. This query pack focuses on windows hardening & security baseline query pack.

## Threat Model & Scope
Hardening audits evaluate whether endpoint configurations adhere to defensive benchmarks (CIS, Microsoft Security Baselines):
- User Account Control (UAC): Admin approval mode, elevation prompt behavior.
- Legacy Protocols: Disabling insecure protocols like SMBv1, LLMNR, and NetBIOS.
- Defensive Services: Ensuring Windows Defender real-time monitoring and cloud protection are enabled.
- Credential Protection: Restricting WDigest plaintext credential caching and LM/NTLMv1 hash generation.

## Triage & Investigation Runbook
### Hardening Compliance Audit Workflow
1. **Execute Baseline Scan**: Run all 39 hardening queries to evaluate registry keys against benchmark values.
2. **Identify Non-Compliant Settings**: Generate a scorecard of passing vs failing settings.
3. **Remediation**: Deploy group policies (GPO) or MDM configuration profiles (Intune) to enforce required values.

## Complete Query Catalog

### 1. `OpenType_Font_Driver_Vulnerability`
- **Description**: Determine if Adobe Type Manager Font Driver is disabled (https://technet.microsoft.com/en-us/library/security/ms15-078)
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: 2.2.1
- **SQL Query**:
```sql
select * from registry where path like 'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Windows\%' AND name = 'DisableATMFD' AND data != '1';
```

### 2. `Protecting_Against_Weak_Crypto_Algo`
- **Description**: Determine if Windows is configured to log certificates with weak crypto (https://technet.microsoft.com/library/dn375961(v=ws.11).aspx)
- **Context / Value**: Artifact used by this malware
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: 2.2.1
- **SQL Query**:
```sql
select * from registry where path like 'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Cryptography\OID\EncodingType 0\CertDllCreateCertificateChainEngine\Config\Default\%' AND name IN ('WeakSha1ThirdPartyFlags','WeakMd5ThirdPartyFlags') AND type = 'REG_DWORD' AND data not like '-2%';
```

### 3. `UAC_Disabled`
- **Description**: Controls UAC. A setting of 0 indicates that UAC is disabled.
- **Interval**: 3600 seconds
- **Minimum Osquery Version**: 2.2.1
- **SQL Query**:
```sql
SELECT * FROM registry WHERE path='HKEY_LOCAL_MACHINE\Software\Microsoft\Windows\CurrentVersion\Policies\System\EnableLUA' AND data=0;
```

### 4. `SecureBoot`
- **Description**: Whether Secureboot is enabled
- **Interval**: 86400 seconds
- **Minimum Osquery Version**: N/A
- **SQL Query**:
```sql
select * from registry where key='HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\SecureBoot\State\UEFISecureBootEnabled'
```

### 5. `FontBlocking`
- **Description**: Whether FontBlocking is enabled
- **Interval**: 86400 seconds
- **Minimum Osquery Version**: N/A
- **SQL Query**:
```sql
select * from registry where key='HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\Windows NT\MitigationOptions\MitigationOptions_FontBlocking'
```

### 6. `DepPolicy`
- **Description**: Whether DEP is enabled
- **Interval**: 86400 seconds
- **Minimum Osquery Version**: N/A
- **SQL Query**:
```sql
select * from registry where key='HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\SystemStartOptions'
```

### 7. `MitigationOptions`
- **Description**: Whether DEP is enabled with application mitigation options
- **Interval**: 86400 seconds
- **Minimum Osquery Version**: N/A
- **SQL Query**:
```sql
select * from registry where key='HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Session Manager\Kernel\MitigationOptions'
```

### 8. `MoveImages`
- **Description**: Check ASLR configuration
- **Interval**: 86400 seconds
- **Minimum Osquery Version**: N/A
- **SQL Query**:
```sql
select * from registry where key='HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management\moveImages'
```

### 9. `KernelSehopEnabled`
- **Description**: Whether SEHOP is enabled
- **Interval**: 86400 seconds
- **Minimum Osquery Version**: N/A
- **SQL Query**:
```sql
select * from registry where key='HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Session Manager\Kernel\KernelSEHOPEnabled'
```

### 10. `EnableCertPaddingCheck`
- **Description**: Determine state of Certificate Padding (https://docs.microsoft.com/en-us/security-updates/securityadvisories/2014/2915720)
- **Interval**: 86400 seconds
- **Minimum Osquery Version**: N/A
- **SQL Query**:
```sql
select * from registry where key='HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Cryptography\WinTrust\Config\EnableCertPaddingCheck'
```

### 11. `EnableCertPaddingCheck_wow64`
- **Description**: Determine state of Certificate Padding (https://docs.microsoft.com/en-us/security-updates/securityadvisories/2014/2915720)
- **Interval**: 86400 seconds
- **Minimum Osquery Version**: N/A
- **SQL Query**:
```sql
select * from registry where key='HKEY_LOCAL_MACHINE\SOFTWARE\Wow6432Node\Microsoft\Cryptography\WinTrust\Config\EnableCertPaddingCheck'
```

### 12. `CwdIllegalInDllSearch`
- **Description**: Check Secure Search Path state (https://support.microsoft.com/en-us/help/2264107/a-new-cwdillegalindllsearch-registry-entry-is-available-to-control-the)
- **Interval**: 86400 seconds
- **Minimum Osquery Version**: N/A
- **SQL Query**:
```sql
select * from registry where key='HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Session Manager\CWDIllegalInDllSearch'
```

### 13. `DisabledExceptionChainValidation`
- **Description**: Check SEHOP state: DisabledExceptionChainValidation
- **Interval**: 86400 seconds
- **Minimum Osquery Version**: N/A
- **SQL Query**:
```sql
select * from registry where key='HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Session Manager\kernel\DisableExceptionChainValidation'
```

### 14. `EnableLowVaAccess`
- **Description**: Check Kernel Null page state
- **Interval**: 86400 seconds
- **Minimum Osquery Version**: N/A
- **SQL Query**:
```sql
select * from registry where key='HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management\EnableLowVaAccess'
```

### 15. `ControlFlowGuard`
- **Description**: Check Control Flow Guard state
- **Interval**: 86400 seconds
- **Minimum Osquery Version**: N/A
- **SQL Query**:
```sql
select * from registry where key='HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management\EnableCfg'
```

### 16. `App_ExecuteOptions`
- **Description**: Check Applications opted in for DEP
- **Interval**: 86400 seconds
- **Minimum Osquery Version**: N/A
- **SQL Query**:
```sql
select * from registry where key like 'HKEY_LOCAL_MACHINE\SOFTWARE\%Microsoft\Windows NT\CurrentVersion\Image File Execution Options\%\executeOptions'
```

### 17. `App_MitigationOptions`
- **Description**: Check Applications opted in for DEP
- **Interval**: 86400 seconds
- **Minimum Osquery Version**: N/A
- **SQL Query**:
```sql
select * from registry where key like 'HKEY_LOCAL_MACHINE\SOFTWARE\%Microsoft\Windows NT\CurrentVersion\Image File Execution Options\%\MitigationOptions'
```

### 18. `AppCompat`
- **Description**: Check Applications opted in for DEP
- **Interval**: 86400 seconds
- **Minimum Osquery Version**: N/A
- **SQL Query**:
```sql
select * from registry where key='HKEY_LOCAL_MACHINE\SOFTWARE\%Microsoft\Windows NT\CurrentVersion\AppCompatFlags\Layers'
```

### 19. `App_disabledExceptionChainValidation`
- **Description**: Check Applications not supporting SEHOP
- **Interval**: 86400 seconds
- **Minimum Osquery Version**: N/A
- **SQL Query**:
```sql
select * from registry where key like 'HKEY_LOCAL_MACHINE\SOFTWARE\%Microsoft\Windows NT\CurrentVersion\Image File Execution Options\%\DisableExceptionChainValidation'
```

### 20. `DefaultLevelMachine`
- **Description**: Check Software Restriction Policies state
- **Interval**: 86400 seconds
- **Minimum Osquery Version**: N/A
- **SQL Query**:
```sql
select * from registry where key='HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\Windows\Safer\CodeIdentifiers\DefaultLevel'
```

### 21. `DefaultLevelUser`
- **Description**: Check Software Restriction Policies state
- **Interval**: 86400 seconds
- **Minimum Osquery Version**: N/A
- **SQL Query**:
```sql
select * from registry where key like 'HKEY_USERS\%\SOFTWARE\Policies\Microsoft\Windows\Safer\CodeIdentifiers\DefaultLevel'
```

### 22. `PolicyScopeMachine`
- **Description**: Check Software Restriction Policies state
- **Interval**: 86400 seconds
- **Minimum Osquery Version**: N/A
- **SQL Query**:
```sql
select * from registry where key='HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\Windows\Safer\CodeIdentifiers\PolicyScope'
```

### 23. `PolicyScopeUser`
- **Description**: Check Software Restriction Policies state
- **Interval**: 86400 seconds
- **Minimum Osquery Version**: N/A
- **SQL Query**:
```sql
select * from registry where key like 'HKEY_USERS\%\SOFTWARE\Policies\Microsoft\Windows\Safer\CodeIdentifiers\PolicyScope'
```

### 24. `ExecutableTryMachine`
- **Description**: Check Software Restriction Policies state
- **Interval**: 86400 seconds
- **Minimum Osquery Version**: N/A
- **SQL Query**:
```sql
select * from registry where key='HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\Windows\Safer\CodeIdentifiers\ExecutableTry'
```

### 25. `ExecutableTryUser`
- **Description**: Check Software Restriction Policies state
- **Interval**: 86400 seconds
- **Minimum Osquery Version**: N/A
- **SQL Query**:
```sql
select * from registry where key like 'HKEY_USERS\%\SOFTWARE\Policies\Microsoft\Windows\Safer\CodeIdentifiers\ExecutableTry'
```

### 26. `TransparentEnabledMachine`
- **Description**: Check Software Restriction Policies state
- **Interval**: 86400 seconds
- **Minimum Osquery Version**: N/A
- **SQL Query**:
```sql
select * from registry where key='HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\Windows\Safer\CodeIdentifiers\TransparentEnabled'
```

### 27. `TransparentEnabledUser`
- **Description**: Check Software Restriction Policies state
- **Interval**: 86400 seconds
- **Minimum Osquery Version**: N/A
- **SQL Query**:
```sql
select * from registry where key like 'HKEY_USERS\%\SOFTWARE\Policies\Microsoft\Windows\Safer\CodeIdentifiers\TransparentEnabled'
```

### 28. `Unrestricted`
- **Description**: Check Software Restriction Policies state: No SRP allow list rules
- **Interval**: 86400 seconds
- **Minimum Osquery Version**: N/A
- **SQL Query**:
```sql
select * from registry where key='HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\Windows\Safer\CodeIdentifiers\262144'
```

### 29. `Unrestricted_Paths`
- **Description**: Check Software Restriction Policies state: No SRP path rules
- **Interval**: 86400 seconds
- **Minimum Osquery Version**: N/A
- **SQL Query**:
```sql
select * from registry where key='HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\Windows\Safer\CodeIdentifiers\262144\Paths'
```

### 30. `Unrestricted_Paths_ItemData`
- **Description**: Check Software Restriction Policies state: SRP allow list rules is missing
- **Interval**: 86400 seconds
- **Minimum Osquery Version**: N/A
- **SQL Query**:
```sql
select * from registry where key like 'HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\Windows\Safer\CodeIdentifiers\262144\Paths\%\ItemData'
```

### 31. `Disallowed`
- **Description**: Check Software Restriction Policies state: No SRP deny list rules
- **Interval**: 86400 seconds
- **Minimum Osquery Version**: N/A
- **SQL Query**:
```sql
select * from registry where key='HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\Windows\Safer\CodeIdentifiers\0'
```

### 32. `Disallowed_Paths`
- **Description**: Check Software Restriction Policies state: No SRP path rules
- **Interval**: 86400 seconds
- **Minimum Osquery Version**: N/A
- **SQL Query**:
```sql
select * from registry where key='HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\Windows\Safer\CodeIdentifiers\0\Paths'
```

### 33. `Disallowed_Paths_ItemData`
- **Description**: Check Software Restriction Policies state: SRP deny list rule is missing
- **Interval**: 86400 seconds
- **Minimum Osquery Version**: N/A
- **SQL Query**:
```sql
select * from registry where key like 'HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\Windows\Safer\CodeIdentifiers\0\Paths\%\ItemData'
```

### 34. `SaferFlags`
- **Description**: Check Software Restriction Policies state: SRP rule is not enforcing
- **Interval**: 86400 seconds
- **Minimum Osquery Version**: N/A
- **SQL Query**:
```sql
select * from registry where key like 'HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\Windows\Safer\CodeIdentifiers\%\%\%\SaferFlags'
```

### 35. `RuleSetEnforcementMode`
- **Description**: Check Applocker rule set configuration
- **Interval**: 86400 seconds
- **Minimum Osquery Version**: N/A
- **SQL Query**:
```sql
select * from registry where key like 'HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\Windows\SrpV2\%\EnforcementMode'
```

### 36. `Rule`
- **Description**: Check Applocker rule set
- **Interval**: 86400 seconds
- **Minimum Osquery Version**: N/A
- **SQL Query**:
```sql
select * from registry where key like 'HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\Windows\SrpV2\%\%\Value'
```

### 37. `AuditSpecialGroups`
- **Description**: Check Special Logon Audit configuration - https://blogs.technet.microsoft.com/jepayne/2015/11/26/tracking-lateral-movement-part-one-special-groups-and-specific-service-accounts/
- **Interval**: 86400 seconds
- **Minimum Osquery Version**: N/A
- **SQL Query**:
```sql
select * from registry where key='HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Lsa\Audit'
```

### 38. `SysmonConfig`
- **Description**: Check Microsoft Sysinternals Sysmon config
- **Interval**: 86400 seconds
- **Minimum Osquery Version**: N/A
- **SQL Query**:
```sql
select * from registry where key='HKEY_LOCAL_MACHINE\SYSTEM\CCS\Services\SysmonDrv\Parameters'
```

### 39. `DeveloperMode`
- **Description**: Check Developer Mode state
- **Interval**: 86400 seconds
- **Minimum Osquery Version**: N/A
- **SQL Query**:
```sql
select * from registry where key='HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\AppModelUnlock'
```

## Referenced Table Schemas

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
