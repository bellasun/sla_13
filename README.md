***************************README.md****************************************
#sla_13 V1.0
#put trace files into \\135.242.80.37\sharing_folder_37\trace_repo\
#trace_file name rule:crXX_[site]summay
#like: cr135719_[SH_TLO]unexpect_CIC_is_blocked


#Manual:
[0] - readme------------------------------------------------------------
What you are seeing...


[1] - Log information--------------------------------------------------
By this function, you can get the detail information for the log file to
be processed.
note:
'start/end time' and 'date' are all referred to the log contents not the files
themselves.
'status' tells you how the log file is decoded as below:
'full decoded': all the rtrc are decoded out
'partial decodede': not all the rtrc decoded
'no trace': means theres is no *.rtrc or *.rtrc_backup detected in the log file
'not decoded': raw log files whithout any *.out decode files
'unknown': ambiguoues state that need your further check.


[2] - unzip, decode and clean-------------------------------------------
This function unzip, decode and flush(default) all the trace files in
the log files.
***tip:
To decode only DTC 210 rtrc files, please input:'2,DTC,201'
only input '2' to decode all the files and delete the undecoded files after
input '2,k' to decode all but keep the tgz and rtrc files


[3] - trace line repetition---------------------------------------------
This function showes the result of the trace line repetion statistics of
TOP 10
*tip:
'3,OCPR' to only calculate the repetition in OCPR.
note: 
above feature not implemented yet.
By default the function will analysze all the *out files. So if you want 
to accelerate it, in [2], input the specific module to unzip and decode.

[4] - auto keyword search-----------------------------------------------
This function is really thrilling that can automatically dignose the log
file to find any historical issues with keywords pre-set by domain experts
*tip:
'4,CM' to narrow down the search sacle to only 'CM' domain.
'4,TEL' for 'Telecom' domain
'4,PM' for pm
'4,PF' for PF
note: above tip mentioned feature would be implemented in V1.01 in future..


[5] - custom search-----------------------------------------------------
This function feedback you the search result of  any word you input
****tip:
key word followed with VCE type to accelerate searching:like: 'CCDC_FFM,OCPR'
further search feature  would be triiggered when custom search result is huge


[s] - select log file--------------------------------------------------------
If the default chose log file is not what you want, you can use this function
to change. Just input 's,your_log_file_name' to change to your_log_file_name
which would be process by all the commands.


[r] - refresh-----------------------------------------------------------------
This function refresh the trace_repo dir to list all the avialable log files
If you have upload a new log file when SLA running, you should use this function.
**tip: to show log output, input command 'r,log' and to turn log off just input again.
     to accelerate the SLA processing speed, input 'r,on' to turn on mutithread porcessing
     feature.

[q] - quit--------------------------------------------------------------------
Quit SLA
tip:
You can quit anytime if an input of 'q' command texted.


PS:
if you can't not access trace_repo, like permission denied
maybe your account doesn't join the group 'vboxsf'
use root to: usermod -a -G vboxsf user

any question please contatct "felix.zhang@alcatel-lucent.com"

***************************README.md****************************************
