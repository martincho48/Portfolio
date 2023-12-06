-------------
---MAIN
-------------

--create new table copying everything in it, create rowid in new table
CREATE TABLE lesson_copy AS 
  SELECT ROWID, *
  FROM lesson;

  
--trim USD from the column
UPDATE lesson_copy
SET profit_bruto_USD = trim(profit_bruto_USD , "USD ");


--add a new column as integer and then copy numbers there
ALTER TABLE lesson_copy
	ADD profit_bruto_USD_new INTEGER;
	
UPDATE lesson_copy
	SET profit_bruto_USD_new = profit_bruto_USD;

ALTER TABLE lesson_copy 
	DROP COLUMN  profit_bruto_USD; 

	
--replace slash with hyphen, change order of datatime (column_name, start, length), ||=and
UPDATE lesson_copy
SET date = substr(date, 7, 5) || '-' ||
           substr(date, 4, 2) || '-' ||
           substr(date, 1, 2)
WHERE date LIKE '__/__/____';

	
--create new table from SELECT everything (add two columns-week and year)
CREATE TABLE week_year_table AS 
	SELECT *, strftime('%W',date) AS week_number, strftime('%Y',date) AS year_number
	FROM lesson_copy;

	
--add column and add number 1 which is amout of lessons
ALTER TABLE week_year_table
	ADD lesson_count INTEGER;
UPDATE week_year_table
	SET lesson_count =1;


--sum profit and lessons according to same month and year using GROUP BY
CREATE TABLE sum_profit_lessons AS --create table form select
select
   week_number, year_number,sum(profit_bruto_USD_new) as profit_bruto_week_USD,sum(lesson_count) as number_of_lessons
from week_year_table
group by week_number, year_number

ORDER BY 
	year_number ASC;

	
--create table with active students
CREATE TABLE active_students AS
--order by same names
SELECT 	*, 
		row_number() OVER ( 
        PARTITION BY "name"
		ORDER BY "name"
		) AS "Function"
--select active students 
FROM
	lesson_copy
WHERE
	"Name" IN (
		SELECT
			"name"
		FROM
			student		
		WHERE
			"Activity_Status" = "active"
		);						


	

	


