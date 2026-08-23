-- Student table sample script for OraCLI 10G

CREATE TABLE student (
    rollno NUMBER,
    name VARCHAR2(50),
    cgpa NUMBER(3,2)
);

INSERT INTO student VALUES (101, 'Rahul', 8.7);
INSERT INTO student VALUES (102, 'Priya', 9.1);
INSERT INTO student VALUES (103, 'Amit', 7.8);

SELECT * FROM student;
