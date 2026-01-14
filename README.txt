# Sistema Prisional 

Este é um sistema desenvolvido para **gerenciamento prisional**, com funcionalidades como:

- Controle de internos
- Controle de pavilões e blocos
- Controle de sanções disciplinares
- Controle de procedimentos administrativos
- Comunicação de transferências
- Eletrônicos de internos
- Listas personalizadas
- Frentes de trabalho
- Leitura pedagógica
- Comunicação interna
- Relatórios em PDF
- entre outros...

---

## Pré-requisitos

Antes de iniciar, é necessário instalar algumas ferramentas:

**Python (última versão)**  
   [Download Python](https://www.python.org/downloads/)

**Extensões do VS Code recomendadas**:  
   - HTML: `HTML CSS Support`  
   - CSS: `CSS IntelliSense`  
   - Django: `Django` (suporte a templates)


## Configuração do ambiente

### 1. Verificar a versão do Python

python --version
2. Ativar o ambiente virtual
No terminal do VS Code com o repositório aberto:


\venv\Scripts\activate

3. Instalar dependências

pip install -r requirements.txt
Se houver problemas, recrie o ambiente virtual e tente novamente.

4. Configurar IP local
Edite o arquivo hosts no Windows:


C:\Windows\System32\drivers\etc\hosts
5. Configurar Django
No arquivo settings.py do projeto, adicione o IP local aos ALLOWED_HOSTS:


ALLOWED_HOSTS = ['IP_LOCAL', 'localhost', '127.0.0.1']
Substitua IP_LOCAL pelo IP da máquina que deseja usar para rodar o servidor.
