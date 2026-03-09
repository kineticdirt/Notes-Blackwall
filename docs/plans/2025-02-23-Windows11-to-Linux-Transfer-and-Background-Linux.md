# Windows 11 → Linux Transfer and Background Linux Instance — Implementation Plan (Concrete)

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Take a fully utilized Windows 11 instance, capture its state, transfer workloads to a Linux instance, run that Linux instance in the background on 8 cores with Nvidia RTX 5070 and AMD Vega56, and enable remote power-on from anywhere (Wake-on-LAN and/or GPIO relay).

**Architecture:** (1) Optional debloat via Talon/Talon Lite (concrete versions and limits). (2) Capture Windows state with a real PowerShell script and JSON manifest. (3) Transfer manifest + Linux-side import with real app-mapping. (4) Background Linux via WSL2 (with concrete `.wslconfig`) or VM/dual-boot; GPU and driver versions specified. (5) Remote wake: WoL (BIOS + OS + relay-over-internet or port-forward) and/or Raspberry Pi + relay on motherboard power-switch pins.

**Tech Stack:** Talon 1.2.0 / Talon Lite (debloat.win, Raven Development Team); PowerShell 5.1+; WSL2 + `.wslconfig`; Ubuntu 22.04+ or Pop!_OS for Nvidia; NVIDIA driver 570.133.07+ (RTX 5070), amdgpu (Vega56); Wake-on-LAN UDP port 9/7; optional: Raspberry Pi + 5V relay, FastAPI relay server, Tailscale/WireGuard.

---

## Research Summary (Concrete)

### Wake-on-LAN (WoL) and Remote Power-On

- **Magic packet:** UDP, usually port 9 or 7; payload = 6×0xFF + target MAC repeated 16 times. Layer-2 (MAC), not IP. NIC must stay powered in S3/S4/S5 for WoL; many boards cut PCIe power in S5 unless ErP is disabled.
- **From internet:** You cannot broadcast to a private LAN from WAN. Options:
  1. **Port forward** UDP 9 (or 7) to target IP: requires static IP or Dynamic DNS; router must deliver packet to host (some routers block directed broadcast to `192.168.x.255`). Security risk: anyone who can reach that port can wake the PC; use a high random port and/or source-IP allow list.
  2. **Always-on relay (recommended):** A device on the LAN (Raspberry Pi, NAS, small server) runs a small service that accepts an authenticated request (e.g. HMAC-signed POST) and sends the magic packet locally. Expose relay via VPN (WireGuard, Tailscale) or reverse tunnel (Cloudflare Tunnel, Tailscale Funnel)—do not expose WoL port directly.
  3. **S5 (full power-off) WoL:** Not guaranteed on all hardware. Windows Fast Startup (hybrid shutdown) must be disabled. BIOS: enable “Wake on LAN from S4/S5” or “Resume by LAN”; disable ErP/EuP so PCIe/NIC keep standby power. Some Dell systems will not WoL with Deep Sleep set to S5—check vendor docs.
- **Concrete OS/BIOS steps:** BIOS: ErP/Deep Sleep off; “Resume by PCI-E/Networking” or “Wake on LAN” on. Windows: Device Manager → NIC → Power Management → “Allow this device to wake the computer,” “Only allow a magic packet”; Advanced → “Wake on Magic Packet” on; disable “Energy Efficient Ethernet” if it prevents wake. Power Options → disable Fast startup. Linux: `ethtool -s eth0 wol g`; persist via NetworkManager or systemd.
- **Sending from anywhere:** Phone apps (e.g. WolOn, AwakeOnLANMobile); cloud: run a small relay on the LAN and call it via VPN or webhook (e.g. Tailscale + UpSnap, or custom FastAPI with HMAC). Retry: send 2–3 magic packets 250–500 ms apart.

**Sources:** thelinuxcode.com (2026 WoL guide), Intel/Dell/MS WoL docs, Tailscale UpSnap blog, F-Droid AwakeOnLANMobile, WolOn app.

### GPIO / Relay: Hardware Remote Power-On

