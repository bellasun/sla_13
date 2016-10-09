#!/usr/bin/python

import subprocess
import sys
import glob
import re
import time, datetime
import logging
from common import *

#felix
###############################################################################
contents = []
f_change = True
###############################################################################
# common functions

# calculate the time difference between stime1 and stime2
# stime1, stime2 format: e.g. 2016-05-06 10:12:59
# output: 2 days, 4:12:58
def diff_time(stime1, stime2):
    time1 = time.strptime(stime1, "%Y-%m-%d %H:%M:%S");
    time2 = time.strptime(stime2, "%Y-%m-%d %H:%M:%S");
    dtime1 = datetime.datetime(time1[0], time1[1], time1[2], time1[3], time1[4], time1[5]);
    dtime2 = datetime.datetime(time2[0], time2[1], time2[2], time2[3], time2[4], time2[5]);
    return dtime2 - dtime1;

def filter_file(file):
    allowed_list = [".out"];
    for ext in allowed_list:
        if file.strip("\n").endswith(ext):
            return True;
    return False;

def filter_line(line):
    '''
    0000039960 2016/04/21 06:25:04:679 ticks upd,sec=1461219889,usec=851573,tickes=537629950258,freq=1795467000
    ====
    0000042747 06:25:48:441 voscomm.c 182 IMSD:BB 0C 00 08 20 4D D8 06 EE 00 ... 
    0000042748 06:25:48:441 voscomm.c 185 IMSD:19 00 00 00 1F 00 06 00 40 00 ...
    0000042749 06:25:48:441 voscomm.c 264 IMSD:msg 1752 FMM25->FMM15
    ====
    2619576910 17:18:45:432 vostask.c 1100 IMRV:1A 01 00 28 20 4D E6 00 02 00 ... 
    2619576911 17:18:45:432 vostask.c 1103 IMRV:07 40 01 01 01 01 01 01 00 00 ...
    2619576912 17:18:45:432 vostask.c 1140 IMRV:VCE 2 msg 230 FMM82->FMM8
    ====
    2619576964 17:18:45:432 cmw-api.c 870 EMSD:msg 1258 Prio 2 VCE2 FMM59 -> VCE614 FMM202
    2619576965 17:18:45:432 cmw-common.c 563 DBUG:Hdr: 1C 00 00 00 66 02 00 00 
                           0: 14 00 00 04 00 2D EA 04  66 02 CA 00 02 00 3B 00 
                          16: 00 02 14 00
    ====
    0000039971 06:25:04:745 cmw-api.c 1085 EMRV:msg 332 Prio 3 VCE888 FMM22 -> VCE238 FMM4
    0000039972 06:25:04:745 cmw-common.c 558 DBUG:Hdr: 56 00 00 00 EE 00 00 00 
                           0: 4E 00 00 00 20 3D 4C 01  EE 00 04 00 78 03 16 00 
                          16: 78 03 16 00 01 00 40 00  07 01 00 00 78 03 A0 14 
    '''
    filter_lines = ["ticks upd,sec=", 
        "voscomm.c 182 IMSD:", "voscomm.c 185 IMSD:",
        "vostask.c 1100 IMRV:", "vostask.c 1103 IMRV:", 
        "cmw-common.c 563 DBUG:Hdr: ", "\t" * 5, "cmw-common.c 558 DBUG:Hdr:",
        # vos.c 120 ITFP:GET_MSG_BUF called by BackgroundTask
        # vos.c 120 ITFP:GET_MSG_BUF called by G_S_YS9SAZ_BSC_LAPD_L2
        # vos.c 126 ITFP:RET_MSG_BUF called by G_S_GXAFAL_RFM_CCCH
        "vos.c 120 ITFP:GET_MSG_BUF called by",
        "vos.c 126 ITFP:RET_MSG_BUF called by",
        # vos.c 108 ITFP:QUICK_GET_MEM called by G_A_AAVYAD_ME_REMOTE_SSD_ITF
        # vos.c 102 ITFP:GET_MEM called by BackgroundTask
        # vos.c 114 ITFP:RET_MEM called by G_S_GXAFAL_RFM_CCCH
        "vos.c 108 ITFP:QUICK_GET_MEM called by",
        "vos.c 102 ITFP:GET_MEM called by",
        "vos.c 114 ITFP:RET_MEM called by",
        # vos.c 66 ITFP:MSG_WAIT called by G_S_GXAFAL_RFM_CCCH
        # vos.c 80 ITFP:MSG_SEND called by G_S_GXAFAL_RFM_CCCH
        "vos.c 66 ITFP:MSG_WAIT called by",
        "vos.c 80 ITFP:MSG_SEND called by",
        # vos.c 72 ITFP:OWN_PROCESS_ID called by G_S_YS9SAZ_BSC_LAPD_L2
        "vos.c 72 ITFP:OWN_PROCESS_ID called by",
        # vos.c 178 ITFP:START_TIMER called by G_S_YS9RAL_RF_MGT_L3
        # vos.c 213 ITFP:RELEASE_TIMER called by G_S_YS9RAL_RF_MGT_L3
        # vos.c 220 ITFP:CANCEL_TIMER called by G_S_YS9SAZ_BSC_LAPD_L2
        # vos.c 199 ITFP:RESTART_TIMER called by G_S_YS9SAZ_BSC_LAPD_L2
        "vos.c 178 ITFP:START_TIMER called by",
        "vos.c 213 ITFP:RELEASE_TIMER called by",
        "vos.c 220 ITFP:CANCEL_TIMER called by",
        "vos.c 199 ITFP:RESTART_TIMER called by",
        # 14160:vos.c 302 ITFP:GET_FMM_ID called by G_S_YS9SAZ_BSC_LAPD_L2
        "vos.c 302 ITFP:GET_FMM_ID called by",
    ];
    for ln in filter_lines:
        if ln  in line:
            return False;
    return True;

