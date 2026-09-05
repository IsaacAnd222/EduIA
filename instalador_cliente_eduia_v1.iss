#define MyAppName "EduIA"
#define MyAppVersion "1.8.0"
#define MyAppPublisher "Isaac Andrade Quiroz"
#define MyAppExeName "EduIA.exe"

[Setup]
AppId={{67A8E287-B324-46E3-9B4F-FC37717935D1}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={localappdata}\Programs\EduIA
DefaultGroupName=EduIA
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
OutputDir=installer
OutputBaseFilename=EduIA_Cliente_Setup_v1.8.0
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
Source: "dist\EduIA\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\EduIA"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\EduIA"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Iniciar EduIA"; Flags: nowait postinstall skipifsilent
