param(
    [string]$Path
)

# Função para verificar se o script está sendo executado com privilégios elevados
function Test-Admin {
    $currentUser = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
    return $currentUser.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

# Se não estiver sendo executado com privilégios elevados, reinicie como administrador
if (-not (Test-Admin)) {
    Start-Process powershell -ArgumentList "-File `"$PSCommandPath`" -Path `"$Path`"" -Verb RunAs
    exit
}

$acl = Get-Acl $Path
$rule = New-Object System.Security.AccessControl.FileSystemAccessRule("Everyone", "FullControl", "ContainerInherit, ObjectInherit", "None", "Allow")
$acl.SetAccessRule($rule)
Set-Acl $Path $acl
