#!/usr/bin/python
#------------------------------------------------------
# import modules
import os
import re 
import sys
import time
import shutil
import string
import platform
import collections
#DEVimport HXP

# some initialization
executable      = ""

if sys.platform == "win32":
    DB_dir      = "C:/Users//michel/HEXPRESS_TEST_DB/_test_cases/"

out_dir         = "TEST_RESULTS"
niversion       = ""
projects        = []            # project list to be run
hostlist        = ""
hosts           = []
domain          = ""
project         = ""
final_out       = "results_all.csv"
caselist        = ""            # can be a DB_dir or a file listing cases
cleanFlag       = 0
extract_result  = 0
compare_result  = 0
optim           = 1
numproc         = 12
conf_modify     = ""
DB_dir          = "."

hostname        = platform.node()

timeval = '[' + time.asctime(time.localtime(time.time())) + ']'

#---------------------------------------------------------------------------------------

def print_usage():
    os.system( "clear" )
    print sys.argv[0]
    print " =============== "
    print
    print "SYNOPSIS: "
    print "   %s -niversion xxx [-list filename] [-hosts host1,host2,...] [-db db_dir] [-out_dir dir] " % (sys.argv[0])
    print
    print
    print "DESCRIPTION: "
    print '   Launches the specified hexpress version in batch mode on a specified list of cases.'
    print "   By default the cases are searched in %s and all cases are run. " % (DB_dir)
    print "   The database itself is not touched. All output go by default to a local %s directory" % (out_dir)
    print
    print "EXAMPLE 1 "
    print '   %s hexpresshexa25_4 -list LIST_2D'  % (sys.argv[0])
    print
    print "   Runs hexpress version 25_4 on the list \"LIST_2D\" located in the default directory %s " % (DB_dir)
    print "   The output goes to %s " % (out_dir)
    print
    print "Example 2: "
    print '   %s hexpress -niversion hexa25_4 -list LIST_2D -out_dir my_output_dir' % (sys.argv[0])
    print
    print "   Runs hexpress version 25_4 on the list \"LIST_2D\" located in the default directory %s " % (DB_dir)
    print "   The output goes to \"my_output_dir\" "
    print
    print "Example 3: "
    print "   %s ./hexpress -db %s -list LIST_2D " % (sys.argv[0],DB_dir)
    print
    print "   Runs local version (for developers only) "
    print
    print "OPTIONS: "
    print
    print "   -list <filename>" + "       specifies the output directory. Default is %s " % (out_dir)
    print "                               The launcher first looks for the file in the local directory." 
    print "                               If not found, it looks in the database directory." 
    print
    print "   -db <db_dir>                specifies the database to use. Default is %s " % (DB_dir)
    print
    print "   -out_dir <dir>              specifies the output directory. Default is %s " % (out_dir)
    print
    print "   -hosts <host1>,<host2>,...  specifies the machines on which to launch the database in //"
    print
    print "   -numproc #proc              specifies the number of proc to use for running tests"
   
#---------------------------------------------------------------------------------------

def mkdir(path):
    try:
        os.makedirs(path)
    except:
        pass

#---------------------------------------------------------------------------------------

def _chmodRecursive(arg, dirname, fnames):
    os.chmod(dirname, arg[0])
    for file in fnames:
        os.chmod(os.path.join(dirname, file), arg[0])

#---------------------------------------------------------------------------------------

def chmodR(path,perm):

    argList    = [1]
    argList[0] = perm
    os.path.walk(path,_chmodRecursive,argList)

#---------------------------------------------------------------------------------------
# Extract command line arguments
#
if len(sys.argv)==1:
    print_usage()
    sys.exit('')
    
#... extract executable. Can be ./hexpress or a hexpress version from multiversion (i.e. hexpress23_4)

this_script = sys.argv[0]
executable  = sys.argv[1]
args        = sys.argv[2:]

out_dir_specified = 0

rsh_args = ""

opt = ''
index = 0
for arg in args :
    if opt == '-niversion':
        niversion = arg
        executable = executable + niversion
    elif opt == '-script':
        script = arg
    elif opt == '-db':
        DB_dir = arg
    elif opt == '-list':
        caselist = arg
    elif opt == '-out_dir':
        out_dir_specified = 1
        out_dir = arg
    elif opt == '-dom':
        domain = arg
    elif opt == '-project':
        project = arg
    elif opt == '-host' or opt == '-hosts':
        hostlist = arg
    elif arg == '-result':
        extract_result = 1
    elif arg == '-compare':
        compare_result = 1
        result_files   = args[index+1:]
    elif arg == '-no_optim':
        optim = 0
    elif opt == '-numproc':
        numproc = arg
    elif opt == '-conf_modify':
        conf_modify = arg
        print("conf_modify "+conf_modify)
        conf_modify = conf_modify.replace('-',' ')
        conf_modify = conf_modify.replace("\\n",'\n')
        print("conf_modify "+conf_modify)
    
    if arg == '-clean':
        cleanFlag=1
        
    if arg == '-help':
        print_usage()
        exit(0)

    opt   = arg
    index = index+1

