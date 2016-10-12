***************************README.md****************************************
#sla_13 V1.0
#put trace files into \\135.242.80.37\sharing_folder_37\trace_repo\
#trace_file name rule:crXX_[site]summay
#like: cr135719_[SH_TLO]unexpect_CIC_is_blocked


#Tips:

[2] - unzip, decode and clean
To decode only DTC 210 rtrc files, please input:'2,DTC,201'
only input '2' to decode all the files and delete the undecoded files after
input '2,k' to decode all but keep the tgz and rtrc files

[3] - trace line repetition
'3,OCPR' to only analysis 'OCPR' [TODO]

[5] - custom search
key word followed with VCE type to accelerate searching
like: 'CCDC_FFM,OCPR'

further search would be triiggered after custom search if result is huge

PS:
if you can't not access trace_repo, like permission denied
maybe your account doesn't join the group 'vboxsf'
use root to: usermod -a -G vboxsf user

any question please contatct "felix.zhang@alcatel-lucent.com"
***************************README.md****************************************
