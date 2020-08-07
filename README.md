# Freigabedatenbank

- venv erstellen
- venv aktivieren


- Packages installieren
- Setup develop
```
pip install -r requirements.txt
python setup.py develop
```

## Development and Testing

Setup the postgres database in docker

```
docker-compose build
docker-compose up -d
```

To verify that the database is accessible:

```
python app/db/manage.py check_health
```

Enter database and install extensions

```
PGPASSWORD=freigabe  psql -p54320 -hlocalhost -U freigabe -d freigabe
```

Run app on local machine

```
python -m app.app
```

If you want to drop the tables:

```
python app/db/manage.py drop_dp
```

And to recreate the schema:

```
python app/db/manage.py drop_dp
```

if you want to upgrade to the latest version of the database:

```
python app/db/manage.py db upgrade
```
migrate
```
python app/db/manage.py db migrate -m "comment"
```
if psql is not installed:

```
brew install libpq
echo 'export PATH="/usr/local/opt/libpq/bin:$PATH"' >> ~/.bash_profile
source ~/.bash_profile
or if usign zsh (pycharm)
echo 'export PATH="/usr/local/opt/libpq/bin:$PATH"' >> ~/.zshrc
source  ~/.zshrc
```

Run the tests

```
coverage run -m pytest
```

With test coverage report:

```
coverage report
```

html coverage report

```
coverage html --fail-under=90
open htmlcov/index.html
```
