#!/bin/sh

#***************************#
#	druspawn INSTALLER  #
#			    #
#	Fernando C.G.	    #
#			    #
#     Este cuadro no dice   #
#    nada importante, pero  #
#     es un buen cliche...  #
#***************************#

instalador () {
	sudo pip install requests 
	sudo pip install requesocks
	sudo pip install requests[socks]
	sudo pip install ansicolors
	sudo pip install untangle
	sudo pip install BeautifulSoup 
	sudo pip install bs4
	sudo chmod 777 ./*
	echo "CREANDO DIRECTORIO /opt/druspawn"
	sudo mkdir -pm 777 /opt/druspawn
	echo "CREANDO DIRECTORIO PARA USUARIO..."
	for dir in /home/*/
	do
		if [ -d $dir.druspawn ];
		then
			echo "Se mantendran directorios en $dir de instalacion previa..."
		else
			mkdir -pm 777 $dir.druspawn/
			echo "Creando $dir.druspawn/"
			mkdir -pm 777 $dir.druspawn/logs
			echo "Creando $dir.druspawn/logs"
			mkdir -pm 777 $dir.druspawn/reportes
			echo "Creando $dir.druspawn/reportes"
		fi
	done
	if [ -d /root/.druspawn ];
		then
			echo "Se mantendran directorios en /root/.druspawn de instalacion previa..."
		else
			echo "Instalando directorios en /root/ para superusuario..."
			sudo mkdir -pm 777 /root/.druspawn/logs /root/.druspawn/reportes
		fi	
	echo "Moviendo archivos necesarios a /opt/druspawn"
	sudo cp -rf ./* /opt/druspawn
	sudo cp ./druspawn /bin/
	sudo chmod 777 /bin/druspawn
	cd /opt/druspawn/config/generadores
	echo "¿Desea utilizar la base de datos que viene con el programa, o desea crear una propia?[ Ingrese S para crearla, cualquier otro caracter para utilizar la base de datos por defecto. ]"
	read valor
	if [ $valor = 'S' ] || [ $valor = 's' ];
	then
		cd /opt/druspawn/config/generadores
		rm -rf drupal_vuln.db
		echo "CREANDO LA BASE DE DATOS, ESTO PUEDE TOMAR MUCHO TIEMPO, PUEDE IN POR UN CAFE :)"
		sudo rm -f drupal_vuln.db
		sudo rm -f drupal_vuln
		sudo sqlite3 drupal_vuln.db < drupal_vuln.sql
		sudo python fill_db.py
		sudo python crear_diccionarios.py
	else
		cd /opt/druspawn/config/generadores
	fi
	echo "\nINSTALACION FINALIZADA, DISFRUTE :)"
}

if [ -d /opt/druspawn ];
then
	echo "Ya se encuentra instalado en el equipo"
else
	if [ $(grep debian /etc/*release|wc -l) ] || [ $(grep kali /etc/*release|wc -l) ];
	then
		sudo apt-get update
		sudo apt-get install -y python-pip tor sqlite3
		instalador
	elif [ $(grep Ubuntu /etc/*release) ];
	then
		if [ $(lsb_release -a|grep precise|wc -l) ];
		then
			sudo deb http://deb.torproject.org/torproject.org precise main
			sudo deb-src http://deb.torproject.org/torproject.org precise main
		elif [ $(lsb_release -a|grep trusty|wc -l) ];
		then 
			sudo deb http://deb.torproject.org/torproject.org trusty main
			sudo deb-src http://deb.torproject.org/torproject.org trusty main
		elif [ $(lsb_release -a|grep trusty|wc -l) ]; 
		then
			sudo deb http://deb.torproject.org/torproject.org xenial main
			sudo deb-src http://deb.torproject.org/torproject.org xenial main
		else 
			echo "No se puede instar TOR en este equipo..."
		fi
		sudo apt-get update
		sudo apt-get install -y python-pip tor sqlite3 deb.torproject.org-keyring
		instalador
	elif [ $(grep fedora /etc/*release|wc -l) ] || [ $(grep centos /etc/*release|wc -l) ];
	then
		sudo wget https://www.torproject.org/dist/tor-0.2.8.9.tar.gz
		sudo tar xzf tor-0.2.8.9.tar.gz; 
		cd tor-0.2.8.9
		sudo ./configure && make
		cd ..
		sudo rm -rf tor-0.2.8.9
		sudo yum install -y python-pip sqlite3
		instalador
	else
		echo "La herramienta no soporta tu distribucion, aun..."
	fi
fi
