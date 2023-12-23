from flask import Flask, jsonify, request
from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep
import re
from pymongo import MongoClient

app = Flask(__name__)

# Conectar ao MongoDB
cliente = MongoClient('mongodb://localhost:27017/')
banco_dados = cliente['dados_similarweb']
colecao = banco_dados['dados_website']

def extrair_dados_similarweb(url):
    driver = webdriver.Chrome()
    driver.get(f'https://www.similarweb.com/website/{url}')
    sleep(5)

    # Seu código de extração de dados aqui

    # Exemplo: Coletar o título
    title_element = driver.find_element(By.XPATH, "//p[@class='wa-overview__title']")
    title_text = title_element.text

    # Exemplo: Coletar a classificação global
    classificacao_global_element = driver.find_element(By.XPATH, "//p[@class='wa-rank-list__value']")
    classificacao_global_text = classificacao_global_element.text

    # Exemplo: Coletar a categoria
    categoria_elements = driver.find_elements(By.XPATH, "//div[@class='wa-rank-list__info']")
    categoria_element = categoria_elements[1]
    categoria_text = categoria_element.text
    categoria_text_sem_parenteses = re.sub(r'\([^)]*\)', '', categoria_text)

    # Exemplo: Mudança de Ranking
    rank_elements = driver.find_elements(By.XPATH, "//span[@class='app-parameter-change app-parameter-change--md app-parameter-change--down']")
    rank_directions = []
    rank_texts = []
    if rank_elements:
        for rank_element in rank_elements:
            rank_text = rank_element.text
            if 'M2.25 4.5h7.5L6 8.25Z' in rank_element.get_attribute('outerHTML'):
                rank_direction = 'Aumentou'
            else:
                rank_direction = 'Diminuiu'
            rank_texts.append(rank_text)
            rank_directions.append(rank_direction)

    # Exemplo: Total de Visitas
    total_elements = driver.find_elements(By.XPATH, "//p[@class='engagement-list__item-value']")
    total_element = total_elements[0]
    total_text = total_element.text

    # Exemplo: Duração Média da Visita
    duracao_elements = driver.find_elements(By.XPATH, "//p[@class='engagement-list__item-value']")
    duracao_element = duracao_elements[3]
    duracao_text = duracao_element.text

    # Exemplo: Páginas por Visita
    pagina_elements = driver.find_elements(By.XPATH, "//p[@class='engagement-list__item-value']")
    pagina_element = pagina_elements[2]
    pagina_text = pagina_element.text

    # Exemplo: Taxa de Rejeição
    taxa_elements = driver.find_elements(By.XPATH, "//p[@class='engagement-list__item-value']")
    taxa_element = taxa_elements[1]
    taxa_text = taxa_element.text

    # Exemplo: Principais Países
    paises_elements = driver.find_elements(By.XPATH, "//a[@class='wa-geography__country-name']")
    paises_text = [element.text for element in paises_elements]
    porcentagem_pais_elements = driver.find_elements(By.XPATH, "//span[@class='wa-geography__country-traffic-value']")
    porcentagem_pais_text = [element2.text for element2 in porcentagem_pais_elements]

    # Exemplo: Distribuição por Gênero
    genero_feminino_element = driver.find_element(By.XPATH, "//li[@class='wa-demographics__gender-legend-item wa-demographics__gender-legend-item--female']")
    genero_feminino_text = genero_feminino_element.text
    genero_masculino_element = driver.find_element(By.XPATH, "//li[@class='wa-demographics__gender-legend-item wa-demographics__gender-legend-item--male']")
    genero_masculino_text = genero_masculino_element.text

    # Exemplo: Distribuição por idade
    script = """
    var elements = document.querySelectorAll('tspan.wa-demographics__age-data-label');
    var textArray = [];
    elements.forEach(function(element) {
        textArray.push(element.textContent);
    });
    return textArray;
    """
    porcentagem_idade_text = driver.execute_script(script)
    faixas_etarias = ["18 - 24", "25 - 34", "35 - 44", "45 - 54", "55 - 64", "65+"]

    driver.quit()

    # Armazenar dados no MongoDB
    dados_website = {
        "url": url,
        "titulo": title_text,
        "classificacao_global": classificacao_global_text,
        "categoria": categoria_text_sem_parenteses.strip(),
        "mudanca_rank": [{"direcao": direcao, "valor": valor} for direcao, valor in zip(rank_directions, rank_texts)],
        "total_visitas": total_text,
        "duracao_media_visita": duracao_text,
        "paginas_por_visita": pagina_text,
        "taxa_rejeicao": taxa_text,
        "principais_paises": [{"pais": pais, "porcentagem": porcentagem} for pais, porcentagem in zip(paises_text[:7], porcentagem_pais_text[:6])],
        "distribuicao_genero": {"feminino": genero_feminino_text.split()[1], "masculino": genero_masculino_text.split()[1]},
        "distribuicao_idade": {faixa: porcentagem for faixa, porcentagem in zip(faixas_etarias, porcentagem_idade_text)}
    }

    colecao.insert_one(dados_website)

    dados_website['_id'] = str(dados_website['_id'])
    
    return dados_website

# Rota para extrair e armazenar dados
@app.route('/salve_info', methods=['POST'])
def salve_info():
    try:
        data = request.get_json()
        url = data.get('url')
        if not url:
            raise ValueError("A URL não foi fornecida.")

        extrair_dados_similarweb(url)
        return jsonify({'success': True, 'message': 'Informações salvas no banco com sucesso.'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e), 'message': 'Falha ao salvar as informações no banco.'})

# Rota para buscar informações do banco de dados
@app.route('/get_info', methods=['POST'])
def get_info():
    try:
        data = request.get_json()
        url = data.get('url')
        if not url:
            raise ValueError("A URL não foi fornecida.")

        dados_website = colecao.find_one({'url': url})
        if dados_website:
            # Converter ObjectId para uma string antes de retornar JSON
            dados_website['_id'] = str(dados_website['_id'])
            return jsonify({'success': True, 'data': dados_website})
        else:
            return jsonify({'success': False, 'error': 'As informações não estão disponíveis no banco de dados.'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)
    cliente.close()
