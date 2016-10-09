#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__="Fernando Castaneda G."
__copyright__="Copyright 2016, UNAM-CERT"
__license__="GPL"
__version__="0.1"
__status__="Prototype"

import common.version as version
import common.lista as listar
import common.session as session
import argparse
import colors
import os

if __name__=="__main__":
    parser = argparse.ArgumentParser(description='Scanner de vulnerabilidades \
    para DRUPAL :D')

    parser.add_argument('-d', required=True, nargs=1, help="Direccion de objetivo")
    parser.add_argument('--listar', action="store_true", help="Lista directorios expuestos y configuraciones de Drupal.")
    parser.add_argument('-p', nargs=1,help="Emplea un proxy, con el fin de mantener el anonimato")
    parser.add_argument('-u', nargs=1, help="Se especifica un user-agent a traves de un archivo")
    parser.add_argument('--ssl',action="store_true",help="conexion cifrada")
    parser.add_argument('--tor',action="store_true",help="Emplea tor como proxy, con el fin de mantener el anonimato")
    parser.add_argument('--verbose','-v',action="store_true",help="Habilita el modo verboso")

    
    verbose=False
    useragent=''
    arguments = parser.parse_args()
    proxy = ''

    if arguments.verbose:
      verbose=True
      print colors.yellow('[**] ')+"Modo verboso habilitado"

    if arguments.p:
      proxy = arguments.p[0]
      print colors.yellow('[**] ')+"Empleando \"%s\" como proxy"%proxy

    if arguments.u:
      f=open(arguments.u[0])
      useragent=f.read()
      print colors.yellow('[**] ')+"Empleando \"%s\" como User-agent"%useragent[:-1]

    req = session.session_parameters(arguments.tor,useragent,arguments.verbose, proxy)

    if arguments.d:
      print colors.blue('[**] ')+"Inicializando escaneo a %s"%arguments.d[0]
      if 'http' not in arguments.d[0] and not arguments.ssl:
        arguments.d[0]='http://'+arguments.d[0]
      if 'https' not in arguments.d[0] and arguments.ssl:
        arguments.d[0]='https://'+arguments.d[0]
      version.version(req,arguments.d[0],arguments.verbose)
      listar.tema(req,arguments.d[0],arguments.verbose)