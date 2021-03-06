import pandas as pd 
import numpy as np
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from random import randint
from time import sleep,time
import csv
import os.path

def obtenerNoticias(text):
	soup = BeautifulSoup(text,features='lxml')
	h4 = soup.find_all("h4", {"class": "is-display-inline title-list"})
	noticias = []
	for elem in h4:
		a = elem.find("a",href=True)
		titulo = a.text
		href = "https://www.pagina12.com.ar"+a['href']
		noticias.append([titulo,href])
	return noticias

def pagina12spider(max_pages,seccion,filename,pag_inicio=None):
	print("extrayendo "+str(seccion))
	if pag_inicio == None:
		page=0
	else:
		page=pag_inicio
		max_pages = max_pages+pag_inicio
	while page <= max_pages:
		url = "https://www.pagina12.com.ar/secciones/"+str(seccion)+"?page="+str(page)
		h = {'user-agent':"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36"}
		html = requests.get(url,headers=h).text
		noticias = obtenerNoticias(html)
		noticias = [x.insert(0,url) or x for x in noticias]
		file_exists = os.path.isfile(filename)
		with open (filename, 'a', encoding='utf-8') as csvfile:
			headers = ["pagSeccion","titulo","href"]
			writer = csv.DictWriter(csvfile, delimiter=';', lineterminator='\n',fieldnames=headers)
			if not file_exists:
				writer.writeheader()
			for notic in noticias:
				writer.writerow({'pagSeccion':notic[0], 'titulo':notic[1],'href':notic[2]})
		### Extraer los elementos de interes
		sleep(randint(50,100)/100+0.5)

		page +=1

def obtenerCuerpoNoticias(url):
	h = {'user-agent':"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36"}
	r = requests.get(url,headers=h)
	if r.status_code == 200:
		print(url,r,r.status_code)
	else:
		print(url,"_____",r.status_code,"______", r.text)
	html = r.text
	soup = BeautifulSoup(html,features='lxml')
	texto = []
	time = soup.find("time").text
	div = soup.find("div", {"class": "article-main-content article-text"})
	if div == None:
		div = soup.find("div", {"class": "article-main-content article-text "})
		if div == None:
			div = soup.find("div", {"class": "article-main-content article-text no-main-image"})
			if div == None:
				div = soup.find("div", {"class": "article-main-content article-text no-main-image "})
	p = div.find_all("p")
	for elem in p:
		texto.append(elem.text)
	cuerpo = " ".join(texto)

	sleep(randint(70,200)/100)

	return cuerpo,time

def generarListasUrls(listaCsvs):
	listaDF =[]
	for csv in listaCsvs:
		df = pd.read_csv(csv,sep=";")
		df[['pagSeccion','borrar']] = df['pagSeccion'].str.replace("https://www.pagina12.com.ar/secciones/","").str.split('?', expand=True)
		del df['borrar']
		df.columns = ['clase', 'titulo','url']
		df = df[['url','clase','titulo']]
		listaUrls = df.values.tolist()
		listaDF.extend(listaUrls)

	return listaDF

def extraccionDataNoticias(listaUrls,filename):
	##Lista urls es una lista asi: [url,clase,titulo]
	for elem in listaUrls:
		url = elem[0]
		clase = elem[1]
		titulo = elem[2]
		cuerpo,time = obtenerCuerpoNoticias(url)
		file_exists = os.path.isfile(filename)
		with open (filename, 'a', encoding='utf-8') as csvfile:
			headers = ["url","titulo","fecha", "cuerpoNoticia","clase"]
			writer = csv.DictWriter(csvfile, delimiter=';', lineterminator='\n',fieldnames=headers)
			if not file_exists:
				writer.writeheader()
			writer.writerow({'url':url, 'titulo':titulo, 'fecha':time, 'cuerpoNoticia':cuerpo,'clase':clase})

if __name__ == '__main__':
	start_time = time()
	pagina12spider(300,"el-pais","urlsPais.csv")
	pagina12spider(300,"economia","urlsEconomia.csv")
	pagina12spider(300,"el-mundo","urlsMundo.csv") 
	lista = generarListasUrls(["urlsPais.csv"])
	extraccionDataNoticias(lista,'dataset.csv')
	sleep(60*5)
	lista = generarListasUrls(["urlsEconomia.csv"])
	extraccionDataNoticias(lista,'dataset.csv')
	sleep(60*5)
	lista = generarListasUrls(["urlsMundo.csv"])
	extraccionDataNoticias(lista,'dataset.csv')
	#Validacion
	pagina12spider(10,"el-pais","urlsPaisValidacion.csv",400)
	pagina12spider(10,"economia","urlsEconomiaValidacion.csv",400)
	pagina12spider(10,"el-mundo","urlsMundoValidacion.csv",400)
	listaVal = generarListasUrls(["urlsPaisValidacion.csv","urlsEconomiaValidacion.csv","urlsMundoValidacion.csv"])
	extraccionDataNoticias(listaVal,'datasetVal.csv')

	print("--- %s seconds ---" % (time() - start_time))