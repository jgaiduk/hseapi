
```python
def get_bachelors_programs_json(): 
    """
    Выдает словарь, где ключами являются названия образовательных программ, 
    а значениями — словари с признаками для каждой программы.
    """
    import re
    import requests
    from bs4 import BeautifulSoup
    import json
    link = "https://www.hse.ru/education/programs"
    r = requests.get(link)
    page = BeautifulSoup(r.text, 'html.parser')
    data_programs_bac_json = {}
    
    for program__title in page.body.find_all("div", re.compile("education_bachelor")):
        field = program__title.h3.text #направление подготовки 07.00.00 Архитектура

        for item in program__title.find_all("div", class_="edu-programm__item small"):
            program = str(item.a.text) # название образовательной программы
            campus = item.find("div", class_="edu-programm__campus").text
            faculty = item.find("div", class_="edu-programm__unit").text #факультет
            duration = item.find("div", class_="edu-programm__edu").text.split()[0] #продолжительность обучения
            form = item.find("span", class_="edu-programm__edu_offline").text #форма обучения - Очная\Заочная
            link = item.find("a").get("href") 

            data_programs_bac_json[program] = {
                "campus": campus,
                "faculty": faculty,
                "duration": duration,
                "form": form,
                "link": link,
                "field": field
            }

            # Этот блок обрабатывает количество мест.

            openings_free_list = item.find_all("div", "edu-programm__place_free") 
            openings_free_list = [n.text.strip().replace("\xa0", " ") for n in openings_free_list]
            if len(openings_free_list) > 1:
                openings_free_sum = int(openings_free_list[0].split()[0])+int(openings_free_list[-1].split()[0])
            else:
                try:
                    openings_free_sum = int(openings_free_list[0].split()[0])
                except IndexError: 
                    openings_free_sum = 0

            openings_paid = item.find_all("div", class_="edu-programm__place_paid")
            openings_paid = [n.text.strip().replace("\xa0", " ") for n in openings_paid]
            if len(openings_paid) > 1:
                openings_paid_rus = int(openings_paid[0].split()[0])
                openings_paid_foreign = int(openings_paid[-1].split()[0])
                data_programs_bac_json[program]["openings"] = {
                    "free": openings_free_sum,
                    "paid_rus": openings_paid_rus,
                    "paid_foreign": openings_paid_foreign}
            else:
                openings_paid_rus = int(openings_paid[0].split()[0])
                data_programs_bac_json[program]["openings"] = {
                    "free": openings_free_sum,
                    "paid_rus": openings_paid_rus}

    return data_programs_bac_json

```


