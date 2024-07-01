param(
    [string]$Path = "$env:USERPROFILE\AppData"
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

# Verifica se a variável $Path está definida, caso contrário, define o caminho padrão para AppData
if (-not $Path) {
    $Path = "$env:USERPROFILE\AppData"
}

# Obtém o objeto de segurança da pasta
$acl = Get-Acl $Path

# Cria uma regra de controle de acesso para conceder permissões totais a "Everyone"
$rule = New-Object System.Security.AccessControl.FileSystemAccessRule("Everyone", "FullControl", "ContainerInherit, ObjectInherit", "None", "Allow")

# Adiciona a regra ao objeto de segurança
$acl.SetAccessRule($rule)

# Aplica as novas permissões à pasta
Set-Acl $Path $acl

Write-Output "Permissões alteradas com sucesso para: $Path"
