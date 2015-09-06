from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand
from toolshed import app, db

manager = Manager(app)
manager.add_command('db', MigrateCommand)
migrate = Migrate(app, db)

if __name__ == '__main__':
    manager.run()
