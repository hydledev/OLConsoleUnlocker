# Script for enabling cheats & developer console within retail Windows version of Outlast (Steam) made by Hydle
# Version 1.0

# ---How to use---
# Run script in CookedPCConsole directory with DECOMPRESSED Engine.upk file (Decompressor: https://www.gildor.org/downloads)

import os
import platform
from pathlib import Path
import hashlib

path = 'Engine.upk'
unmoddedHash = "47bb2a1692d6c84361f5ba4e456bfe40"
moddedHash = "88752d80734589a97618f56b59b305f5"

# Modified AOB for GameViewportClient::Init function to add console creation and registration
GameViewportClientInit = '''703A0000A333000000000000903A00000000000000000000973A
                            0000000000009A0200008D4100002503000089020000099A0200
                            77190180FFFFFF09004B2F000000014B2F00002A160F01A07700
                            0001A37700000F00943A00001B5725000000000000160F00913A
                            0000250733019600913A000000943A0000160F00933A00001BAB
                            2400000000000000913A0000160F00923A000011170B0B00933A
                            00000B0712019A1B1A2900000000000000923A00004A161DFFFF
                            FFFF160F48973A0000A81F4661696C656420746F206164642069
                            6E746572616374696F6E20746F20476C6F62616C496E74657261
                            6374696F6E732061727261793A00385600923A00001604281B06
                            4300000000000000923A000016A500913A00001606570009B602
                            007701CA7700002A160F01687A000011170B0B01CA7700000B07
                            CA019A1B1A2900000000000001687A00004A161DFFFFFFFF160F
                            48973A0000A81F4661696C656420746F2061646420696E746572
                            616374696F6E20746F20476C6F62616C496E746572616374696F
                            6E732061727261793A00385601687A00001604280F00953A0000
                            11170B0B20275E00000B0751029A1B1A2900000000000000953A
                            00004A161DFFFFFFFF160F48973A0000A81F4661696C65642074
                            6F2061646420696E746572616374696F6E20746F20476C6F6261
                            6C496E746572616374696F6E732061727261793A00385600953A
                            0000160428076A022D01A17600001B2415000000000000272816
                            0f01697a000011170b0b190180ffffff09004d2f000000014b2f
                            00000b0705039a1b1a2900000000000001697a00004a161dffff
                            ffff160f48993a0000a81f4661696c656420746f206164642069
                            6e746572616374696f6e20746f20476c6f62616c496e74657261
                            6374696f6e732061727261793a00385601697a0000160428041B
                            C01300000000000048973A000016043A963A0000530000000208
                            42008E28000000000000'''

initFuncAOB = bytes.fromhex(GameViewportClientInit)
# Offset of GameViewportClient::Init export within Engine package
exportHeaderOffset = 1630195 #(0018DFF3)
# Updated object file size for modified export
newObjFileSize = bytearray([0xC8, 0x02, 0x00, 0x00]) #712
# Updated object data location (end of file)
newExportOffset = bytearray([0x8A, 0xD7, 0x57, 0x00]) #5,756,810

# Offset into package header for compression flag
compressionFlagOffset = 109
# Offset into package for cheat enable token
tokenOffset = 3139461
# True parameter token value
trueToken = b'\x27'

def calculate_md5(filepath):
    md5_hash = hashlib.md5()
    
    with open(filepath, 'rb') as file:
        for chunk in iter(lambda: file.read(4096), b''):
            md5_hash.update(chunk)
    
    return md5_hash.hexdigest()

try:
    with open(path, 'rb+') as file:

        # File hash check
        hash = calculate_md5(path)
        if(hash == moddedHash):
            print("Engine.upk file is already modified. No further changes needed.")
            exit(0)
        elif(hash != unmoddedHash):            
            raise ValueError('Engine.upk file hash does not match unmodified decompressed Windows retail version. Aborting to prevent potential file corruption!')

        file.seek(tokenOffset)
        # AddCheats() -> AddCheats(true)
        # Forces cheat manager to be created by entering a true parameter token
        file.write(trueToken)
        print("Successfully enabled cheats!")

        # Update GameViewportClient::Init Export header data file size
        file.seek(exportHeaderOffset + 32)
        file.write(newObjFileSize)
        # Update GameViewportClient::Init Export header data offset
        file.seek(exportHeaderOffset + 36)
        file.write(newExportOffset)

        file.close()

    with open(path, 'ab') as file:
        # Dump modified GameViewportClient::Init function to end of package
        file.write(initFuncAOB)
        print("Successfully enabled developer console!")
        file.close()


    # Update config files to ensure cheats are enabled
    configPaths = [Path("..") / "Config" / "OLGame.ini", Path("..") / "Config" / "DefaultGame.ini"]

    # Add Windows Documents path for user config
    if platform.system() == "Windows":
        configPaths.append(Path(os.path.expanduser("~")) / "Documents" / "My Games" / "Outlast" / "OLGame" / "Config" / "OLGame.ini")
    
    for cfgPath in configPaths:
        if cfgPath.exists():
            with open(cfgPath, 'r') as f:
                lines = f.readlines()
            
            inCheatSection = False
            cheatFound = False
            modifiedLines = []
            
            for line in lines:
                if line.strip() == "[OLGame.OLCheatManager]":
                    inCheatSection = True
                    modifiedLines.append(line)
                elif inCheatSection and line.strip().startswith("bCheatsEnabled"):
                    modifiedLines.append("bCheatsEnabled=true\n")
                    cheatFound = True
                    inCheatSection = False
                elif line.strip().startswith("[") and inCheatSection:
                    # New section started, add bCheatsEnabled if not found
                    if not cheatFound:
                        modifiedLines.append("bCheatsEnabled=true\n")
                    modifiedLines.append(line)
                    inCheatSection = False
                else:
                    modifiedLines.append(line)
            
            # If section exists but setting wasn't found
            if inCheatSection and not cheatFound:
                modifiedLines.append("bCheatsEnabled=true\n")
            
            with open(cfgPath, 'w') as f:
                f.writelines(modifiedLines)
            
            print(f"Successfully set bCheatsEnabled=true in {cfgPath}")
        else:
            print(f"Warning: Could not find config file at {cfgPath}.")
            print(f"Ensure bCheatsEnabled is set to true!")
            print("[OLGame.OLCheatManager]")
            print("bCheatsEnabled=true")
        

except FileNotFoundError:
    print("Failed to find Engine.upk!")
except ValueError as e:
    print(e)