- **Principle:** Short the same two pins the PC’s front-panel power button uses (momentary contact); polarity does not matter. No direct GPIO-to-motherboard connection: use a relay or optocoupler for isolation.
- **Hardware:** Raspberry Pi (or any SBC with GPIO) + 5V relay module. Relay common (COM) and normally open (NO) in series with the two power-switch pins on the motherboard front-panel header (often labeled PWR_SW or similar; consult motherboard manual). One pulse (e.g. 0.5–1 s) = power toggle; for “power on” only, rely on BIOS “Power On After AC Loss” or “Restore on AC/Power Loss” so that applying power (or a pulse) boots the PC.
- **Software:** On the Pi, trigger a GPIO pin (e.g. GPIO 4) via SSH or a small HTTP API (e.g. Flask/FastAPI with auth). Example: `gpio -g mode 4 out; gpio -g write 4 0; sleep 1; gpio -g write 4 1`. Access the Pi over VPN or Tailscale so the relay is not exposed to the internet.
- **When to use:** WoL fails (e.g. S5 not supported, or NIC not powered); or you want a single “cold boot” method that does not depend on NIC firmware.

**Sources:** Raspberry Pi relay + front-panel power switch (hjr265.me, RPi forums, Jeff Geerling); ATX front-panel pinouts (ifixit, tech4gamers).

### Talon Debloater (Windows 11)

- **Talon:** Full debloat for **fresh** Windows 11 Home/Pro only. Removes bloatware, telemetry, optional AI; can remove Edge (reinstall possible). Not for in-use or Windows 10—risk of app failure or corruption.
- **Talon Lite:** For **in-use** Windows 10/11; lighter, safer on existing systems.
- **Usage:** Download from debloat.win or GitHub (ravendevteam/talon). Run the executable; “two clicks” to complete. Version 1.2.0 (March 2024) current. License: BSD-3-Clause. Caveat: script may set IPv4-over-IPv6 preference; can affect IPv6-only or dual-stack users.

### Windows 11 → Linux Migration (Reality)

- **No automated Win→Linux migration tool.** Microsoft USMT and Windows Backup are Windows-to-Windows only. Migration is manual: app list (Settings → Apps), data backup (files, configs), then replace with Linux equivalents (Snapcraft, Flathub, Wine/Bottles, appdb.winehq.org).
- **Export:** Custom PowerShell to dump installed apps (Get-AppxPackage, Win32 products), WSL distros, user paths → JSON manifest. No secrets; no binary copy of data in the manifest.

### WSL2 and GPUs (Concrete)

- **`.wslconfig`** path: `C:\Users\<username>\.wslconfig`. After edit, run `wsl --list --running` then `wsl --shutdown`; wait ~8 s before starting WSL again. Options: `processors = 8`, `memory = 16GB` (or as needed), `gpuSupport = true`. Default `processors = 0` = all cores; `memory = 0` = 50% of RAM.
- **Nvidia in WSL2:** Use Windows NVIDIA driver; WSL2 gets GPU via that. RTX 5070: on Linux bare metal use driver 570.133.07+ (e.g. Ubuntu 22.04+, Linux Mint 22); 50xx needs open-source/gsp firmware and kernel 6.6+ on some distros.
- **AMD Vega56:** Standard amdgpu driver on Linux; no special version called out for this plan.

---

## Phase 0: Remote Wake (WoL + GPIO) — Concrete Implementation

### Task 0.1: Document WoL and GPIO Remote Wake (Research + Steps)

**Files:**
- Create: `docs/plans/research/Remote-Wake-WoL-and-GPIO.md`

**Content (concrete):**

1. **WoL checklist**
   - BIOS: disable ErP/EuP; enable Wake on LAN / Resume by LAN / PME; if available, enable WoL from S5.
   - Windows: NIC Power Management → allow wake, magic packet only; disable Fast Startup; NIC Advanced → Wake on Magic Packet on, Energy Efficient Ethernet off.
   - Linux: `ethtool -s eth0 wol g`; make persistent.
   - Get MAC: `ipconfig /all` (Windows), `ip link` (Linux).

2. **WoL from internet — two options**
   - **Option A — Port forward:** Static IP or DDNS; forward UDP 9 (or high random port) to target PC’s static LAN IP. Send magic packet to WAN IP. Security: restrict source IP if possible; prefer not to expose port 9 directly.
   - **Option B — Relay (recommended):** Always-on device on LAN runs WoL relay (see Task 0.2). From anywhere: connect via VPN (Tailscale/WireGuard) or authenticated webhook to relay; relay sends magic packet on LAN. No WoL port exposed to internet.

