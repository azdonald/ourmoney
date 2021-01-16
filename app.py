from src import create_app, init_celery
from flask_migrate import MigrateCommand, Migrate
from flask_script import Manager
from src.models import db

app = create_app()
celery = init_celery(app)
app.app_context().push()


manager = Manager(app)
migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)


@manager.command
def run():
    app.run(debug=True)


if __name__ == '__main__':
    manager.run()
