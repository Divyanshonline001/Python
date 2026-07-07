CREATE DATABASE college;

CREATE DATABASE IF NOT EXISTS instagram;

DROP DATABASE IF EXISTS instagram;

SHOW DATABASES;

USE instagram;


CREATE TABLE user(
	id INT NOT NULL,
    age INT ,
    name VARCHAR(30) NOT NULL,
    email VARCHAR(30) UNIQUE,
    followers  INT DEFAULT 0,
    following  INT,
    constraint CHECK (age>=13) ,
    PRIMARY KEY (id)
);

INSERT INTO user 
(id, age, name, email, followers, following)
VALUES
(1, 14, "adam", "adam@yahoo.in", 123, 145),
(2, 15, "bob", "bob123@gmail.com", 200, 200),
(3, 16, "casey", "casey@gmail.com", 300, 302),
(4, 17, "donald", "donald@gmail.com", 100, 135);

INSERT INTO user 
(id, age, name, email, followers, following)
VALUES
(5, 14, "eve" , "eve@gmail.com", 34, 56),
(6, 17, "drax", "drax@gmail.com", 234,10000);

ALTER TABLE user
DROP COLUMN city;

ALTER TABLE instauser
RENAME to user;

SELECT * FROM user 
ORDER BY followers ASC;

SELECT age,count(id),max(followers) from user
group by age
HAVING max(followers)>=200
ORDER BY max(followers) DESC;

UPDATE user 
SET followers=600
WHERE age=14;

DELETE from user
WHERE age=17;

TRUNCATE  TABLE user;

SET SQL_SAFE_UPDATES=0;

CREATE TABLE post(
	id INT PRIMARY KEY,
    content VARCHAR(100) NOT NULL,
	user_id INT,
    foreign key (user_id) REFERENCES user(id)
);

INSERT INTO post 
(id, content, user_id)
VALUES
(101,"Hello World",3),
(102,"BYE BYE",1),
(103,"Hello Dalle",3);

DROP TABLE post;

SELECT * FROM post;


USE college;

CREATE TABLE teacher(
	id INT NOT NULL,
    name VARCHAR(40),
    subject VARCHAR(20),
    salary INT DEFAULT 10000
);

INSERT INTO teacher 
(id, name, subject, salary)
VALUES
(23,"ajay","math",50000),
(47,"bharat","english",60000),
(18,"chetan","chemistry",45000),
(9,"divya","physics",75000);

ALTER TABLE teacher 
CHANGE COLUMN salary ctc INT;

UPDATE teacher 
SET ctc = ctc + (0.25 * ctc);

ALTER TABLE teacher 
ADD COLUMN city VARCHAR(20) DEFAULT "GURGAON";

ALTER TABLE teacher 
DROP COLUMN ctc;

CREATE TABLE student(
	rollno INT NOT NULL,
    name VARCHAR(40),
    city VARCHAR(20),
    marks INT DEFAULT 0
);

INSERT INTO student
(rollno,name,city,marks)
VALUES
(110,"adam","Delhi",76),
(108,"bob","Mumbai",65),
(124,"casey","Pune",94),
(112,"duke","Pune",80);

SELECT city FROM student
GROUP BY city;

SELECT * FROM student;


CREATE TABLE Students (
    student_id INT,
    name VARCHAR(50),
    course_id INT
);

INSERT INTO Students VALUES
(1,'Divyansh',101),
(2,'Rahul',102),
(3,'Anjali',103),
(4,'Priya',104);

CREATE TABLE Courses (
    course_id INT,
    course_name VARCHAR(50)
);

INSERT INTO Courses VALUES
(101,'CSE'),
(102,'IT'),
(103,'ECE'),
(105,'Mechanical');

SELECT Students.name, Courses.course_name
FROM Students
INNER JOIN Courses
ON Students.course_id = Courses.course_id;

SELECT Students.name, Courses.course_name
FROM Students
LEFT JOIN Courses
ON Students.course_id = Courses.course_id;

SELECT Students.name, Courses.course_name
FROM Students
RIGHT JOIN Courses
ON Students.course_id = Courses.course_id;

SELECT Students.name, Courses.course_name
FROM Students
LEFT JOIN Courses
ON Students.course_id = Courses.course_id
UNION
SELECT Students.name, Courses.course_name
FROM Students
RIGHT JOIN Courses
ON Students.course_id = Courses.course_id;

SELECT Students.name, Courses.course_name
FROM Students
CROSS JOIN Courses;