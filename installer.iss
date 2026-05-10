[Setup]
AppName=AIApp
AppVersion=1.0.0
AppPublisher=AIApp
AppPublisherURL=https://github.com/guythatlivesandcodes/aiapp
DefaultDirName={autopf}\AIApp
DefaultGroupName=AIApp
AllowNoIcons=yes
OutputDir=Output
OutputBaseFilename=AIApp_Setup
SetupIconFile=
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\AIApp.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\AIApp"; Filename: "{app}\AIApp.exe"
Name: "{group}\{cm:UninstallProgram,AIApp}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\AIApp"; Filename: "{app}\AIApp.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\AIApp.exe"; Description: "{cm:LaunchProgram,AIApp}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: dirifempty; Name: "{app}"
