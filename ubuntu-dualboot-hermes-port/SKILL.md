---
name: ubuntu-dualboot-hermes-port
description: "Use when dual-booting Ubuntu or porting Hermes to Linux."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, windows]
metadata:
  hermes:
    tags: [ubuntu, dual-boot, partitioning, bitlocker, migration, obsidian, hermes-port]
    related_skills: [hermes-agent, obsidian, file-organization, lerobot-environment-setup]
---

# Ubuntu dual-boot + porting Hermes/Obsidian to native Linux

Use for: installing Ubuntu alongside Windows, sizing/reshaping the partition, choosing an install medium, and moving a Hermes profile + Obsidian vault across operating systems.

## Pre-flight on Windows (verify, never assume)

- **BitLocker needs an admin shell** (`manage-bde -status C:` fails without one). If `Protection On`: back up the 48-digit key (`manage-bde -protectors -get C: -type recoverypassword`) **off-machine**, then **suspend before any bootloader change** (`manage-bde -protectors -disable C:`) and re-enable after the first Windows boot (`-protectors -enable C:`). Keep **Secure Boot ON** — the default TPM profile measures the Secure Boot state (PCR 7), so leaving it untouched is what prevents the recovery prompt. Don't flash BIOS in between.
- **A BitLocker-protected volume cannot be mounted from Linux** (no driver without `dislocker` plus the recovery key), so every "read it from Ubuntu at `/mnt/win/...`" path in a plan is fiction for an encrypted `C:` — the vault, the agent profile, `robot_101`, the pre-install backup. Anything on such a volume must be **staged onto a payload while Windows is still bootable**, and the payload is then the only route in, not a convenience. Have the user run `manage-bde -status C:` (admin) *before* planning paths, and check the real mount on first boot (`ls /mnt/win | head`) instead of trusting the guide. A non-encrypted data partition (`D:`) stays readable, which is where a second copy belongs.
- **`powercfg /h off` is mandatory, not a nicety.** Fast Startup leaves NTFS hibernated, and Linux writing that volume can genuinely corrupt it.
- **Before shrinking, check for unmovable files:** a page file on that volume (`Get-CimInstance Win32_PageFileSetting`) or shadow copies parked at the end will cap the shrink. Shrink only ever releases space at the **end** of a partition — it moves no data, so it cannot damage files; it just offers less.
- **Reversibility:** if the reclaimed space is at the end of the disk, deleting Linux later lets Windows `Extend Volume` swallow it back for free. Growing ext4 later needs a GParted live USB and physically **moves** the partition. Decide the size up front; a "hedge" (allocate less now, leave the rest unallocated) removes the need for any future move.

## What Windows sees afterwards (users expect a third drive — there isn't one)

- Unallocated space is not a drive. An ext4 partition gets **no drive letter** and never appears in Explorer; D: simply has less capacity.
- Never let Windows format or run chkdsk on a partition it reports as unknown/RAW — that destroys the Linux install (Windows files survive).

## Install medium

- **List the target drive's contents before advising a wipe.** A "spare" drive can be someone's archive (CV, family photos, coursework). Rufus wipes the whole device.
- The ISO source must never live on the drive being written — Rufus would destroy the file it is reading.
- **Check the ISO's internals before choosing a write mode.** Rufus ISO-image mode needs no file >4 GiB (FAT32). Some Ubuntu point releases ship layered squashfs (`casper/MINIMAL*.SQUASHFS`, nothing over 4 GiB), so ISO mode works; DD mode is the fallback if a boot fails. A classic single `filesystem.squashfs` over 4 GiB forces DD mode.
- **Ventoy's non-destructive install requires the first partition to be NTFS** — exFAT doesn't qualify without a third-party shrink. Don't promise it for an exFAT drive. Its Secure Boot support also needs a one-time MOK enrollment.

## Installer choices

- Manual partitioning: one ext4 at `/` in the free space. **Never format the existing EFI System Partition** — GRUB goes there and Windows' boot entry stays intact.
- Installing to an **external drive**: create the ESP **on the external disk** and set "Device for boot loader installation" to it, then verify the internal ESP has no `EFI/ubuntu` folder. Otherwise unplugging the drive turns Windows' boot into a `grub rescue` prompt (Windows is undamaged, but the boot flow is broken).

## Moving a Hermes profile across OSes

