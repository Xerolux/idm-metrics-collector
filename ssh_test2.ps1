$password = "sebi2634"
$server = "192.168.178.52"

try {
    # Try using a different method - SSH via WSL or other tools
    $output = cmd /c "echo $password | ssh -o StrictHostKeyChecking=no root@${server} 'docker ps -a'" 2>&1
    Write-Output $output
} catch {
    Write-Output "Error: $_"
}