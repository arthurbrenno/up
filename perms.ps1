$tempPath = "$env:USERPROFILE\AppData\Local\Temp"
$acl = Get-Acl $tempPath
$usersSID = New-Object System.Security.Principal.SecurityIdentifier("S-1-5-32-545")
$rule = New-Object System.Security.AccessControl.FileSystemAccessRule($usersSID,"FullControl","ContainerInherit,ObjectInherit","None","Allow")
$acl.SetAccessRule($rule)
Set-Acl $tempPath $acl