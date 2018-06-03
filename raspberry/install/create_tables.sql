create table sensors(time timestamp without time zone default timezone('utc'::text, now()), temperature real, humidity real);
CREATE TABLE cadastro(id serial not null, data_cadastro timestamp not null default now(), tempo int, minutos int, umi_min int, umi_max int, tempo_min int, temp_max int, modo int not null, primary key (id));
