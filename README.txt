

	1 - Baixar o Python ultima versão .
	https://www.python.org/downloads/

	baixar Node js
	https://nodejs.org/pt

	baixar todas as extensões Obs: dentro do Vs Code.
	HTML: Extensão como HTML CSS Support.
	CSS: Extensão CSS IntelliSense.
	Django: Extensão como Django para facilitar o desenvolvimento em templates Django.
	JavaScript: Extensão JavaScript (ES6).
	
	2 - dentro do terminal verificar a versão do python - 
	python --version
	
	3 - já dentro do vscode com o repositorio aberto, ir ao terminal e abrir o 
	ambiente virtual.   digite o comando. 
	\venv\Scripts\activate
	
	4- Após isso instale o requirements.txt 
	Obs: se não instalar pode ser que o o ambiente virual não esteja configurado ou possa ter bugado.
	então sugiro que desinstale atual e reinstale novamente, e assim poderá tentar novamente instalar o requirements.txt
	
	

	5 - Acessar a parta da windows e configurar o ip local
C:\Windows\System32\drivers\etc\hosts

	6 - depois colocar dentro do setings.py do sistema 
ALLOWED_HOSTS = ['IP LOCAL', 'localhost', '127.0.0.1']
Modificar o nome ip local pelo ip da rede da maquina que desejar fazer a configuração paa deixar online o servidor.





	Comando para deixar o banco de dados ativo.. 
usndo o power shell

uvicorn banco_de_dados_upaca.asgi:application --host 10.110.37.178 --port 8000
