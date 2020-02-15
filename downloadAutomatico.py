#!/usr/bin/python3

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

#Object used to save the requests session cookies
session = requests.session()

#Set Username and Password of your user, needed to verify that you're enabled to open it's private folders
username = ""
password = ""

#For hiding ssl-related warnings
disable_warnings()

#Name of the base folder where to recreate the directory tree
baseFolder = ""
#Starting id of the folder to download,:last bit of the url, before get patameters)
startingFolderID = ""

#ID of the professor, got from the url as from below
docente = ""

endUrl = "?codIns="
#Url structured used for the requests
baseUrl = "https://www.docenti.unina.it:443/webdocenti-be/docenti/"+str(docente)+"/materiale-didattico/areapubb/"

#Check for existing directory, if it doesn't, it will create all the tree
def checkDir(path):
    print("Verifico",path)
    if not os.path.exists(path):
        print("Creo", path)
        os.makedirs(path)

#Download the given file, knowing both its name, id and save path
def scaricaFile(nome,id, path = ""):
    #Creating the full url neded to download the file
    fileUrl = "https://www.docenti.unina.it:443/webdocenti-be/allegati/materiale-didattico/"+str(id)
    #Get the file content
    fileContent = session.get(fileUrl, headers = burp0_headers)
    pathFile = baseFolder + str(path)
    #Create the full directory path if needed
    checkDir(pathFile)
    #Write the file content in its path
    open(str(pathFile)+"/"+str(nome),"wb").write(fileContent.content)
    print("File",nome,"scaricato")

#Crawling recursively the given directory and all its subfolder, downloading contained files
def navigaDirectory(id, nome, pathCorrente = ""):
    #Current crawled path
    path = pathCorrente + "/" + nome
    urlDirectory = baseUrl + str(id) + endUrl
    #Get the path content
    response = session.get(urlDirectory, headers = burp0_headers, verify = False)
    #Load the json response
    dirContent = json.loads(response.text)
    #For each element in the directory
    for item in dirContent['contenutoCartella']:
        if item['tipo'] is 'D':
            #If it's a directory, open it and download its content
            print("Entro nella cartella ", item["nome"], "@", item["id"])
            navigaDirectory(item["id"], item["nome"], path)
        else:
            #If it's a file, download it
            print("In", id, "File", item["nome"], "@", item["id"], "#", item["tipo"])
            scaricaFile(item["nome"],item["id"], path)

#Base URL fot the login
burp0_url = "https://www.docenti.unina.it:443/webdocenti-be/auth/login-post"
#Starting session cookies
burp0_cookies = {}
#Headers needed in order to fool the browser check and create valid requests
burp0_headers = {"User-Agent": "Mozilla/5.0 (X11; rv:70.0) Firefox/70.0", "Accept": "application/json, text/plain, */*", "Accept-Encoding": "gzip, deflate", "Content-Type": "application/json;charset=utf-8", "Origin": "https://www.docenti.unina.it", "Connection": "close", "Referer": "https://www.docenti.unina.it/"}
#Login parameters request
burp0_json={"password": password, "username": username}
#Requesto to do the login
r1 = session.post(burp0_url, headers=burp0_headers, cookies=burp0_cookies, json=burp0_json, verify=False)


def crawler():
    #Starting url for the crawler
    burp0_url = baseUrl+str(startingFolderID)+endUrl
    #Get the first folder content
    r = session.get(burp0_url, headers=burp0_headers)
    dirTree = json.loads(r.text)
    #Same as navigaDirectory (then why I've made different functions? idk)
    if dirTree['directory'] is True:
        for item in dirTree['contenutoCartella']:
            if item['tipo'] is 'D':
                print("Entro nella cartella ", item["nome"], "@", item["id"])
                navigaDirectory(item["id"], item["nome"])
            else:
                print("Il file",item["nome"], "ha id", item["id"])
                scaricaFile(item["nome"],item["id"], "")
    else:
        #You gave me a wrong identifier
        print("startingFolderID può essere solo l'identificativo di una cartella per il quale hai i diritti di accesso")


#TODO: check if the login is valid
#TODO: check if the user has the right to access the "startingFolder" course
#TODO: Search for Course code and Professor Code

def todo():
    nome = ""
    burp0_url = "https://www.docenti.unina.it:443/webdocenti-be/docenti?nome="+str(nome)
    res = session.get(burp0_url, headers=burp0_headers)
    docenti = json.loads(res.text)
    """
    Struttura risposta:
    public class Docente {
        public String id;
        public String nome;
        public String cognome;
        public String dipartimento;
        public String codicefiscale;
    }

    public class Risposta {
        public List<Docente> docenti;
        public boolean last;
        public int totalElements;
        public int totalPages;
        public object sort;
        public int numberOfElements;
        public boolean first;
        public int size;
        public int number;
    }
    """

    burp0_url = "https://www.docenti.unina.it:443/webdocenti-be/docenti/"+str(docente)+"/materiale-didattico/areapubb/?codIns="
    response = session.get(burp0_url, headers=burp0_headers)
    corsi = json.loads(response.text)
    """
    Risposta; List<Corso>
    public class Corso {
        public String nome;
        public int id;
        public boolean pubblica;
        public boolean libera;
        public String tipo;
        public String percorso;
        public boolean cancella;
        public String codInse;
    }
    """
    print(docenti, corsi)


#TODO: fix lambda function
validate = lambda s: '' if s is None else s

#TODO: Add argument-based input
def main(argv):
    username = validate(argv.user)
    password = validate(argv.password)
    startingFolderID = validate(argv.corso)
    docente = validate(argv.docente)
    baseFolder = validate(argv.path)
    #If needed parameters are not set, stop code execution
    if(len(username) is 0 or len(password) is 0 or len(startingFolderID) is 0 or len(docente) is 0 or len(baseFolder) is 0):
        print("Parametri non settati")
        exit(2)
    
    crawler()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="Docenti Unina Donwloader",usage="TODO")
    parser.add_argument('-u', '--user', dest="User", help="Username per l'accesso su docenti.unina.it", type=str, required=True)
    parser.add_argument('-p', '--password', dest="Password", help="Password per l'accesso", type=str, required=True)
    parser.add_argument('-f', '--folder', dest="Path", help="Percorso della cartella dove scaricare i file (Default: %(default)s)", type=str, default=".", required=False)
    parser.add_argument('-d', '--docente', dest="Docente", help="Id del docente associato al corso", type=str, required=True)
    parser.add_argument('-c', '--corso', dest="Corso", help="Id del corso associato al materiale didattico o della relativa cartella", type=str, required=True)
    args = parser.parse_args()
    main(args)