#---------------------------------------------------------------------------------------

def get_full_path(executable):
    if sys.platform == "win32":
        return os.path.abspath(executable)
    else:
        full_path_executable = executable
        if  os.path.exists( full_path_executable ) and executable[0] != "/":
            full_path_executable = os.getcwd() + "/" + executable
        return full_path_executable

#---------------------------------------------------------------------------------------
# Open file for script-based test cases
# It is the caller responsabilit to close the stream when finished

out_script_file = ""
out_script_dir  = ""

def init_script_test():
    global out_script_dir
    
    script_file = ""

    # find the script filename from the -script <...> argument
    count = 0
    for arg in sys.argv:
        if arg == "-script":
            script_file =  sys.argv[count+1]
            break
        count = count + 1

    out_script_dir = os.path.dirname(script_file) + "/"
    out_file       = out_script_dir + "RESULT.txt"

    return open(out_file,"w")

#---------------------------------------------------------------------------------------
# Extract project list. Fill in the project array
#
def extract_project_list_from_args():
    global DB_dir
    global caselist
    global projects

    if not os.path.isdir(DB_dir):
        sys.exit('ERROR: '+DB_dir+' directory does not exist !')
        
    if (caselist == ''):
        # ... No list filename specified
        # ...   => All project from CASES/ directory will be launched.    print
        print 'All testcases from the database will be launched ...'
        print 
        
        for pj in os.listdir(DB_dir):
            projects.append(pj)

    elif os.path.isdir(caselist):
        DB_dir = caselist
        for pj in os.listdir(DB_dir):
            projects.append(pj)

    else :
        # ... A single project has been specified.
        # ... Can be either a .dom file or a file containing a list of cases from the db
        # ...   => All project specified in this file will be launched.
     
        if ( os.path.exists( caselist )==0 ):
            caselist = DB_dir + "/" + caselist
            
        if ( os.path.exists( caselist ) ):

            if caselist[-4:len(caselist)] == ".dom":
                print "isol case"
            print
            print 'Testcases specified in file '+caselist+' will be launched ...'
            print

            list_file = open(caselist,"r")
            for pj in list_file.readlines():
                if ( pj[0] != '#' and pj[0] != '\n'):
                    pji = pj[0:len(pj)-1]
                    projects.append(pji)
            list_file.close()
        else:
            sys.exit('ERROR: '+caselist+' does not exist !')
    
#---------------------------------------------------------------------------------------
# Extract project list. Fill in the project array
#
def extract_hostlist_from_args():
    global hosts
    
    print hostlist
    if hostlist!='':
        # ... A list filename has been specified
        # ...   => All project will run on all platforms specified in the file.
        hostfilename = hostlist
        if ( os.path.exists( hostfilename ) ):
            host_file = open(hostfilename,"r")
            host_list = host_file.readlines()
            for hj in host_list:
                if (string.split(hj) == []) : continue
                if ( hj[0] != '#'):
                    hji = string.split(hj)
                    hosts.append(hji[0])
            host_file.close()
        else:           # hosts list passed as: -hosts lax,maxwell,blasius

            hosts = string.split(hostlist,",")
    else:
        #
        # Running locally
        pass
   
 
#fieldsStats = ["Cells","Hexahedrons","Prisms","Pyramids","Tetras","Neg Jacobian","Max ratio 1.0-actVol/optVol","Max ratio > .95","Max ratio > .9","Min edge length","Average edge length","Max edge length","Concave cells","Twisted cells"]
#fieldsStats = ["Cells","Hexahedrons","Prisms","Pyramids","Tetras","Neg Jacobian","Max ratio 1.0-actVol/optVol","Max ratio > .95","Max ratio > .9 ","Min edge length","Average edge length","Max edge length"]
fieldsStats = ["Cells","Hexahedrons","Prisms","Pyramids","Tetras","Neg Jacobian","Max ratio 1.0-actVol/optVol","Max ratio > .95","Max ratio > .9 ","Min edge length","Average edge length","Max edge length","Max equiangular skewness","Max adjacent volume ratio","Max expansion ratio"]
fieldsIndex = ["Mesh generation time (s)"]
#comparator = { "Cells" : 0,"Hexahedrons" : 2,"Prisms" : 2,"Pyramids" : 2,"Tetras" : 2,"Neg Jacobian" : 0,"Max ratio 1.0-actVol/optVol" : 0,"Max ratio > .95" : 0,"Max ratio > .9 " : 0,"Min edge length" : 1,"Average edge length" : 2,"Max edge length" : 2 , "Mesh generation time" : 0}
comparator = { "Cells" : 0,"Hexahedrons" : 2,"Prisms" : 2,"Pyramids" : 2,"Tetras" : 2,"Neg Jacobian" : 0,"Max ratio 1.0-actVol/optVol" : 0,"Max ratio > .95" : 0,"Max ratio > .9 " : 0,"Min edge length" : 1,"Average edge length" : 2,"Max edge length" : 2 ,"Max equiangular skewness":0,"Max adjacent volume ratio":0,"Max expansion ratio":0, "Mesh generation time (s)" : 0}