- **Portable as-is:** `memories/`, `skills/` (content only), `cron/jobs.json`, `config.yaml`, `.env`, `auth.json`, `SOUL.md`, `sessions/`, `state.db`, `plugins/`, `desktop-plugins/`, `pets/`.
- **Snapshot SQLite with the backup API** (`sqlite3` + `Connection.backup`) — a plain copy of a live `state.db` can be inconsistent. Don't copy `-wal`/`-shm` while the agent is running.
- **Rebuild, don't copy:** Python venvs, `node_modules`, git-installed source, `bin/` launchers.
- **After the move:** re-path every cron prompt and any skill that hardcodes `C:\` / `C:/Users` paths; `chmod 600 .env`; keep the payload **off cloud sync** — it contains live API keys.
- **Stage the payload twice: the USB stick and a copy on the shared NTFS data partition** (`/mnt/data/hermes-port/`). That partition is readable from both OSes — an encrypted `C:` never is — so the stick stops being a single point of failure. If the user still wants a copy inside a cloud-synced folder, say what that uploads (live credentials) and make the local copy the primary.
- **Ship it with checksums and a runbook** (`SHA256SUMS.txt` verified by `sha256sum -c` on both sides of the hop; a phased runbook with checkpoints and a troubleshooting table inside the payload). Payload mechanics, scoped ports and re-syncing live in `hermes-profile-migration`.
- **Histories don't merge:** `state.db` is per-machine. And exactly **one** machine may poll a messaging bot (WeChat/Telegram) at a time, or two gateways fight over the same messages.
- Diff the restored `config.yaml` against the freshly installed one — the new install's platform defaults should win.

## Clocks and the RTC between the two OSes

- **The RTC convention is one shared setting — pick a side or the 8-hour error just changes hands.** Windows' default (`RealTimeIsUniversal` unset) is RTC-holds-*local*; Ubuntu's default is RTC-in-UTC. Each OS writes the RTC when it shuts down, so with no decision made the clock ping-pongs: correcting Windows' time makes Ubuntu boot 8 h *ahead* next time, and vice versa. Settle it once — either `sudo timedatectl set-local-rtc 1` (no `--adjust-system-clock`) or `RealTimeIsUniversal=1`. **Never both** (that puts the two OSes 8 h out in opposite directions).
- Read the direction off the size of the error: exactly the UTC offset (8 h for China), not minutes, means the RTC convention, not crystal drift.
- **`w32time`'s "The computer did not resync because no time data was available" says nothing about the cause.** Check in order: (1) `w32tm /query /peers` — is the peer count sane? (2) `w32tm /stripchart /computer:<server> /samples:3 /dataonly` — live data plus the exact offset, or genuinely unreachable? (3) the network's source port (below).
- **`/manualpeerlist:` is SPACE-delimited.** `ntp.aliyun.com,ntp.tencent.com,cn.pool.ntp.org` is read as **one** host name (a comma only introduces a flag such as `,0x8`), DNS never resolves it, and the tells are `w32tm /query /peers` reporting `#Peers: 1` plus Event ID 47 naming the whole comma string as the peer. Use `"a.com b.com c.com"` — DNS round-robin then legitimately shows more entries than you listed.
- **Some networks silently drop NTP whose source port is 123 — the exact port w32time always sends from — so no server choice or config fixes it, ever.** Test before configuring: `scripts/ntp_source_port_probe.py` sends SNTP from source port 123 (stop w32time first to free the port) and from an ephemeral port. Source-123 timeout with ephemeral OK = network filter, and the only fix is to set the clock directly.
- Set it with the measured offset: `Set-Date -Adjust (New-TimeSpan -Seconds $offset)` (admin). With that fallback in place, `Last Successful Sync Time: unspecified` and `Source: Local CMOS Clock` forever are expected on this class of machine — not a fault to keep chasing.
- When the *service* is the stubborn part, turn on w32time's own file log — `FileLogName` / `FileLogEntries` / `FileLogSize` under `HKLM\SYSTEM\CurrentControlSet\Services\W32Time\Config` — then empty them again; a leftover path logs indefinitely.
- Working tool + log on this machine: `E:\windows-clock-fix\` on the USB stick (`istoretings`). `fix-windows-clock.bat` self-elevates, configures w32time and falls back to the direct step. Keep a `pause` at the end of the .bat or the elevated window closes before the user reads the result.
- **An unelevated agent session cannot do any of this**: `w32tm /config`, `/resync`, `Set-Date` and `net stop w32time` all need admin. Launch elevated work with `Start-Process -Verb RunAs -Wait` (the user clicks the UAC prompt) and have the script write its output to a log file — reading that log is the only way to verify a privileged run from outside. `net session` is the cheap admin test.

## Native Linux wins and gotchas (robotics)

- Native Ubuntu removes the `usbipd` USB-passthrough hop: the arm appears as `/dev/ttyACM*` directly. Use `usermod -aG dialout` or a udev rule instead of `chmod 666`.
- Scripts copied **from NTFS can carry CRLF**, and bash dies on `$'\r': command not found`. Strip with `find … -name '*.sh' -exec sed -i 's/\r$//' {} +`, or keep working copies on ext4. **For code going to Linux, export it rather than copying the worktree**: `git -c core.autocrlf=false -c core.eol=lf archive --format=tar.gz -o D:/payload/<repo>.tar.gz HEAD` — a Windows git with the default `core.autocrlf=true` makes even `git archive` emit CRLF, which silently breaks every shell script in the repo on the Linux side. Hand native programs (git, tar, node) **forward-slash or native paths**, never `/d/...`: MSYS does not translate them for non-MSYS binaries, so `-o /d/...` writes somewhere you will not look. Verify by extracting and counting CR-bearing text files (`grep -rlU $'\r' <extracted> | wc -l` — expect 0), not by trusting the Windows worktree.
- Datasets/checkpoints belong on the shared NTFS partition (`HF_HOME`); a conda env there is second-class (no hardlink optimisation, symlink-hostile) — fine on ext4 instead.
- A **Windows-side proxy** (e.g. Clash on `127.0.0.1:7897`) does not exist in an Ubuntu boot. Plan Tsinghua mirrors and/or a Linux proxy client. **Fetch anything that needs GitHub/raw.githubusercontent while Windows is still bootable** and park it on the shared NTFS partition — the ROS 2 apt signing key is the one that bites, because the download that succeeds through the proxy fails without it and the failure surfaces much later as an apt error. Inside Ubuntu, `mirrors.tuna.tsinghua.edu.cn/{ubuntu,ros2/ubuntu}` covers apt, the TUNA PyPI index covers pip, and `HF_ENDPOINT=https://hf-mirror.com` covers model weights, so the proxy is usually unnecessary.
- NTFS is writable from Linux but ext4 is invisible to Windows: keep anything both OSes must see on the NTFS side, and allow only one writer per vault/asset at a time.
