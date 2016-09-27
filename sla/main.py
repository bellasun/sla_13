#!/usr/bin/python

import subprocess
import sys
import glob
import re
import time, datetime
from common import *

#felix
###############################################################################
g_result = [];
g_dict = {};

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
def read_log_info(root):
    info = {};
    # read BSC version
    h = open("%s/BSC-Genaral.txt"%root, "r");
    while True:
        line = h.readline();
        if not line:
            break;
        if "BSC_VERSION" in line:
            version_list = line.strip("\n").strip("\r").split(":");
            info["version"] = version_list[1];
            break;
    h.close();
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
    h = open("%s/trace_collection.log"%root, "r");
    key = "starttime";
    while True:
        line = h.readline();
        if not line:
            break;
        l = re.match(r"YEAR=(\d+) MONTH=(\d+) DAY=(\d+) HOUR=(\d+) MINUTE=(\d+)", line);
        if l:
            r = [t(s) for t,s in zip((int, int, int, int, int), l.groups())];
            info[key] = "%4d-%02d-%02d %02d:%02d:00"%(r[0], r[1], r[2], r[3], r[4]);
            '''
            time_tuple = time.strptime(line.strip("\n").strip("\r"), 
                    "YEAR=%Y MONTH=%m DAY=%d HOUR=%H MINUTE=%M");
            info[key] = time.strftime("%Y-%m-%d %H:%M:%S", time_tuple);
            '''
            if key == "endtime":
                break;
            key = "endtime";
    h.close();
    return info;

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

def uncompress_log(dir) :
    printd("start uncompress %s ...\n"%dir);
    # start uncompress ./LR14.3G_CMCC_NAL/sltrace/TCK trace/40_standby/secured/realtime ...
    # unzip ls: cannot access ./LR14.3G_CMCC_NAL/sltrace/TCK: No such file or directory
    # [TODO] tar: Cannot connect to ls: resolve failed
    p = subprocess.Popen("ls %s/*.tgz"%dir, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT);  
    while True:
        buff = p.stdout.readline();
        if buff == '' and p.poll() != None:  
            break;
        file = buff.strip("\n");
        printd("unzip %s\n"%file);
        #  -m don't extract file modified time
        # tar: 20160510_021642_20160517_193338_1.3.9_DTC_[210]_210.rtrc: time stamp 2016-05-18 03:34:55 is 42539.416074181 s in the future 
        ptar = subprocess.Popen("tar -mxvf %s -C %s > /dev/null"%(file, dir), shell=True);
        ptar.wait();

def decode_log(dir) :
    printd("start decode %s ...\n"%dir);
    p = subprocess.Popen("./tools/BSCTraceDecode -l %s"%(dir), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT);
    while True:
        buff = p.stdout.readline();
        if buff == '' and p.poll() != None:
            break;
        elif buff == '':
            continue;
        printd(buff);

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

def process(opt, root_dir):
    realtime_dir = "%s/realtime"%root_dir;
    if 1 == opt:
        info = read_log_info(root_dir);
        list_log_info(info);

    elif 2 == opt:
        # uncompress trace files
        uncompress_log(realtime_dir);

        # decode the real time trace file
        decode_log(realtime_dir);

    elif 3 == opt:
        # stat line info
        sdict = stat_line(realtime_dir);
        list_stat_result(realtime_dir, sdict);

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
            result = grep_key_word(x, realtime_dir);
            result.append(key_words_total[x]); # add the remark field
            g_result.append(result);

        # list the result
        list_grep_result(g_result);

        # grep the key word detail
        list_detail_result(realtime_dir, g_result);

    elif 5 == opt:
        # grep custom key word
        key_word_custom = raw_input("please input the custom key word: ");
        grep_key_word_custom(key_word_custom, realtime_dir);

    elif 9 == opt:
        exit(0);

    else:
        printd("unknown process code: %d\n"%opt);

if __name__ == "__main__" :
    root_dir = "./site-xxxx-20160330/omcp1";
    opt_str = "";
    i = 1; # omit the sys.argv[0];
    while i < len(sys.argv):
        arg = sys.argv[i];
        if arg == "-d":
            root_dir = sys.argv[i + 1];
            i = i + 1;
        elif arg == "-p":
            opt_str = sys.argv[i + 1];
            i = i + 1;
        i = i + 1;

    printd("Hello world! Welcome to BSC SLA system! %s\n"%time.asctime());
    printd("process site: %s\n"%root_dir);

    printd("select the corresponding number to start the process ...\n");
    printd("[1] - read the log information\n");
    printd("[2] - uncompress log files and decode the real time files\n");
    printd("[3] - stat lines information\n");
    printd("[4] - auto grep the key words\n");
    printd("[5] - grep custom key word\n");
    printd("[9] - quit\n");
    while "" == opt_str:
        opt_str = raw_input("your select(example: 1,3,4): ");
    opt_list = opt_str.split(",");

    for opt in opt_list:
        process(int(opt), root_dir);

    printd("Complete! Bye!  %s\n"%time.asctime());