headers = ["CASE"] + fieldsStats + fieldsIndex

#---------------------------------------------------------------------------------------

def compare_one_result(field_name,ref_value,new_value):
    global comparator
    
    #print "ref_value,new_value %s %s" % (ref_value,new_value)

    if ref_value=="-" or new_value=="-":
        return "NA"
   
    if string.find(ref_value,"FAILED")!=-1 or string.find(new_value,"FAILED")!=-1 or string.find(ref_value,"Optimization")!=-1 or string.find(new_value,"Optimization")!=-1 or string.find(new_value,":")!=-1:
        return "NA"

    typeComparison = comparator[field_name]
    ref_val = float(ref_value)
    new_val = float(new_value)
    
    nbDecimalInPercentComputation = 3
    
    if(typeComparison == 0):
        if new_val < ref_val:
            if ref_val >0 :             
                percent = round(abs((new_val/ref_val-1)*1000./10.),nbDecimalInPercentComputation)
                return "better("+`percent`+" %)"
        elif new_val > ref_val:
            if ref_val >0 :
                percent = round(abs((new_val/ref_val-1)*1000./10.),nbDecimalInPercentComputation)
                return "worse("+`percent`+" %)"
        else:
            return " == "
    elif(typeComparison == 1):
        if new_val > ref_val:
            if ref_val >0 :             
                percent = round(abs((new_val/ref_val-1)*1000./10.),nbDecimalInPercentComputation)
                return "better("+`percent`+" %)"
        elif new_val < ref_val:
            if ref_val >0 :
                percent = round(abs((new_val/ref_val-1)*1000./10.),nbDecimalInPercentComputation)
                return "worse("+`percent`+" %)"
        else:
            return " == "

    return "-"
    
#---------------------------------------------------------------------------------------

def compare_results():
    results_ref = {}
    other_res = {}
    
    order_case = collections.OrderedDict()
    
    # Open reference result file
    #
    fref = open(result_files[0],"r")

    #.... Read reference file......

    # skip first line (header)
    theaders = fref.readline()
    case_num=0
    for lines in fref.readlines():
        splitted_line = string.split(lines)
        case          = splitted_line[0]    # first field of line is always case name

        results_ref[case] = splitted_line[1:]
        order_case[case_num]=case
        case_num=case_num+1
        
    fref.close()

    #... Read other result files:
    for file in result_files[1:]:
        other_res[file] = {}
        result = open(file,"r")

        # skip first line (header)
        result.readline()
        for lines in result.readlines():
            splitted_line = string.split(lines)
            case          = splitted_line[0]    # first field of line is always case name

            other_res[file][case] = splitted_line[1:]


    out_file = open("compare.csv","w")
    out_file.write(theaders)

    field = 1
    #for case in results_ref.keys():
    for case_num in order_case.keys():
	case=order_case[case_num]
        out_file.write("%s\t" % case)
        
        ref_results = results_ref[case]
        
        for j in ref_results:
            out_file.write("%s\t" % j)

        out_file.write("\n")

        #... Loop over other result files
        #
        for k in other_res.keys():

            out_file.write(" \t")

            if other_res[k].has_key(case):
                new_results  = other_res[k][case]
                diff_results = {}
                
                # Loop over result fields
                #
                for w in range(len(new_results)):
                    new_value = new_results[w]
                    out_file.write("%s\t" % new_value)
                    
                    if len(ref_results)>=len(new_results):
                        ref_value = ref_results[w]
                        diff_results[w] = compare_one_result(headers[w+1],ref_value,new_value)
                    else:
                        diff_results[w] = "-"

                out_file.write("\n")

                out_file.write("%s\t" % "  ")
                for w in range(len(new_results)):
                    out_file.write("%s\t" % diff_results[w])
                out_file.write("\n")
                
        field = field + 1

        out_file.write("\n")
    
    out_file.close()

    return " "
     
