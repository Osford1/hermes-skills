---
name: windows-linux-dual-boot
description: "Use when dual-booting Linux or resizing a Windows disk."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows, linux]
metadata:
  hermes:
    tags: [dual-boot, partitioning, bitlocker, uefi, rufus, ubuntu, ntfs]
    category: systems
    related_skills: [file-organization, lerobot-environment-setup]
---

# Installing Linux alongside Windows

Covers adding a Linux partition to a Windows machine, resizing Windows volumes, making install
media, and the bootloader/encryption traps that decide whether the existing OS survives.
Verified on a UEFI + BitLocker laptop with a single NVMe (GPT, no unallocated space).

## How to run this with the user
- **Recon, then report, then act.** Read the disk/encryption/firmware facts first and state them
  back with the exact sizes. The user needs the numbers, not the plan.
- **One instruction at a time.** This user pauses, verifies, and asks "is this safe / will it
  corrupt anything" before every destructive step. Lead each turn with the single next command
  and its blast radius.
- **Explain a command before asking for it**: plain English, in this shape — what it reads or
  changes, whether it is reversible, what the output looks like. If it needs admin, say so and why.
- **Never run privileged steps yourself.** `manage-bde` and `powercfg` fail unelevated; hand the
  user the command for an admin shell and read their pasted output.
- **Gate irreversible actions explicitly**: state the data-loss consequence, the reversal path,
  and the exact space cost every time, then wait.
- **When the user revises a decided number** (partition size and the like), update *every* document
  carrying it in the same pass — plan, guide, manifest, index — and re-state the derived figures
  (new volume sizes, free space, what no longer fits). One stale number is how a later session
  talks the user into a wrong click.
- **Ask for the partitioner screen before it is confirmed.** It is the only step in the job where
  a single click destroys a filesystem.

## Recon (before touching anything)
| Need | Command | Note |
|---|---|---|
| Disks, bus, partition style | `Get-Disk` | `BusType` separates `NVMe` from `USB` targets |
| Partition offsets/sizes | `Get-Partition -DiskNumber 0 \| Sort-Object Offset` | is the shrink candidate the LAST partition? |
| Existing free space | `(Get-Disk 0).LargestFreeExtent` | 0 means everything comes from a shrink |
| Encryption | `manage-bde -status C:` | **needs admin**; unelevated it returns "access denied" |
| Secure Boot | `Get-ItemProperty 'HKLM:\SYSTEM\CurrentControlSet\Control\SecureBoot\State' -Name UEFISecureBootEnabled` | readable unelevated |
| Page file / shadow copies | `Get-CimInstance Win32_PageFileSetting` | a pagefile at the partition tail caps the shrink |
| What is already cloud-protected | `HKCU:\...\Explorer\User Shell Folders` | Desktop/Documents/Pictures redirected into OneDrive are already backed up; anything else is local-only |

## Order of operations
1. **Back up what is not in the cloud and not in git** — local-only user folders, project dirs that
   are not repos, dotfiles, and any device calibration/state file living outside a repo.
   - Find what is already covered first: the `User Shell Folders` key above shows which folders
     OneDrive has redirected; everything else is local-only.
   - **Verify the copy by counting, not by eyeballing sizes.** Diff the sorted file lists per folder
     (`comm -23 <(cd src && find . -type f|sort) <(cd dst && find . -type f|sort)`) — an empty
     "in source, not in destination" list is the pass. `robocopy` follows symlinks, so extra files
     in the destination are expected (a `checkpoints/last` link duplicates its target); a *missing*
     file is the failure.
   - Exclude toolchains from the copy: `node_modules/`, `.venv/`, editor `extensions/`,
     `.curator_backups/`. They are re-downloadable and they dominate copy time.
   - **An archive carrying `.env` or other credentials stays off cloud storage** — local disk only,
     then `chmod 600` after restoring it.
   - In git-bash, `tar -czf "C:\...\out.tar.gz"` fails with `Cannot connect to C: resolve failed`
     because the drive letter parses as a remote host — give `tar` an MSYS output path.
2. **BitLocker**: key out first, protection suspended last.
3. `powercfg /h off`.
4. Shrink → media → BIOS → install → re-enable BitLocker.

