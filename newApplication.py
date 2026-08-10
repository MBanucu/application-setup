import time
import os
import subprocess
import shutil
from pathlib import Path
import xml.etree.ElementTree as ET
import App

app = App.App()
matchingDirs = app.getAllApplicationDirs("^" + app.dirBase + ".*$")

count = len(matchingDirs) + 1
newDir = f'{app.dirBase} {count:02d}'

companyReceiver = app.inputParameterFile.searchParameter("companyReceiver")
newDir = f'{newDir} - {companyReceiver}'
newDirAbs = os.path.join(app.applicationsLocation, newDir)

process = subprocess.Popen(["git", "clone", "https://github.com/MBanucu/application.git", newDirAbs])
output, error = process.communicate()

source_dir = os.path.join('patches', 'Bewerbung')
target_dir = os.path.join(newDirAbs, 'Bewerbung')
if os.path.exists(source_dir):
    shutil.copytree(source_dir, target_dir, dirs_exist_ok=True)

pathToParametersTex = os.path.join(app.applicationsLocation, newDir, "Bewerbung/parameters/texProject/receiver/generated/parameters.tex")
pathToParametersXml = os.path.join(app.applicationsLocation, newDir, "Bewerbung/parameters/parameters.xml")
# process = subprocess.Popen(["code", "--goto", pathToParameters, os.path.join(applicationsLocation, newDir)])
# output, error = process.communicate()


def generateParametersTex(pathToParametersTex: str):
    tree = ET.parse("parameters.xml")
    root = tree.getroot()
    fileText = ""
    for command in root:
        commandName = command.attrib["name"]
        parameters = []
        for parameter in command:
            parameterText = parameter.text
            if (parameterText != None):
                parameterText = parameterText.replace("&", "\\&").replace("%", "\\%").replace("#", "\\#")
            else:
                parameterText = ""
            parameters.append(f'{{{parameterText}}}')
        fileText += f'\\{commandName}{"".join(parameters)}\n'
    path = Path(pathToParametersTex)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(pathToParametersTex, "w") as file:
        file.write(fileText)

generateParametersTex(pathToParametersTex)

path = Path(pathToParametersXml)
path.parent.mkdir(parents=True, exist_ok=True)
shutil.copy2("parameters.xml", pathToParametersXml)

emailReceiver = app.inputParameterFile.searchParameter("emailReceiver")
applicationPosition = app.inputParameterFile.searchParameter("applicationPosition")
surnameReceiver = app.inputParameterFile.searchParameter("surnameReceiver")
applicationHref = app.inputParameterFile.searchParameter("applicationHref")
emailTo = f'\'{emailReceiver}\''
def getEmailSubject():
    match app.inputParameterFile.searchParameter("applicationLanguage"):
        case "German":
            return f'\'Bewerbung als "{applicationPosition}"\''
        case "English":
            return f'\'Application as "{applicationPosition}"\''
        
emailSubject = getEmailSubject()
def getAnrede():
    gender = app.inputParameterFile.searchGender()
    language = app.inputParameterFile.searchParameter("applicationLanguage")
    surnameReceiver = app.inputParameterFile.searchParameter("surnameReceiver")
    if not surnameReceiver:
        surnameReceiver = "Unknown"
    match language:
        case "German":
            match gender:
                case "Mr":
                    return f"Sehr geehrter Herr {surnameReceiver}"
                case "Mrs":
                    return f"Sehr geehrte Frau {surnameReceiver}"
                case _:
                    return "Sehr geehrte Damen und Herren"
        case "English":
            match gender:
                case "Mr":
                    return f"Dear Mr. {surnameReceiver}"
                case "Mrs":
                    return f"Dear Mrs. {surnameReceiver}"
                case _:
                    return "Dear Sir or Madam"

def getEmailBody():
    match app.inputParameterFile.searchParameter("applicationLanguage"):
        case "German":
            return f'\
<html>\n\
    <body>\n\
        <p>{getAnrede()},</p>\n\
        <p>ich habe die Stelle auf <a href=\"{applicationHref}\">{applicationHref}</a> gefunden.</p>\n\
        <p>Im Anhang befinden sich meine Bewerbungsunterlagen.</p>\n\
        <p>Mit freundlichen Grüßen<br>\n\
            Michael Banucu</p>\n\
    </body>\n\
</html>'
        case "English":
            return f'\
<html>\n\
    <body>\n\
        <p>{getAnrede()},</p>\n\
        <p>I found the job listing at <a href=\"{applicationHref}\">{applicationHref}</a>.</p>\n\
        <p>In the attachment you can find my application documents.</p>\n\
        <p>Best regards,<br>\n\
            Michael Banucu</p>\n\
    </body>\n\
</html>'
    return ''

emailBody = getEmailBody()

def getPathToBuildFile():
    language = app.inputParameterFile.searchParameter("applicationLanguage") or "German"
    date = app.now.strftime("%Y-%m-%d")
    pdfName = dict[str, str]()
    pdfName["English"] = f'{date} Application Banucu Michael.pdf'
    pdfName["German"] = f'{date} Bewerbung Banucu Michael.pdf'
    return os.path.abspath(os.path.join(app.applicationsLocation, newDir, "Bewerbung", "build", language, pdfName[language]))

pathToBuildFileDir = os.path.abspath(os.path.join(app.applicationsLocation, newDir, "Bewerbung"))
pathToBuildFile = os.path.join(pathToBuildFileDir, "build.sh")
os.system(f"cd '{pathToBuildFileDir}' && ls -l && chmod +x '{pathToBuildFile}' && ./build.sh")
# process = subprocess.Popen(["./build.sh"], cwd=pathToBuildFileDir)
# output, error = process.communicate()

file_path = getPathToBuildFile()
while not os.path.exists(file_path):
    time.sleep(1)

emailAttachment = f'attachment=\'{getPathToBuildFile()}\''
def generateMailFile(emailBody: str) -> str:
    pathToMailFile = os.path.abspath(os.path.join(app.applicationsLocation, newDir, "E-Mail", "body.html"))
    path = Path(pathToMailFile)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(pathToMailFile, "w") as file:
        file.write(emailBody)
    return pathToMailFile
pathToMailFile = generateMailFile(emailBody)
emailMessage = f'\'{pathToMailFile}\''
emailFrom = "from='michael.banucu@googlemail.com'"
process = subprocess.Popen(["thunderbird", "-compose", f'{emailFrom},to={emailTo},subject={emailSubject},message={emailMessage},{emailAttachment}'])
# output, error = process.communicate()

app.saveJobListing(newDir)