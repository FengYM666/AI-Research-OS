param(
    [string]$Event = "complete"
)

Add-Type -AssemblyName System.Windows.Forms

switch ($Event) {
    "complete" {
        [System.Media.SystemSounds]::Asterisk.Play()
    }
    "notification" {
        [System.Media.SystemSounds]::Exclamation.Play()
    }
    "error" {
        [System.Media.SystemSounds]::Hand.Play()
    }
    default {
        [System.Media.SystemSounds]::Asterisk.Play()
    }
}