def remove_time_stamp(line):
    i = len("0009048553 03:00:20:079 ");
    key_line = line.strip("\n")[i:-1];
    return key_line;

###############################################################################
def read_log_info(file_path):
    info = {};
    # read BSC version
    # "BSC-Genaral.txt"
    try:
        h = open("%s"%file_path, "r");
        while True:
            line = h.readline();
            if not line:
                break;
            if "BSC_VERSION" in line:
                version_list = line.strip("\n").strip("\r").split(":");
                info["version"] = version_list[1];
                break;
    except Exceptions as e:
    #just return am empty info if error
        print e
        return info
    h.close()

    # read log time period
    '''
    3.Input StartTime [YYYYMMDDHHMM], e.g. 200901012300
    YEAR=2016 MONTH=03 DAY=30 HOUR=02 MINUTE=55
    4.Input EndTime [YYYYMMDDHHMM], e.g. 200901012359
    YEAR=2016 MONTH=03 DAY=30 HOUR=03 MINUTE=15
    or
    YEAR=2016 MONTH=05 DAY=18 HOUR=19 MINUTE=15
    YEAR=2016 MONTH=05 DAY=18 HOUR=19 MINUTE=40
    Starttime is 201605181915, EndTime is 201605181940
    '''
    #read trace_collection.log file content:
    log_list = []
    pare_dir = file_path.strip("BSC-Genaral.txt")

    try:
        h_log = open("%strace_collection.log"%pare_dir, "r");
        #key = date,starttime,endtime"
        key = "date"
        while True:
            line = h_log.readline();
            if not line:
                break;
            l = re.match(r"YEAR=(\d+) MONTH=(\d+) DAY=(\d+) HOUR=(\d+) MINUTE=(\d+)", line);
            if l:
                r = [t(s) for t,s in zip((int, int, int, int, int), l.groups())];
                if key == "date":
                    info[key] = "%4d-%02d-%02d"%(r[0], r[1], r[2]);
                    key = "starttime"
                if key == "starttime" or key == "endtime":
                    info[key] = "%02d:%02d:00"%(r[3], r[4]);
                '''
                time_tuple = time.strptime(line.strip("\n").strip("\r"), 
                        "YEAR=%Y MONTH=%m DAY=%d HOUR=%H MINUTE=%M");
                info[key] = time.strftime("%Y-%m-%d %H:%M:%S", time_tuple);
                '''
                if key == "endtime":
                    break;
                key = "endtime";
    except Exception as e:
        print e
        return info

    h_log.close();
    return info;
