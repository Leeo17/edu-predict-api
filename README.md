# Edu Predict API

Este é o back-end do Edu Predict, um projeto que usa Machine Learning para determinar um índice de potencial evasão de estudantes da UFPR. Para usar o Edu Predict, você pode seguir os passos abaixo para rodar a API do projeto localmente ou acessar o seguinte site em que ela está hospedada: [https://edu-predict-api-a5d21e2f0917.herokuapp.com/docs](https://edu-predict-api-a5d21e2f0917.herokuapp.com/docs).

## 1. Instalar o Python

Este projeto foi desenvolvido usando a linguagem Python e, portanto, é necessário instala-lá em seu sistema. A versão do Python usada foi a 3.12, que pode ser baixada através do link [https://www.python.org/downloads/release/python-3120/](https://www.python.org/downloads/release/python-3120/). Certifique-se de marcar a opção "Adicionar Python 3.12 ao PATH" durante a instalação.

## 2. Clonar o repositório do projeto

Clone o repositório do projeto usando o Git através do seguinte comando:

`git clone https://github.com/Leeo17/edu-predict-api.git`

## 4. Navegue até o diretório do projeto

Abra o terminal ou prompt de comando no diretório clonado anteriormente.

## 5. Configuração do Ambiente Virtual (Opcional, mas recomendado)

1. Instale o virtualenv com o seguinte comando (se ainda não estiver instalado):

   `pip install virtualenv`

2. Crie um ambiente virtual

   - No Windows:

     `.\venv\Scripts\activate`

   - No Linux ou macOS:

     `source venv/bin/activate`

## 6. Instale as dependências do projeto

Execute o seguinte comando para instalar as dependências do projeto usando o pip:

`pip install -r requirements.txt`

## 6. Configure o .env

Mova o arquivo `.env` para a pasta raiz deste repositório. O arquivo `.env` deve ter sido enviado junto ao link de compartilhamento do código fonte e do PDF do projeto.

## 8. Rode o projeto

Utilize o seguinte comando para rodar o projeto:

`uvicorn app.main:app --reload`

- `app.main` refere-se caminho do arquivo `main.py` sem a extensão. Ou seja, o arquivo `main.py` está dentro da pasta `app`.
- O segundo `app` refere-se à instância do FastAPI criada no arquivo.
- A opção `--reload` é usada para que o servidor seja reiniciado automaticamente sempre que o código for alterado.

## 9. Testar a API

Abra um navegador da web no seguinte endereço:

[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

A ferramenta Swagger UI será apresentada. Ela oferece uma interface interativa para explorar e testar os endpoints da API.
