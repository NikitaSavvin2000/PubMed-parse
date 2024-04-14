import json
from collections import OrderedDict
import time

path = '/Users/nikitasavvin/Desktop/AIDAM/PubMed-parse/src/downloads_json/PMC16145.xml'
from crossref.restful import Works
from crossref.restful import Works
from habanero import Crossref
# Инициализируем объект Works
works = Works()


def get_publication_date_by_doi(doi):
    try:
        work = works.doi(doi)
        publication_date = work['issued']['date-parts'][0]

        return '-'.join(map(str, publication_date))
    except Exception as e:
        print("Ошибка при получении данных:", str(e))

        return None

def get_publication_date_by_title(title):
    try:
        cr = Crossref()
        doi = cr.works(query=title)['message']['items'][0]['DOI']
        works = Works()
        work = works.doi(doi)
        publication_date = work['issued']['date-parts'][0]
        publication_date = '-'.join(map(str, publication_date))
        return publication_date, doi
    except Exception as e:
        print("Ошибка при получении данных:", str(e))

        return None, None
    raise



def parse_json(path):

    with open(path, 'r') as file:
        json_string = file.read()
        data_json = json.loads(json_string)

    parts = data_json['documents'][0]['passages']
    abstract_flag = ['ABSTRACT', 'ABSTRACTS', 'ABSTRAKT', 'ABSTRACTIONS', 'ABSTRACTIONS.', 'ABSTARCT', 'Abstract',
                     'Abstracts', 'Abstrakt', 'Abstractions', 'Abstractions.', 'Abstarct', 'abstract', 'abstracts',
                     'abstrakt', 'abstractions', 'abstractions.', 'abstarct']
    title_flag = ['TITLE', 'title', 'Title']
    ids = ['article-id_doi', 'article-id_pmc', 'article-id_pmid', 'article-id_publisher-id']
    ref_flag = ['REF', 'ref', 'Ref', 'REFERENCES', 'references', 'References']

    section_types = []

    for item in parts:
        section_type = item['infons'].get('section_type')
        if section_type:
            section_types.append(section_type)
    section_types = list(OrderedDict.fromkeys(section_types))

    len_parts = len(parts)
    doi = None
    article_id_pmc = None
    article_id_pmid = None
    article_id_publisher = None
    article_title = None
    autors = []
    abstract = ''
    full_text = ''
    pub_date = ''
    intro_texts_dict = {key: [item['text'] for item in parts if item['infons'].get('section_type') == key] for key in
                        section_types}
    references = {}
    for part in range(len_parts):
        infons = parts[part]['infons']
        # print(infons)
        inform_keys = infons.keys()
        text = parts[part]['text']
        section_type = infons.get('section_type', None)

        # ---------------------------------- doi title autors parser ---------------------------------

        # Проверяем что если doi, id и прочее в первой половине статьи (part < (len_parts/2)) то принимаем,
        # что эти данные относятся к конкретной статье, а не к списку литературы
        if any(key in inform_keys for key in ids) and (part < (len_parts / 2)) or (section_type in title_flag):

            names_list = [key for key in inform_keys if 'name' in key]
            for name in names_list:
                article_author = {}
                for parts_name in infons.get(name).split(';'):
                    key, value = parts_name.split(':')
                    article_author[key] = value
                    autors.append(article_author)

            doi = infons.get('article-id_doi', None)
            article_id_pmc = infons.get('article-id_pmc', None)
            article_id_pmid = infons.get('article-id_pmid', None)
            article_id_publisher = infons.get('article-id_publisher-id', None)
            article_title = text

        # ----------------------------------------------------------------------------------------------------
        ref_authors = []
        if any(key in inform_keys for key in ref_flag) and (part > (len_parts / 2)) or (section_type in ref_flag):
            names_list = [key for key in inform_keys if 'name' in key]
            for name in names_list:
                ref_author = {}
                for parts_name in infons.get(name).split(';'):
                    key, value = parts_name.split(':')
                    ref_author[key] = value
                    ref_authors.append(ref_author)
            references[text] = ref_authors

    for section in section_types:
        if section not in ref_flag:
            full_text += f'. {section}: '
            full_text += ' '.join(intro_texts_dict[section])
        if section in abstract_flag:
            abstract += ' '.join(intro_texts_dict[section])
            abstract = abstract.replace('  ', ' ')
    full_text = full_text[2:]
    result_dict = {}
    if doi is not None:
        pub_date = get_publication_date_by_doi(doi)
    else:
        pub_date, doi = get_publication_date_by_title(article_title)

    result_dict['doi'] = doi
    result_dict['article_id_pmc'] = article_id_pmc
    result_dict['article_id_pmid'] = article_id_pmid
    result_dict['article_id_publisher'] = article_id_publisher
    result_dict['article_title'] = article_title
    result_dict['pub_date'] = pub_date
    result_dict['autors'] = autors
    result_dict['abstract'] = abstract
    result_dict['full_text'] = full_text
    result_dict['references'] = references

    return result_dict



if __name__ == '__main__':
    import time

    start_time = time.time()
    result_dict = parse_json(path)
    end_time = time.time()
    execution_time = end_time - start_time
    print("Execution time:", execution_time, "seconds")

    print(result_dict['pub_date'])
