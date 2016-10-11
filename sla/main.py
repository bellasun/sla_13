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
    except Exception as e:
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
#################### end read_log_info ##########################################


def uncompress_log(realtime_dir_list):

    for dir in realtime_dir_list: 

        #Bug1 decide if untar by *.tgz existed or not
        #decide if untar necessary:
        #ne =  subprocess.Popen("find %s -name *.rtrc.out"%dir, shell=True,\
        #stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        #ne.wait()
        #buff = ne.stdout.readline()
        #print "DEBUG dir",dir
        #print "DEBUG buff",buff
        #if buff != "":
        #    continue

        p = subprocess.Popen("ls %s/*.tgz"%dir, shell=True, stdout=subprocess.PIPE,\
        stderr=subprocess.STDOUT)
        p.wait()
        while True:
            buff = p.stdout.readline();
            #ls output is different with find when no file seached:
            #ls: cannot access dir1/*.tgz: No such file or directory
            #no *.tgz case, just do nothing
            if buff == '' or "ls" in buff.split(":"):
                break;
            file = buff.strip("\n");
            printd("unzip %s\n"%file.replace("/media/sf_trace_repo/", ""))
            #  -m don't extract file modified time
            ptar = subprocess.Popen("tar -mxvf %s -C %s > /dev/null"%(file, dir), shell=True);
            ptar.wait();

            printd ("finish unzip\n")
        print
    
###############end uncompress_log###############################


def decode_log(realtime_dir_list) :

    for dir in realtime_dir_list:

        #Bug1 decide to decode by rtrc files existed
        #decide if untar necessary:
        ne =  subprocess.Popen("find %s -name *.rtrc"%dir, shell=True, stdout=subprocess.PIPE,\
                stderr=subprocess.STDOUT)
        ne.wait()
        buff = ne.stdout.readline()
        if buff == '' or "ls" in buff.split(":"):
            continue

        printd("Start decode in %s\n"%dir)
        p = subprocess.Popen("./tools/BSCTraceDecode -l %s"%(dir), shell=True,\
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT);

        while True:
            buff = p.stdout.readline();
            if buff == '' and p.poll() != None:
                break;
            elif buff == '':
                continue;
            buff = buff.strip("\n")
            print(""+buff.replace(dir, ""))

        printd("Finish decode\n")

##############end decode_log##################################