#---------------------------------------------------------------------------------------

def get_field_value(field_name,position_after_field,next_field):
    global lines

    field_length = len(field_name)

    # scan each line until finding field_name
    for w in range(len(lines)):
        line = lines[w]
            
        # line contains the field name: proceed further
        if string.find(line,field_name)!=-1:
            lines = lines[w+1:]
            
            if position_after_field == "skip":
                return "skip"

            # do not browser beyond next_field
            if string.find(line,next_field)!=-1:
                return None

            # Inside the line, we extract the value at position_after_field
            for i in range(len(line)):                
                if line[i:i+field_length]==field_name:
                    remaining = line[i+field_length:-1]
                    s = string.split(remaining)
                    if len(s)>= position_after_field:
                        return s[position_after_field-1]
                    return None
                    break
            break
    if position_after_field == "skip":
        return "skip"
    return None

#---------------------------------------------------------------------------------------
global lines


def extract_results_of_one_project(project,of):
    global fieldsStats
    global fieldsIndex
    global lines
   
    #... Opening .rep file for data extraction
    #
    #filename = out_dir + "/" + project + "/Report_resultMesh/statistics.html"
    if os.path.isdir(out_dir+"/"+project)==0 : 
        return
    stat_dir = ""
    for name in os.listdir(out_dir+"/"+project+"/") :
        if string.find(name,"Report_")!=-1 :
            if string.find(name,".")==-1 :
                stat_dir = out_dir + "/" + project + "/" + name
                if name == "Report_resultMesh":
                    break
    filename = stat_dir+"/statistics.html"

    values = []
    values.append(project)              # same project name

    if os.path.exists(filename) == 0:   # no result file associated with project
        #print "NO result file"
        return                            
    else:
        print filename
        f     = open(filename,"r")
        lines = f.readlines()
        f.close()

        fieldsStatsFound = []
        for line in lines:
            p = re.compile(r'<.*?>')
            stripped_line = p.sub(' ', line)
            for field in fieldsStats:
	        if (fieldsStatsFound.count(field)):
	            continue
                parsed_line = re.search('(' + field + '\s*)([0-9+\-.Ee]*)', stripped_line )
                if( parsed_line ):
                    values.append( parsed_line.group(2) )
                    fieldsStatsFound.append(field)
    
    #... Opening .rep file for data extraction
    #
    #filename = out_dir + "/" + project + "/Report_resultMesh/index.html"
    filename=stat_dir+"/index.html"

    if os.path.exists(filename) == 0:   # no result file associated with project
        #print "NO result file"
        return                            
    else:
        print filename
        f     = open(filename,"r")
        lines = f.readlines()
        f.close()

        fieldsIndexFound = []
        for line in lines:
            p = re.compile(r'<.*?>')
            stripped_line = p.sub(' ', line)
            for field in fieldsIndex:
                field = field.replace("(", "\(")
                field = field.replace(")", "\)")
	        if (fieldsIndexFound.count(field)):
	            continue
                parsed_line = re.search('(' + field + '\s*)([0-9+\-.Ee]*)', stripped_line )
                if( parsed_line ):
                    values.append( parsed_line.group(2) )
                    fieldsIndexFound.append(field)

    for i in range(len(values)):
        of.write("%s\t" % values[i])
    of.write("\n")

#--------------------------------------------------------------------------

def extract_results():
    global projects
    
    out_file = out_dir + "/" + final_out
    
    if caselist != "":
        list_name = string.split(caselist,"/")[-1]
        out_file = out_dir + "/" + "results_" + list_name + ".csv"

    print out_file
    
    #... Open global output file
    #
    of = open(out_file,"w")

    #... Write header
    #
    for i in range(len(headers)):
        of.write("%s\t" % headers[i])
    of.write("\n")

    all_cases = projects
    # Sort case name alphabetically
    #
    all_cases.sort()

    #... write to file
    #
    for pj in all_cases:
        extract_results_of_one_project(pj,of)
        
    #... Close file
    of.close()
    print " Result extracted"

#-----------------------------------------------------------------------

