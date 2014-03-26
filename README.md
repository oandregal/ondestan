## Onde Están

To run onde-estan, you'll need to:

- create a working environment - [python 2.7 & pyramid 1.4]([How to create and configure the environment](http://docs.pylonsproject.org/projects/pyramid/en/1.4-branch/narr/install.html))
- create a [PostGIS enabled database](https://gist.github.com/nosolosw/5976731) and populate it. Something in the line of:


    createdb -h localhost -p 5432 -U postgres -T template_postgis ondestan
    psql -h localhost -p 5432 -U postgres ondestan < ./sql/schema.sql

- configure DB & SMTP connection params in development.ini / production.ini

Then, you'll be able to run the project:

    pserve development.ini --reload
