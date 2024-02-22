from bs4 import BeautifulSoup
import requests
import psycopg2

# Блок подключения СУБД
conn = psycopg2.connect(
    port="5432",
    dbname="Citi",
    user="postgres",
    password="1488",
    host="localhost",
)
conn.autocommit = True


# Блок функции поиска и доработки ссылок
def parse_song_links(soup):
    full_link = {}
    for link in soup.find_all(
        "li", class_=None
    ):  # Отменяю все заголовочне буквы типа F, Z , A
        name = link.text  # НАХОЖУ ВСЕ НАЗВАНИЯ И ЗАГОЛОВКИ
        for item in link.find_all("a"):
            Material = item.get("href")  # ВСЕ ССЫЛКИ БЕЗ HHTPS://
            Link_text = (
                "https://www.gr-oborona.ru" + Material
            )  # ТУТ Я ПОЛУЧАЮ ПОСЛЕДНЮЮ ССЫЛКУ И ПРЕВРАЩАЮ ЕЕ В ОТКРЫВАЕМУЮ
    return full_link


def get_html(url):
    response = requests.get(url).text
    return BeautifulSoup(response, "lxml")


def main():
    song_urls = get_song_urls()
    pars_songs(song_urls)
    pass


def get_song_urls():
    soup = get_html("https://www.gr-oborona.ru/texts/")
    return parse_song_links(soup)


def update_sql(autor, album, Lyrics):
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO text (autor,album,lyrics) VALUES (%s,%s,%s);",
            (autor, album, Lyrics),
        )


def pars_songs(url_dict):
    for cell in url_dict:
        cell_link = requests.get(url_dict[cell]).text
        result = BeautifulSoup(cell_link, "lxml")
        written = result.find("div", id=None)
        if written.find_all("ul"):
            tag_to_remove = written.find("ul")
            tag_to_remove.decompose()
            p_tags = written.find_all("p")[-1].decompose()
            written = written
        if written.find("p"):
            autor = written.find("p").extract().text.replace("Автор: ", "").title()
            written = written
        if written.find("p"):
            album = written.find("p").extract().text.replace("Альбом: ", "").title()
            written = written
        Lyrics = written.getText()
        update_sql(autor, album, Lyrics)
        print(autor)
        print(album)
        print(Lyrics)


main()
exit()
