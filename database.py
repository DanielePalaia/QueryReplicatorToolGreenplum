# -*- coding: utf-8 -*-
import pygresql
from pygresql import pg
from properties import *
from utils import *
import os
import string

# function to connect to a database
def connectToDataBase(hostname, username, dbname, port):
    db = pg.connect(dbname=dbname, host=hostname, port=port, user=username)
    return db

# select query from log file
# statement is a variable which show the sql operation to search
# limit in case we want to limit the number of rows
def executeQueryOnLog(dbInput):

    if (typeExecution == 'session'):
       query_tmp_statement1 = 'create temp table T1 as (select user_name, database_name, debug_query_string, event_detail,gp_session_id,thread,gp_command_count \n'
       query_tmp_statement1 = query_tmp_statement1 + 'from ( select user_name, database_name, debug_query_string, event_time \n'
       query_tmp_statement1 = query_tmp_statement1 + ', substr(gp_session_id,4) as  gp_session_id,mod(substr(gp_session_id,4)::integer,'+N_PROC+') as thread\n'
       query_tmp_statement1 = query_tmp_statement1 + ', substr(gp_command_count,4)::integer as gp_command_count\n'
       query_tmp_statement1 = query_tmp_statement1 + ', max(case when event_detail like \'parameters: $1 = %\' then event_detail else null end) over (partition by session_start_time,gp_session_id,process_id,gp_command_count) as event_detail\n'
       query_tmp_statement1 = query_tmp_statement1 + ', rank() over (partition by session_start_time,gp_session_id,process_id,gp_command_count order by event_time) as rank \nfrom ' 
       query_tmp_statement1 = query_tmp_statement1 + logDatabaseTable + '\n' 
       query_tmp_statement1 = query_tmp_statement1 + 'where event_message not like \'duration:%\' and event_message not ilike \'execute %: insert%values%(%)%\''
       query_tmp_statement1 = query_tmp_statement1 + ' and debug_query_string not ilike \'%BEGIN%\' and debug_query_string not ilike \'%COMMIT%\''
       query_tmp_statement2 = ') T where rank = 1) distributed randomly;\n'
       query_tmp_statement3 = 'analyze t1;\n select * from T1 where not exists (select 1 from ' + excludedQueryTable + ' where lower(debug_query_string) similar to lower(query_pattern)) order by gp_session_id,gp_command_count;\n'
    else:
       query_tmp_statement1 = 'create temp table T1 as (select user_name, database_name, debug_query_string\n'
       query_tmp_statement1 = query_tmp_statement1 + ', max(case when event_detail like \'parameters: $1 = %\' then event_detail else null end) as event_detail\n'
       query_tmp_statement1 = query_tmp_statement1 + ' from ' + logDatabaseTable + '\n'
       query_tmp_statement1 = query_tmp_statement1 + 'where event_message not like \'duration:%\' and event_message not ilike \'execute %: insert%values%(%)%\''
       query_tmp_statement1 = query_tmp_statement1 + ' and debug_query_string not ilike \'%BEGIN%\' and debug_query_string not ilike \'%COMMIT%\''
       query_tmp_statement2 = 'group by 1,2,3) distributed randomly;\n'
       query_tmp_statement3 = 'analyze t1;\n'
       query_tmp_statement3 = query_tmp_statement3 + 'select *,null as gp_session_id, mod(row_number() over(),'+N_PROC+') as thread from T1\n' 
       query_tmp_statement3 = query_tmp_statement3 + ' where not exists (select 1 from ' + excludedQueryTable + ' where lower(debug_query_string) similar to lower(query_pattern));\n'


    if (filterInputDatabases ==''):
        query_results=dbInput.query(query_tmp_statement1 + query_tmp_statement2 + query_tmp_statement3).getresult()
        print(query_tmp_statement1 + query_tmp_statement2 + query_tmp_statement3)
    else:
        database_condition=' and '
        count = 0
        for database in filterInputDatabases.split(','):
            count = count + 1
            if (count < len(filterInputDatabases.split(',')) ):
                database_condition=database_condition + ' database_name=' + '\'' + database + '\' or '
            else:
                database_condition=database_condition + ' database_name=' + '\'' + database + '\''
        print('executing: ')
        print(query_tmp_statement1 + database_condition + query_tmp_statement2 + query_tmp_statement3)
        query_results=dbInput.query(query_tmp_statement1 + database_condition + query_tmp_statement2 + query_tmp_statement3).getresult()
    return query_results

def executeQueryOutput(dbOutput, queryStatement):
    query_results = dbOutput.query(queryStatement)

#Create output table (to be tested)
def createOutputTable(dbInput):
    query_results=dbInput.query('CREATE TABLE IF NOT EXISTS ' + outputTableName + '(id int NOT NULL AUTO_INCREMENT, user varchar(255), database varchar(255), statement varchar(255), success Boolean)')
    return query_results

def resetOutputTable(hostname, username, dbname, port):
    db = pg.connect(dbname=dbname, host=hostname, port=port, user=username)
    try:
        query_results=db.query('DROP table if exists ' + outputTableName)
        query_results=db.query('CREATE TABLE ' + outputTableName + ' (sequence serial primary key, userQuery VARCHAR(100000), database VARCHAR(100000), statement VARCHAR(100000), success VARCHAR(100000), error VARCHAR(100000), timestamp_start timestamp, timestamp_end timestamp)')
    except Exception as e:
        print('impossible to create output table: System error' + str(exception))

#Query output table
def queryOutputTable(hostname, username, dbname, port):
    dbInput = connectToDataBase(hostname, username, dbname, port)
    query_results=dbInput.query('SELECT userQuery, database, statement from ' + outputTableName + ' where success=\'False\';' ).getresult()
    return query_results, dbInput

def batchCopy(db_Input, filePath):
    statement = 'COPY ' + outputTableName + '(userQuery, database, statement, success, error, timestamp_start, timestamp_end) FROM \'' + filePath + '\''
    statement = statement + ' WITH CSV DELIMITER \'~\' LOG ERRORS SEGMENT REJECT LIMIT 100 PERCENT;'
    print (statement)
    db_Input.query(statement)

#Query output table
def countOutputTable(dbInput):
    query_results=dbInput.query('SELECT count(*) from ' + outputTableName + ';').getresult()
    line = query_results[0]
    return line[0]

def countOutputTableSuccess(dbInput):
    query_results=dbInput.query('SELECT count(*) from ' + outputTableName + ' WHERE success=\'True\';').getresult()
    line = query_results[0]
    return line[0]


