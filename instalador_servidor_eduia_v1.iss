#define MyAppName "Servidor EduIA"
#define MyAppVersion "1.8.0"
#define MyAppPublisher "Isaac Andrade Quiroz"
#define MyAppExeName "ServidorEduIA.exe"
#define MyFirewallRule "Servidor EduIA - Puerto 8765"

[Setup]
AppId={{15764872-1E37-412D-B19B-C058C903240B}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\Servidor EduIA
DefaultGroupName=Servidor EduIA
DisableProgramGroupPage=yes
PrivilegesRequired=admin
OutputDir=installer
OutputBaseFilename=EduIA_Servidor_Setup_v1.8.0
SetupIconFile=assets\icono_eduia.ico
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
UninstallDisplayIcon={app}\{#MyAppExeName}
CloseApplications=yes

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; Description: "Crear un acceso directo en el escritorio"; GroupDescription: "Accesos directos:"; Flags: unchecked

[Files]
Source: "dist\ServidorEduIA\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Servidor EduIA"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\Servidor EduIA"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{sys}\netsh.exe"; Parameters: "advfirewall firewall delete rule name=""{#MyFirewallRule}"""; Flags: runhidden
Filename: "{sys}\netsh.exe"; Parameters: "advfirewall firewall add rule name=""{#MyFirewallRule}"" dir=in action=allow protocol=TCP localport=8765 program=""{app}\{#MyAppExeName}"" profile=private enable=yes"; Flags: runhidden
Filename: "{app}\{#MyAppExeName}"; Description: "Iniciar el servidor de EduIA"; Flags: nowait postinstall skipifsilent

[UninstallRun]
Filename: "{sys}\netsh.exe"; Parameters: "advfirewall firewall delete rule name=""{#MyFirewallRule}"""; Flags: runhidden; RunOnceId: "EliminarReglaFirewallEduIA"
