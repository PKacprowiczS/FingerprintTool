import os
import argparse
import sys
import re
import json
import pandas

def getKeywords(line):
    keywords = list()
    pattern = re.compile('((["\'],)|t) ([A-z]+):')
    for match in pattern.findall(line):
        keywords.append(match[2])
    return keywords

def fillDeviceColumns(keywords, deviceSet):
    columns = dict()
    for keyword in keywords:
        columns[keyword] = ""
    
    for parameter in deviceSet.keys():
        columns[parameter] = deviceSet[parameter]
    line = ''
    for column in columns.values():
        line += column + ';'

    return line

def getNewDeviceJoinName(oldDJN, newDJN):
    if "SpringsWindowFashions" in newDJN and "Remote" in oldDJN:
        return "SpringsWindowFashions Remote"
    elif "Extender" in newDJN:
        position = newDJN.find("Extender")
        return f"{newDJN[:position]}Range Extender"
    elif "Open/closed" in newDJN:
        return newDJN.replace("Open/closed", "Open/Closed").replace("sensor","Sensor")
    elif "Trisensor" in newDJN:
        return newDJN.replace("Trisensor", "Multiporpose Sensor")
    elif "Multi-porpose" in newDJN:
        return newDJN.replace("Multi-porpose", "Multiporpose")
    elif "Philips Lighting" in newDJN:
        return newDJN.replace("Philips Lighting", "PhilipsHue Light")
    elif "Lighting" in newDJN:
        return newDJN.replace("Lighting", "Light")
    elif "Blacklisted" in oldDJN:
        return newDJN
    else:
        toReturn = ""
        for it in range(0, len(newDJN)):
            if newDJN[it].isupper():
                toReturn += newDJN[it]
            else:
                toReturn += newDJN.title()[it]
        
        return toReturn


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository", nargs=1, help="Path to local, cloned SmartThings repository from which fingerprints are needed to be extracted")
    arguments = parser.parse_args()
    outputFormat = "JSON"
    gitPath = "/home/p.kacprowicz/GIT/"
    try:
        # path = arguments.repository[0] TODO: uncomment this
        path = "/home/p.kacprowicz/GIT/SmartThingsPublic"
    except IOError:
        print("Couldn't find anything at provided path. Aborting.")
        sys.exit("Directory doesn't exist")
    except Exception as e:
        print("Exception: {}".format(e))
        sys.exit()
    
    allKeywords = set()
    rootDirPosition = path.find('SmartThings')

    data = list()
    fileWithChangedNames = open('Fingerprints - Public.csv', 'rt', encoding="UTF-8")
    csvNames = pandas.read_csv(fileWithChangedNames)
    paths = csvNames[['path']]
    paths = paths.drop_duplicates()
    csvNames = csvNames[['deviceJoinName', 'deviceJoinNameExpected', 'path', 'model']]
    csvNames = csvNames.drop_duplicates()
    # print(csvNames)
    for deviceTypeHandler in paths.itertuples():
        isThisDeviceInFile = csvNames['path'] == deviceTypeHandler[1]
        devicesInDTH = csvNames[isThisDeviceInFile]

        for device in devicesInDTH.itertuples():
            try:
                if device[2] == "(TBD)":
                    continue
                
                for character in device[1]:
                    if ord(character) > 122:
                        print(f'Review change for {device[1]} - {device[3]}')
                        break
                
                if "IKEA" in device[1] and "Lighting" not in device[2]:
                    print(f'Review change for {device[1]} - {device[3]}')

            except TypeError:
                print(f'Error for {device[1]} {device[2]} - {device[3]}')

            tempPath = gitPath + device[3]
            with open(tempPath, "r", encoding='UTF-8') as dthFile:
                outputFileString = ""
                for line in dthFile: 
                    fingerprintPosition = line.find('fingerprint')
                    if fingerprintPosition >= 0 and line.find('deviceJoinName') >= 0:
                        model_pattern = re.compile('model:( |)[\"\'](.*?)[\'\"]')
                        if model_pattern.search(line):
                            model = model_pattern.search(line).group(2)
                        else:
                            model = None
                        pattern = re.compile('deviceJoinName:( |)[\"\'](.*?)[\'\"]')
                        devJN = pattern.search(line)
                        devJNfirst = devJN.span(2)[0]
                        devJNlast = devJN.span(2)[1]
                        if (device[1] == devJN.group(2)) or (model == device[4] and model is not None):
                            # print(line[:devJNfirst] + device[2] + "\"")
                            line = line.replace('\n','')
                            outputFileString += line[:devJNfirst] + getNewDeviceJoinName(device[1], device[2]) + line[devJNlast:] + f' //{devJN.group(2)}\n'
                        else:
                            outputFileString += line
                        
                    else:
                        outputFileString += line

                dthFile.close()

            with open(tempPath, 'w', encoding="UTF-8") as dthFile:
                dthFile.write(outputFileString)
                dthFile.close()

    # for device in csvNames.itertuples():
    #     try:
    #         if device[2] == "(TBD)":
    #             continue
            
    #         for character in device[1]:
    #             if ord(character) > 122:
    #                 print(f'Review change for {device[1]} - {device[3]}')
    #                 break
            
    #         if "IKEA" in device[1] and "Lighting" not in device[2]:
    #             print(f'Review change for {device[1]} - {device[3]}')

    #     except TypeError:
    #         print(f'Error for {device[1]} {device[2]} - {device[3]}')

    #     tempPath = gitPath + device[3]
    #     with open(tempPath, "r", encoding='UTF-8') as dthFile:
    #         outputFileString = ""
    #         for line in dthFile: 
    #             fingerprintPosition = line.find('fingerprint')
    #             if fingerprintPosition >= 0 and line.find('deviceJoinName') >= 0:
    #                 model_pattern = re.compile('model:( |)[\"\'](.*?)[\'\"]')
    #                 if model_pattern.search(line):
    #                     model = model_pattern.search(line).group(2)
    #                 else:
    #                     model = None
    #                 pattern = re.compile('deviceJoinName:( |)[\"\'](.*?)[\'\"]')
    #                 devJN = pattern.search(line)
    #                 devJNfirst = devJN.span(2)[0]
    #                 devJNlast = devJN.span(2)[1]
    #                 if (device[1] == devJN.group(2)) or (model == device[4] and model is not None):
    #                     # print(line[:devJNfirst] + device[2] + "\"")
    #                     line = line.replace('\n','')
    #                     outputFileString += line[:devJNfirst] + getNewDeviceJoinName(device[1], device[2]) + line[devJNlast:] + f' //{devJN.group(2)}\n'
    #                 else:
    #                     outputFileString += line
                    
    #             else:
    #                 outputFileString += line

    #         dthFile.close()

    #     with open(tempPath, 'w', encoding="UTF-8") as dthFile:
    #         dthFile.write(outputFileString)
    #         dthFile.close()
        

    # # print(os.listdir(path + '/devicetypes/fibargroup'))
    # path = path + '/devicetypes'
    # for subdir, dirs, files in os.walk(path):
    #     for file in files:
    #         fileData = dict()
    #         pathToFile = os.path.join(subdir, file)
    #         realtivePath = pathToFile[rootDirPosition:]
            
    #         with open(pathToFile, 'rt', encoding="ISO-8859-1") as dthFile:
    #             isFingerprintInFile = False
    #             fileData['devices'] = list()
    #             for line in dthFile: 
    #                 line = line.replace('\t', '')
    #                 line = line.replace('    ', '')
    #                 line = line.replace('\n', '')

    #                 if line.find('definition') >= 0 and line.find('name') >= 0:
    #                     fileData['name'] = re.findall('name:( |)[\"\'](.*?)[\'\"]', line)[0][1]

    #                 fingerprintPosition = line.find('fingerprint')
    #                 fileData['path'] = realtivePath
    #                 if fingerprintPosition >= 0 and line.find('deviceJoinName') >= 0:
    #                     parameters = dict()
    #                     keywords = getKeywords(line)
    #                     allKeywords.update(keywords)
    #                     isFingerprintInFile = True

    #                     for keyword in keywords:
    #                         regex = keyword + ':( |)[\"\'](.*?)[\'\"]'
    #                         pattern = re.compile(regex)
    #                         parameters[keyword] = pattern.findall(line)[0][1]
    #                         # print(f"{keyword}: {pattern.findall(line)[0][1]}")
                        
    #                     fileData['devices'].append(parameters)

    #             if isFingerprintInFile:
    #                 data.append(fileData)

    #             dthFile.close()
    


    # print(os.listdir(path + '/devicetypes/fibargroup'))
    # path = path + '/devicetypes'
    # for subdir, dirs, files in os.walk(path):
    #     for file in files:
    #         fileData = dict()
    #         pathToFile = os.path.join(subdir, file)
    #         realtivePath = pathToFile[rootDirPosition:]
            
    #         with open(pathToFile, 'r', encoding="UTF-8") as dthFile:
    #             isFingerprintInFile = False
    #             fileData['devices'] = list()
    #             try:
    #                 for line in dthFile: 

    #                     if line.find('definition') >= 0 and line.find('name') >= 0:
    #                         fileData['name'] = re.findall('name:( |)[\"\'](.*?)[\'\"]', line)[0][1]

    #                     fingerprintPosition = line.find('fingerprint')
    #                     fileData['path'] = realtivePath
    #                     pattern = re.compile('deviceJoinName:( |)[\"\'](.*?)[\'\"]')
    #                     if fingerprintPosition >= 0 and line.find('deviceJoinName') >= 0:
    #                         devJN = pattern.search(line)
    #                         if devJN is not None: 
    #                             # print(f'{devJN.group(2)} : {devJN.span()} : {line[devJN.span()[0]:devJN.span()[1]][1:]}')
    #                             print(f'{line[:devJN.span(2)[0]]}')
    #                         else:
    #                             print(devJN)
    #             except UnicodeDecodeError:
    #                 print(pathToFile)
                        
    #             dthFile.close()
    #         pathOutput = "/home/p.kacprowicz/GIT/SmartThingsPublicFingerprint/devicetypes"
    #         pathToFileOutput = os.path.join(subdir, file)
    #         with open(pathToFileOutput, 'w', encoding="UTF-8") as dthFile:
    #             dthFile.close()


    # print(data)
    # if outputFormat == "JSON":
    #     with open('private.json', 'w') as output:
    #         json.dump(data, output, indent=4, sort_keys=True, ensure_ascii=False)
    # elif outputFormat == "CSV":
    #     with open('private.csv', 'w') as output:
    #         firstLine = "name;"
    #         for parameter in allKeywords:
    #             firstLine += parameter + ';'
    #         firstLine += "path\n"
    #         output.write(firstLine)
    #         for file in data:
    #             for device in file['devices']:
    #                 line = ""
    #                 line += file['name'] + ';'
    #                 line += fillDeviceColumns(allKeywords, device)
    #                 line += file['path'] + '\n'
    #                 output.write(line)