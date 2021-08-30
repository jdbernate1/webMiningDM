import pandas as pd 
import numpy as np
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from random import randint
from time import sleep
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

def pagina12spider(max_pages,seccion,filename):
	print("extrayendo "+str(seccion))
	page=0
	while page <= max_pages:
		url = "https://www.pagina12.com.ar/secciones/"+str(seccion)+"?page="+str(page)
		html = requests.get(url).text
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
	r = requests.get(url)
	if r.status_code == 200:
		print(url,r,r.status_code)
	else:
		print(url,"_____",r.status_code,"______", r.text)
	html = r.text
	soup = BeautifulSoup(html,features='lxml')
	texto = []
	div = soup.find("div", {"class": "article-main-content article-text"})
	if div == None:
		div = soup.find("div", {"class": "article-main-content article-text no-main-image"})
	p = div.find_all("p")
	for elem in p:
		texto.append(elem.text)
	cuerpo = " ".join(texto)

	sleep(randint(55,90)/100)

	return cuerpo

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
		cuerpo = obtenerCuerpoNoticias(url)
		file_exists = os.path.isfile(filename)
		with open (filename, 'a', encoding='utf-8') as csvfile:
			headers = ["url","titulo", "cuerpoNoticia","clase"]
			writer = csv.DictWriter(csvfile, delimiter=';', lineterminator='\n',fieldnames=headers)
			if not file_exists:
				writer.writeheader()
			writer.writerow({'url':url, 'titulo':titulo, 'cuerpoNoticia':cuerpo,'clase':clase})


if __name__ == '__main__':
	pagina12spider(150,"sociedad","urlsSociedad.csv")
	pagina12spider(150,"economia","urlsEconomia.csv")
	pagina12spider(150,"deportes","urlsDeportes.csv")
	lista = generarListasUrls(["urlsSociedad.csv","urlsEconomia.csv","urlsDeportes.csv"])
	extraccionDataNoticias(lista,'dataset.csv')

