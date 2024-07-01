$tempPath = "$env:USERPROFILE\AppData\Local\Temp"
$acl = Get-Acl $tempPath
$rule = New-Object System.Security.AccessControl.FileSystemAccessRule("Users","FullControl","ContainerInherit,ObjectInherit","None","Allow")
$acl.SetAccessRule($rule)
Set-Acl $tempPath $acl