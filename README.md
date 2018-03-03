# Nepali Dictionary
 Database of Nepali Contemporary Dictionary available [here](http://ltk.org.np/nepalisabdakos/index.php?option=db)
 
# Getting Used To
`nepali_dictionary.sqlite3` is the old database, which is available [here](http://ltk.org.np/nepalisabdakos/index.php?option=db),
after migrating from mysql to sqlite3

`nep_dict.sqlite3` is the new and refined database.

`main.py` contains script which converted old database to new one.

*You might not want to do that in your computer, it took my computer 30mins.*

# Download Database

Click [here](https://github.com/anuragregmi/nepali_dictionary/raw/master/nep_dict.sqlite3) to download the database.

# Database Structure 
for `nep_dict.sqlite3`

| word         | definition | example      |
|------        |---------  |--------      |
| **id**       | **id**    |**id**        |
|value         | *word_id* |*definition_id*|
|part_of_speech| value     |value         |
