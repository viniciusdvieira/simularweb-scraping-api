from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep
import re


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

#Mudança de Ranking
rank_elements = driver.find_elements(By.XPATH, "//span[@class='app-parameter-change app-parameter-change--md app-parameter-change--down']")
if rank_elements:
    rank_texts = []
    rank_directions = []
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

#Duração Média da Visita
duracao_elements = driver.find_elements(By.XPATH, "//p[@class='engagement-list__item-value']")
duracao_element = duracao_elements[3]
duracao_text = duracao_element.text
print("Duração Média da Visita: ", duracao_text)

#Páginas por Visita
pagina_elements = driver.find_elements(By.XPATH, "//p[@class='engagement-list__item-value']")
pagina_element = pagina_elements[2]
pagina_text = pagina_element.text
print("Páginas por Visita: ", pagina_text)

#Taxa de Rejeição
taxa_elements = driver.find_elements(By.XPATH, "//p[@class='engagement-list__item-value']")
taxa_element = taxa_elements[1]
taxa_text = taxa_element.text
print("Taxa de Rejeição: ", taxa_text)

driver.quit()
