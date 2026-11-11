# Registers a Task Scheduler task that runs `thunderbot tick` at 15:10 and 15:20 on weekdays (local time;
# keep Windows on India time). Edit these two paths, then run this script once in PowerShell.
$Worker = 'C:\thunderbot\worker'                              # the folder that holds .env
$Exe    = 'C:\thunderbot\worker\.venv\Scripts\thunderbot.exe'

$days    = 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'
$action  = New-ScheduledTaskAction -Execute $Exe -Argument 'tick' -WorkingDirectory $Worker
$first   = New-ScheduledTaskTrigger -Weekly -DaysOfWeek $days -At '15:10'
$second  = New-ScheduledTaskTrigger -Weekly -DaysOfWeek $days -At '15:20'   # a no-op when the first run worked
# Wake the laptop for the task, run it as soon as possible if the time was missed, and do not skip it on battery.
$settings = New-ScheduledTaskSettingsSet -WakeToRun -StartWhenAvailable -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries -RunOnlyIfNetworkAvailable -ExecutionTimeLimit (New-TimeSpan -Minutes 10)
Register-ScheduledTask -TaskPath '\Thunderbot\' -TaskName 'Tick' -Action $action -Trigger $first, $second `
    -Settings $settings -Description 'Thunderbot daily investing check' -Force
