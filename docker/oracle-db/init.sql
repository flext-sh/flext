-- Oracle Database initialization for FLEXT Docker container
-- Creates test schema compatible with FLEXT projects

-- Switch to the FLEXTDB pluggable database
ALTER SESSION SET CONTAINER = FLEXTDB;

-- Create basic test tables
CREATE TABLE flext_test.employees (
    employee_id NUMBER(6) PRIMARY KEY,
    first_name VARCHAR2(20),
    last_name VARCHAR2(25) NOT NULL,
    email VARCHAR2(25) NOT NULL UNIQUE,
    salary NUMBER(8,2)
);

CREATE TABLE flext_test.departments (
    department_id NUMBER(4) PRIMARY KEY,
    department_name VARCHAR2(30) NOT NULL
);

CREATE TABLE flext_test.jobs (
    job_id VARCHAR2(10) PRIMARY KEY,
    job_title VARCHAR2(35) NOT NULL
);

-- Create sequences
CREATE SEQUENCE flext_test.emp_seq START WITH 1000 INCREMENT BY 1;
CREATE SEQUENCE flext_test.dept_seq START WITH 100 INCREMENT BY 10;

-- Insert basic test data
INSERT INTO flext_test.departments VALUES (10, 'Administration');
INSERT INTO flext_test.departments VALUES (20, 'Marketing');

INSERT INTO flext_test.jobs VALUES ('AD_PRES', 'President');
INSERT INTO flext_test.jobs VALUES ('IT_PROG', 'Programmer');

INSERT INTO flext_test.employees VALUES (1001, 'Steven', 'King', 'SKING', 24000);
INSERT INTO flext_test.employees VALUES (1002, 'Neena', 'Kochhar', 'NKOCHHAR', 17000);

-- Commit changes
COMMIT;

-- Display summary
SELECT 'FLEXT Oracle basic initialization completed' AS status FROM DUAL;
SELECT 'Tables created: ' || COUNT(*) AS result FROM all_tables WHERE owner = 'FLEXT_TEST';
SELECT 'Employees inserted: ' || COUNT(*) AS result FROM flext_test.employees;

EXIT;