# Set console output encoding
[Console]::OutputEncoding = [Text.Encoding]::UTF8
Set-PowerCLIConfiguration -Scope User -ParticipateInCEIP $false -Confirm:$false -ErrorAction SilentlyContinue
# This script is used to create VMs in bulk based on information defined in a CSV file
$vc = "192.168.1.100"
$user = "administrator@vsphere.local"
$password = ""
$vm_file = "D:\DeployVM.csv"
$Gateway = "192.168.1.1"
Connect-VIServer -Server $vc -username $user -Password $password

# Disconnect-VIServer -Server $vc

$vms = Import-Csv $vm_file
$vms.Count
# $vms

foreach ($vm in $vms)
{
    # Select host, template, customization specification, VM storage location, VLAN, CPU, memory, description, IP, subnet mask, gateway, VM name
    $vmhost = $vm.Host
    $template = $vm.Template
    $custsysprep = $vm.Rule

    $datastore = $vm.Datastore
    $network = $vm.Vlan
    $cpu = $vm.CPU
    $memory = $vm.Memory
    $Notes = $vm.Description
    $IP = $vm.IP
    $vmname_IP = (($ip -Split '\.')[(-1)])
    $NetMask = "255.255.255.0"
    
    # Configure DNS information
    [array]$DNSs = "223.5.5.5", "223.6.6.6"

    # VM name concatenated with IP information
    $vmname = "$($vm.Name)_IP$vmname_IP"
    # If the CSV provides a computer name, set it
    if ($vm.ComputerName.Length -gt 0)
    {
        Get-OSCustomizationSpec $custsysprep | Set-OSCustomizationSpec -NamingScheme fixed -NamingPrefix $vm.ComputerName
    }
    # Write IP information into the customization specification, DNS does not need to be changed
    if ((Get-OSCustomizationSpec $custsysprep).OSType -eq "Linux")
    {
        Get-OSCustomizationSpec $custsysprep | Get-OSCustomizationNicMapping | Set-OSCustomizationNicMapping -IpMode UseStaticIP -IpAddress $IP -SubnetMask $NetMask -DefaultGateway $Gateway
    }
    else
    {
        Get-OSCustomizationSpec $custsysprep | Get-OSCustomizationNicMapping | Set-OSCustomizationNicMapping -IpMode UseStaticIP -IpAddress $IP -SubnetMask $NetMask -DefaultGateway $Gateway -Dns $DNSs
    }

    # Create a new VM using the template and customization specification to configure IP, VM MAC will be regenerated
    New-VM -Name $vmname -VMHost $vmhost -Network $network -Template $template -OSCustomizationSpec $custsysprep -Datastore $datastore

    # If there is an error when copying the template, wait for the copy to complete before executing subsequent commands
    if ((Get-OSCustomizationSpec $custsysprep).OSType -eq "Linux")
    {
        Start-Sleep -Seconds 60
    }
    else
    {
        Start-Sleep -Seconds 120
    }
    # Set VM hardware version compatibility
    Get-VM -Name $vmname | Set-VM -HardwareVersion vmx-18 -Confirm:$false
    # Set VM to reference the customization specification file
    Get-VM -Name $vmname | Set-VM -OSCustomizationSpec $custsysprep -Confirm:$false
    # Set VM CPU, memory, and description
    Get-VM -Name $vmname | Set-VM -NumCPU $cpu -MemoryGB $memory -Notes $Notes -Confirm:$false
    # Set VM network
    Get-VM -Name $vmname | Get-NetworkAdapter | Set-NetworkAdapter -NetworkName $network -Confirm:$false
    # Set CD drive
    Get-VM -Name $vmname | Get-CDDrive | Set-CDDrive -NoMedia -Confirm:$false
    # Enable network adapter
    Get-VM -Name $vmname | Get-NetworkAdapter | Set-NetworkAdapter -StartConnected $true -Confirm:$false
    # Assume "DiskCapacityGB" column contains the capacity of the new disk to be added
    if ($vm.DiskCapacityGB -gt 0)
    {
        $capacityGB = $vm.DiskCapacityGB
        Get-VM -Name $vmname | New-HardDisk -CapacityGB $capacityGB -Confirm:$false
    }
    # Start VM
    Get-VM -Name $vmname | Start-VM
}