########################################################

def list_log_info(info):
    printd("==================================================================\n");
    printd(" LOG INFOMATION\n");
    sformat = " %-20s: %-40s\n";
    printd(sformat%("BSC Version", info["version"]));
    if info.has_key("starttime"):
        # for standby OMCP, the start time can not be extraced! 
        printd(sformat%("Start Time", info["starttime"]));
        printd(sformat%("End Time", info["endtime"]));
        printd(sformat%("Duration Time", diff_time(info["starttime"], info["endtime"])));
    printd("==================================================================\n");

#####################end list_log_info############################

def uncompress_log(realtime_dir_list):

    for dir in realtime_dir_list: 

        #decide if untar necessary:
        ne =  subprocess.Popen("find %s -name *.rtrc.out"%dir, shell=True, stdout=subprocess.PIPE,\
                stderr=subprocess.STDOUT)
        ne.wait()
        buff = ne.stdout.readline()
        if buff != "":
            continue

        p = subprocess.Popen("ls %s/*.tgz"%dir, shell=True, stdout=subprocess.PIPE,\
        stderr=subprocess.STDOUT)
        p.wait()
        while True:
            buff = p.stdout.readline();
            if buff == '' and p.poll() != None:  
                break;
            file = buff.strip("\n");
            printd("unzip %s\n"%file);
            #  -m don't extract file modified time
            ptar = subprocess.Popen("tar -mxvf %s -C %s > /dev/null"%(file, dir), shell=True);
            ptar.wait();

        print
    
###############end uncompress_log###############################


def decode_log(realtime_dir_list) :

    for dir in realtime_dir_list:

        #decide if untar necessary:
        ne =  subprocess.Popen("find %s -name *.rtrc.out"%dir, shell=True, stdout=subprocess.PIPE,\
                stderr=subprocess.STDOUT)
        ne.wait()
        buff = ne.stdout.readline()
        if buff != "":
            print "decoded trace already exist."
            continue

        p = subprocess.Popen("./tools/BSCTraceDecode -l %s"%(dir), shell=True,\
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT);

        while True:
            buff = p.stdout.readline();
            if buff == '' and p.poll() != None:
                break;
            elif buff == '':
                continue;
            printd(buff);

##############end decode_log##################################


def flush_rtrc(realtime_dir_list):

    for dir in realtime_dir_list:
        p = subprocess.Popen("rm %s/*.rtrc %s/*.rtrc_backup"%(dir,dir), shell=True,\
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT);
        p.wait()

##############end flush_rtrc#################################

def stat_line(dir) :
    printd("start stat line info %s ...\n"%dir);
    mdict = {};
    files = glob.glob("%s/*.out"%dir);
    count = len(files);
    i = 1;
    for fn in files:
        printd("[%2d/%2d] %s\n"%(i, count, fn));
        i = i + 1;
        if not filter_file(fn):
            continue;
        file = open(fn);
        while True:
            lines = file.readlines(100000);
            if not lines:
                break;
            n = 0;
            for line in lines : 
                #print(line.strip("\n"));
                n = n + 1;
                if filter_line(line):
                    key_line = remove_time_stamp(line);
                    if mdict.has_key(key_line):
                        mdict[key_line] += 1;
                    else:
                        mdict[key_line] = 1;
    # sort
    sdict = sorted(mdict.iteritems(), key=lambda d:d[1], reverse = True);
    return sdict;

def read_key_word_list(file):
    key_words = {};
    key_words_file = open(file, "r");
    while True:
        line = key_words_file.readline();
        if not line:
            break;
        word = line.strip("\n").strip(" ");
        if word == "" or word.startswith("#"):
            continue;
        else:
            pair = [word, ""];
            separator = "%%"; # config file separator
            if separator in word:
                pair = word.split(separator);
            key_words[pair[0].strip(" ")] = pair[1].strip(" ");
    key_words_file.close();
    return key_words;

