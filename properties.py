# PROPERTIES CONFIGURATION FILE FOR THE QUERY REPLICATOR TOOL #
# In this file you must set all the properties that the Query Replicator tool will use to work#

# where greenplum logs are stored
str_Input_File='/home/gpadmin/Customer/Tranquilidade/10_Input/logs/gpdb-2018-04-23_000000.csv.gz'
# are the logs compressed or not)
flag_Compress=True
# name of the input table
logDatabaseTable = 'public.test_tranquilidade_20180423'

# input database info (to be replaced by command shell parameters)
logDatabaseIPAddress= '10.91.51.23'
logDatabaseUsername= 'gpadmin'
logDatabasePort = 5533
logDatabaseName = 'test_gpdb5'
excludedQueryTable = 'public.t_list_excluded_query'
excludedQueryFile = '/home/gpadmin/Temp/QueryReplicator/scripts/GPDB_t_list_excluded_query.csv'

# Database Settings
DatabaseStatementTimeout='15s'
DatabaseOptimizer='off'

# output database info (where to inject the input queries)
outputDatabaseIPAddress= '10.91.51.23'
outputDatabaseUsername= 'gpadmin'
outputDatabasePort = 5533

# input database filtering (just execute queries for the databases specified)
filterInputDatabases='pr_grupo_tranquilidade'

#Type of Execution
#    - session ==> the queries are executed in session as in the original DB (useful in case of temp tables)
#    - distinct ==> the queries are deduplicated (faster because less queries to execute)
typeExecution='session'

# name of the table where you want to store the results of the Query replicator tool computation
outputTableName="results_20180423_thread10"

N_PROC = '10'
