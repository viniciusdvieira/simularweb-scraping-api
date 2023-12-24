# simularweb-scraping-api

simularweb-scraping-api é uma api utilizando selenium para fazer o webscraping da [similarweb](https://www.similarweb.com/pt/)

## Installation

Clone este repositorio em seu computador para utilizalo ou baixe o seu zip.

```bash
git clone https://github.com/viniciusdvieira/simularweb-scraping-api.git
```

## Usage

### Instale a requetiments.txt 

```bash
pip install -r requirements.txt
```
Inicie o script flask!
```bash
python app.py
```
Utilize ferramentas para testar a api como postman ou cURL e tenha o mongoDB instalado

Crie uma nova workspace em modo HTTPO
### Endpoints

 `POST /salve_info`:
link da api `http://127.0.0.1:5000/salve_info`

`POST /get_info`:
link da api `http://127.0.0.1:5000/get_info`

### Exemplo de uso
No corpo body do postman selecione o raw 
```JSON
[
  { "url": "instagram.com" },
  { "url": "globo.com" },
  { "url": "live.com" }
]
```
isso funciona tanto na salve_info quanto na get_info
