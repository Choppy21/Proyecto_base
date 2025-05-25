create table alumnos(
id_a int auto_increment primary key,
nombre varchar(100) not null,
email varchar(100) unique not null,
telefono varchar(10)
);
alter table alumnos auto_increment = 1000;

create table materia(
id_m int auto_increment primary key,
nombre varchar(100) not null
);

create table inscripcion(
id_i int auto_increment primary key,
alumno_id int,
materia_id int,
foreign key (alumno_id) references alumnos(id_a),
foreign key (materia_id) references materia(id_m)
);

create table usuario(
alumno_id int primary key,
password varchar(255) not null,
foreign key (alumno_id) references alumnos(id_a)
);