def grep_key_word_custom(key_word, dir):
    printd("start grep custom key word '%s' in %s ...\n"%(key_word, dir));
    p = subprocess.Popen("grep -c '%s' %s/*.out"%(key_word, dir), shell=True, stdout=subprocess.PIPE);
    flag = 0;
    while True:
        buff = p.stdout.readline();
        if buff == '' and p.poll() != None:
            break;
        if buff == '':
            continue;
        data = buff.strip("\n").split(":");
        if (len(data) > 1 and int(data[1]) > 0):
            printd(buff);
            ph = subprocess.Popen("grep -hn '%s' %s"%(key_word, data[0]), shell=True, stdout=subprocess.PIPE);
            while True:
                line = ph.stdout.readline();
                if line == '' and ph.poll() != None:
                    break;
                if line == '':
                    continue;
                printd(line, False);

def grep_key_word(key_word, dir) :
    printd("start grep key word '%s' in %s ...\n"%(key_word, dir));
    count = 0;
    p = subprocess.Popen("grep -c '%s' %s/*.out"%(key_word, dir), shell=True, stdout=subprocess.PIPE);
    files = [];
    while True:
        buff = p.stdout.readline();
        if buff == '' and p.poll() != None:
            break;
        data = buff.strip("\n").split(":");
        if (len(data) > 1 and int(data[1]) > 0):
            count += int(data[1]);
            files.append(data[0]);
            printd(buff);
    printd("key_word: %s, count: %d\n"%(key_word, count));
    result = [key_word, count, files];
    return result;

def grep_key_word_detail(key_word, file) :
    #printd("start grep key word detail: %s in %s ...\n"%(key_word, file));
    p = subprocess.Popen("grep '%s' %s"%(key_word, file), shell=True, stdout=subprocess.PIPE);
    mdict = {};
    while True:
        buff = p.stdout.readline();
        if buff == '' and p.poll() != None:
            break;
        elif buff == '':
            continue;
        i = len("0009048553 03:00:20:079 ");
        key_line = buff[i:-1];
        if mdict.has_key(key_line):
            mdict[key_line] += 1;
        else:
            mdict[key_line] = 1;
    return mdict;

def list_stat_result(dir, sdict):
    printd("==================================================================\n");
    stat_result = open("%s/stat_result"%dir, "w");
    i = 0;
    for item in sdict:
        info = "%d:%s"%(item[1], item[0]);
        stat_result.write(info + "\n");
        if i < 10:
            printd(info + "\n");
        elif i == 10:
            printd("... \n");
            printd("full stat result in %s/stat_result\n"%(dir));
        i = i + 1;
    stat_result.close();
    printd("==================================================================\n");

def list_grep_result(result) :
    printd("start list result ...\n");
    #print(result);
    printd("==================================================================\n");
    printd(" %-40s | %-5s | %-20s\n"%("key word", "count", "remark"));
    printd("------------------------------------------------------------------\n");
    for x in result:
        printd(" %-40s | %-5d | %-20s\n"%(x[0], x[1], x[3]));
    printd("==================================================================\n");

def list_detail_result(dir, result):
    search_result = open("%s/search_result"%dir, "w");
    for x in result:
        # ---------------------------------------------------------------------
        search_result.write("%s\n"%(80*"-"));
        search_result.write("detail: %s:%d\n"%(x[0], x[1]));
        for f in x[2]:
            search_result.write("====in %s\n"%f);
            mdict = grep_key_word_detail(x[0], f);
            for k in mdict.keys():
                search_result.write("%d:%s\n"%(mdict[k], k));
        search_result.write("%s\n"%(80*"-"));
        # ---------------------------------------------------------------------
    printd("detail result in %s/search_result\n"%(dir));
    search_result.close();

################################################################################

