#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__="Fernando Castaneda G."
__copyright__="Copyright 2016, UNAM-CERT"
__license__="GPL"
__version__="0.1"
__status__="Prototype"

import requests
import requesocks
import colors
import sys
import sqlite3
import commands
import os
from requests.packages.urllib3.exceptions import InsecureRequestWarning


def session_parameters(tor=False,user_agent='',verbose=False,proxy=''):
	requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
	if proxy is not '' and tor:
		print colors.yellow('\b[**] ')+"Debe elegir solo una de las opciones, proxy o tor"
		sys.exit()
	if tor:
		p = commands.getoutput("ps -e|grep tor|wc -l")
		if '1' in p:
			os.system("sudo service tor restart")
		elif '0' in p:
			os.system("sudo service tor start")
		print colors.green('\b[*] ')+"Utilizando tor..."
		s = requesocks.Session()
		s.proxies = {'http':  'socks5://127.0.0.1:9050','https': 'socks5://127.0.0.1:9050'}
		if user_agent is not '':
			s.headers = {'User-agent':user_agent[:-1]}
			allow_redirects=False
		print colors.green('[*] ')+" Se asigno la IP: "+s.get('http://ipecho.net/plain').text+"\n" if verbose else '',
		s.verify=False
		return s
	if proxy is not '':
		s = requests.Session()
		s.proxies = s.proxies = {'http': proxy, 'https': proxy}
		if user_agent is not '':
			s.headers = {'User-agent':user_agent[:-1]}
			allow_redirects=False
		print colors.green('[*] ')+" Se esta utilizando la IP: "+s.get('http://ipecho.net/plain').text+"\n" if verbose else '',
		s.verify=False
		return s
	else:
		s = requests.Session()
		if user_agent is not '':
			s.headers = {'User-agent':user_agent[:-1]}
		s.verify=False
		return s
