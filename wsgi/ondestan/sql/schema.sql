BEGIN;

DROP TABLE IF EXISTS roles CASCADE;
CREATE TABLE roles (
	id SERIAL PRIMARY KEY,
	name VARCHAR NOT NULL UNIQUE
);

DROP TABLE IF EXISTS users CASCADE;
CREATE TABLE users (
	id SERIAL PRIMARY KEY,
	login VARCHAR NOT NULL UNIQUE,
	password VARCHAR NOT NULL,
	name VARCHAR NOT NULL,
	email VARCHAR NOT NULL UNIQUE,
	phone VARCHAR NOT NULL,
	activated BOOL NOT NULL DEFAULT FALSE,
	role_id INTEGER REFERENCES roles NOT NULL DEFAULT 1
);

DROP TABLE IF EXISTS orders CASCADE;
CREATE TABLE orders (
	id SERIAL PRIMARY KEY,
	units INTEGER NOT NULL,
	address VARCHAR NOT NULL,
	user_id INTEGER REFERENCES users NOT NULL
);

DROP TABLE IF EXISTS order_states CASCADE;
CREATE TABLE order_states (
	id SERIAL PRIMARY KEY,
	state INTEGER NOT NULL DEFAULT 0,
	"date" TIMESTAMP NOT NULL,
	order_id INTEGER REFERENCES orders NOT NULL
);

DROP TABLE IF EXISTS plots CASCADE;
CREATE TABLE plots (
	id SERIAL PRIMARY KEY,
	name VARCHAR NOT NULL,
	user_id INTEGER REFERENCES users NOT NULL
);
SELECT AddGeometryColumn ('public', 'plots', 'geom', 3857, 'POLYGON', 2);

DROP TABLE IF EXISTS animals CASCADE;
CREATE TABLE animals (
	id SERIAL PRIMARY KEY,
	name VARCHAR,
	type VARCHAR DEFAULT 'cow',
	imei VARCHAR UNIQUE NOT NULL,
	active BOOL NOT NULL DEFAULT FALSE,
	user_id INTEGER REFERENCES users NOT NULL,
	order_id INTEGER REFERENCES orders,
	plot_id INTEGER REFERENCES plots
);

DROP TABLE IF EXISTS positions CASCADE;
CREATE TABLE positions (
	id SERIAL PRIMARY KEY,
	"date" TIMESTAMP NOT NULL,
	battery REAL,
	coverage REAL,
	animal_id INTEGER REFERENCES animals NOT NULL,
	UNIQUE ("date", animal_id)
);
SELECT AddGeometryColumn ('public', 'positions', 'geom', 3857, 'POINT', 2);

-- data insertion

INSERT INTO roles(name) VALUES
	('viewer'),
	('manager'),
	('admin');

INSERT INTO users(login, password, role_id, name, email, phone, activated) VALUES
('admin', 'c7ad44cbad762a5da0a452f9e854fdc1e0e7a52a38015f23f3eab1d80b931dd472634dfac71cd34ebc35d16ab7fb8a90c81f975113d6c7538dc69dd8de9077ec', 3, 'Admin', 'admin@admin.admin', '111111111', True),
('manager', '5fc2ca6f085919f2f77626f1e280fab9cc92b4edc9edc53ac6eee3f72c5c508e869ee9d67a96d63986d14c1c2b82c35ff5f31494bea831015424f59c96fff664', 2, 'Manager', 'manager@manager.manager', '222222222', True),
('viewer', 'a8d73e712d9257a75bce54754e0ad3074894e29feeec1709f9e47b761dc38d7ab923a62f1b4883a19569115e8b68850cc86b27fda81a0daa5305538e4d910168', 1, 'Viewer', 'viewer@viewer.viewer', '333333333', True);

INSERT INTO orders(units, address, user_id) VALUES
(1, 'Avenida Menor - Ourense', 2),
(2, 'Praza Maior - Ourense', 3);

INSERT INTO order_states(state, date, order_id) VALUES
(0, now() - INTERVAL '3 days', 1),
(1, now()- INTERVAL '2 days', 1),
(2, now()- INTERVAL '1 days', 1),
(3, now(), 1),
(0, now()- INTERVAL '3 days', 2),
(1, now()- INTERVAL '2 days', 2),
(2, now()- INTERVAL '1 days', 2),
(3, now(), 2);

INSERT INTO plots(user_id, name, geom) VALUES
(2, 'Parcela 1', ST_GeomFromText('POLYGON ((-0.10592 51.51611, -0.08532 51.52412, -0.07999 51.51077, -0.10592 51.51611))', 3857)),
(3, 'Parcela 2', ST_GeomFromText('POLYGON ((-0.10592 51.51611, -0.08532 51.52412, -0.04738 51.51334, -0.10592 51.51611))', 3857));

INSERT INTO animals(user_id, order_id, name, imei, password, plot_id) VALUES
(2, 1, 'Manuela', '1', '1', 1),
(3, 2, 'Pepa', '2', '2', 2),
(3, 2, 'Rubia', '3', '3', 2);

INSERT INTO positions(animal_id, battery, coverage, geom, date) VALUES
(1, 5, 50, ST_GeomFromText('POINT(-7.55421 42.25482)', 3857), now()),
(2, 100, 80, ST_GeomFromText('POINT(-7.54726 42.25323)', 3857), now()),
(3, 45, 50, ST_GeomFromText('POINT(-7.55421 42.25323)', 3857), now());

COMMIT;
