CREATE TABLE roles (
	id SERIAL PRIMARY KEY,
	name VARCHAR NOT NULL UNIQUE
);

CREATE TABLE users (
	id SERIAL PRIMARY KEY,
	login VARCHAR NOT NULL UNIQUE,
	password VARCHAR NOT NULL,
	role_id INTEGER REFERENCES roles NOT NULL DEFAULT 1
);

CREATE TABLE plots (
	id SERIAL PRIMARY KEY,
	name VARCHAR NOT NULL,
	user_id INTEGER REFERENCES users NOT NULL
);

SELECT AddGeometryColumn ('public', 'plots', 'geom', 3857, 'POLYGON', 2);

CREATE TABLE cows (
	id SERIAL PRIMARY KEY,
	name VARCHAR NOT NULL,
	battery_level REAL,
	user_id INTEGER REFERENCES users NOT NULL,
	plot_id INTEGER REFERENCES plots
);

SELECT AddGeometryColumn ('public', 'cows', 'geom', 3857, 'POINT', 2);

INSERT INTO roles(name) VALUES
	('viewer'),
	('manager'),
	('admin');

INSERT INTO users(login, password, role_id) VALUES
('admin', 'c7ad44cbad762a5da0a452f9e854fdc1e0e7a52a38015f23f3eab1d80b931dd472634dfac71cd34ebc35d16ab7fb8a90c81f975113d6c7538dc69dd8de9077ec', 3),
('manager', '5fc2ca6f085919f2f77626f1e280fab9cc92b4edc9edc53ac6eee3f72c5c508e869ee9d67a96d63986d14c1c2b82c35ff5f31494bea831015424f59c96fff664', 2),
('viewer', 'a8d73e712d9257a75bce54754e0ad3074894e29feeec1709f9e47b761dc38d7ab923a62f1b4883a19569115e8b68850cc86b27fda81a0daa5305538e4d910168', 1);

INSERT INTO plots(user_id, name, geom) VALUES
(2, 'Parcela 1', ST_GeomFromText('POLYGON ((-0.10592 51.51611, -0.08532 51.52412, -0.07999 51.51077, -0.10592 51.51611))', 3857)),
(3, 'Parcela 2', ST_GeomFromText('POLYGON ((-0.10592 51.51611, -0.08532 51.52412, -0.04738 51.51334, -0.10592 51.51611))', 3857));

INSERT INTO cows(user_id, name, battery_level, plot_id, geom) VALUES
(2, 'Manuela', 5, 1, ST_GeomFromText('POINT(-0.09407 51.51569)', 3857)),
(3, 'Pepa', 100, 2, ST_GeomFromText('POINT(-0.05442 51.49218)', 3857));
