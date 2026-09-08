# ProxyGuard: 开机自检系统代理（防止"上次关机没关代理软件"导致开机断网）
# 逻辑：系统代理开关开着但代理端口不通 => 判定为残留状态 => 自动关闭系统代理
# 端口活着(梯子自启了)或本来就关着 => 什么都不做。只在登录瞬间跑约 0.15 秒，零常驻。
# 可选参数 -Port：你代理软件的实际端口（常见 Clash/V2ray 7890，Clash Verge 7897，本用户自由猫 7892）
param([int]$Port = 7892)

$log = "$env:USERPROFILE\.zcode\proxyguard.log"
$reg = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Internet Settings"
try {
    if ((Get-ItemProperty -Path $reg -Name ProxyEnable -ErrorAction Stop).ProxyEnable -ne 1) { exit 0 }

    $alive = $false
    try {
        $c = New-Object System.Net.Sockets.TcpClient
        $ar = $c.BeginConnect("127.0.0.1", $Port, $null, $null)
        $alive = $ar.AsyncWaitHandle.WaitOne(1500) -and $c.Connected
        $c.Close()
    } catch { $alive = $false }

    if ($alive) { exit 0 }

    Set-ItemProperty -Path $reg -Name ProxyEnable -Value 0
    "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] 检测到死代理残留(127.0.0.1:$Port 不通)，已自动关闭系统代理" | Out-File $log -Append -Encoding utf8
} catch {
    "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] 出错: $($_.Exception.Message)" | Out-File $log -Append -Encoding utf8
}