## BitLocker
- Protection On → get the 48-digit key: `manage-bde -protectors -get C: -type recoverypassword`,
  stored **off the machine**. A copy on the machine it unlocks is worthless. Never let the user
  paste the key into a chat.
- A Microsoft-account sign-in (`Get-LocalUser <name> | Select PrincipalSource`) normally means it is
  already escrowed at account.microsoft.com/devices/recoverykey.
- Suspend immediately before booting the installer: `manage-bde -protectors -disable C:`. Re-enable
  on the first Windows boot after: `manage-bde -protectors -enable C:`. In between the volume opens
  with no key at all — keep that window as short as the install.
- **Keep Secure Boot ON and do not flash a BIOS update inside the window.** The default TPM profile
  measures the Secure Boot state (PCR 7), so an unchanged state is what stops Windows demanding the
  key; toggling it is what produces the recovery screen.

## Clock skew between the two OSes (expect it, fix it once)
Ubuntu stores the hardware clock in **UTC**; Windows assumes the RTC holds **local** time. After the
first Linux boot, Windows shows the time shifted by exactly one timezone offset (e.g. −8 h 00 m for
China Standard Time) and looks merely "a bit wrong".

- Diagnose by reading, not guessing: `w32tm /query /status` showing `Source: Local CMOS Clock`,
  `Leap Indicator: 3(not synchronized)`, `Last Successful Sync Time: unspecified` means it has never
  synced; `reg query "HKLM\SYSTEM\CurrentControlSet\Control\TimeZoneInformation" /v RealTimeIsUniversal`
  failing with "unable to find the specified registry key or value" confirms the RTC is being read as
  local, and so does a key that exists holding `0x0` (something set the local-time meaning
  explicitly); only `0x1` means the RTC is read as UTC. An offset that is *exactly* a whole number of hours (to within a second) is the signature —
  a drifting clock is never that tidy.
- Confirm with two or more independent sources before changing anything (NTP query + an HTTP `Date:`
  header). A TLS connection succeeding proves nothing: certificates are valid for months, so an
  hours-sized clock error sails through.
- **Fix ONE side to match the other — never both independently.** Two half-fixes add the offset twice:
  setting `RealTimeIsUniversal=1` on a Windows box whose Linux is already on `set-local-rtc 1` makes
  Windows exactly one offset **fast** (the mirror of the usual complaint) and the RTC gets rewritten in
  the wrong meaning again. Determine what Linux already has first (its `timedatectl` output or the 3rd
  line of `/etc/adjtime`, `LOCAL` vs `UTC`) — a prior session very likely already applied one of these.
- Permanent fix (elevated), pick the branch that matches Linux:
  - Linux on **local** RTC (correct and harmless in a no-DST zone like China):
    `reg add "HKLM\SYSTEM\CurrentControlSet\Control\TimeZoneInformation" /v RealTimeIsUniversal /t REG_DWORD /d 0 /f`
    That is Windows' own default — nothing unofficial to lose — and `set-local-rtc 1` survives updates.
  - Linux left on **UTC** (distro default):
    `reg add "...\TimeZoneInformation" /v RealTimeIsUniversal /t REG_DWORD /d 1 /f` and keep
    `timedatectl set-local-rtc 0`. Unofficial; Windows updates can revert it.
- **Pick the branch from the RTC's actual contents, not from the symptom.** If the time Windows shows
  equals the true **UTC** value rather than the true local value, the RTC already holds UTC, so the
  UTC branch is the consistent one whatever Linux is configured to do — the double-offset trap is
  ruled out by measurement, not by inspection. Confirm afterwards with an offset of ~0 s against
  three independent peers.
- **When the user asks for the fix itself instead of instructions**, drive the elevated step through
  UAC rather than pasting commands into chat: write the commands into a `.ps1` that appends everything
  to a log in `%TEMP%`, launch it with
  `Start-Process powershell -Verb RunAs -ArgumentList '-NoProfile','-ExecutionPolicy','Bypass','-File',<path>`,
  then poll for the log's end marker and read the before/after timestamps and `w32tm` output out of it.
  That leaves a verifiable artifact when a UAC click is the only interactive part.