def run_project(project):
    print "Running %s" % (project)

    out_dir_abs_path = os.path.abspath( out_dir )
    ref_project_dir  = DB_dir       + "/" + project
    out_mesh_dir     = out_dir      + "/" + project
    project_result   = out_mesh_dir + "/html/statistics.html"
    
    if  os.path.exists(project_result) :
        print "Result file already exists, skipping %s " % project
        return
    
    if os.path.exists(out_mesh_dir):
        for dirtmp in os.listdir(out_mesh_dir):
            if os.path.isdir(out_mesh_dir+"/"+dirtmp) and dirtmp[0:6]=="Report":
                print "Result directory already exists, skipping %s " % project
                return

    if not os.path.exists( out_mesh_dir ):
        shutil.copytree( ref_project_dir, out_mesh_dir )
    chmodR(out_mesh_dir,0750)     
 
    if cleanFlag == 1:
        if os.path.isdir(out_d):
            print 'Cleaning directory: '+ out_d
            os.system('/bin/rm -rf '+out_d)
    else:
        # Execute hexpress on the single .igg project
        #
        full_path_exe = get_full_path(executable)
        
        tmp_out = out_dir_abs_path + "/tmp/RUNNING_"+project
       
        print "CUR_DIR",os.getcwd() 
        fout = open(tmp_out,"w")
        fout.write(hostname)
        fout.close()

        for file in os.listdir(out_mesh_dir):
                if string.find(file,".conf")!=-1: 
                        cur_dir = os.getcwd()
                        os.chdir(out_mesh_dir)
                        if conf_modify!="":
                             os.rename( file, file+"~" )
                             destination= open( file, "w" )
                             source= open( file+"~", "r" )
                             for line in source:
                                  if string.find(line,"END")!=-1:
                                       destination.write(conf_modify) 
                                  destination.write( line )
                             source.close()
                             destination.close()
                             os.remove(file+"~")
                        command = full_path_exe + '  ' + file + ' -numproc ' + numproc + ' -print ' + ' > console.log' 
                        os.system( command )
                        print "CHANGE", out_dir_abs_path
                        os.chdir( cur_dir )
        
        os.system(" /bin/rm  " + out_dir+"/tmp/RUNNING_"+project)

#-----------------------------------------------------------------------

def main():
    global out_dir
    global project
    global domain
    
    #
    # Adapt output dir name according to the hexpress version used
    #
    if out_dir_specified==0 and niversion != "":
        out_dir = out_dir + niversion
    elif executable[0:8]=="hexpress":
        out_dir = out_dir + executable[8:]
        
    out_dir = get_full_path(out_dir)
    
    mkdir(out_dir+"/tmp")

    if extract_result==1:
        extract_project_list_from_args()
        extract_results()
        return

    if compare_result==1:
        compare_results()
        return
    
    if project !="":
        run_project(project)
    else:
        # From input arguments, extract list of projects to run & hosts
        #
        extract_project_list_from_args()
        extract_hostlist_from_args()

        if len(hosts) != 0:
            #---------------------------------------------
            #... A list of hosts has been specified:
            #... o dispatch the projects evenly among hosts
            #... o then run the list for each host in parallel
        
            full_path_exe     = get_full_path(executable)
            full_path_script  = get_full_path(this_script)
            full_path_out_dir = get_full_path(out_dir)
            
            host_caselist = []
            for i in range(len(hosts)):
                host_caselist.append([])

            #... Distribute projects among hosts
            #
            cur_host = 0
            for case in projects:
                host_caselist[cur_host].append(case)
                cur_host = cur_host + 1
                if cur_host>=len(hosts):
                    cur_host = 0

            #--------------------------------------------
            #... For each host, proceed to launch:
            #... 1. save case list for the host
            #... 2. fork and spawn the hexpress
            
            
            for id in range(len(hosts)):
                hostname = hosts[id]

                #... Save case list
                #
                casefile_name = full_path_out_dir+"/tmp/"+hostname+`id`
                casefile = open(casefile_name,"w")
                for case in host_caselist[id]:
                    casefile.write("%s\n" % case)
                casefile.close()
                
                pid = os.fork()
                CHILD = 0
                if pid == CHILD:
#DEV                    command = "ssh " + hostname + " " + full_path_exe + " -batch -script _python/_igg/HXP_test.py -list " + casefile_name
                    command = "ssh " + hostname + " " + full_path_script + " " + full_path_exe + " -db " + DB_dir + " -list " + casefile_name + " -out_dir " + full_path_out_dir
                    if optim == 0:
                        command = command + " -no_optim"
                    os.system(command)
                    return
                else:
                    pass
            #
            #... end of hostlist launching process --> exiting
            return

        #---------------------------------------------
        #... Run (or clean) each project in turn
        #
        for project in projects:
            run_project(project)

#DEV        for domain in projects:
#DEV            run_domain(domain)

        #---------------------------------------------
        #... Final extraction of all results in a final output file
        #

#--------------------------------------------------------------------------
#--------------------------------------------------------------------------
#... Execute the script

main()