3. **GPIO/relay option**
   - Hardware: Raspberry Pi + 5V relay. Relay contacts in series with motherboard front-panel power-switch pins (consult motherboard manual for PWR_SW).
   - BIOS: set “Power On After AC Loss” or “Restore on AC/Power Loss” to “Power On” so one pulse can start the PC.
   - Pi: expose a small HTTP endpoint (with auth) or SSH; on request, pulse GPIO to close relay 0.5–1 s. Access Pi via VPN/Tailscale only.

4. **Sending magic packets**
   - Local: Python/Node script (6×0xFF + MAC×16, UDP to 255.255.255.255:9).
   - Remote: WolOn / AwakeOnLANMobile to WAN IP (if port forward) or to relay URL over VPN; or custom client calling relay API.

**Step 2: Commit**

```bash
git add docs/plans/research/Remote-Wake-WoL-and-GPIO.md
git commit -m "docs: add concrete WoL and GPIO remote wake research and steps"
```

---

### Task 0.2: WoL Relay Server (Optional — For Secure Remote Wake)

**Files:**
- Create: `library/remote-wake/wol-relay/README.md`
- Create: `library/remote-wake/wol-relay/relay_server.py` (FastAPI: POST /wake with mac + HMAC token; send magic packet on LAN)
- Create: `library/remote-wake/wol-relay/requirements.txt` (fastapi, uvicorn, pydantic)

**Implementation (concrete):**

- **relay_server.py:**  
  - Read MAC and optional broadcast IP from env or config.  
  - POST body: `{"mac": "AA:BB:CC:DD:EE:FF", "token": "<hmac_sha256(mac, SECRET)>"}`.  
  - If token valid, build magic packet (6×0xFF + MAC bytes×16), send UDP to broadcast (e.g. 255.255.255.255:9). Return 200. Else 403.  
  - No SECRET in repo; use env var.

- **README.md:** How to run (e.g. `uvicorn relay_server:app --host 0.0.0.0 --port 9090`), set SECRET, run on Pi or always-on host; expose via Tailscale or reverse tunnel, not raw port to internet.

**Step 2: Commit**

```bash
git add library/remote-wake/wol-relay/
git commit -m "feat: add WoL relay server for secure remote wake"
```

---

### Task 0.3: GPIO Relay Wiring and Script (Optional)

**Files:**
- Create: `docs/plans/research/GPIO-Relay-Power-On.md`
- Create: `library/remote-wake/gpio-relay/power_pulse.sh` (example: pulse GPIO 4 for 1 s on Raspberry Pi, using `gpio` or Python RPi.GPIO)

**Content (concrete):**

- **GPIO-Relay-Power-On.md:** Diagram or list: Pi GPIO 4 → relay input; relay COM/NO in series with motherboard PWR_SW pins; BIOS “Power On After AC Loss” = On. Warning: isolate Pi from motherboard (relay only); do not connect Pi GND to PC.
- **power_pulse.sh:** Detect platform; if Pi, set GPIO 4 output, drive low 1 s, drive high; exit. Document dependency (wiringpi or python3-rpi.gpio). Call from cron or small HTTP server with auth for “remote” trigger.

**Step 2: Commit**

```bash
git add docs/plans/research/GPIO-Relay-Power-On.md library/remote-wake/gpio-relay/
git commit -m "docs and script: GPIO relay power-on wiring and pulse example"
```

---

## Phase 1: Talon Debloater (Windows 11)

### Task 1: Document Talon Usage and Boundaries (Concrete)

**Files:**
- Create: `docs/plans/research/Talon-Debloater-Notes.md`

**Content:** Talon = fresh Windows 11 only; Talon Lite = in-use Win10/11. Download: debloat.win or GitHub ravendevteam/talon; version 1.2.0 (March 2024). Steps: run executable, two clicks. Warnings: IPv4-over-IPv6; full Talon on in-use system can cause corruption. License: BSD-3-Clause. No automation from this repo; user runs manually after restore point.

**Step 2: Commit**

```bash
git add docs/plans/research/Talon-Debloater-Notes.md
git commit -m "docs: add Talon Debloater research notes (concrete)"
```

---

### Task 2: Windows Debloat Library and Talon Lite Usage

