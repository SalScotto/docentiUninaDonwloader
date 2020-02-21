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
alternativeTyped = lambda a,b,c: a if (a is not None and type(a) is c) else b
alternative = lambda a,b: a if (a is not None) else b

disable_warnings()

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

    def __getUrl(self, doc: str, fold: str, codIns: str = "") -> str:
        if notStr(doc) or notStr(fold) or notStr(codIns):
            raise TypeError
        return "{}/docenti/{}/materiale-didattico/{}?codIns={}".format(self.baseUrl, doc, fold, codIns)
    
    def __getDownloadUrl(self, folderID):
        return self.__getUrl(self.docente, folderID, self.insegnamento)

    def login(self):
        loginUrl = self.baseUrl+"/auth/login-post"
        requestBody = {"username": self.user, "password": self.passwd}
        req = self.session.post(loginUrl, headers=self.headers, cookies=self.cookies, json=requestBody, verify=False)
        self.status = req.status_code
        return req.status_code
    
    def __createDirectory(self, path):
        if not os.path.exists(path):
            os.makedirs(path)
    
    def __downloadFile(self, fileID, filename, downloadPath = ""):
        fileUrl = self.baseUrl+"/allegati/materiale-didattico/{}".format(fileID)
        fileContent = self.session.get(fileUrl, headers = self.headers)
        filePath = self.basePath + str(downloadPath)
        self.__createDirectory(filePath)
        open("{}/{}".format(filePath, filename), "wb").write(fileContent.content)
    
    def __getDirName(self, dirID, docente, corso = ""):
        url = "{}/docenti/{}/materiale-didattico/areapubb/{}?codIns?{}".format(self.baseUrl,docente,dirID,corso)
        resposne = self.session.get(url, headers = self.headers)
        respValues = json.loads(resposne.text)
        dirName = respValues['percorso'][1:]
        return dirName

    def __parseDirectory(self, dirID, dirName, currentPath = ""):
        path = "{}/{}".format(currentPath, dirName)
        dirUrl = self.__getDownloadUrl(dirID)
        response = self.session.get(dirUrl, headers = self.headers, verify = False)
        jsonResponse = json.loads(response.text)
        if jsonResponse['directory'] is False:
            print("{}:{} is not a Folder".format(dirID, dirName))
            return
        directoryContent = jsonResponse['contenutoCartella']
        for item in directoryContent:
            if item['tipo'] is 'D':
                self.__parseDirectory(item['id'], item['nome'], path)
            else:
                self.__downloadFile(item['id'], item['nome'], path)

    def crawler(self, _docente: str, _materiale: str, _corso: str = ""):
        self.docente = _docente
        self.insegnamento = _corso
        self.materiale = _materiale
        attempts = 3
        while(self.status != 200 or attempts > 0):
            attempts -= 1
            self.login()
        if(attempts <= 0):
            exit(3)
        nomeCorso = self.__getDirName(self.materiale, self.docente, self.insegnamento)
        self.__parseDirectory(self.materiale, nomeCorso, self.basePath)

if __name__ == "__main__":
    u = Secret.username
    p = Secret.password
    scaricatoreDiPorti = Downloader(u, p, "testDev")
    r = scaricatoreDiPorti.login()
    print(r)
