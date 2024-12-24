# Function: Auto repack ipa file
# Author: Crifan Li
# Update: 20241224

import codecs
import re
import os
from datetime import datetime,timedelta
from datetime import time  as datetimeTime
import argparse
import subprocess
import shutil
import zipfile

################################################################################
# Config & Settings & Const
################################################################################

mainDelimiter = "="*30
subDelimiter = "-"*30

# newIpaNamePart = "restoredSymbols"
newIpaNamePart = "idaAllSymbols"

isDeleteRepackIpaFolderAfterDone = True

################################################################################
# Util Function
################################################################################

def loadTextFromFile(fullFilename, fileEncoding="utf-8"):
  """load file text content from file"""
  with codecs.open(fullFilename, 'r', encoding=fileEncoding) as fp:
    allText = fp.read()
    # logging.debug("Complete load text from %s", fullFilename)
    return allText

def saveTextToFile(fullFilename, text, fileEncoding="utf-8"):
  """save text content into file"""
  with codecs.open(fullFilename, 'w', encoding=fileEncoding) as fp:
    fp.write(text)
    fp.close()


def datetimeToStr(inputDatetime, format="%Y%m%d_%H%M%S"):
  """Convert datetime to string

  Args:
      inputDatetime (datetime): datetime value
  Returns:
      str
  Raises:
  Examples:
      datetime.datetime(2020, 4, 21, 15, 44, 13, 2000) -> '20200421_154413'
  """
  datetimeStr = inputDatetime.strftime(format=format)
  # print("inputDatetime=%s -> datetimeStr=%s" % (inputDatetime, datetimeStr)) # 2020-04-21 15:08:59.787623
  return datetimeStr


def getCurDatetimeStr(outputFormat="%Y%m%d_%H%M%S"):
  """
  get current datetime then format to string

  eg:
      20171111_220722

  :param outputFormat: datetime output format
  :return: current datetime formatted string
  """
  curDatetime = datetime.now() # 2017-11-11 22:07:22.705101
  # curDatetimeStr = curDatetime.strftime(format=outputFormat) #'20171111_220722'
  curDatetimeStr = datetimeToStr(curDatetime, format=outputFormat)
  return curDatetimeStr


def runCommand(consoleCommand):
  """run command using subprocess call"""
  isRunCmdOk = False
  errMsg = "Unknown Error"

  try:
    resultCode = subprocess.check_call(consoleCommand, shell=True)
    if resultCode == 0:
      isRunCmdOk = True
      errMsg = ""
    else:
      isRunCmdOk = False
      errMsg = "%s return code %s" % (consoleCommand, resultCode)
  except subprocess.CalledProcessError as callProcessErr:
    isRunCmdOk = False
    errMsg = str(callProcessErr)
    # "Command 'ffmpeg -y -i /Users/crifan/.../debug/extractAudio/show_112233_video.mp4 -ss 00:00:05.359 -to 00:00:06.763 -b:a 128k /.../show_112233_video_000005359_000006763.mp3 2> /dev/null' returned non-zero exit status 1."

  return isRunCmdOk, errMsg


def getCommandOutput(consoleCommand, consoleOutputEncoding="utf-8", timeout=2):
  """get command output from terminal

  Args:
    consoleCommand (str): console/terminal command string
    consoleOutputEncoding (str): console output encoding, default is utf-8
    timeout (int): wait max timeout for run console command
  Returns:
    console output (str)
  Raises:
  """
  # print("getCommandOutput: consoleCommand=%s" % consoleCommand)
  isRunCmdOk = False
  consoleOutput = ""
  try:
    # consoleOutputByte = subprocess.check_output(consoleCommand)

    consoleOutputByte = subprocess.check_output(consoleCommand, shell=True, timeout=timeout)

    # commandPartList = consoleCommand.split(" ")
    # print("commandPartList=%s" % commandPartList)
    # consoleOutputByte = subprocess.check_output(commandPartList)
    # print("type(consoleOutputByte)=%s" % type(consoleOutputByte)) # <class 'bytes'>
    # print("consoleOutputByte=%s" % consoleOutputByte) # b'640x360\n'

    consoleOutput = consoleOutputByte.decode(consoleOutputEncoding) # '640x360\n'
    consoleOutput = consoleOutput.strip() # '640x360'
    isRunCmdOk = True
  except subprocess.CalledProcessError as callProcessErr:
    cmdErrStr = str(callProcessErr)
    print("Error %s for run command %s" % (cmdErrStr, consoleCommand))

  # print("isRunCmdOk=%s, consoleOutput=%s" % (isRunCmdOk, consoleOutput))
  return isRunCmdOk, consoleOutput

