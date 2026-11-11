# Running the daily check from a laptop

`thunderbot tick` does one pass and exits: it writes a heartbeat, makes the 15:10 IST decision if it is
due and not yet made today, and runs any backtests queued from the dashboard. Schedule it twice a day
(15:10 and 15:20 IST) and the second run is a harmless no-op when the first one worked.

With `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` in `worker/.env`, the laptop shares its state with the
dashboard and with the cloud schedulers, and the run lock in Supabase makes sure only one of them acts on
a given day. Without them it keeps a local journal in `TB_DATA_DIR`.

All three schedulers use the computer's local clock. Keep the laptop on India time, or change the times.

| System | File | Wakes a sleeping laptop? | Catches up a missed run? |
|---|---|---|---|
| Windows 10/11 | `windows-task.ps1` | Usually on mains power; often not on battery or with the lid shut (Modern Standby) | Yes, when the laptop next wakes |
| macOS | `com.thunderbot.tick.plist` | Only with `pmset repeat` (below), and not reliably with the lid shut | Yes after sleep; no after a shutdown |
| Linux | `thunderbot-tick.service` + `.timer` | Only as a system timer with `WakeSystem=true`, hardware permitting | Yes (`Persistent=true`) |

A catch-up can start hours late. That is safe: a paper run that starts after the close uses closing prices
and says so; a live run that starts after 15:25 IST refuses to trade and tries again the next trading day.

## Windows

```powershell
# In PowerShell, from this folder. Edit the two paths at the top of the script first.
powershell -ExecutionPolicy Bypass -File .\windows-task.ps1
# Let scheduled tasks wake the laptop (run as administrator):
powercfg /setacvalueindex SCHEME_CURRENT SUB_SLEEP RTCWAKE 1
powercfg /setdcvalueindex SCHEME_CURRENT SUB_SLEEP RTCWAKE 1
powercfg /setactive SCHEME_CURRENT
Start-ScheduledTask -TaskPath '\Thunderbot\' -TaskName 'Tick'    # run once now to test
```

## macOS

```bash
# Edit the paths in the plist first, then:
cp com.thunderbot.tick.plist ~/Library/LaunchAgents/
launchctl bootstrap gui/$UID ~/Library/LaunchAgents/com.thunderbot.tick.plist
launchctl kickstart -k gui/$UID/com.thunderbot.tick      # run once now to test
sudo pmset repeat wakeorpoweron MTWRF 15:05:00           # wake the Mac five minutes early
```

## Linux

```bash
# Edit the paths in the service file first, then:
mkdir -p ~/.config/systemd/user && cp thunderbot-tick.service thunderbot-tick.timer ~/.config/systemd/user/
systemctl --user daemon-reload && systemctl --user enable --now thunderbot-tick.timer
loginctl enable-linger "$USER"                           # run even when you are not logged in
systemctl --user start thunderbot-tick.service && journalctl --user -u thunderbot-tick -n 20
```

## Live orders from a laptop

Brokers accept API orders only from the static IP registered to your account. A laptop meets that rule
only on a broadband connection with a static public IP that you have registered with Groww. Set
`TB_EXPECTED_STATIC_IP` and `TB_LIVE_TRADING_ENABLED=true` in `worker/.env`, and change the scheduled
command to `thunderbot tick --live --i-understand-the-risks`. The command checks the public IP first and
refuses to trade from any other address.
