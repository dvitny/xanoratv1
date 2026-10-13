# Discord-Based RAT — Malware Research

## Overview

This project documents the analysis of a **Python-based Remote Access Trojan (RAT)** targeting Windows systems.

The RAT uses Discord as its **Command & Control (C2)** communication channel, allowing a remote operator to send commands and receive information through a Discord server.

The analyzed implementation combines remote system administration, surveillance, data collection, file transfer, privilege escalation attempts, and persistence mechanisms.

> **Disclaimer:** This repository is intended for cybersecurity research, malware analysis, and educational purposes. Testing should only be performed in isolated environments or on systems with explicit authorization.

## How It Works

The RAT communicates with Discord using the `discord.py` library.

When connected, it identifies the host computer, searches for or creates a Discord category named after its hostname, and uses a `session` text channel for command communication.

Commands received through the designated channel are processed locally, and results can be returned as Discord messages or file attachments.

The implementation primarily targets Windows and relies on Windows-specific APIs, PowerShell, registry operations, and system utilities.

## Features & Capabilities

### Remote Command Execution
- `!cmd` — Execute PowerShell commands remotely.
- `!cd` — Change the working directory.
- `!dir` — Display the current working directory.

### System Information
- `!getip` — Retrieve the host's resolved IP address.
- `!getinfo` — Collect hostname, IP address, username, and working directory.
- `!admincheck` — Check whether the process has administrator privileges.

### Screen & Camera Surveillance
- `!screenshot` / `!ss` — Capture a screenshot.
- `!screenrecord` — Send a sequence of ten screenshots.
- `!getcams` — Enumerate available cameras.
- `!setcam` — Select a camera.
- `!capture` — Capture and upload an image from the selected camera.
- `!windowstart` / `!windowstop` — Start or stop reporting the foreground window title through Discord presence.

### Data Collection
- `!clipboard` — Retrieve clipboard contents.
- `!history` — Collect browser history.
- `!startkeylogger` — Start capturing keyboard input.
- `!stopkeylogger` — Attempt to stop keyboard monitoring.
- `!dumpkeylogger` — Upload collected keystroke logs.
- `!micstart` — Record microphone audio and upload the resulting WAV file.

### File Transfer
- `!download` — Transfer a file from the target computer to Discord.
- `!upload` — Save a Discord attachment to the target computer.

### Remote Desktop Interaction
- `!text` — Display a Windows message box.
- `!voice` — Convert text to speech.
- `!wallpaper` — Change the desktop wallpaper.
- `!website` — Open a URL in the default browser.
- `!volume` — Set the system volume.
- `!volumemax` — Set the volume to 100%.
- `!volumezero` — Mute system output by setting volume to zero.
- `!sing` / `!stopsing` — Open media and attempt to control its playback process.

### System Control
- `!logout` — Log out the current user.
- `!shutdown` — Shut down Windows.
- `!restart` — Restart Windows.
- `!BSOD` — Request a forced restart.
- `!blockinput` / `!unblockinput` — Attempt to block or restore keyboard and mouse input.
- `!disabletaskmgr` / `!enabletaskmgr` — Change registry policies affecting Task Manager availability.

### Privileges & Persistence
- `!tryadmin` — Attempt elevation through a Windows UAC prompt.
- `!uacbypass` — Contains an attempted UAC bypass involving registry modifications and `fodhelper.exe`.
- `!taskschedule` — Attempt to create a Windows scheduled task for execution at logon.
- `!delete` — Attempt to terminate and remove the scheduled task.

The source additionally defines functions for Startup-folder persistence using a VBS launcher and `pythonw.exe`.

## Technical Details

| Component | Implementation |
|---|---|
| Programming language | Python |
| Target operating system | Windows |
| C2 communication | Discord API |
| Command execution | PowerShell |
| Screenshots | Pillow |
| Camera access | OpenCV |
| Audio recording | SoundDevice / SciPy |
| Keyboard monitoring | pynput |
| Browser history | browserhistory |
| Windows interaction | ctypes / pywin32 |
| Audio output control | pycaw |
| Persistence mechanisms | Windows Task Scheduler / Startup-folder code |
| Privilege escalation attempts | UAC elevation / fodhelper technique |

## Important Analysis Findings

Static analysis revealed several limitations and potentially unreliable behaviors.

1. **Keylogger shutdown:** The stop command changes a thread attribute, but the keyboard listener does not check that attribute. Therefore, monitoring may continue.
2. **Screen recording:** The feature sends individual screenshots rather than generating a video file. The loop also lacks a one-second delay.
3. **Microphone recording:** The configured duration is 180 seconds, although the built-in help message describes two minutes.
4. **BSOD command:** The implementation invokes a shutdown command and does not directly trigger a Windows bug check.
5. **Persistence:** Scheduled-task creation may be unreliable because of path, permission, and elevation requirements.
6. **Startup behavior:** Startup-folder persistence functions exist in the source, but no invocation of those functions was identified.
7. **UAC bypass:** The presence of a bypass routine does not establish that it works on supported Windows versions.
8. **Access control:** The bot filters messages by channel and ignores bot authors, but does not implement an explicit authorized-user allowlist.

These observations are based on source-code analysis, not verified execution in a sandbox.

## Security Risks

The RAT presents several significant security concerns:

- Unauthorized remote command execution.
- Exposure of private files and clipboard contents.
- Collection of keyboard input, potentially including credentials.
- Access to the camera and microphone.
- Browser activity monitoring.
- Remote modification of system settings.
- Attempts to establish persistence after user logon.
- Possible privilege escalation.
- Potential exfiltration of sensitive information through Discord.

Because of these capabilities, the sample should be considered **high-risk** when executed outside a controlled research environment.

## Research Scope

This documentation is based on static analysis of the provided Python source code.

It describes the commands and behaviors present in the implementation. It does not guarantee that every feature is operational, compatible with current Windows versions, or capable of evading endpoint protection.

Dynamic analysis, network traffic inspection, persistence verification, and detection engineering would be necessary to validate its behavior further.

## Intended Use

This analysis is intended for:

- Malware reverse engineering
- Cybersecurity education
- Threat modeling
- C2 communication analysis
- Windows persistence research
- Defensive detection development

**Only analyze or execute the sample in an authorized, isolated test environment.**