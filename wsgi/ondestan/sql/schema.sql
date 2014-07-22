BEGIN;

DROP TABLE IF EXISTS roles CASCADE;
CREATE TABLE roles (
	id SERIAL PRIMARY KEY,
	name VARCHAR NOT NULL UNIQUE
);

DROP TABLE IF EXISTS users CASCADE;
CREATE TABLE users (
	id SERIAL PRIMARY KEY,
	password VARCHAR NOT NULL,
	name VARCHAR NOT NULL,
	email VARCHAR NOT NULL UNIQUE,
	phone VARCHAR NOT NULL,
	activated BOOL NOT NULL DEFAULT FALSE,
	last_login TIMESTAMP,
	locale VARCHAR,
	role_id INTEGER REFERENCES roles NOT NULL DEFAULT 1
);

DROP TABLE IF EXISTS notifications CASCADE;
CREATE TABLE notifications (
	id SERIAL PRIMARY KEY,
	level INTEGER,
	text VARCHAR NOT NULL,
	"type" INTEGER NOT NULL,
	"date" TIMESTAMP NOT NULL,
	archived BOOL NOT NULL DEFAULT FALSE,
	user_id INTEGER REFERENCES users NOT NULL
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
	phone VARCHAR UNIQUE NOT NULL,
	active BOOL NOT NULL DEFAULT FALSE,
	checks_wo_pos INTEGER NOT NULL DEFAULT 0,
	user_id INTEGER REFERENCES users NOT NULL,
	plot_id INTEGER REFERENCES plots ON DELETE SET NULL,
	order_id INTEGER REFERENCES orders
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
('pepe', '974f3036f39834082e23f4d70f1feba9d4805b3ee2cedb50b6f1f49f72dd83616c2155f9ff6e08a1cefbf9e6ba2f4aaa45233c8c066a65e002924abfa51590c4', 2, 'Pepe', 'pepe@pepe.pepe', '222222222', True),
('juan', '673d4b1d7deabe33d0037d3a39927ec3d56397a45f5eb9ac0512c75808c293f0d022e04adc5555cd3644d18cf79e9e9ebaea7e3a8e96744b0c49312a7f8af398', 1, 'Juan', 'juan@juan.juan', '333333333', True);

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

INSERT INTO animals(user_id, order_id, name, imei, phone, active, plot_id) VALUES
(2, 1, 'Manuela', '1', '666666666', TRUE, 1),
(3, 2, 'Pepa', '2', '666666667', TRUE, 2),
(3, 2, 'Rubia', '3', '666666668', FALSE, NULL);

INSERT INTO positions(animal_id, battery, coverage, geom, date) VALUES
(1, 5, 50, ST_GeomFromText('POINT(-7.55421 42.25482)', 3857), now()),
(2, 100, 80, ST_GeomFromText('POINT(-7.54726 42.25323)', 3857), now()),
(3, 45, 50, ST_GeomFromText('POINT(-7.55421 42.25323)', 3857), now());

COMMIT;