```python
get_bachelors_programs_json()
```




    {'Библеистика и история древнего Израиля': {'campus': 'Москва',
      'duration': '5',
      'faculty': 'Институт классического Востока и античности',
      'field': '58.00.00 Востоковедение и африканистика',
      'form': 'Очная',
      'link': 'https://www.hse.ru/ba/israel/',
      'openings': {'free': 12, 'paid_foreign': 5, 'paid_rus': 10}},
     'Бизнес-информатика': {'campus': 'Пермь',
      'duration': '4',
      'faculty': 'Факультет экономики, менеджмента и бизнес-информатики',
      'field': '38.00.00 Экономика и управление',
      'form': 'Очная',
      'link': 'https://perm.hse.ru/ba/bi/',
      'openings': {'free': 33, 'paid_foreign': 3, 'paid_rus': 20}},
     'Востоковедение': {'campus': 'Санкт-Петербург',
      'duration': '5',
      'faculty': 'Санкт-Петербургская школа социальных и гуманитарных наук',
      'field': '41.00.00 Политические науки и регионоведение',
      'form': 'Очная',
      'link': 'https://spb.hse.ru/ba/oriental/',
      'openings': {'free': 25, 'paid_foreign': 4, 'paid_rus': 70}},
     
     



```python
def get_masters_programs_json():
    """
    Выдает словарь, где ключами являются названия образовательных программ, 
    а значениями — словари с признаками для каждой программы.
    """
    import re
    import requests
    from bs4 import BeautifulSoup
    import json
    link = "https://www.hse.ru/education/programs"
    r = requests.get(link)
    page = BeautifulSoup(r.text, 'html.parser')
    
    data_programs_mag_json = {}
    for program__title in page.body.find_all("div", re.compile("education_magister")):
        field = program__title.h3.text #направление подготовки 07.00.00 Архитектура

        for item in program__title.find_all("div", class_="edu-programm__item small"):
            program = str(item.a.text) # название образовательной программы
            campus = item.find("div", class_="edu-programm__campus").text
            faculty = item.find("div", class_="edu-programm__unit").text #факультет
            duration = item.find("div", class_="edu-programm__edu").text.split()[0] #продолжительность обучения
            form = item.find("span", class_="edu-programm__edu_offline").text #форма обучения - Очная\Заочная
            link = item.find("a").get("href") 

            data_programs_mag_json[program] = {
                    "campus": campus,
                    "faculty": faculty,
                    "duration": duration,
                    "form": form,
                    "link": link,
                    "field": field
                }


            # Этот блок обрабатывает количество мест.
            #.text.strip().replace("\xa0", " ").split()[0])

            openings_free_list = item.find_all("div", "edu-programm__place_free") 
            openings_free_list = [n.text.strip().replace("\xa0", " ") for n in openings_free_list]
            if len(openings_free_list) > 1:
                openings_free_sum = int(openings_free_list[0].split()[0])+int(openings_free_list[-1].split()[0])
            elif len(openings_free_list) == 0:
                openings_free_sum = 0
            else:
                openings_free_sum = int(openings_free_list[0].split()[0])

            openings_paid = item.find_all("div", class_="edu-programm__place_paid")
            openings_paid = [n.text.strip().replace("\xa0", " ") for n in openings_paid]
            if len(openings_paid) > 1:
                openings_paid_rus = int(openings_paid[0].split()[0])
                openings_paid_foreign = int(openings_paid[-1].split()[0])
                data_programs_mag_json[program]["openings"] = {
                    "free": openings_free_sum,
                    "paid_rus": openings_paid_rus,
                    "paid_foreign": openings_paid_foreign}
            else:
                openings_paid_rus = int(openings_paid[0].split()[0])
                data_programs_mag_json[program]["openings"] = {
                    "free": openings_free_sum,
                    "paid_rus": openings_paid_rus}



    # [int(s) for s in str.split() if s.isdigit()]

    return data_programs_mag_json

```


```python
get_masters_programs_json()
```




    {'Smart-маркетинг: данные, аналитика, инсайты': {'campus': 'Пермь',
      'duration': '2',
      'faculty': 'Факультет экономики, менеджмента и бизнес-информатики',
      'field': '38.00.00 Экономика и управление',
      'form': 'Очная',
      'link': 'https://perm.hse.ru/ma/smart/',
      'openings': {'free': 20, 'paid_foreign': 3, 'paid_rus': 5}},
     'Адвокат по гражданским и уголовным делам': {'campus': 'Москва',
      'duration': '2',
      'faculty': 'Факультет права, Кафедра уголовного права и криминалистики',
      'field': '40.00.00 Юриспруденция',
      'form': 'Очная',
      'link': 'https://www.hse.ru/ma/lawyer/',
      'openings': {'free': 20, 'paid_foreign': 5, 'paid_rus': 10}},
     'Анализ больших данных в бизнесе, экономике и обществе': {'campus': 'Санкт-Петербург',
      'duration': '2',
      'faculty': 'Санкт-Петербургская школа экономики и менеджмента',
      'field': '01.00.00 Математика и механика ',
      'form': 'Очная',
      'link': 'https://spb.hse.ru/ma/analysis/',
      'openings': {'free': 15, 'paid_foreign': 3, 'paid_rus': 10}},
     'Анализ данных в биологии и медицине': {'campus': 'Москва',
      'duration': '2',
      'faculty': 'Факультет компьютерных наук',
      'field': '01.00.00 Математика и механика ',
      'form': 'Очная',
      'link': 'https://www.hse.ru/ma/adbm/',
      'openings': {'free': 15, 'paid_foreign': 3, 'paid_rus': 5}},
     


