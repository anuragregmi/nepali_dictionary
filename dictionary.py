from sqlite3 import connect, DatabaseError

class Word:
    """
    Represents a word

    Attributes:
    
    `word` : Word
    `pk` : id in the database
    `definitions` : Definitions of the word
    `pos`: Part of speech

    `connection`: Database connection
    """

    def __init__(self, *args, **kwargs):
        """
        Initiallizes the word.

        Pass at least either `pk` while instantiating a word
        """
        
        word = kwargs.get('value', None)
        pk = kwargs.get('pk', None)
        definitions = kwargs.get('definitions', None)
        connection = kwargs.get('connection', None)

        if not pk:
            raise AssertionError("Expected pk in kwargs. Id of the word")

        self.pk = pk
        self.word = word
        self.definitions = definitions
        self.connetion = connection

    def load_word(self):
        try:
            self.word = self.connection.execute("
                        SELECT value from word
                        WHERE id=?
                    ", (self.pk))

        except DatabaseError as e:
            # TODO : Handle error better
            print(e)

class App:
    """
    An interface for the dictionary
    """

    def __init__(self, source):
        self.db_connection = connect('nep_dict.sqlite3')

    def search_word(self, word):
        query = "SELECT id, value from words where value like '%?%'"
        query_set = self.db_connection.execute(query, (word,))
        return queryset
