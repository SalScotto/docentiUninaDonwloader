#!/usr/bin/python3
# -*- coding: utf-8 -*-

#Used for http requests
import requests
#Used to import the json in the http response
import json
#Used to hide the warnings from the unsigned ssl certificate
from urllib3 import disable_warnings
#Used for making the dirTree (make dir function)
import os
#Used for arguments management
import argparse

#WIP:
from secret import Secret
notStr = lambda s: (type(s) != str)
validate = lambda s: '' if s is None else s
alternativeTyped = lambda a,b,c: a if (a is not None and type(a) == c) else b
alternative = lambda a,b: a if (a is not None) else b

disable_warnings()
from pprint import pprint
#TODO: Try-catch everything!!
class Downloader:

    docente = None
    insegnamento = None
    materiale = None
    status = None

    def __init__(self, _user, _passwd, _path):
        self.user = _user
        self.passwd = _passwd
        self.basePath = _path
        self.session = requests.session()
        self.cookies = {}
        self.baseUrl = "https://www.docenti.unina.it:443/webdocenti-be"
        self.headers = {"User-Agent": "Mozilla/5.0 (X11; rv:70.0) Firefox/70.0", "Accept": "application/json, text/plain, */*", "Accept-Encoding": "gzip, deflate", "Content-Type": "application/json;charset=utf-8", "Origin": "https://www.docenti.unina.it", "Connection": "close", "Referer": "https://www.docenti.unina.it/"}
    

    def __getDownloadUrl(self, folderID):
        return "{}/docenti/{}/materiale-didattico/areapubb/{}?codIns={}".format(self.baseUrl, self.docente, folderID, self.insegnamento)

    def login(self):
        loginUrl = self.baseUrl+"/auth/login-post"
        requestBody = {"username": self.user, "password": self.passwd}
        req = self.session.post(loginUrl, headers=self.headers, cookies=self.cookies, json=requestBody, verify=False)
        self.status = req.status_code
        print(req.status_code)
        if req.status_code == 401:
            print("Credenziali errate")
            exit(5)
        elif req.status_code == 500:
            print("Account non valido")
            exit(6)
        return req.status_code
    
    def __createDirectory(self, path):
        if not os.path.exists(path):
            os.makedirs(path)
    
    def __downloadFile(self, fileID, filename, downloadPath = ""):
        fileUrl = self.baseUrl+"/allegati/materiale-didattico/{}".format(fileID)
        fileContent = self.session.get(fileUrl, headers = self.headers)
        filePath = str(downloadPath) #self.basePath + 
        self.__createDirectory(filePath)
        open("{}/{}".format(filePath, filename), "wb").write(fileContent.content)
    
    def __getDirName(self, dirID, docente, corso = ""):
        url = "{}/docenti/{}/materiale-didattico/areapubb/{}?codIns={}".format(self.baseUrl,docente,dirID,corso)
        resposne = self.session.get(url, headers = self.headers)
        respValues = json.loads(resposne.text)
        if 'error' in respValues:
            if respValues['error'] is None:
                print("Codice cartella non valido")
            elif respValues['code'] == 800 or resposne.status_code == 404:
                print("Risorsa non trovata.")
                print("Prova a controllare il codice docente")
            exit(4)
            raise Exception(respValues["error"])
        dirName = respValues['percorso'][1:]
        return dirName

    def __parseDirectory(self, dirID, dirName, currentPath = ""):
        path = "{}/{}".format(currentPath, dirName)
        dirUrl = self.__getDownloadUrl(dirID, True)
        print(dirUrl)
        response = self.session.get(dirUrl, headers = self.headers, verify = False)
        jsonResponse = json.loads(response.text)
        if jsonResponse['directory'] == False:
            print("{}:{} isn't a Folder".format(dirID, dirName))
            return
        directoryContent = jsonResponse['contenutoCartella']
        for item in directoryContent:
            if item['tipo'] == 'D':
                self.__parseDirectory(item['id'], item['nome'], path)
            else:
                self.__downloadFile(item['id'], item['nome'], path)

    def crawler(self, _docente: str, _materiale: str, _corso: str = ""):
        self.docente = _docente
        self.insegnamento = _corso
        self.materiale = _materiale
        attempts = 3
        while(self.status != 200 and attempts > 0):
            attempts -= 1
            self.login()
        if(attempts <= 0):
            exit(3)
        nomeCorso = self.__getDirName(self.materiale, self.docente, self.insegnamento)
        print("Stai scaricando",nomeCorso)
        self.__parseDirectory(self.materiale, nomeCorso, self.basePath)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="Docenti Unina",
        usage="TODO",
        description="Un qualcosa che funziona male per scaricare i file da www.docenti.unina.it. Inserisci le credenziali nel file secret.py",
        epilog="Semplice, no?"
    )
    parser.add_argument("-f", "--folder", dest="Path", help="Percorso della castella dove scaricare i file [Default %(default)s]", type=str, default=".", required=False)
    parser.add_argument("-d", "--docente", dest="Docente", help="ID del docente associato al corso", type=str, required=True)
    parser.add_argument("-m", "--materiale", dest="Materia", help="ID della cartella del corso da scaricare", type=str, required=True)
    parser.add_argument("-c", "--corso", dest="Corso", help="ID del corso associato alla cartella [Opzionale]", type=str, required=False)

    args = parser.parse_args()

    u = Secret.username
    p = Secret.password
    f = args.Path
    d = args.Docente
    m = args.Materia
    c = "" if args.Corso is None else args.Corso
    scaricatoreDiPorti = Downloader(u, p, f)
    r = scaricatoreDiPorti.login()
    scaricatoreDiPorti.crawler(d, m, c)
