
import sqlite3
from emby_client import authenticate, load_emby_data

conn = sqlite3.connect(":memory:")
cursor = conn.cursor()
load_emby_data(cursor)
conn.commit()

while True:
    query = raw_input('Query:\n')
    if query == "exit":
        break

    try:
        result = cursor.execute(query)

        col_names = list(map(lambda x: x[0], result.description))

        print "\t".join(col_names)

        for row in result:
            line_data = []
            for item in row:
                if type(item) == int:
                    item = str(item)
                line_data.append(item)
            print "\t".join(line_data)

    except Exception as err:
        print err

conn.close()





