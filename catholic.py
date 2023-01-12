# Librerias necesarias
from bs4 import BeautifulSoup
import requests
import pandas as pd
from docx.shared import Pt
from docx import Document
import datetime

# Funcion para obtener el contenido de la pagina web
def get_soup(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    return soup

# Funcion para obtener los enlaces de la pagina web
def get_href(soup):
    href = []
    for link in soup.find_all('a', class_='DTTitulo'):
        href.append(link.get('href'))
    return href

# Funcion para obtener la url de la pagina web
def get_url(links):
    url = []
    for link in links:
        url.append('https://es.catholic.net' + link)
    return url

# Funcion para obtener el titulo de cada campo
def get_title(soup):
    title = []
    for link in soup.find_all('a', class_='DTTitulo'):
        title.append(link.get_text())
    return title

# Funcion para obtener el texto de entrada de cada campo
def get_texto(soup):
    texto = []
    for link in soup.find_all('div', id='DTTexto'):
        texto.append(link.get_text())
    return texto

# Funcion para acceder a cada url y extraer el texto de cada una
def get_texto_from_url(url):
    texto = []
    for link in url:
        soup = get_soup(link)
        for i in soup.find('div', {'id': 'art_texto'}).text:
            texto.append(i)
    return texto

# Funcion para exportar el dataframe a un archivo docx
def export_df_to_doc_v3(df, file_path):
    document = Document()

    # Agregar encabezado
    header = document.sections[0].header
    header.paragraphs[0].text = 'Un lugar de encuentro para católicos'
    header.paragraphs[0].style = 'Header'

    # Agregar pie de página
    footer = document.sections[0].footer
    footer.paragraphs[0].text = 'Realizado por @MundoBits'
    footer.paragraphs[0].style = 'Footer'

    # Agregar contenido del DataFrame al documento
    for row in df.itertuples():
        p = document.add_paragraph("")
        run = p.add_run(row.Tema)
        run.bold = True
        run.font.size = Pt(18)
        p = document.add_paragraph("")
        run = p.add_run(row.Titulo)
        run.bold = True
        run.font.size = Pt(16)
        p = document.add_paragraph("")
        run = p.add_run(str(row.Entrada))
        run.italic = True
        run.font.size = Pt(14)
        document.add_paragraph("" + row.Texto)
        document.add_paragraph(" ")

    # Guardar documento
    document.save(file_path)


def main():
    website = 'https://es.catholic.net/'
    soup = get_soup(website)
    links = get_href(soup)
    url = get_url(links)
    title = get_title(soup)
    texto = get_texto(soup)

    text_art = []

    for i in range(3):
        try:
            response = requests.get(url[i])
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')
            text_art.append(soup.find('div', {'id': 'art_texto'}).text)

        except requests.exceptions.ConnectionError as e:
            print(e)

    temas = ['El Evangelio meditado', 'Meditacion para hoy', 'Tema actual']
    df = pd.DataFrame({'Tema': temas, 'Titulo': title[:3], 'Entrada': texto[:3], 'Texto': text_art})

    # llamar la funcion export_df_to_doc_v3 y guardar el archivo con catholic + fecha de hoy
    fecha = datetime.datetime.now().strftime("%Y-%m-%d")
    export_df_to_doc_v3(df, 'catholic' + fecha + '.docx')


if __name__ == '__main__':
    main()
