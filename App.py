from datetime import datetime
import os
from pathlib import Path
import re
import subprocess
import xml.etree.ElementTree as ET
import pytz

from weasyprint import CSS, HTML


class ParameterFile:
    fileLocation: str
    dateOfApplication: datetime

    def __init__(self, fileLocation: str, dateOfApplication: str) -> None:
        self.fileLocation = os.path.abspath(fileLocation)
        self.dateOfApplication = datetime.strptime(dateOfApplication, "%Y%m%d")
        self.tree = ET.parse(self.fileLocation)

    def searchParameter(self, parameter: str):
        for command in self.tree.getroot():
            if (command.attrib["name"] == "newcommand"):
                parameter1 = command[0]
                if (parameter1.text == f'\\{parameter}'):
                    return command[1].text
        return None

    def searchGender(self):
        for command in self.tree.getroot():
            if (command.attrib["name"] == "adaptGender"):
                return command[0].text
        return ""

    def getRowCsv(self):
        jobHref = filter(None, [
            self.searchParameter("jobAgent"),
            self.searchParameter("applicationHref")
        ])
        cols = [
            "beworben",
            "Firma",
            "Interview",
            "Absage",
            "letzte Antwort",
            "Vermittleragentur",
            "Kontakt Anrede",
            "Kontakt Vorname",
            "Kontakt Nachname",
            "Kontakt E-Mail Adresse",
            "Vermittler"
        ]
        row = [
            self.dateOfApplication.strftime("%Y-%m-%d"),
            self.searchParameter("companyReceiver"),
            "",
            "",
            "",
            "",
            self.searchGender(),
            self.searchParameter("prenameReceiver"),
            self.searchParameter("surnameReceiver"),
            self.searchParameter("emailReceiver"),
            "\n".join(filter(lambda param: param !=
                      None and param != "", jobHref)),
        ]
        return cols, row

    def saveJobListingPDF(self, jobListingLocation: str):
        applicationHref = self.searchParameter("applicationHref")
        if not applicationHref:
            return

        path = Path(jobListingLocation)
        path.parent.mkdir(parents=True, exist_ok=True)

        css = CSS(string=''' @page {size: 315mm 445.5mm;} ''')
        pdf = HTML(applicationHref).write_pdf(stylesheets=[css])
        if not pdf:
            print(f"Error: Could not create PDF from {applicationHref}")
            return

        with open(jobListingLocation, 'wb') as file:
            file.write(pdf)

    def saveJobListingHTML(self, jobListingLocation: str):
        applicationHref = self.searchParameter("applicationHref")
        if not applicationHref:
            return

        path = Path(jobListingLocation)
        path.parent.mkdir(parents=True, exist_ok=True)
        process = subprocess.Popen(
            [
                "wget",
                "-p",
                "--convert-links",
                applicationHref
            ], cwd=path.parent.resolve())

    def saveJobListing(self, jobListingLocation: str):
        self.saveJobListingHTML(jobListingLocation)
        self.saveJobListingPDF(jobListingLocation)


class App:
    applicationsLocation = "applications"
    now = datetime.now(pytz.timezone("Europe/Berlin"))
    dirBase = now.strftime("%Y%m%d")
    inputParameterFile = ParameterFile("parameters.xml", dirBase)
    
    def __init__(self):
        self.applicationsLocation = os.path.abspath(self.applicationsLocation)
        Path(self.applicationsLocation).mkdir(parents=True, exist_ok=True)

    def getAllApplicationDirs(self, regex=r"^\d\d\d\d\d\d\d\d.*$") -> list[str]:
        dirs = os.listdir(self.applicationsLocation)
        matchingDirs = []
        for dir in dirs:
            if re.search(regex, dir):
                matchingDirs.append(dir)
        matchingDirs.sort()
        return matchingDirs

    def getAllParameterXml(self) -> list[ParameterFile]:
        appDirs: list[str] = self.getAllApplicationDirs()
        parameterDirs = []
        for appDir in appDirs:
            parameterDir = os.path.join(
                self.applicationsLocation, appDir, "Bewerbung/parameters/parameters.xml")
            if (os.path.isfile(parameterDir)):
                reResult = re.search(r"^(\d\d\d\d\d\d\d\d).*$", appDir)
                if not reResult:
                    continue
                parameterDirs.append(ParameterFile(
                    parameterDir, reResult.group(1)))
        return parameterDirs

    def saveJobListing(self, newDir: str):
        self.inputParameterFile.saveJobListing(
            self.getJobListingLocation(newDir))

    def getJobListingLocation(self, newDir: str) -> str:
        return os.path.abspath(os.path.join(self.applicationsLocation, newDir, "Stellenanzeige", "jobListing.pdf"))
