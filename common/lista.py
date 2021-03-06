#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__="Fernando Castaneda G."
__copyright__="Copyright 2016, UNAM-CERT"
__license__="UNAM CERT"
__version__="1.0"
__status__="Prototype"

import requests
import re
import colors
import requesocks
import untangle
import hashlib
import os
import sqlite3
import reportes


def general(req,target,verbose,archivo):
	lista = []
	vuln = []
	tema(req,target,verbose,archivo,lista,vuln)

def tema(req, target, verbose, archivo, lista, vuln):
	try:
		html = req.get(target).text
		regex = '"theme":"(\w+)"'
		pattern =  re.compile(regex)
		theme = re.findall(pattern,html)
		if theme:
			pwd = os.getcwd()
			c = sqlite3.connect('/opt/druspawn/config/generadores/drupal_vuln.db')
			con = c.cursor()
			respuesta = con.execute("Select v.id_vuln,v.fecha,v.nivel,v.tipo,v.url from vulnerabilidades as v where v.id_proyecto='%s' COLLATE NOCASE"%theme[0].replace('_',' ').title()).fetchall()
			print colors.green('\n[*] ')+"Tema instalado:\n\t %s\n\n"%theme[0] if verbose else '',
			lista.append("<strong>Tema instalado:<strong> %s<br/>"%theme[0])
			if respuesta:
				for a in respuesta:
					if theme in a[1].replace(' ','_').lower():
						print "\tPosible vulnerabilidad:\n\t%s\n"%a[0] if verbose else '',
						cves = con.execute("Select id_cve,url from cve where id_vuln='%s'"%a[0]).fetchall()
						vuln.append([respuesta,cves])
			mod_pagina(req, target, verbose, archivo, lista, vuln)	
		else:
			print colors.red('\n[*] ')+"No se pudo encontrar el tema especifico.\n" if verbose else '',
			lista.append("No se pudo encontrar el tema instalado<br/>")
			mod_pagina(req, target, verbose, archivo, lista, vuln)
	except Exception as e:
		#print e
		mod_pagina(req, target, verbose, archivo, lista, vuln)
		#pass
		

def mod_pagina(req, target, verbose, archivo, lista, vuln):
	pwd = os.getcwd()
	c = sqlite3.connect('/opt/druspawn/config/generadores/drupal_vuln.db')
	con = c.cursor()
	html = req.get(target).text
	lines = html.split('\n')
	lista_mod=[]
	for line in lines:
			line=line.split("modules")
			if len(line)>1 :
				if line[0][-1] == '/' or line[0][-1:] == '\\\\':
					lista_mod.append(line[1].split("/")[1].split("\\")[0])

	if lista_mod:
		print colors.green('[**] ')+"Modulos encontrados en pagina principal: \n" if verbose else '',
		lista.append("<strong>Modulos en pagina: <strong><br/>")
		lista.append('<ul>')
		for modulo in list(set(lista_mod)):
			lista.append("<li>%s</li>"%modulo)
			print colors.blue('[*] ')+"=> "+modulo+'\n' if verbose else '',
			respuesta = con.execute("Select v.id_vuln,v.id_proyecto,v.fecha,v.nivel,v.tipo,v.url from vulnerabilidades as v where v.id_proyecto='%s' COLLATE NOCASE"%modulo.replace('_',' ').title()).fetchall()
			if respuesta:
				if modulo == respuesta[0][1].replace(' ','_').lower():
					cves = con.execute("Select id_cve,url from cve where id_vuln='%s'"%respuesta[0][0]).fetchall()
					print "\tPosible vulnerabilidad:\n\t%s\n"%respuesta[0][0] if verbose else '',
					vuln.append([respuesta,cves])
		#print vuln
		lista.append("</ul>")
	directorios(req, target, verbose, archivo, lista, vuln)

	

