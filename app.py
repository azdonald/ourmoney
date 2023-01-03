from main import create_app, init_celery
from flask_script import Manager
from models import db

app = create_app()
celery = init_celery(app)
app.app_context().push()


manager = Manager(app)
#manager.add_command('db', MigrateCommand)


@manager.command
def run():
    app.run(debug=True)


if __name__ == '__main__':
    manager.run()
