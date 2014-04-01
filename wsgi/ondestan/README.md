## Onde Están

To run onde-estan, you'll need to:

- create a [virtualenv environment](http://docs.pylonsproject.org/projects/pyramid/en/1.4-branch/narr/install.html)
- configure DB & SMTP connection params in development.ini / production.ini
- create a [PostGIS enabled database](https://gist.github.com/nosolosw/5976731) and populate it.
- install dependencies and have fun!

Something in the line of:

    <virtualenv: install & activate>
    <config: edit to match your configuration>
    createdb -h localhost -p 5432 -U postgres -T template_postgis ondestan
    psql -h localhost -p 5432 -U postgres ondestan < ./sql/schema.sql
    python setup.py develop
    pserve development.ini --reload
