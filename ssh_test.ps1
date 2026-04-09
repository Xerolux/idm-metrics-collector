$password = "sebi2634"
$server = "192.168.178.52"
$username = "root"

$secpasswd = ConvertTo-SecureString $password -AsPlainText -Force
$credential = New-Object System.Management.Automation.PSCredential($username, $secpasswd)

try {
    # Try to use SSH.NET library if available
    $assemblyPath = Join-Path $env:TEMP "Renci.SshNet.dll"
    if (-not (Test-Path $assemblyPath)) {
        Write-Output "Installing SSH.NET via NuGet..."
        Invoke-WebRequest -Uri "https://www.nuget.org/api/v2/package/SSH.NET/2024.0.0" -OutFile "$env:TEMP\ssh.net.zip"
        Expand-Archive "$env:TEMP\ssh.net.zip" -Force -DestinationPath "$env:TEMP\ssh.net"
        Copy-Item "$env:TEMP\ssh.net\lib\net6.0\Renci.SshNet.dll" -Destination $assemblyPath -Force
    }

    Add-Type -Path $assemblyPath

    $client = New-Object Renci.SshNet.SshClient($server, 22, $username, $password)
    $client.Connect()

    $cmd = $client.RunCommand("docker ps -a")
    Write-Output $cmd.Result

    $client.Disconnect()
} catch {
    Write-Output "Error: $_"
}