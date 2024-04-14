from crossref.restful import Works

# Инициализируем объект Works
works = Works()


def get_publication_date(doi):
    try:
        work = works.doi(doi)
        publication_date = work['issued']['date-parts'][0]
        return '-'.join(map(str, publication_date))
    except Exception as e:
        print("Ошибка при получении данных:", str(e))
        return None


# Пример использования
doi = "10.1172/jci.insight.133429"
publication_date = get_publication_date(doi)
if publication_date:
    print("Дата публикации:", publication_date)
else:
    print("Не удалось получить дату публикации.")
