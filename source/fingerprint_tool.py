import os
import argparse
import sys
import re
import json

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

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository", nargs=1, help="Path to local, cloned SmartThings repository from which fingerprints are needed to be extracted")
    arguments = parser.parse_args()
    outputFormat = "JSON"
    try:
        # path = arguments.repository[0] TODO: uncomment this
        path = "/home/p.kacprowicz/GIT/SmartThingsPrivate"
    except IOError:
        print("Couldn't find anything at provided path. Aborting.")
        sys.exit("Directory doesn't exist")
    except Exception as e:
        print("Exception: {}".format(e))
        sys.exit()
    
    allKeywords = set()
    rootDirPosition = path.find('SmartThings')

    data = list()

    # print(os.listdir(path + '/devicetypes/fibargroup'))
    path = path + '/devicetypes'
    for subdir, dirs, files in os.walk(path):
        for file in files:
            fileData = dict()
            pathToFile = os.path.join(subdir, file)
            realtivePath = pathToFile[rootDirPosition:]
            
            with open(pathToFile, 'rt', encoding="ISO-8859-1") as dthFile:
                isFingerprintInFile = False
                fileData['devices'] = list()
                for line in dthFile: 
                    line = line.replace('\t', '')
                    line = line.replace('    ', '')
                    line = line.replace('\n', '')

                    if line.find('definition') >= 0 and line.find('name') >= 0:
                        fileData['name'] = re.findall('name:( |)[\"\'](.*?)[\'\"]', line)[0][1]

                    fingerprintPosition = line.find('fingerprint')
                    fileData['path'] = realtivePath
                    if fingerprintPosition >= 0 and line.find('deviceJoinName') >= 0:
                        parameters = dict()
                        keywords = getKeywords(line)
                        allKeywords.update(keywords)
                        isFingerprintInFile = True

                        for keyword in keywords:
                            regex = keyword + ':( |)[\"\'](.*?)[\'\"]'
                            pattern = re.compile(regex)
                            parameters[keyword] = pattern.findall(line)[0][1]
                            # print(f"{keyword}: {pattern.findall(line)[0][1]}")
                        
                        fileData['devices'].append(parameters)

                if isFingerprintInFile:
                    data.append(fileData)

                dthFile.close()
    
    # print(data)
    if outputFormat == "JSON":
        with open('private.json', 'w') as output:
            json.dump(data, output, indent=4, sort_keys=True, ensure_ascii=False)
    elif outputFormat == "CSV":
        with open('private.csv', 'w') as output:
            firstLine = "name;"
            for parameter in allKeywords:
                firstLine += parameter + ';'
            firstLine += "path\n"
            output.write(firstLine)
            for file in data:
                for device in file['devices']:
                    line = ""
                    line += file['name'] + ';'
                    line += fillDeviceColumns(allKeywords, device)
                    line += file['path'] + '\n'
                    output.write(line)