from sqlite3 import connect, DatabaseError

import re
from bs4 import BeautifulSoup

# We use these variables to keep the count of entries
# Since AUTOINCREMENT is not used these variables are
# also used while assigning the primary key
WORD_COUNT = 0
DEFINITION_COUNT = 0
EXAMPLE_COUNT = 0


def get_records(connection):
    """Extract record from the database"""
    query = 'SELECT ' \
            'component_main_entry_index_title, ' \
            'component_main_entry_index_result ' \
            'from tbl_component_main_entry_index'
    return connection.execute(query)


def parse_record(record):
    """
    Parse the record generate dictionary entry

    :param record: Database Queryset
    :return: parsed result
        {
            'word': '',
            'pos': '', # part of speech

            'definitions': [
                {
                    'defn': '',
                    'examples': ['example1', 'example2', ...]
                },
                ...
            ]
        }
        eg. For example refer to docstring of `save_to_db`

    """
    regex = re.compile('[०१२३४५६७८९]\. ')
    word, tag = record[0], record[1]

    bs = BeautifulSoup(tag, 'html.parser')
    defns = bs.find_all(class_='defn')
    egs = bs.find_all(class_='grey2')
    pos = bs.find(class_='pos')

    result = {
        'word': word,
        'definitions': [],
        'pos': pos.get_text() if pos else 'N/A'
    }

    for i in range(len(defns)):
        try:
            examples = egs[i].get_text()
            examples = examples.split('\xa0')  # split by &nbsp;

            for l in range(len(examples)):
                examples[l] = regex.sub('', examples[l])

            result['definitions'].append({
                'defn': defns[i].get_text(),
                'examples': examples[2::]  # first two are not examples actually
            })
        except Exception as e:
            print(e)
    return result


def create_tables_for_destination(connection):
    """ create tables to store refined entries """
    queries = [
        'CREATE TABLE IF NOT EXISTS `word`(\
        `id` int(11) NOT NULL PRIMARY KEY,\
        `value` varchar(255) NOT NULL,\
        `part_of_speech` varchar(100)\
        );',

        'CREATE TABLE IF NOT EXISTS `definition`(\
        `id` int(11) NOT NULL PRIMARY KEY,\
        `word_id` int(11) NOT NULL,\
        `value` TEXT\
        );',
        'CREATE TABLE IF NOT EXISTS `example`(\
        `id` int(11) NOT NULL PRIMARY KEY,\
        `definition_id` int(11) NOT NULL,\
        `value` TEXT\
        );'
    ]
    for query in queries:
        connection.execute(query)


def save_word(word, pos, connection):
    """ save word to the database """
    pk = globals()['WORD_COUNT'] + 1

    query = '''
        INSERT INTO `word`
        (id, value, part_of_speech)
        VALUES 
        (?,?,?)
    '''

    try:
        connection.execute(query, (pk, word, pos))
        globals()['WORD_COUNT'] = pk
        return pk
    except DatabaseError as e:
        print(e)
    return globals()['WORD_COUNT']


def save_examples(examples, definition_id, connection):
    """ save examples to the database """
    query = '''
              INSERT INTO `example`
              (id, definition_id, value)
              VALUES 
              (?,?,?)
            '''
    for example in examples:
        pk = globals()['EXAMPLE_COUNT'] + 1
        try:
            connection.execute(query, (pk, definition_id, example))
            globals()['EXAMPLE_COUNT'] = pk
        except DatabaseError as e:
            print(e)


def save_definitions(definitions, word_id, connection):
    """ save definitions to the database """
    query = '''INSERT INTO definition
              (`id`, `word_id`, `value`)
              VALUES 
              (?,?,?)
            '''
    for definition in definitions:
        pk = globals()['DEFINITION_COUNT'] + 1
        if definition.get('defn'):

            try:
                connection.execute(query, (pk, word_id, definition.get('defn')))
                if definition.get('examples').__len__() != 0:
                    save_examples(
                        examples=definition.get('examples'),
                        definition_id=pk,
                        connection=connection
                    )
                globals()['DEFINITION_COUNT'] = pk
            except DatabaseError as e:
                print(e)


def save_to_db(result, connection):
    """

    :param result: details of word
    eg.
    {
        'word': 'अँ',
        'definitions': [
        {
            'defn': 'कुनै कुरा मान्छु वा हो भन्ने बुझाउन प्रयोग गरिने शब्द',
            'examples': [
                'अँ बुझेँ — बोलीको साथसाथै ऊ सिरकलाई फेरि तानेर आफ्नो टाउको सम्म पुर्याउँछ। '
            ]
        },
        {
            'defn': 'कुनै कुरा मान्दिन वा गर्दिन भन्ने बुझाउन प्रयोग गरिने शब्द',
             'examples': [
                'अँ छोडुँला! ',
                'अँ हुन्थ्यो! '
             ]
        },
        {
            'defn': 'कुनै नयाँ प्रसङ्ग सुरु गर्न वा केही बेर रोकिएर फेरि प्रसङ्ग जोड्न प्रयोग गरिने शब्द',
            'examples': [
                'अँ यो कहाँ रहिछ? ', 'अँ त म भन्दै थिएँ, यो बाटोमा भेटियो। '
            ]
        },
        {
            'defn': 'कुरा गर्दागर्दै अलमलिँदा वा बिर्सँदा खाली ठाउँ भर्न प्रयोग गरिने शब्द',
            'examples': [
                'मुखले भने गुड्डी हाँकेर ऐले नै अँ के रे मोती समेत फुलाउँछ क्यारे जस्तो गर्छ '
            ]
        }],
        'pos': ' नि.'
    }
    :param connection: database connection
    :return: None
    """

    word_id = save_word(
        word=result.get('word', None),
        pos=result.get('pos', None),
        connection=connection
    )

    save_definitions(
        definitions=result.get('definitions'),
        word_id=word_id,
        connection=connection
    )


def main():
    source_db_name = 'nepali_dictionary.sqlite3'
    destination_db_name = 'nep_dict.sqlite3'

    source_connection = connect(source_db_name)
    records = get_records(source_connection)

    destination_connection = connect(destination_db_name)
    create_tables_for_destination(destination_connection)

    for record in records:
        result = parse_record(record)
        save_to_db(result, destination_connection)

    source_connection.close()
    destination_connection.commit()
    destination_connection.close()

    print(str(WORD_COUNT) + 'words written')


if __name__ == '__main__':
    main()