- The flag is normally read **at boot only**, so a one-off step (`Set-Date`, or `w32tm /resync` once
  it works) is what fixes the running session. **Measured exception:** restarting the service right
  after the `reg add` — `net stop w32time` then `net start w32time`, both elevated — makes the running
  clock jump the full offset within seconds (the log's before/after stamps differ by exactly the
  offset). No reboot needed. The RTC is rewritten in the newly active meaning at the next poll or
  shutdown, so re-check after the next boot.
- **Same convention is not enough — Windows must actually sync, or nothing self-heals.** In this class
  of machine the Windows failure is the service's own name resolution, not the network: Time-Service log
  event 134 (`DNS resolution error on 'cn.pool.ntp.org'`) and event 47 (peer unreachable) appear while a
  user-context UDP query to the same hosts answers fine. Give w32time **numeric IP peers**
  (`/manualpeerlist:"203.107.6.88,0x9 120.25.115.20,0x9 119.28.183.184,0x9"`) and it syncs; the service
  does a fresh poll on every start, which is what rescues a wrong RTC at boot.
- After a step the size of a timezone offset, `w32tm /query /status` still reads
  `Leap Indicator: 3(not synchronized)`, `Stratum: 0`, `Root Dispersion: <the step size>` until the next
  poll — cosmetic, and with the `0x8`/`0x9` special-interval flag that next poll is a full
  `SpecialPollInterval` (32768 s = 9.1 h) away. Verify the clock itself against independent servers
  instead of trusting that status line.
- **Never let a script auto-step the clock.** Guard any step behind: two independent NTP sources
  agreeing within 2 s, offset under 10 minutes, and abort otherwise. A bad step is worse than a wrong
  clock — it stamps files, cron state and DB rows with impossible dates. Guard on the *measured*
  offset, never on one hardcoded expected value: a guard tuned to exactly the expected error will
  silently refuse to fire once a sync has already corrected the clock (harmless, but it also refuses
  any other genuine error). Accept a step only when `2 s < |offset| < 24 h`, and re-measure first.
- **SNTP timestamp trap:** the NTP transmit timestamp counts seconds from **1900**, not 1970.
  Subtract 2208988800 before converting, or the "time" lands 70 years in the future. The bug is
  invisible in the offset arithmetic when the clock is also wrong, which is exactly when it fires.
- If the clock does jump decades ahead, **wait before hand-fixing**: Windows self-corrects large jumps
  from TLS timestamps (`UtilizeSslTimeData=1`, applied by `svchost.exe`) within about 30 minutes and
  lands within a second. Check `Microsoft-Windows-Kernel-General` event ID 1 for who changed it and by
  how much.
- `w32tm /resync` reporting *"The computer did not resync because no time data was available"* while
  the same peers answer a user-context NTP query points at a third-party firewall/AV blocking
  `svchost.exe` UDP 123 (McAfee in this class of machine), not at the peers.
- After any jump, sweep for collateral: `find <dirs> -newermt <tomorrow>` finds files stamped with the
  wrong era, and cron state is the place it actually breaks — `next_run` computed while the clock was
  wrong stays in the future forever, so every job silently stops firing.

## Fast Startup is a requirement, not a nicety
`powercfg /h off` in an admin shell. Fast Startup leaves NTFS volumes hibernated, and Linux writing
an NTFS volume in that state can corrupt it — this is the real corruption risk in a dual-boot, and
the step users skip. State the side effects up front: hiberfil.sys is deleted (several GB back on a
full C:), the Hibernate power option disappears. If the user actually uses hibernation, use the
surgical registry form (`HiberbootEnabled=0`) instead of turning hibernation off.

## Shrinking
- **Shrink the LAST partition on the disk.** The freed space then lands at the end of the disk and
  the Linux install is a clean append — no partition has to be moved afterwards.
- A shrink only releases free space at the tail; it does not move or rewrite files, so it cannot
  lose data by itself. Unmovable files at the tail just make Windows offer less.
- Say plainly: a partition is a hard carve, not elastic allocation. The other volume gets smaller
  and the carved space is unreachable from Windows — no new drive letter appears.
