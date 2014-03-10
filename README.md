## Onde Están

To run onde-estan, you'll need:

- python 2.7 & pyramid 1.4 - [see how]([How to create and configure the environment](http://docs.pylonsproject.org/projects/pyramid/en/1.4-branch/narr/install.html))
- a PostGIS enabled database - [see how](https://gist.github.com/nosolosw/5976731)
- configure DB & SMTP connection params in development.ini / production.ini
- populate the db with test data `psql <db-connection-params> < ./scripts/schema.sql`

After that, you'll be able to run the project:

    pserve development.ini --reload
