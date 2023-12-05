# Function: Auto repack ipa file
# Author: Crifan Li
# Update: 20231205

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

mainDelimiter = "="*20

################################################################################
# Util Function
################################################################################

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

################################################################################
# Main
################################################################################

if __name__ == "__main__":
  curDateStr = getCurDatetimeStr("%Y%m%d")
  print("curDateStr=%s" % curDateStr)
  whatsappVersionStr = "v23.20.79"

  newParser = argparse.ArgumentParser()
  # newParser.add_argument("-m", "--macho-file", type=str, dest="machoFile", default=None, help="Mach-O file")
  # newParser.add_argument("-s", "--symbol-file", type=str, dest="symbolFile", default=None, help="symbol file to restore")
  newParser.add_argument("-o", "--output-ipa-file", type=str, dest="outputIpaFile", default=None, help="Output repacked IPA file")
  args = newParser.parse_args()
  print("%s Parsing input arguments %s" % (mainDelimiter , mainDelimiter))

  # for debug
  # args.machoFile = "/Users/crifan/dev/dev_src/ios_reverse/symbol/restore-symbol/crifan/restore-symbol/test/WhatsApp/input/WhatsApp"
  # args.symbolFile = "/Users/crifan/dev/dev_src/ios_reverse/symbol/restore-symbol/crifan/restore-symbol/tools/mergeSymbols/output/WhatsApp_mergedSymbols_20231121_102056.json"

  # symbolFilename_WhatsApp = "WhatsApp_IDASymbols_FunctionsNames_20231126_171758.json"
  # symbolFilename_WhatsApp = "WhatsApp_IDASymbols_FunctionsNames_20231128_213634.json"
  # symbolFilename_SharedModules = "SharedModules_IDASymbols_FunctionsNames_20231128_214111.json"
  # symbolFilename_WhatsApp = "WhatsApp_IDASymbols_FunctionsNames_20231129_223621.json"
  # symbolFilename_SharedModules = "SharedModules_IDASymbols_FunctionsNames_20231129_224249.json"
  symbolFilename_WhatsApp = "WhatsApp_IDASymbols_FunctionsNames_20231205_220128.json"
  symbolFilename_SharedModules = "SharedModules_IDASymbols_FunctionsNames_20231205_220317.json"

  print("args=%s" % args)
  # machoFile = args.machoFile
  # print("machoFile=%s" % machoFile)
  # symbolFile = args.symbolFile
  # print("symbolFile=%s" % symbolFile)
  outputIpaFile = args.outputIpaFile
  print("outputIpaFile=%s" % outputIpaFile)


  # machoFilename = os.path.basename(machoFile)
  # print("machoFilename=%s" % machoFilename)

  if not outputIpaFile:
    # outputIpaFile = "%s_%s.ipa" % (machoFilename, curDateStr)
    outputIpaFile = "WhatsApp_%s_%s.ipa" % (whatsappVersionStr, curDateStr)
    print("outputIpaFile=%s" % outputIpaFile)

  # common part
  symbolFolder = "/Users/crifan/dev/dev_src/ios_reverse/symbol/restore-symbol/crifan/restore-symbol/tools/IDAScripts/export_ida_symbol/output"

  restoreSymbolExec ="/Users/crifan/dev/dev_src/ios_reverse/symbol/restore-symbol/crifan/restore-symbol/restore-symbol"

  # ==================== WhatsApp ====================
  print("%s restore-symbol + resign for WhatsApp %s" % (mainDelimiter , mainDelimiter))
  machoFullPath_WhatsApp = "/Users/crifan/dev/dev_src/ios_reverse/symbol/restore-symbol/crifan/restore-symbol/test/WhatsApp/input/WhatsApp"
  restoredFilename_WhatsApp = "WhatsApp_mergedSymbols_%s" % curDateStr
  print("restoredFilename_WhatsApp=%s" % restoredFilename_WhatsApp)
  restoredOutputFolder_WhatsApp = "/Users/crifan/dev/dev_src/ios_reverse/symbol/restore-symbol/crifan/restore-symbol/test/WhatsApp/output"
  print("restoredOutputFolder_WhatsApp=%s" % restoredOutputFolder_WhatsApp)
  restoredFullPath_WhatsApp = os.path.join(restoredOutputFolder_WhatsApp, restoredFilename_WhatsApp)
  print("restoredFullPath_WhatsApp=%s" % restoredFullPath_WhatsApp)
  symbolFullPath_WhatsApp = os.path.join(symbolFolder, symbolFilename_WhatsApp)
  print("symbolFullPath_WhatsApp=%s" % symbolFullPath_WhatsApp)

  # call restore-symbol
  restoreSymbolCmd = "%s -w true -s false -j %s -o %s %s" % (restoreSymbolExec, symbolFullPath_WhatsApp, restoredFullPath_WhatsApp, machoFullPath_WhatsApp)
  print("restoreSymbolCmd=%s" % restoreSymbolCmd)
  # /Users/crifan/dev/dev_src/ios_reverse/symbol/restore-symbol/crifan/restore-symbol/restore-symbol -s false -j /Users/crifan/dev/dev_src/ios_reverse/symbol/restore-symbol/crifan/restore-symbol/tools/mergeSymbols/output/WhatsApp_mergedSymbols_20231121_102056.json -o /Users/crifan/dev/dev_src/ios_reverse/symbol/restore-symbol/crifan/restore-symbol/test/WhatsApp/output/WhatsApp_mergedSymbols_20231121 /Users/crifan/dev/dev_src/ios_reverse/symbol/restore-symbol/crifan/restore-symbol/test/WhatsApp/input/WhatsApp
  isRestoreOk, errMsg = runCommand(restoreSymbolCmd)
  if not isRestoreOk:
    print("isRestoreOk=%s, errMsg=%s" % (isRestoreOk, errMsg))
    exit(1)

  # do resign
  # copy for resign
  copySrc_WhatsApp = restoredFullPath_WhatsApp
  resignFilename_WhatsApp = "%s_resigned" % restoredFilename_WhatsApp
  copyDest_WhatsApp = os.path.join(restoredOutputFolder_WhatsApp, resignFilename_WhatsApp)
  cpCmd = "cp %s %s" % (copySrc_WhatsApp, copyDest_WhatsApp)
  print("cpCmd=%s" % cpCmd)
  isCpResignOk, errMsg = runCommand(cpCmd)
  if not isCpResignOk:
    print("isCpResignOk=%s, errMsg=%s" % (isCpResignOk, errMsg))
    exit(1)

  # call codesign
  entitlementFilename_WhatsApp = "WhatsApp_entitlements.xml"
  entitlementFolder_WhatsApp = "/Users/crifan/dev/dev_src/ios_reverse/symbol/restore-symbol/crifan/restore-symbol/test/WhatsApp/output"
  entitlementFullPath_WhatsApp = os.path.join(entitlementFolder_WhatsApp, entitlementFilename_WhatsApp)
  resignedFullPath_WhatsApp = copyDest_WhatsApp
  codesignCmd = "codesign --force --sign - --entitlements %s --timestamp=none --generate-entitlement-der %s" % (entitlementFullPath_WhatsApp, resignedFullPath_WhatsApp)
  print("codesignCmd=%s" % codesignCmd)
  # codesignCmd=codesign --force --sign - --entitlements /Users/crifan/dev/dev_src/ios_reverse/symbol/restore-symbol/crifan/restore-symbol/test/WhatsApp/output/WhatsApp_entitlements.xml --timestamp=none --generate-entitlement-der /Users/crifan/dev/dev_src/ios_reverse/symbol/restore-symbol/crifan/restore-symbol/test/WhatsApp/output/WhatsApp_mergedSymbols_20231128_resigned
  isCodesignOk, errMsg = runCommand(codesignCmd)
  if not isCodesignOk:
    print("isCodesignOk=%s, errMsg=%s" % (isCodesignOk, errMsg))
    exit(1)

  # ==================== SharedModules ====================
  print("%s restore-symbol + resign for SharedModules %s" % (mainDelimiter , mainDelimiter))

  machoFullPath_SharedModules = "/Users/crifan/dev/dev_src/ios_reverse/symbol/restore-symbol/crifan/restore-symbol/test/SharedModules/input/SharedModules"
  restoredFilename_SharedModules = "SharedModules_mergedSymbols_%s" % curDateStr
  print("restoredFilename_SharedModules=%s" % restoredFilename_SharedModules)
  restoredOutputFolder_SharedModules = "/Users/crifan/dev/dev_src/ios_reverse/symbol/restore-symbol/crifan/restore-symbol/test/SharedModules/output"
  print("restoredOutputFolder_SharedModules=%s" % restoredOutputFolder_SharedModules)
  restoredFullPath_SharedModules = os.path.join(restoredOutputFolder_SharedModules, restoredFilename_SharedModules)
  print("restoredFullPath_SharedModules=%s" % restoredFullPath_SharedModules)
  symbolFullPath_SharedModules = os.path.join(symbolFolder, symbolFilename_SharedModules)
  print("symbolFullPath_SharedModules=%s" % symbolFullPath_SharedModules)

  # call restore-symbol
  restoreSymbolCmd = "%s -w true -s false -j %s -o %s %s" % (restoreSymbolExec, symbolFullPath_SharedModules, restoredFullPath_SharedModules, machoFullPath_SharedModules)
  print("restoreSymbolCmd=%s" % restoreSymbolCmd)
  # /Users/crifan/dev/dev_src/ios_reverse/symbol/restore-symbol/crifan/restore-symbol/restore-symbol -s false -j /Users/crifan/dev/dev_src/ios_reverse/symbol/restore-symbol/crifan/restore-symbol/tools/mergeSymbols/output/WhatsApp_mergedSymbols_20231121_102056.json -o /Users/crifan/dev/dev_src/ios_reverse/symbol/restore-symbol/crifan/restore-symbol/test/WhatsApp/output/WhatsApp_mergedSymbols_20231121 /Users/crifan/dev/dev_src/ios_reverse/symbol/restore-symbol/crifan/restore-symbol/test/WhatsApp/input/WhatsApp
  isRestoreOk, errMsg = runCommand(restoreSymbolCmd)
  if not isRestoreOk:
    print("isRestoreOk=%s, errMsg=%s" % (isRestoreOk, errMsg))
    exit(1)

  # do resign
  # copy for resign
  copySrc_SharedModules = restoredFullPath_SharedModules
  resignFilename_SharedModules = "%s_resigned" % restoredFilename_SharedModules
  copyDest_SharedModules = os.path.join(restoredOutputFolder_SharedModules, resignFilename_SharedModules)
  cpCmd = "cp %s %s" % (copySrc_SharedModules, copyDest_SharedModules)
  print("cpCmd=%s" % cpCmd)
  isCpResignOk, errMsg = runCommand(cpCmd)
  if not isCpResignOk:
    print("isCpResignOk=%s, errMsg=%s" % (isCpResignOk, errMsg))
    exit(1)

  # call codesign
  resignedFullPath_SharedModules = copyDest_SharedModules
  codesignCmd = "codesign --force --sign - --timestamp=none --generate-entitlement-der %s" % resignedFullPath_SharedModules
  print("codesignCmd=%s" % codesignCmd)
  # /Users/crifan/dev/dev_src/ios_reverse/symbol/restore-symbol/crifan/restore-symbol/restore-symbol -s false -j /Users/crifan/dev/dev_src/ios_reverse/symbol/restore-symbol/crifan/restore-symbol/tools/IDAScripts/export_ida_symbol/output/SharedModules_IDASymbols_FunctionsNames_20231128_214111.json -o /Users/crifan/dev/dev_src/ios_reverse/symbol/restore-symbol/crifan/restore-symbol/test/SharedModules/output/SharedModules_mergedSymbols_20231128 /Users/crifan/dev/dev_src/ios_reverse/symbol/restore-symbol/crifan/restore-symbol/test/SharedModules/input/SharedModules
  isCodesignOk, errMsg = runCommand(codesignCmd)
  if not isCodesignOk:
    print("isCodesignOk=%s, errMsg=%s" % (isCodesignOk, errMsg))
    exit(1)

  # unzip ipa
  origWhatsappIpaFilename = "WhatsApp_%s.ipa" % whatsappVersionStr
  origWhatsappIpaFolder = "/Users/crifan/dev/dev_root/iosReverse/WhatsApp/ipa"
  origWhatsappIpaFullPath = os.path.join(origWhatsappIpaFolder, origWhatsappIpaFilename)
  unzipOutputFolderName = "forRepackIpa_%s" % curDateStr
  unzipOutputFullPath = os.path.join(origWhatsappIpaFolder, unzipOutputFolderName)
  createFolder(unzipOutputFullPath)
  unzipFile(origWhatsappIpaFullPath, unzipOutputFullPath)

  # replace with resigned file
  unzipedFullPath_WhatsApp = os.path.join(unzipOutputFullPath, "Payload/WhatsApp.app/WhatsApp")
  cpCmd_WhatsApp = "cp %s %s" % (copyDest_WhatsApp, unzipedFullPath_WhatsApp)
  print("cpCmd_WhatsApp=%s" % cpCmd_WhatsApp)
  isCpOk_WhatsApp, errMsg = runCommand(cpCmd_WhatsApp)
  if not isCpOk_WhatsApp:
    print("isCpOk_WhatsApp=%s, errMsg=%s" % (isCpOk_WhatsApp, errMsg))
    exit(1)

  unzipedFullPath_SharedModules = os.path.join(unzipOutputFullPath, "Payload/WhatsApp.app/Frameworks/SharedModules.framework/SharedModules")
  cpCmd_SharedModules = "cp %s %s" % (copyDest_SharedModules, unzipedFullPath_SharedModules)
  print("cpCmd_SharedModules=%s" % cpCmd_SharedModules)
  isCpOk_SharedModules, errMsg = runCommand(cpCmd_SharedModules)
  if not isCpOk_SharedModules:
    print("isCpOk_SharedModules=%s, errMsg=%s" % (isCpOk_SharedModules, errMsg))
    exit(1)

  # zip folder
  outputZipFilename = "WhatsApp_%s_idaAllSymbols_%s.ipa" % (whatsappVersionStr, curDateStr)
  outputZipFullPath = os.path.join(origWhatsappIpaFolder, outputZipFilename)
  zipFolder(unzipOutputFullPath, outputZipFullPath)

  # do clean work
  # remove forRepackIpa folder
  deleteFolder(unzipOutputFullPath)