def createFolder(folderFullPath):
  """
    create folder, even if already existed
    Note: for Python 3.2+
  """
  os.makedirs(folderFullPath, exist_ok=True)

def deleteFolder(folderFullPath):
  """
    delete folder
    Note:makesure folder is already existed
  """
  if os.path.exists(folderFullPath):
    shutil.rmtree(folderFullPath)


def unzipFile(zipFileFullPath, outputFolder):
  """
    unzip a zip file
  """
  with zipfile.ZipFile(zipFileFullPath, 'r') as zip_ref:
    zip_ref.extractall(outputFolder)

def zipFolder(toZipFolder, outputZipFile):
  """
    zip/compress a whole folder/directory to zip file
  """
  print("Zip for foler %s" % toZipFolder)
  with zipfile.ZipFile(outputZipFile, 'w', zipfile.ZIP_DEFLATED) as zipFp:
    for dirpath, dirnames, filenames in os.walk(toZipFolder):
      # print("%s" % ("-"*80))
      # print("dirpath=%s, dirnames=%s, filenames=%s" % (dirpath, dirnames, filenames))
      # print("Folder: %s, Files: %s" % (dirpath, filenames))
      for curFileName in filenames:
        # print("curFileName=%s" % curFileName)
        curFilePath = os.path.join(dirpath, curFileName)
        # print("curFilePath=%s" % curFilePath)
        fileRelativePath = os.path.relpath(curFilePath, toZipFolder)
        # print("fileRelativePath=%s" % fileRelativePath)
        # print("  %s" % fileRelativePath)
        zipFp.write(curFilePath, arcname=fileRelativePath)
  print("Completed zip file %s" % outputZipFile)


def findAppFolder(rootFolder):
  """
    Find xxx.app folder full path under root folder
  """
  appFolerPath = None
  for dirpath, dirnames, filenames in os.walk(rootFolder):
    # print("%s" % ("-"*80))
    # print("dirpath=%s, dirnames=%s, filenames=%s" % (dirpath, dirnames, filenames))
    for curDirName in dirnames:
      # print("curDirName=%s" % curDirName)
      if curDirName.endswith(".app"):
        curFolderPath = os.path.join(dirpath, curDirName)
        # print("curFolderPath=%s" % curFolderPath)
        appFolerPath = os.path.abspath(curFolderPath)
        # print("appFolerPath=%s" % appFolerPath)
        # appFolerPath=/Users/crifan/dev/dev_root/iosReverse/WhatsApp/ipa/forRepackIpa_WhatsApp_v23.20.79_20231206/Payload/WhatsApp.app
        return appFolerPath

  return appFolerPath