- Size with measured proxies, not guesses: the user's own WSL distro footprints (a conda/CUDA
  robotics env ~18–35 GB, a ROS 2 dev distro ~9 GB), base OS ~12 GB, driver ~2 GB, and 30–50 GB for
  datasets/checkpoints. A 50 GB root does not hold the robotics stack; ~100 GB does.
- If they are unsure, offer the hedge: shrink by the larger figure but allocate only part of it and
  leave the rest unallocated. Growing ext4 into right-adjacent unallocated space needs no data move,
  and an NTFS partition can be created there instantly. The cost is that it is unusable until decided.

## Reversibility (state this before they commit)
| Goal | Cost |
|---|---|
| Remove Linux entirely → space back to Windows | free: delete the partition, then `Extend Volume` on the neighbour to its left |
| Shrink the Linux partition | GParted must move it — Windows cannot touch ext4 — tens of minutes, low risk, Windows untouched |
| Grow Linux after a later Windows shrink | also a move: the free space lands between the two partitions |

## Install media
- Desktop AMD64 image, not server/netboot/WSL. Verify `certutil -hashfile <iso> SHA256` against SHA256SUMS.
- Rufus x64 for an AMD64 machine (not `_arm64`, not `_x86`); confirm the signature reads "Akeo
  Consulting". Portable vs standard is cosmetic (settings in an ini rather than the registry).
- Partition scheme **GPT**, target **UEFI (non-CSM)**.
- **ISO Image mode vs DD mode:** decide by whether any file *inside* the ISO exceeds FAT32's 4 GiB
  limit — run `scripts/iso_big_file_check.py`. Recent Ubuntu desktop images ship layered squashfs
  with nothing over 4 GiB, so ISO Image mode works and leaves a browsable stick. A >4 GiB member
  (some distros) forces DD mode, which Windows then cannot browse.
- **Never target the drive holding the ISO** — the write destroys the file being read.
- **Inspect the target medium for existing data first** (`Get-Volume`, then list it). A "spare"
  drive is often the user's only copy of something; one external SSD in this class of task held the
  user's CV, family photos and a semester archive. Ventoy keeps a large drive usable, but its
  non-destructive install needs an **NTFS first partition** (exFAT is refused) and Secure Boot
  requires a one-time MOK enrolment.

## Installer discipline (the only step that can destroy data)
- Manual partitioning: create ext4 at `/` in the free space; **do not format the EFI System
  Partition** — reuse it, the installer adds its own loader there. Point the bootloader device at the
  internal disk. Leave every other partition untouched.
- Check the size labels before confirming (system volume as it stands, the data volume as shrunk,
  the new free space as planned). Anything unexpected → stop.
- First boot after: run Windows once and re-enable BitLocker immediately.

## What Windows shows afterwards
Nothing new — and users ask about this. ext4 gets no drive letter, so Explorer still shows the same
volumes, and Disk Management shows the partition with no recognised filesystem (sometimes "RAW").
Unallocated space before installation is likewise not a drive. Warn against the two destructive
reflexes: formatting the "unknown" volume, and running chkdsk on it.

## Portable Linux on an external drive (the zero-risk variant)
- Install to the external drive with its **own ESP** (300–500 MB, FAT32, mounted `/boot/efi`) and set
  "Device for boot loader installation" to that disk. Otherwise GRUB's config lives on the external
  drive and unplugging it drops the machine to `grub rescue` instead of booting Windows.
- Verify afterwards: mount the internal ESP and confirm it has no `EFI/ubuntu` directory; clear any
  stale NVRAM entry with `efibootmgr`.
- Costs: much slower than NVMe (fine for editing/ROS 2, noticeable for video-heavy training), Linux
  exists only while plugged in, and yanking the drive mid-session freezes the OS.
- It can be tried *before* committing to an internal partition — the two are not exclusive.

## When the real worry is giving Windows space away
A WSL2 distro's `ext4.vhdx` grows on demand and is the only configuration where Windows keeps the
space until Linux actually uses it. That is the honest alternative to a fixed carve.

## Support files
- `scripts/iso_big_file_check.py` — reports the largest files inside an ISO and whether any exceeds
  FAT32's 4 GiB limit, which decides Rufus ISO-image vs DD mode.
