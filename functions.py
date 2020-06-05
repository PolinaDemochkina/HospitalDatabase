create_drop_db = """
create extension if not exists dblink;
CREATE OR REPLACE FUNCTION create_database(name varchar) returns void as $$
    begin
        if not exists (select from pg_database where datname = name) then
            perform dblink_exec(
                'dbname=postgres user=postgres',
                'create database ' || quote_ident(name) || ' with owner polina'
          );
        end if;
    end;
$$ language plpgsql;

create extension if not exists dblink;
CREATE OR REPLACE FUNCTION delete_database(name varchar) returns void as $$
    begin
            perform dblink_exec(
                'dbname=postgres user=postgres',
                'drop database if exists ' || quote_ident(name)
            );
    end;
$$ language plpgsql;
"""

all_functions = """
CREATE TABLE if not exists doctors (
    id bigserial PRIMARY KEY NOT NULL,
    name varchar(30) UNIQUE NOT NULL
);create index if not exists doctor_id on doctors (id);

CREATE TABLE if not exists patients (
    id bigserial PRIMARY KEY NOT NULL,
    name varchar(30) UNIQUE NOT NULL,
    birthday date NOT NULL,
    phone_number varchar(11) NOT NULL,
    doctor_id bigserial NOT NULL references doctors (id) ON DELETE CASCADE ON UPDATE CASCADE,
    check_in_time TIMESTAMP WITH TIME ZONE default CURRENT_TIMESTAMP
);create index if not exists patient_name on patients (name);

CREATE OR REPLACE FUNCTION check_in_time() RETURNS TRIGGER AS $body$
    BEGIN
        NEW.check_in_time = CURRENT_TIMESTAMP;
        return NEW;
    END; 
$body$ LANGUAGE plpgsql;

DROP TRIGGER if exists check_in_time on patients;
CREATE TRIGGER check_in_time
    BEFORE UPDATE on patients
FOR ROW EXECUTE PROCEDURE check_in_time();
    END;
    
CREATE OR REPLACE FUNCTION get_all_patients() RETURNS json as $$
    begin
        return (select json_agg(patients) FROM patients);
    end;
$$ language plpgsql;

CREATE OR REPLACE FUNCTION get_all_doctors() RETURNS json as $$
    begin
        return (select json_agg(doctors) FROM doctors);
    end;
$$ language plpgsql;

CREATE OR REPLACE FUNCTION add_patient(name_ varchar, birthday_ varchar, phone_number_ varchar, 
                                       doctor_id_ bigint) returns void as $$
begin
    INSERT INTO patients (name, birthday, phone_number, doctor_id) values (name_, to_date(birthday_, 'DD-MM-YYYY'), phone_number_, doctor_id_);
    end;
$$ language plpgsql;

CREATE OR REPLACE FUNCTION add_doctor(name_ varchar) RETURNS void as $$
begin
    insert into doctors (name) values (name_);
    end;
$$ language plpgsql;

CREATE OR REPLACE FUNCTION delete_patient_by_ID(id_ bigint) RETURNS void as $$
    begin
        delete FROM patients WHERE id = id_;
    end;
$$ language plpgsql;

CREATE OR REPLACE FUNCTION delete_patient_by_name(name_ varchar) RETURNS void as $$
begin
    delete FROM patients WHERE name = name_;
    end;
$$ language plpgsql;

CREATE OR REPLACE FUNCTION delete_patient_by_birthday(birthday_ varchar) RETURNS void as $$
begin
    delete FROM patients WHERE birthday = to_date(birthday_, 'DD-MM-YYYY');
    end;
$$ language plpgsql;

CREATE OR REPLACE FUNCTION delete_patient_by_phone_number(phone_number_ varchar) RETURNS void as $$
begin
    delete FROM patients WHERE phone_number = phone_number_;
    end;
$$ language plpgsql;

CREATE OR REPLACE FUNCTION delete_patient_by_doctor(doctor_id_ bigint) RETURNS void as $$
begin
    delete FROM patients WHERE doctor_id = doctor_id_;
    end;
$$ language plpgsql;

CREATE OR REPLACE FUNCTION delete_doctor_by_ID(id_ bigint) RETURNS void as $$
    begin
        delete FROM doctors WHERE id = id_;
    end;
$$ language plpgsql;

CREATE OR REPLACE FUNCTION delete_doctor_by_name(name_ varchar) RETURNS void as $$
begin 
    delete FROM doctors WHERE name = name_;
    end;
$$ language plpgsql;

CREATE OR REPLACE FUNCTION check_patient(_id bigint) RETURNS json as $$
begin
    return (select json_agg(1) FROM patients WHERE id = _id);
    end;
$$ language plpgsql;

CREATE OR REPLACE FUNCTION check_doctor(_id bigint) RETURNS json as $$
begin
    return (select json_agg(1) FROM doctors WHERE id = _id);
    end;
$$ language plpgsql;

CREATE OR REPLACE FUNCTION edit_patient_name(id_ bigint, new_name varchar) RETURNS void as $$
begin
    update patients set name = new_name WHERE id = id_;
    end;
$$ language plpgsql;

CREATE OR REPLACE FUNCTION edit_patient_birthday(id_ bigint, birthday_ varchar) RETURNS void as $$
begin
    update patients set birthday = to_date(birthday_, 'DD-MM-YYYY') WHERE id = id_;
    end;
$$ language plpgsql;

CREATE OR REPLACE FUNCTION edit_patient_phone_number(id_ bigint, phone_number_ varchar) RETURNS void as $$
begin
    update patients set phone_number = phone_number_ WHERE id = id_;
    end;
$$ language plpgsql;

CREATE OR REPLACE FUNCTION edit_patient_doctor(id_ bigint, doctor_id_ bigint) RETURNS void as $$
begin
    update patients set doctor_id = doctor_id_ WHERE id = id_;
    end;
$$ language plpgsql;

CREATE OR REPLACE FUNCTION edit_doctor_name(id_ bigint, name_ varchar) RETURNS void as $$
begin 
    update doctors set name = name_ WHERE id = id_;
    end;
$$ language plpgsql;

CREATE OR REPLACE FUNCTION get_patients_by_name(name_ varchar) RETURNS json as $$
    begin
        return (select json_agg(patients) FROM patients WHERE name = name_ );
    end;
$$ language plpgsql;

CREATE OR REPLACE FUNCTION get_patients_by_birthday(birthday_ varchar) RETURNS json as $$
    begin
        return (select json_agg(patients) FROM patients WHERE birthday = to_date(birthday_, 'DD-MM-YYYY') );
    end;
$$ language plpgsql;

CREATE OR REPLACE FUNCTION get_patients_by_phone_number(phone_number_ varchar) RETURNS json as $$
    begin
        return (select json_agg(patients) FROM patients WHERE phone_number = phone_number_);
    end;
$$ language plpgsql;

CREATE OR REPLACE FUNCTION get_patients_by_doctor(doctor_id_ bigint) RETURNS json as $$
    begin
        return (select json_agg(patients) FROM patients WHERE doctor_id = doctor_id_);
    end;
$$ language plpgsql;

CREATE OR REPLACE FUNCTION get_doctors_by_name(name_ varchar) RETURNS json as $$
    begin
        return (select json_agg(doctors) FROM doctors WHERE name = name_);
    end;
$$ language plpgsql;

CREATE OR REPLACE FUNCTION clear_patients() RETURNS void as $$
    begin
        TRUNCATE patients;
    end;
$$ language plpgsql;

CREATE OR REPLACE FUNCTION clear_doctors() RETURNS void as $$
    begin
        TRUNCATE doctors cascade;
    end;
$$ language plpgsql;
"""