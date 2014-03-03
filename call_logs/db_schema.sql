create table call_log_info(id integer primary key autoincrement, name varchar(250), numbertype tinyint, number varchar(100), log_date datetime not null unique, duration int(11), is_new tinyint, call_id int(11), type tinyint);  
				
				
