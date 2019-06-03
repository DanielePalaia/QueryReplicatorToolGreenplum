drop EXTERNAL WEB TABLE if exists :v_ext_table_name;
CREATE EXTERNAL WEB TABLE :v_ext_table_name
(event_time	text,
user_name	text,
database_name	text,
process_id	text,
thread_id	text,
remote_host	text,
remote_port	text,
session_start_time	text,
transaction_id 	text,
gp_session_id	text,
gp_command_count	text,
gp_segment	text,
slice_id	text,
distr_tranx_id	text,
local_tranx_id	text,
sub_tranx_id	text,
event_severity	text,
sql_state_code	text,
event_message 	text,
event_detail	text,
event_hint	text,
internal_query	text,
internal_query_pos	text,
event_context	text,
debug_query_string	text,
error_cursor_pos	text,
func_name	text,
file_name	text,
file_line	text,
stack_trace	text)
 EXECUTE E:v_read_file
 ON MASTER 
 FORMAT 'csv' (delimiter ',' null ''  quote '"');