**Files:**
- Create: `library/windows-debloat/README.md`
- Create: `library/windows-debloat/talon-lite-usage.md`

**Content:** README: this folder is research only; no bundled binaries; user downloads from official source. Talon Lite: create restore point; download from debloat.win; verify hash if published; run; document optional revert steps if available.

**Step 2: Commit**

```bash
git add library/windows-debloat/README.md library/windows-debloat/talon-lite-usage.md
git commit -m "docs: Windows debloat library and Talon Lite usage"
```

---

## Phase 2: Capture Windows 11 State (Concrete)

### Task 3: State Export Spec and Schema

**Files:**
- Create: `docs/plans/state-export-spec.md`
- Create: `library/windows-to-linux/windows-state-manifest-schema.json`

**Content:** Spec: inventory (Get-AppxPackage, Get-WmiObject Win32_Product or PackageManagement; wsl -l -v); user paths (Documents, Desktop, AppData key paths); no secrets. Output: JSON. Schema: `schemaVersion`, `osVersion`, `apps` (name, version, type), `wslDistros`, `userPaths` (list of folder paths).

**Step 2: Commit**

```bash
git add docs/plans/state-export-spec.md library/windows-to-linux/windows-state-manifest-schema.json
git commit -m "docs: state export spec and JSON schema"
```

---

### Task 4: PowerShell State Export Script (Runnable)

**Files:**
- Create: `library/windows-to-linux/Export-WindowsState.ps1`
- Create: `library/windows-to-linux/README.md`

**Implementation:** Script accepts `-OutPath` (default `.\windows-state-manifest.json`). Collect: `Get-AppxPackage | Select Name, Version`; Win32_Product or winget list; `wsl -l -v` output; `$env:USERPROFILE\Documents`, `Desktop`, `AppData\Roaming` paths; `[Environment]::OSVersion`. Write JSON matching schema. README: run with `powershell -ExecutionPolicy Bypass -File Export-WindowsState.ps1 -OutPath .\manifest.json`; no secrets; run explicitly by user.

**Step 2: Commit**

```bash
git add library/windows-to-linux/Export-WindowsState.ps1 library/windows-to-linux/README.md
git commit -m "feat: PowerShell Windows state export script"
```

---

## Phase 3: Transfer to Linux (Concrete)

### Task 5: Linux Equivalents and Manifest Mapping

**Files:**
- Create: `docs/plans/linux-equivalents.md`
- Modify: `library/WINDOWS_TO_LINUX_MIGRATION_GUIDE.md` (add reference to manifest and this plan)

**Content:** Table: Windows app or role → Linux package (apt/snap/flatpak) or Wine/Bottles note. Map manifest `apps[].name` patterns to install commands (e.g. “Visual Studio Code” → `sudo snap install code` or flatpak). Reference existing WINDOWS_TO_LINUX_MIGRATION_GUIDE for distro choice and hardware.

**Step 2: Commit**

```bash
git add docs/plans/linux-equivalents.md library/WINDOWS_TO_LINUX_MIGRATION_GUIDE.md
git commit -m "docs: Linux equivalents and manifest-to-install mapping"
```

---

### Task 6: Linux Import Script (Parse Manifest, Dry-Run Install List)

**Files:**
- Create: `library/windows-to-linux/import-on-linux.sh`

**Implementation:** Accept path to `windows-state-manifest.json` or stdin. Parse JSON (jq); print “would install” list from linux-equivalents mapping. Optional `--apply` flag: document that it may run apt/snap (implementation optional); by default dry-run only. Header comment: target Ubuntu/Debian or Pop!_OS; Nvidia 570.133.07+ and amdgpu are separate steps.

**Step 2: Commit**

```bash
git add library/windows-to-linux/import-on-linux.sh
git commit -m "feat: Linux import script (manifest parse, dry-run)"
```

---

## Phase 4: Background Linux (8 Cores, Nvidia 5070, Vega56) — Concrete

### Task 7: Resource and GPU Layout (Concrete)

**Files:**
- Create: `docs/plans/background-linux-resources.md`

**Content:**

