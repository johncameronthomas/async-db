from async_db import Database

db = Database('test.json')
db.start()
db.initialize({'key': 'value', 'hello': 'world'})
print(db.dump())
db.stop()