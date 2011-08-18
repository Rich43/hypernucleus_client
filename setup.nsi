;NSIS Modern User Interface
;Basic Example Script
;Written by Joost Verburg
;Modified by Richie Ward

;--------------------------------
;Include Modern UI

  !include "MUI2.nsh"

;--------------------------------
;General
  Name "Hypernucleus"
  OutFile "hypernucleus_10_32.exe"
  InstallDir "$PROGRAMFILES\Hypernucleus"
  InstallDirRegKey HKCU "Software\Hypernucleus" ""
  RequestExecutionLevel admin
  SetCompressor lzma
  
;--------------------------------
;Interface Settings

  !define MUI_ABORTWARNING

;--------------------------------
;Pages

  !insertmacro MUI_PAGE_DIRECTORY
  !insertmacro MUI_PAGE_INSTFILES
  
  !insertmacro MUI_UNPAGE_CONFIRM
  !insertmacro MUI_UNPAGE_INSTFILES
  
;--------------------------------
;Languages
 
  !insertmacro MUI_LANGUAGE "English"

;--------------------------------
;Installer Sections

Section "Install" SecDummy
  SetOutPath "$INSTDIR"
  File /r build\exe.win32-3.2\*.*
  CreateDirectory "$SMPROGRAMS\Hypernucleus"
  CreateShortCut "$SMPROGRAMS\Hypernucleus\Hypernucleus.lnk" "$INSTDIR\run_hypernucleus.exe"
  CreateShortCut "$DESKTOP\Hypernucleus.lnk" "$INSTDIR\run_hypernucleus.exe"
  CreateShortCut "$SMPROGRAMS\Hypernucleus\Uninstall.lnk" "$INSTDIR\Uninstall.exe"
  WriteRegStr HKCU "Software\Hypernucleus" "" $INSTDIR
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Hypernucleus" \
                 "DisplayName" "Hypernucleus Client"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Hypernucleus" \
                 "UninstallString" "$\"$INSTDIR\Uninstall.exe$\""
  WriteUninstaller "$INSTDIR\Uninstall.exe"
SectionEnd

;--------------------------------
;Descriptions

  ;Language strings
  LangString DESC_SecDummy ${LANG_ENGLISH} "A test section."

  ;Assign language strings to sections
  !insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
    !insertmacro MUI_DESCRIPTION_TEXT ${SecDummy} $(DESC_SecDummy)
  !insertmacro MUI_FUNCTION_DESCRIPTION_END

;--------------------------------
;Uninstaller Section

Section "Uninstall"
  RMDir /r "$INSTDIR"
  RMDir /r "$SMPROGRAMS\Hypernucleus"
  Delete "$DESKTOP\Hypernucleus.lnk"
  DeleteRegKey /ifempty HKCU "Software\Hypernucleus"
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Hypernucleus"
SectionEnd