def processEntitlementBoolKeyValue(keyName, entitlementXmlStr):
  """
  eg:
    get-task-allow
      if existed, but false -> replace to true
      if not existed -> add it
      if found and already true -> do nothing
      => final to:
        <key>get-task-allow</key>
        <true/>
  """
  newEntitlementXmlStr = entitlementXmlStr

  keyTrueStrTemplate = """<key>%s</key>
	<true/>"""
  # print("keyTrueStrTemplate=%s" % keyTrueStrTemplate)
  keyTrueStr = keyTrueStrTemplate.replace("%s", keyName)
  # print("keyTrueStr=%s" % keyTrueStr)
  keyValuePattern = "<key>\s*%s\s*</key>.+?<(?P<keyValue>\w+)/>" % keyName
  # print("keyValuePattern=%s" % keyValuePattern)

  keyValueMatch = re.search(keyValuePattern, entitlementXmlStr, re.DOTALL)
  print("keyValueMatch=%s" % keyValueMatch)
  if keyValueMatch:
    # exist: no action or replace to true
    keyValue = keyValueMatch.group("keyValue")
    # print("keyValue=%s" % keyValue)
    keyValueLower = keyValue.lower()
    # print("keyValueLower=%s" % keyValueLower)
    if keyValueLower == "true":
      # do nothing
      print("Already: %s" % keyTrueStr)
    elif keyValueLower == "false":
      # replace valeu to true
      matchStart = keyValueMatch.start()
      # print("matchStart=%s" % matchStart)
      matchEnd = keyValueMatch.end()
      # print("matchEnd=%s" % matchEnd)
      matchedStr = entitlementXmlStr[matchStart:matchEnd]
      # print("matchedStr=%s" % matchedStr)
      # replace it
      newEntitlementXmlStr = re.sub(matchedStr, keyTrueStr, entitlementXmlStr)
      # print("newEntitlementXmlStr=%s" % newEntitlementXmlStr)
  else:
    # no exist, insert to end
    """
    </dict>
    </plist>
    """
    endDictPlistMatch = re.search("</dict>.+?</plist>$", entitlementXmlStr, re.DOTALL)
    # print("endDictPlistMatch=%s" % endDictPlistMatch)
    matchStart = endDictPlistMatch.start()
    # print("matchStart=%s" % matchStart)
    matchEnd = endDictPlistMatch.end()
    # print("matchEnd=%s" % matchEnd)
    matchedStr = entitlementXmlStr[matchStart:matchEnd]
    # print("matchedStr=%s" % matchedStr)
    keyTrueAndEndStr = "\t%s\n%s" % (keyTrueStr, matchedStr)
    # print("keyTrueAndEndStr=%s" % keyTrueAndEndStr)
    newEntitlementXmlStr = re.sub(matchedStr, keyTrueAndEndStr, entitlementXmlStr)

  print("newEntitlementXmlStr=%s" % newEntitlementXmlStr)
  return newEntitlementXmlStr




################################################################################
# Main
################################################################################

