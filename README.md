### MicroServicio para el estudio de
~~~
	- proxy.
	- proxy inverso.
	- balanceador de carga.
	- persistencia de sesiones.
~~~

#### Levantar 3 replicas con podman
~~~bash
$ podman run -d --rm -it -p 5001:5001 formatcom/miniserver --port 5001
$ podman run -d --rm -it -p 5002:5002 formatcom/miniserver --port 5002
$ podman run -d --rm -it -p 5003:5003 formatcom/miniserver --port 5003
~~~

#### Levantar 3 replicas con docker
~~~bash
$ docker run -d --rm -it -p 5001:5001 formatcom/miniserver --port 5001
$ docker run -d --rm -it -p 5002:5002 formatcom/miniserver --port 5002
$ docker run -d --rm -it -p 5003:5003 formatcom/miniserver --port 5003
~~~