def process(file_name,opt, dir_list):

    global contents

    if opt.isdigit():
        opt = int(opt)
    else:
        print "Please kindly input a correct command"
        return    

    l_realtime_dir = dir_list
    
    if 0 == opt:
        contents = list_dir(root_parent)

    elif 1 == opt:
        res = []
        for item in contents:
            if file_name == item[0]:
                res.append(item)
        key = ["name","date","start time","end time","version"]
        print
        printd(" LOG INFOMATION:\n");
        display(key, res,40) 
       # list_log_info(info);

    elif 2 == opt:

        
        uncompress_log(l_realtime_dir)
        decode_log(l_realtime_dir)
        flush_rtrc(l_realtime_dir)

    elif 3 == opt:
        # stat line info
        sdict = stat_line(l_realtime_dir);
        list_stat_result(l_realtime_dir, sdict);

    elif 4 == opt: 
        # grep key words
        '''
        0000004260 08:18:50:868 voserr.c 679 ERIR:System restart. 
        392657731 17:35:13:711 vosmem.c 1756 ERIR:ReleaseMemory: invalid memory state=0.
        392657732 17:35:13:711 voserr.c 556 ERIR:Error report called. PROC: G_S_KGHXAL_GPRS_TSM 
        class: 1 type: 1077 seq: 3userData0: 1 userData1: 59 userData2: 80, userData3: 0
        392657733 17:35:13:711 voserr.c 616 ERIR:VOS non-recoverable error.
        '''
        key_words_default = {
                #"Error report called. PROC:" : "",
                "Wrong MSC_SBL_NUM" : "p3, call can't be setup, CR01806507", 
                "OMCP Reboot" : "", 
                "CCP takeover" : "", 
                "System restart" : "", 
                "VOS non-recoverable error" : ""
                };
        key_words_custom  = read_key_word_list("./key_words.cfg");
        key_words_total = dict(key_words_default.items() + key_words_custom.items());
        for x in key_words_total.keys():
            result = grep_key_word(x, l_realtime_dir);
            result.append(key_words_total[x]); # add the remark field
            g_result.append(result);

        # list the result
        list_grep_result(g_result);

        # grep the key word detail
        list_detail_result(l_realtime_dir, g_result);

    elif 5 == opt:
        # grep custom key word
        key_word_custom = raw_input("please input the custom key word: ");
        grep_key_word_custom(key_word_custom, l_realtime_dir);

    else:
        printd("feature to be deployed..%d\n"%opt);
        
#############################################################################
def list_dir(dir_path):
    '''
    #List all the files in the root path with log info

    '''
    
    contents = []
    p = subprocess.Popen("ls %s -Ft|grep /"%dir_path, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT);  
    p.wait()
    while True:
        file_name = p.stdout.readline()
        if file_name == "" and p.poll() != None:
            break

        file_name = file_name.strip("\n")
        trace_file_path= "%s/%s" %(dir_path,file_name)
        #deal with blanks in the path since find command would failed
        trace_file_path = trace_file_path.replace(" ", "\ ")
        log_info_name = "BSC-Genaral*"
        p_find = subprocess.Popen("find %s -name %s"%(trace_file_path,log_info_name),\
        shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT);  
        p_find.wait()
        
        while True:
            file_info = []
            info = {}
            res = p_find.stdout.readline()
            if res == "" and p_find.poll() != None:
                break
            res = res.strip("\n")
            info = read_log_info(res)
            #judge if it is a master omcp by has_key starttime and endtime?
            if info.has_key("starttime") and info.has_key("endtime")\
            and info.has_key("date") and info.has_key("version"):
                file_info.append(file_name.strip("/"))
                file_info.append(info["date"])
                file_info.append(info["starttime"])
                file_info.append(info["endtime"])
                file_info.append(info["version"])
                contents.append(file_info)
            else:
                #This is slave omcp file
                pass

    logging.info("logging,contents = %s"%(contents))
    
    return contents
######################################################

