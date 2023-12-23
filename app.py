from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep
import re
from pymongo import MongoClient

# Conectar ao MongoDB
cliente = MongoClient('mongodb://localhost:27017/')
banco_dados = cliente['dados_similarweb']
colecao = banco_dados['dados_website']


driver = webdriver.Chrome()
driver.get('https://www.similarweb.com/pt/website/google.com')
sleep(5)

#Titulo do site
title_element = driver.find_element(By.XPATH, "//p[@class='wa-overview__title']")
title_text = title_element.text
print("Titulo:", title_text)

#classficações
classificacao_global_element = driver.find_element(By.XPATH, "//p[@class='wa-rank-list__value']")
classificacao_global_text = classificacao_global_element.text
print("Classificacao:", classificacao_global_text)

#categoria
categoria_elements = driver.find_elements(By.XPATH, "//div[@class='wa-rank-list__info']")
categoria_element = categoria_elements[1]
categoria_text = categoria_element.text
categoria_text_sem_parenteses = re.sub(r'\([^)]*\)', '', categoria_text)
print("Categoria:", categoria_text_sem_parenteses.strip())

# Mudança de Ranking
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
    for rank_text, rank_direction in zip(rank_texts, rank_directions):
        print(f"{rank_direction}: {rank_text}")
else:
    print("Não teve mudanca de rank.")


#Total de Visitas
total_elements = driver.find_elements(By.XPATH, "//p[@class='engagement-list__item-value']")
total_element = total_elements[0]
total_text = total_element.text
print("Total de Visitas:", total_text)

#Duração Média da Visita
duracao_elements = driver.find_elements(By.XPATH, "//p[@class='engagement-list__item-value']")
duracao_element = duracao_elements[3]
duracao_text = duracao_element.text
print("Duração Média da Visita:", duracao_text)

#Páginas por Visita
pagina_elements = driver.find_elements(By.XPATH, "//p[@class='engagement-list__item-value']")
pagina_element = pagina_elements[2]
pagina_text = pagina_element.text
print("Páginas por Visita:", pagina_text)

#Taxa de Rejeição
taxa_elements = driver.find_elements(By.XPATH, "//p[@class='engagement-list__item-value']")
taxa_element = taxa_elements[1]
taxa_text = taxa_element.text
print("Taxa de Rejeição:", taxa_text)

#Principais Países
paises_elements = driver.find_elements(By.XPATH, "//a[@class='wa-geography__country-name']")
paises_text = [element.text for element in paises_elements]
porcentagem_pais_elements = driver.find_elements(By.XPATH, "//span[@class='wa-geography__country-traffic-value']")
porcentagem_pais_text = [element2.text for element2 in porcentagem_pais_elements]
print("Principais países:", ", ".join([f"{pais} = {porcentagem}" for pais, porcentagem in zip(paises_text[:7], porcentagem_pais_text[:6])]))


#Distribuição por Gênero 
genero_feminino_element = driver.find_element(By.XPATH, "//li[@class='wa-demographics__gender-legend-item wa-demographics__gender-legend-item--female']")
genero_feminino_text = genero_feminino_element.text
genero_masculino_element = driver.find_element(By.XPATH, "//li[@class='wa-demographics__gender-legend-item wa-demographics__gender-legend-item--male']")
genero_masculino_text = genero_masculino_element.text
print(f"Distribuição por Gênero: Feminino = {genero_feminino_text.split()[1]}, Masculino = {genero_masculino_text.split()[1]}")

#Distribuição por idade
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
print("Distribuição por idade: " + " ".join([f"({faixa}={porcentagem})" for faixa, porcentagem in zip(faixas_etarias, porcentagem_idade_text)]))


# Armazenar dados no MongoDB
dados_website = {
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

# Fechar o navegador e desconectar do MongoDB
driver.quit()
cliente.close()