def directorios(req, target, verbose, archivo, lista, envio):
	#print envio
	dirs = ['/includes/',
	'/misc/',
	'/modules/',
	'/profiles/',
	'/scripts/',
	'/sites/',
	'/includes/',
	'/themes/',
	'/robots.txt',
	'/xmlrpc.php',
	'/CHANGELOG.txt',
	'/core/CHANGELOG.txt'] 
	i = 0
	print colors.green('\n[***] ')+' Directorios y archivos:\n' if verbose else '',
	lista.append("<strong>Directorios y archivos</strong></br>")
	lista.append("<ul>")
	for d in dirs:
		try:
			i+=1
			print colors.blue('[*] ')+"=> Respuesta("+str(req.get(target+d).status_code)+") para %s \n"%(target+d) if verbose else '',
			lista.append("<li><a href='%s'>%s </a><strong>Respuesta: %s</strong></li>"%(target+d,target+d,str(req.get(target+d).status_code)))
		except Exception as e:
			print e
			print colors.red('[*] ')+"=> Hubo un problema al intentar acceder a %s, posible redireccionamiento \n"%(target+d) if verbose else '',
	lista.append('</ul>')
	if i == 0:
		print colors.green('\t[*] ')+'Wow! no tiene directorios comunes de drupal expuestos o incluso indicios de su existencia!'
		lista.append("<p>Wow! no tiene directorios comunes de drupal expuestos o incluso indicios de su existencia!</p>")
	
	lista.append('<strong>LOGIN: </strong><br/>')
	if req.get(target+'/user/login').status_code == 200 and 'password' in req.get(target+'/user/login').text:
		print colors.green('\n[**] ')+"Pagina para ingreso de usuarios:\n\t %s/user/login\n"%target if verbose else '',
		lista.append('<p><a href="%s">%s</p>'%(target+'/user/login',target+'/user/login'))
	elif req.get(target+'/?q=user/login').status_code == 200 and 'password' in req.get(target+'/?q=user/login').text:
		print colors.green('\n[**] ')+"Pagina para ingreso de usuarios:\n\t %s/?q=user/login\n"%target if verbose else '',
		lista.append('<p><a href="%s">%s</a></p>'%(target+'/?q=user/login',target+'/?q=user/login'))
	
	reportes.listado(archivo,lista)
	if envio:
		reportes.vuln(archivo,envio)

def full_scan(req, target, verbose, reporte):
	try:
		lista = []
		vulnes = []
		pwd = os.getcwd()
		c = sqlite3.connect('/opt/druspawn/config/generadores/drupal_vuln.db')
		con = c.cursor()
		print colors.green('[***] ')+"Full Scan habilitado, esto puede demorar varios minutos..."
		lista.append('<strong>FULL SCAN HABILITADO</strong><br/>')
		murls = ['%s/sites/all/modules/%s/','%s/sites/all/modules/%s/README.txt','%s/sites/all/modules/%s/LICENSE.txt','%s/modules/%s/','%s/modules/%s/README.txt','%s/modules/%s/LICENSE.txt']
		turls = ['%s/sites/all/themes/%s/','%s/sites/all/themes/%s/README.txt','%s/sites/all/themes/%s/LICENSE.txt','%s/themes/%s/','%s/themes/%s/README.txt','%s/themes/%s/LICENSE.txt']
		modulos = [line.rstrip() for line in file("/opt/druspawn/config/modulos.dat").readlines()]
		temas = [line.rstrip() for line in file("/opt/druspawn/config/temas.dat").readlines()]
		encontrado = []
		tmp = con.execute("Select id_proyecto,id_vuln from vulnerabilidades").fetchall()
		c = 0
		for tema in tmp:
			for url in turls:
				if req.get(url%(target,tema[0].replace(' ','_').lower())).status_code in [200,403] and tema[0].replace(' ','_').lower() not in ['',' ','   ']:
					if tema[0].replace(' ','_').lower() not in encontrado:
						encontrado.append(tema[0].replace(' ','_').lower())
						encontrado.append(req.get(url%(target,tema[0].replace(' ','_').lower())).status_code)
					encontrado.append(url%(target,tema[0].replace(' ','_').lower()))
			if c == 600:
				break
			c += 1
		if encontrado:
			print colors.green('\n[**] ')+"TEMAS O MODULOS ENCONTRADOS: "
			lista.append('<strong>TEMAS O MODULOS ENCONTRADOS. </strong><br/>')
			lista. append('<ul>')
			for m in encontrado:
				if 'http' in str(m):
					print '\t\t %s\n'%m if verbose else '',
					lista.append('<strong>Recurso:</strong><a href="%s">%s</a><br/>'%(m,m))
				else:
					print colors.blue('[**] ')+' %s\n'%m if verbose and m not in [200,403] else '',
					if m not in [200,403] and not m in ['',' ','  ',None]:
						lista.append('<li>%s<li>'%m)
						respuesta = con.execute("Select v.id_vuln,v.id_proyecto,v.fecha,v.nivel,v.tipo,v.url from vulnerabilidades as v where v.id_proyecto='%s' COLLATE NOCASE"%m.replace('_',' ').title()).fetchall()
						cves = con.execute("Select id_cve,url from cve where id_vuln='%s'"%respuesta[0][0]).fetchall()
						#print '\t '+cves[0]
						vulnes.append([respuesta,cves])
			lista.append('</ul>')
			con.close()
		else:
			print colors.green('\n\t')+"No se encontraron temas... "
		encontrado = []
		reportes.full(reporte,lista)
		reportes.vuln(reporte,vulnes)
	except Exception as e:
		print e