def display(key,contents, num):
    '''
    display in a nice way
    '''
    #assume len(key) = every len(contents[x])
    limit = 0
    if num != 0:
       limit = num 
    max_len = []
    for i in range(len(key)):
        max_len.append(0)
    
    for i in range(len(key)):
        for j in range(len(contents)):
                max_len[i] = max(max_len[i], len(key[i]), len(contents[j][i]))
                if limit != 0 and max_len[i] > limit:
                    max_len[i] = limit

    #for 1st key row:
    num_len = 0
    for i in range(len(key)):
        num_len = num_len + (len(key[i]) + max_len[i]-len(key[i]) +  3)

    num_len = num_len + 1
    print "-"* num_len

    for i in range(len(key)):
        print "%s"%(key[i])," "*(max_len[i]-len(key[i])), "|",
    print

    print "-"* num_len
    # for contents:
    for j in range(len(contents)):
        for i in range(len(key)):
            if limit != 0 and len(contents[j][i]) > limit:
                print  "%s"%(contents[j][i][:limit]), "|",
            else:
                print "%s"%(contents[j][i])," "*(max_len[i]-len(contents[j][i])), "|",
        print

    print "-"* num_len
    print

#####################################################

def choose_file(all_files,choose):

    if choose not in all_files:
        return False
    else:
        return choose

       
#####################################################




if __name__ == "__main__" :

    
    root_parent = "/media/sf_trace_repo"
    contents = []
    f_change = True
    print "\n"*2
    title = "Hello, Welcome to Use BSC SLA!"
    print title.center(70)
    print "\n"*2
    #logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(name)s:%(levelname)s: %(message)s") 

    f_default = True
    while True:
        #Display the title and show all available trace diectories
        if f_change:
            contents = list_dir(root_parent)
        
        all_file = []
        for i in range(len(contents)):
            all_file.append(contents[i][0])

        print ""
        print "Below are all the trace files:"
        key = ["File","Date"]
        display(key,contents,0)
        
        if f_default:
            if len(contents) > 0:
                process_file = contents[0][0]
            else:
                process_file = " "
        
        name =(root_parent + "/" + process_file).replace(" ", "\ ")
        p = subprocess.Popen("find %s -name realtime"%(name), shell=True,\
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT);  
        p.wait()

        res = p.stdout.readlines()
        dir_list = []
        for i in range(len(res)):
            dir_list.append(res[i].strip("\n"))
        
        printd("To be process file: %s \n"%process_file)
        for i in range(len(dir_list)):
            printd("trace full path: %s\n"%dir_list[i])
        print ""
        
        print("select the corresponding number to start the process ...")
        print("[0] - refresh list contents")
        print("[1] - read the log information")
        print("[2] - uncompress log files and decode the real time files")
        print("[3] - stat lines information")
        print("[4] - auto grep the key words")
        print("[5] - grep custom key word")
        print("[s] - select trace file")
        print("[q] - quit")

        
        opt = ""   
        com = []
        opt = raw_input("your select ==> ").strip(" ")
        if len(opt) == 0:
            continue
        com = opt.split(" ")
        opt = com[0]

        if opt == "q" or opt == "quit" or opt == "Q" or opt == "exit"\
        or opt == "Exit":
            print ""
            print("Complete! Bye!  %s\n"%time.asctime())
            print "*"*50
            print ""
            exit(0)
            print "not a digit.."
        elif opt =="s" or opt =="S" or opt == "select" or opt == "sel":
            #s filename case
            if len(com)>1 and com[1] in all_file:
                process_file = com[1]
            else:
                choose = raw_input("input the file name ==>")
                process_file = choose_file(all_file,choose)
                
                while not process_file:
                    print "File name wrong, input again.."
                    choose = raw_input("trace file name ==>")
                    if choose == "q":
                        break
                    process_file = choose_file(all_file,choose)
                    
                if choose == "q":
                    continue

            f_default = False
            continue

        #dir_list is a list contents like */*/realtime
        if len(com)>1 and com[1] in all_file:
            process_file = com[1]
        process(process_file,opt, dir_list)
    
        if opt != "0":
            print ""
            raw_input("tap enter to continue...")

###############end main################