- **CPU:** 8 cores: WSL2 `processors = 8` in `.wslconfig`; or VM give 8 vCPUs; or bare metal dedicate all 8 to Linux.
- **Nvidia RTX 5070:** WSL2: use Windows NVIDIA driver + WSL2; Linux bare metal: driver 570.133.07+ (Ubuntu 22.04+, kernel 6.6+; GSP firmware). VM: single GPU passthrough (VFIO) to one OS at a time unless SR-IOV.
- **AMD Vega56:** amdgpu; use for host display or for Linux when Nvidia is passed through to guest.
- **Background:** Headless + SSH recommended; or WSL2 default distro start at login; document `.wslconfig` path and `wsl --shutdown` after edits.

**Step 2: Commit**

```bash
git add docs/plans/background-linux-resources.md
git commit -m "docs: background Linux resources and GPU (concrete)"
```

---

### Task 8: WSL2 and VM/Dual-Boot Options (Concrete)

**Files:**
- Create: `library/windows-to-linux/background-linux-options.md`
- Create: `library/windows-to-linux/wslconfig-example.txt`

**Content:** Options: (1) WSL2 with `.wslconfig`: paste example `[wsl2]\nprocessors=8\nmemory=16GB\ngpuSupport=true`; path `C:\Users\<user>\.wslconfig`; `wsl --shutdown` then start distro; start at boot via Task Scheduler or `wsl -d <distro>`. (2) VM: Hyper-V or QEMU/KVM; 8 vCPU, 16GB, disk; SSH for headless. (3) Dual boot: GRUB default; “background” = boot Linux and run services. Decision table: “Windows + Linux same time” → WSL2; “Isolated Linux, GPU” → VM or dual boot.

**Step 2: Commit**

```bash
git add library/windows-to-linux/background-linux-options.md library/windows-to-linux/wslconfig-example.txt
git commit -m "docs: WSL2/VM/dual-boot options and .wslconfig example"
```

---

### Task 9: Start Linux in Background Script (Concrete)

**Files:**
- Create: `library/windows-to-linux/start-linux-background.ps1`

**Implementation:** Set `$distro` (e.g. Ubuntu); run `wsl -d $distro -- bash -c "echo Linux is up; exit 0"`; optional: ensure default distro. Comment: adjust `$distro`; for “always on” background, WSL2 stays running after first launch; optional Task Scheduler entry to run at logon.

**Step 2: Commit**

```bash
git add library/windows-to-linux/start-linux-background.ps1
git commit -m "feat: start WSL2 Linux in background (concrete script)"
```

---

## Summary Checklist (Concrete)

| # | Task | Deliverable |
|---|------|-------------|
| 0.1 | WoL + GPIO remote wake doc | `docs/plans/research/Remote-Wake-WoL-and-GPIO.md` |
| 0.2 | WoL relay server (optional) | `library/remote-wake/wol-relay/` (README, relay_server.py, requirements.txt) |
| 0.3 | GPIO relay wiring + pulse script | `docs/plans/research/GPIO-Relay-Power-On.md`, `library/remote-wake/gpio-relay/power_pulse.sh` |
| 1 | Talon notes (concrete) | `docs/plans/research/Talon-Debloater-Notes.md` |
| 2 | Windows debloat library | `library/windows-debloat/README.md`, `talon-lite-usage.md` |
| 3 | State export spec + schema | `docs/plans/state-export-spec.md`, `windows-state-manifest-schema.json` |
| 4 | PowerShell export script | `Export-WindowsState.ps1`, README |
| 5 | Linux equivalents + mapping | `linux-equivalents.md`, update WINDOWS_TO_LINUX_MIGRATION_GUIDE |
| 6 | Linux import script | `import-on-linux.sh` |
| 7 | Resource and GPU layout | `docs/plans/background-linux-resources.md` |
| 8 | WSL2/VM/dual-boot + .wslconfig | `background-linux-options.md`, `wslconfig-example.txt` |
| 9 | Start Linux background script | `start-linux-background.ps1` |

---

## Execution Handoff

Plan complete and saved to `docs/plans/2025-02-23-Windows11-to-Linux-Transfer-and-Background-Linux.md`.

**Two execution options:**

1. **Subagent-Driven (this session)** — One subagent per task, review between tasks.
2. **Parallel Session** — New session with **executing-plans**, batch with checkpoints.

If **Subagent-Driven:** use **superpowers:subagent-driven-development**.  
If **Parallel Session:** use **superpowers:executing-plans** in the new session.

**Which approach?**