def flush_rtrc(realtime_dir_list):

    for dir in realtime_dir_list:
        #Bug 1 delete *.tgz also 
        p = subprocess.Popen("rm %s/*.rtrc %s/*.rtrc_backup %s/*.tgz"\
        %(dir,dir,dir), shell=True,\
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT);
        p.wait()
        
        #delete more *.rtrc by manual uploaded
        ne =  subprocess.Popen("find %s -name *.rtrc -o -name *.rtrc_backup |xargs rm -f"\
        %dir, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        ne.wait()
        buff = ne.stdout.readline()
        if buff == '':
            continue
        else:
            logging.warning("%s"%(buff))

##############end flush_rtrc#################################


def stat_line(realtime_dir_list) :

    mdict = {}
    
    for dir in realtime_dir_list:
        print 
        printd("compute  repetition in |%s\n"%dir);
        file = glob.glob("%s/*.out"%dir)
        count = len(file);
        i = 1

        for fn in file:
            print("[%2d/%2d] %s"%(i, count, fn.replace(dir,"")));
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
        printd("finished\n")
                        
    # sort
    sdict = sorted(mdict.iteritems(), key=lambda d:d[1], reverse = True)
    return sdict
################end state_line#####################

def read_key_word_list(file):
    key_words = {};
    try:
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
    except Exception as e:
        print e
        return key_words

    key_words_file.close();
    return key_words;

############# end read_key_word_list ####################

def grep_key_word_custom(key_word, realtime_dir_list, type="all"):
    
    to_name = "custom_search"
    scale = "*" + type +"*.out"
    if type == "all":
        scale = "*.out"
    elif type == "further":
        scale = to_name
    
    hits_total = 0
    hits = 0
    #write to a file
    try:
        if type == "further":
            to_name = "custom_search_further"
            h = open("%s%s"%(realtime_dir_list[0].strip("realtime"),to_name), "w");
        else:
            h = open("%s%s"%(realtime_dir_list[0].strip("realtime"),to_name), "w");

        for dir in realtime_dir_list:
            if type == "further":
                dir = dir[:-9]
            printd("start grep custom key word '%s' in %s/%s ...\n"\
            %(key_word, dir, scale));
            p = subprocess.Popen("grep -ci '%s' %s/%s"%(key_word, dir, scale),\
            shell=True, stdout=subprocess.PIPE);
            flag = 0;
            while True:
                buff = p.stdout.readline();
                if buff == '' and p.poll() != None:
                    break;
                if buff == '':
                    continue;
                data = buff.strip("\n").split(":");
                #bug if 2 files has 0 hits
                #grep format problem
                #if only one file the output is only a number no matter hit or not
                if len(data) > 1: #int(data[1]) > 0:
                    ph = subprocess.Popen("grep -ihn '%s' %s"%(key_word, data[0]),\
                    shell=True, stdout=subprocess.PIPE);
                    if data[1]>0:
                        h.write("-------- %s hits in file:%s\n"%(data[1],data[0]))
                    while True:
                        line = ph.stdout.readline();
                        if line == '' and ph.poll() != None:
                            break;
                        if line == '':
                            continue;
                        h.write(line)
                        print(line.strip("\n"))
                     
                    hits = int(data[1])
                    if hits > 0:
                        print '\033[1;31;40m',
                        print "%s hits in file %s"%(data[1],data[0].replace(dir,"")),
                        print '\033[0m'
                        hits_total += hits 

                else:#for only one result case:
                    ph = subprocess.Popen("grep -ihn '%s' %s/%s"%(key_word, dir, scale),\
                    shell=True, stdout=subprocess.PIPE);
                    if type == "further":
                        h.write("---Twice Search Result----- %s hits in the only file\n"%(data[0]))
                    else:
                        if data[0]>0:
                            h.write("-------- %s hits in the only file\n"%(data[0]))
                    while True:
                        line = ph.stdout.readline();
                        if line == '' and ph.poll() != None:
                            break;
                        if line == '':
                            continue;
                        h.write(line)
                        print(line.strip("\n"))
                    hits = int(data[0])
                    if hits > 0:
                        print '\033[1;31;40m',
                        print "%s hits for this file"%data[0]
                        print '\033[0m'
                        hits_total += hits
                    
            hits = 0

            if type == "futher":
                break

    except Exception as e:
        print e
        return

    h.close()
    printd("custom search finished!\n") 
    print("result saved in %s%s"%(realtime_dir_list[0].strip("realtime"),to_name))
    return hits_total
############## end grep_key_word_custom ###########################


def grep_key_word(key_word, realtime_dir_list):

    result = {}
    result[key_word] = 0
    for dir in realtime_dir_list:
        printd ("start search: '%s' in %s\n"%(key_word, dir.replace("/media/sf_trace_repo/", "")))
        count = 0;
        p = subprocess.Popen("grep -c '%s' %s/*.out"%(key_word, dir), shell=True,\
        stdout=subprocess.PIPE);
        p.wait()
        while True:
            buff = p.stdout.readline();
            #if buff == '' and p.poll() != None:
            if buff == '':
                break;
            #grep -c output only a number if found
            #otherwise none ""
            #bug for only one file then grep -c output only one number
            #otherwise output like :xxx:2
            data = buff.split(":")
            if len(data)==1:#"only one .out file case"
                count += int(buff)
            else:
                count += int(data[1])
        result[key_word] += count 
    
        if result[key_word] > 0 and len(data) > 1:
            print '\033[1;31;40m',
            printd("'%s' found, %d hits in file %s "\
            %(key_word,result[key_word], data[0].replace(dir,"")))
            print '\033[0m'
    result[key_word] = str(result[key_word])

    return result
############# end grep_key_word #############################


def grep_key_word_detail(key_word, file) :
    '''
    output grep keyword result with more context
    '''
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

#########################end grep_key_word_detail########################


def list_stat_result(realtime_dir_list, sdict):
    dir = realtime_dir_list[0].strip("realtime")
    stat_result = open("%srepeat_result.txt"%dir, "w");
    i = 0;
    print ""
    print("TRACE REPEAT")
    print "-"*60
    print ("Ra|Repeats|" + "content")
    print "-"*60
    for item in sdict:
        info = "%-2d|%-7d|%-60s"%(i+1,item[1], item[0][:60])
        info_full = "%-2d|%-7d|%s"%(i+1,item[1], item[0])
        stat_result.write(info_full + "\n");
        if i < 10:
            print (info)
        elif i == 10:
            print("...")
            print "-"*60
            print("Details saved in %srepeat_result.txt"%(dir))
            break
        i = i + 1;

    stat_result.close();

##########################end list_stat_result##############################


def save_result(realtime_dir_list, result_list, to_name, method = 'w'):

    dir = realtime_dir_list[0].strip("realtime")
    try:
        h = open("%s%s"%(dir,to_name), method)
        h.write("key word: counts\n")
        for result in result_list:
            for i in range(len(result)):
                h.write("%s "%result[i])
            h.write("\n")

        print("result saved in %s%s"%(dir,to_name))
    except Exception as e:
        print e
        return

    h.close();


#################### end save_results ##################################

def save_custom_result(realtime_dir_list, result_list, to_name):

    dir = realtime_dir_list[0].strip("realtime")
    try:
        h = open("%s%s"%(dir,to_name), "w");
        h.write("key word: counts\n")
        for result in result_list:
            for i in range(len(result)):
                h.write("%s "%result[i])
            h.write("\n")

        print("result saved in %s%s"%(dir,to_name))
    except Exception as e:
        print e
        return

    h.close();
################### end save_custom_result ##########################


def process(file_name,opt, dir_list):

    global contents

    if opt.isdigit():
        opt = int(opt)
    else:
        print "please kindly input a correct command"
        return False   

    l_realtime_dir = dir_list
    

    if 1 == opt:
        res = []
        for item in contents:
            if file_name == item[0]:
                res.append(item)
        key = ["name","date","start time","end time","version"]
        print
        print("LOG INFOMATION");
        display(key, res,40) 


    elif 2 == opt:
        # stat line info
        uncompress_log(l_realtime_dir)
        decode_log(l_realtime_dir)
        flush_rtrc(l_realtime_dir)

        sdict = stat_line(l_realtime_dir);
        list_stat_result(l_realtime_dir, sdict);

    elif 3 == opt: 
        # grep key words
        '''
        like
        392657733 17:35:13:711 voserr.c 616 ERIR:VOS non-recoverable error.
        '''
        uncompress_log(l_realtime_dir)
        decode_log(l_realtime_dir)
        flush_rtrc(l_realtime_dir)

        g_result = []
        key_words_default = {
                #"Error report called. PROC:" : "",
                "Wrong MSC_SBL_NUM" : "p3, call can't be setup, CR01806507", 
                "OMCP Reboot" : "None Remark", 
                "CCP takeover" : "NONE", 
                "System restart" : "NONE", 
                "VOS non-recoverable error" : "This triggers a core dump"
                };
        #[TODO] save keyword in Excel file
        key_words_custom  = read_key_word_list("./key_words.cfg");
        #Transform between list and dict:
        #dict.items ==> list, dict(list) ==> dict
        key_words_total = dict(key_words_default.items()\
        + key_words_custom.items());
        for key_word in key_words_total.keys():
            result = grep_key_word(key_word, l_realtime_dir);
            #transform to a list like ["keyword","4"]
            result = list(result.items()[0])
            result.append(key_words_total[key_word]); # add the remark field
            g_result.append(result);
        # list the result
        key = ["key word","find","Note"]
        print
        print("AUTO SEARCH RESULTS")
        g_result = sorted(g_result, key=lambda result:result[1],reverse=True)
        display(key, g_result,40) 

        # grep the key word detail

        save_result(l_realtime_dir, g_result, "auto_result.txt",'w');

    elif 4 == opt:
        uncompress_log(l_realtime_dir)
        decode_log(l_realtime_dir)
        flush_rtrc(l_realtime_dir)

        # grep custom key word
        key_word_custom = raw_input("input key word to search ==> ")\
        .strip(" ")
        cmd = key_word_custom.split(",")
        if cmd[0] == "q" or cmd[0] == "Q" or len(cmd[0])<=2:
            return
        
        start_c = time.time()
        if len(cmd) == 1:
            hits_total = grep_key_word_custom(cmd[0], l_realtime_dir)

        else:
            hits_total = grep_key_word_custom(cmd[0], l_realtime_dir, cmd[1].strip(" "))
            
        
        end_c = time.time()
        interval_c = end_c - start_c
        if len(cmd) == 1 and hits_total > 0 and interval_c > 30:
            print "key word followed with VCE type to accelerate searching"
            print "like: 'CCDC_FFM,OCPR'"

        #[5.5] feature: Further Search
        if interval_c < 3 or hits_total <= 200:
            return

        print
        cmd = raw_input("want a further search? ===>")
        if cmd == "q" or cmd == "Q" or cmd == "NOK" or len(cmd) <= 2: 
            return
        else:
            #search again based on the previous result
            grep_key_word_custom(cmd, l_realtime_dir, "further")
        
    else:
        print("feature to be deployed..%d"%opt);
        return False

    return True
        
##################### end process ###########################################
def list_dir(dir_path):
    '''
    #List all the files in the root path with log info

    '''
    
    contents = []
    #ls -F ==> dir1/ dir2/, -t sort by time
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

################### end display ########### #####################

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
    title = "Hello, Welcome to BSC SLA v1.0"
    print '\033[1;31;40m',
    print title.center(70),
    print '\033[0m',
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
        print "LOG FILES:"
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
        
        #printd("To be process file: %s \n"%process_file)
        #for i in range(len(dir_list)):
        #    printd("trace full path: %s\n"%dir_list[i])
        #print ""
        
        print("select command on file:"),
        print '\033[1;31;40m',
        print ("%s")%process_file,
        print '\033[0m'
        print("[1] - log information")
        print("[2] - trace line repetition")
        print("[3] - auto keyword search")
        print("[4] - custom search")
        print ""
        print("[s] - select log file   [r] - refresh  [q] - quit")

        
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
            
        if "r" == opt or "R" == opt:
            contents = list_dir(root_parent)
            continue

        #dir_list is a list contents like */*/realtime
        if len(com)>1 and com[1] in all_file:
            process_file = com[1]
        f = process(process_file,opt, dir_list)
    
        if opt != "0" and f:
            print ""
            cmd = raw_input("tap enter...")
            if cmd == "q" or cmd == "Q" or cmd == "exit" or cmd == "Exit":
                print "Goodbye!"
                break
   #while True
###############end main################