if __name__ == "__main__":
  curDateStr = getCurDatetimeStr("%Y%m%d")
  print("curDateStr=%s" % curDateStr)

  newParser = argparse.ArgumentParser()
  newParser.add_argument("-i", "--input-ipa-file", type=str, dest="inputIpaFile", default=None, required=True, help="Input IPA file full path")
  newParser.add_argument("-o", "--output-ipa-file", type=str, dest="outputIpaFile", default=None, help="Output repacked IPA file")
  newParser.add_argument("-r", "--restore-symbol", type=str, dest="restoreSymbol", default="restore-symbol", help="restore-symbol exectuable full path. Default: restore-symbol")
  newParser.add_argument("-l", "--symbol-list", type=str, dest="symbolList", default=[], nargs="+", action='append', help="Symbol list restore, support multiple item to to list, single item format: {machoFileInIpa}={JsonSymbolFile}")
  newParser.add_argument("-d", "--is-add-debuggable", type=bool, dest="isAddDebuggable", default=True, help="Enable/Disable to auto edit entitlement file to add debuggable (get-task-allow, task_for_pid-allow, run-unsigned-code)")
  args = newParser.parse_args()
  print("%s Parsing input arguments %s" % (mainDelimiter , mainDelimiter))

  print("args=%s" % args)
  restoreSymbol = args.restoreSymbol
  print("restoreSymbol=%s" % restoreSymbol)
  isAddDebuggable = args.isAddDebuggable
  print("isAddDebuggable=%s" % isAddDebuggable)

  inputIpaFile = args.inputIpaFile
  print("inputIpaFile=%s" % inputIpaFile)
  if inputIpaFile:
    # for workaround VSCode launch.json args bug: redundant preceding space
    inputIpaFile = inputIpaFile.strip()

  ipaFilePath = os.path.dirname(inputIpaFile)
  print("ipaFilePath=%s" % ipaFilePath)
  ipaFilename = os.path.basename(inputIpaFile)
  print("ipaFilename=%s" % ipaFilename)

  outputIpaFile = args.outputIpaFile
  ipaFilenameOnly = None
  if not outputIpaFile:
    ipaFilenameOnly, ipaExt = os.path.splitext(ipaFilename)
    print("ipaFilenameOnly=%s, ipaExt=%s" % (ipaFilenameOnly, ipaExt))
    newIpaFilename = "%s_%s_%s%s" % (ipaFilenameOnly, newIpaNamePart, curDateStr, ipaExt)
    print("newIpaFilename=%s" % newIpaFilename)
    outputIpaFile = os.path.join(ipaFilePath, newIpaFilename)
  print("outputIpaFile=%s" % outputIpaFile)

  print("%s Unzip %s %s" % (mainDelimiter, ipaFilename, mainDelimiter))
  unzipOutputFolderName = "forRepackIpa_%s_%s" % (ipaFilenameOnly, curDateStr)
  print("unzipOutputFolderName=%s" % unzipOutputFolderName)
  unzipOutputFullPath = os.path.join(ipaFilePath, unzipOutputFolderName)
  print("unzipOutputFullPath=%s" % unzipOutputFullPath)

  # delete if existe foler
  deleteFolder(unzipOutputFullPath)

  createFolder(unzipOutputFullPath)
  print("Created unzip foler: %s" % unzipOutputFullPath)
  unzipFile(inputIpaFile, unzipOutputFullPath)

  # find out xxx.app
  appFolderFullPath = findAppFolder(unzipOutputFullPath)
  print("appFolderFullPath=%s" % appFolderFullPath)
  appFolderName = os.path.basename(appFolderFullPath)
  print("appFolderName=%s" % appFolderName)

  # create tmp foler for later use
  tmpFolderPath = os.path.join(unzipOutputFullPath, "tmp")
  print("tmpFolderPath=%s" % tmpFolderPath)
  createFolder(tmpFolderPath)
  print("Created tmp foler: %s" % tmpFolderPath)

  symbolList = args.symbolList
  print("symbolList=%s" % symbolList)
  for curNum, eachSymbolList in enumerate(symbolList, start=1):
    eachSymbol = eachSymbolList[0]
    splitList = eachSymbol.split("=")
    # print("splitList=%s" % splitList)
    machoFileInIpa = splitList[0]
    machoFilename = os.path.basename(machoFileInIpa)
    print("%s [%d] %s %s" % (subDelimiter, curNum, machoFilename, subDelimiter))
    print("machoFileInIpa=%s" % machoFileInIpa)
    symbolFullPath = splitList[1]
    print("symbolFullPath=%s" % symbolFullPath)
    if not os.path.isfile(symbolFullPath):
      print("Not existed symbol file: %s" % symbolFullPath)
      exit(1)

    machoFullPath = os.path.join(appFolderFullPath, machoFileInIpa)
    print("machoFullPath=%s" % machoFullPath)
    if not os.path.isfile(machoFullPath):
      print("Not existed Mach-O file: %s" % machoFullPath)
      exit(1)
    
    hasEntitlement = False

    print("%s Extract entitlement using ldid %s" % (mainDelimiter, mainDelimiter))
    entitlementFile = "%s_entitlements.xml" % machoFilename
    print("entitlementFile=%s" % entitlementFile)
    entitlementFullPath = os.path.join(tmpFolderPath, entitlementFile)
    print("entitlementFullPath=%s" % entitlementFullPath)
    ldldCmd = """ldid -e "%s" > "%s" """ % (machoFullPath, entitlementFullPath)
    # ldid -e WhatsApp_mergedSymbols_20231117 > WhatsApp_mergedSymbols_20231117_entitlements.xml
    print("ldldCmd=%s" % ldldCmd)
    isLdidOk, errMsg = runCommand(ldldCmd)
    if not isLdidOk:
      print("isLdidOk=%s, errMsg=%s" % (isLdidOk, errMsg))
      exit(1)

    entitlementFileSize = os.path.getsize(entitlementFullPath)
    print("entitlementFileSize=%s" % entitlementFileSize)
    if entitlementFileSize > 0:
      hasEntitlement = True
    print("hasEntitlement=%s" % hasEntitlement)

    if hasEntitlement:
      if isAddDebuggable:
        entitlementXml = loadTextFromFile(entitlementFullPath)
        print("entitlementXml=%s" % entitlementXml)
        newEntitlementXml = entitlementXml
        """
          <key>get-task-allow</key>
          <true/>
          <key>task_for_pid-allow</key>
          <true/>
          <key>run-unsigned-code</key>
          <true/>
        """
        newEntitlementXml = processEntitlementBoolKeyValue("get-task-allow", newEntitlementXml)
        newEntitlementXml = processEntitlementBoolKeyValue("task_for_pid-allow", newEntitlementXml)
        newEntitlementXml = processEntitlementBoolKeyValue("run-unsigned-code", newEntitlementXml)
        print("newEntitlementXml=%s" % newEntitlementXml)
        # writeback
        debuggableEntitlementFile = "%s_entitlements_debuggable.xml" % machoFilename
        print("debuggableEntitlementFile=%s" % debuggableEntitlementFile)
        debuggableEntitlementFullPath = os.path.join(tmpFolderPath, debuggableEntitlementFile)
        print("debuggableEntitlementFullPath=%s" % debuggableEntitlementFullPath)
        saveTextToFile(debuggableEntitlementFullPath, newEntitlementXml)
        entitlementFullPath = debuggableEntitlementFullPath

    print("%s Restore symbol using restore-symbol %s" % (mainDelimiter, mainDelimiter))
    restoreSymbolCmd = """ %s -w true -s false -j "%s" -o "%s" "%s" """ % (restoreSymbol, symbolFullPath, machoFullPath, machoFullPath)
    print("restoreSymbolCmd=%s" % restoreSymbolCmd)
    # restoreSymbolCmd=/Users/crifan/dev/dev_src/ios_reverse/symbol/restore-symbol/crifan/restore-symbol/restore-symbol -w true -s false -j /Users/crifan/dev/dev_src/ios_reverse/symbol/restore-symbol/crifan/restore-symbol/tools/IDAScripts/export_ida_symbol/output/WhatsApp_IDASymbols_FunctionsNames_20231205_220128.json -o /Users/crifan/dev/dev_root/iosReverse/WhatsApp/ipa/forRepackIpa_WhatsApp_v23.20.79_20231206/Payload/WhatsApp.app/WhatsApp /Users/crifan/dev/dev_root/iosReverse/WhatsApp/ipa/forRepackIpa_WhatsApp_v23.20.79_20231206/Payload/WhatsApp.app/WhatsApp
    isRestoreOk, errMsg = runCommand(restoreSymbolCmd)
    if not isRestoreOk:
      print("isRestoreOk=%s, errMsg=%s" % (isRestoreOk, errMsg))
      exit(1)

    print("%s Resign using codesign %s" % (mainDelimiter, mainDelimiter))
    entitlementPart = ""
    if hasEntitlement:
      entitlementPart = """--entitlements "%s" """ % entitlementFullPath
    codesignCmd = """codesign --force --sign - %s --timestamp=none --generate-entitlement-der "%s" """ % (entitlementPart, machoFullPath)
    print("codesignCmd=%s" % codesignCmd)
    # codesignCmd=codesign --force --sign - --entitlements /Users/crifan/dev/dev_root/iosReverse/WhatsApp/ipa/forRepackIpa_WhatsApp_v23.20.79_20231206/tmp/WhatsApp_entitlements.xml --timestamp=none --generate-entitlement-der /Users/crifan/dev/dev_root/iosReverse/WhatsApp/ipa/forRepackIpa_WhatsApp_v23.20.79_20231206/Payload/WhatsApp.app/WhatsApp
    isCodesignOk, errMsg = runCommand(codesignCmd)
    if not isCodesignOk:
      print("isCodesignOk=%s, errMsg=%s" % (isCodesignOk, errMsg))
      exit(1)
  
  # remove tmp folder
  deleteFolder(tmpFolderPath)
  # print("Deleted tmp foler: %s" % tmpFolderPath)

  # zip folder
  outputIpaFilename = "%s_%s_%s.ipa" % (ipaFilenameOnly, newIpaNamePart, curDateStr)
  print("outputIpaFilename=%s" % outputIpaFilename)
  outputIpaFullPath = os.path.join(ipaFilePath, outputIpaFilename)
  print("outputIpaFullPath=%s" % outputIpaFullPath)
  zipFolder(unzipOutputFullPath, outputIpaFullPath)

  if isDeleteRepackIpaFolderAfterDone:
    deleteFolder(unzipOutputFullPath)
    # print("Deleted unzip foler: %s" % unzipOutputFullPath)
