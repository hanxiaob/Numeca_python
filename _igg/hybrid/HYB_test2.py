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
import mail

# some initialization
executable      = ""
DB_dir          = "."

if sys.platform == "win32":
    DB_dir      = "C:/Users//michel/HEXPRESS_TEST_DB/_test_cases/"

out_dir         = "TEST_RESULTS"
niversion       = ""
refversion      = ""
ref_path        = "/develop/tests/hybrid/_reference_results/"
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

# daily test stuff
daily_test      = 0
mpi             = False;
list_name       = ""
mailto          = 'iouri.antonik@numeca.be,nicolas.delsate@numeca.be,vladimir.gael@numeca.be,numeca.dev@duallab.com'
child_process   = 0
big_sleep       = 300 # polling period in seconds for checking if the tests are done
result_files    = []
is_result_better  = 0
is_result_worse   = 0
is_result_worse_20= 0
is_result_changed = 0

hostname        = platform.node()

timeval = '[' + time.asctime(time.localtime(time.time())) + ']'

#---------------------------------------------------------------------------------------

def print_usage():
    os.system( "clear" )
    print sys.argv[0]
    print " =============== "
    print
    print "SYNOPSIS: "
    print "   %s -niversion xxx [-list filename] [-hosts host1,host2,...] [-db db_dir] [-out_dir dir] [-daily_test [-mail_to address]] " % (sys.argv[0])
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
    print "   -daily_test                 runs daily test and sends the notificatoin to the address specified by -mail_to"
    print "   -mail_to  <e-mail1>,<e-mail2> sends a notification about test results to the specified e-mail addresses"
    print "   -mpi <mpi_path>             runs a given binary as MPI version of hybrid using the specified mpi_patch"
   
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
    if opt == '-refversion':
        refversion = arg
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
    elif arg == '-daily_test':
        daily_test = 1
    elif opt == '-mail_to':
        mailto = arg
    elif arg == '-child': # for internal use only
        child_process = 1
    elif opt == '-numproc':
        numproc = arg
    elif opt == '-conf_modify':
        conf_modify = arg
        print("conf_modify "+conf_modify)
        conf_modify = conf_modify.replace('-',' ')
        conf_modify = conf_modify.replace("\\n",'\n')
        print("conf_modify "+conf_modify)
    elif opt == '-mpi':
        mpi = True
        mpi_path = arg
    
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
        # ...   => All project from CASES/ directory will be launched.
        print 'All testcases from the database will be launched ...'
        print 
        
        for pj in os.listdir(DB_dir):
            projects.append(pj)

    elif os.path.isdir(caselist):
        DB_dir = caselist
        for pj in os.listdir(DB_dir):
            projects.append(pj)

    elif len(projects) == 0:
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
   

# for HHybrid version <6.1
#fieldsStats = ["Cells","Hexahedrons","Prisms","Pyramids","Tetras","Neg Jacobian","Max ratio 1.0-actVol/optVol","Max ratio > .95","Max ratio > .9 ","Min edge length","Average edge length","Max edge length","Max equiangular skewness","Max adjacent volume ratio","Max expansion ratio"]
# for HHybrid version >=6.1
fieldsStats = ["Number of hexahedrons","Number of tetrahedrons","Number of prisms","Number of pyramids","Number of cells","Number of patches","Number of selections","Num negative jacobian","Max equiangular skewness","Max adjacent volume ratio","Max expansion ratio"]
fieldsIndex = ["Mesh generation time (s)"]

# Comparison types:
# 0 - the smaller the better
# 1 - the greater the better
# 2 - if different then set "is_result_changed" flag
# -1 - the smaller the better but do NOT set "is_better" flag
# -2 - ignore the difference

# by default all the fields are compared, difference in time does not change is_better/is_worse flags
# for HHybrid version <6.1
#default_comparator = { "Cells" : 0,"Hexahedrons" : 2,"Prisms" : 2,"Pyramids" : 2,"Tetras" : 2,"Neg Jacobian" : 0,"Max ratio 1.0-actVol/optVol" : 0,"Max ratio > .95" : 0,"Max ratio > .9 " : 0,"Min edge length" : 1,"Average edge length" : 2,"Max edge length" : 2 ,"Max equiangular skewness":0,"Max adjacent volume ratio":0,"Max expansion ratio":0, "Mesh generation time (s)" : -1}
# for HHybrid version >=6.1
default_comparator = { "Number of hexahedrons" : 2, "Number of tetrahedrons" : 2, "Number of prisms" : 2, "Number of pyramids" : 2, "Number of cells" : 0, "Number of patches" : 2, "Number of selections" : 2, "Num negative jacobian" : 0, "Max equiangular skewness":0, "Max adjacent volume ratio":0, "Max expansion ratio":0, "Mesh generation time (s)" : -1}

# do not compare time
# for HHybrid version <6.1
#daily_comparator = { "Cells" : 0,"Hexahedrons" : 2,"Prisms" : 2,"Pyramids" : 2,"Tetras" : 2,"Neg Jacobian" : 0,"Max ratio 1.0-actVol/optVol" : 0,"Max ratio > .95" : 0,"Max ratio > .9 " : 0,"Min edge length" : 1,"Average edge length" : 2,"Max edge length" : 2 ,"Max equiangular skewness":0,"Max adjacent volume ratio":0,"Max expansion ratio":0, "Mesh generation time (s)" : -2}
# for version >=6.1
daily_comparator = { "Number of hexahedrons" : 2, "Number of tetrahedrons" : 2, "Number of prisms" : 2,"Number of pyramids" : 2, "Number of cells" : 0, "Number of patches" : 2, "Number of selections" : 2, "Num negative jacobian" : 0, "Max equiangular skewness":0, "Max adjacent volume ratio":0, "Max expansion ratio":0, "Mesh generation time (s)" : -2}


headers = ["CASE"] + fieldsStats + fieldsIndex

#---------------------------------------------------------------------------------------

def compare_one_result(field_name,ref_value,new_value, comparator):
    global is_result_better
    global is_result_worse
    global is_result_worse_20
    global is_result_changed
    
    #print "field_name: %s, ref_value,new_value %s %s" % (field_name,ref_value,new_value)

    #in case surface mesh and detection of type mesh is not done correctly then result is set to E
    if ref_value=="E" or new_value=="E":
        return "NA"

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
                is_result_better = 1
                return "better("+`percent`+" %)"
        elif new_val > ref_val:
            if ref_val >0 :
                percent = round(abs((new_val/ref_val-1)*1000./10.),nbDecimalInPercentComputation)
                is_result_worse = 1
                if percent > 20.0:
                    is_result_worse_20 = 1
                return "worse("+`percent`+" %)"
            elif ref_val <= 0:
                is_result_worse = 1
                is_result_worse_20 = 1
                return "worse(INF %)"            
        else:
            return " == "
    elif(typeComparison == 1):
        if new_val > ref_val:
            if ref_val >0 :             
                percent = round(abs((new_val/ref_val-1)*1000./10.),nbDecimalInPercentComputation)
                is_result_better = 1
                return "better("+`percent`+" %)"
        elif new_val < ref_val:
            if ref_val >0 :
                percent = round(abs((new_val/ref_val-1)*1000./10.),nbDecimalInPercentComputation)
                is_result_worse = 1
                if percent > 20.0:
                    is_result_worse_20 = 1
                return "worse("+`percent`+" %)"
        else:
            return " == "
    elif(typeComparison == 2):
        if new_val != ref_val:
            is_result_changed = 1
            return "changed"
        else:
            return " == "
    elif(typeComparison == -1):
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
    elif(typeComparison == -2):
        return " == "

    return "-"
    
#---------------------------------------------------------------------------------------

def compare_results(comparator=default_comparator, send_mail=0):
    global is_result_better
    global is_result_worse
    global is_result_worse_20
    global is_result_changed
    global list_name
    results_ref = {}
    other_res = {}

    better_cases = []
    worse_cases = []
    worse_cases_20 = []
    crashed_cases = []
    new_cases = []
    changed_cases = []
    
    is_results_better = 0
    is_results_worse = 0
    is_results_changed = 0
    is_possible_crash = 0

    print "Comparing results..."

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
    res_case_num = 0
    for file in result_files[1:]:
        other_res[file] = {}
        result = open(file,"r")

        # skip first line (header)
        result.readline()
        for lines in result.readlines():
            splitted_line = string.split(lines)
            case          = splitted_line[0]    # first field of line is always case name

            other_res[file][case] = splitted_line[1:]
            res_case_num = res_case_num + 1

    nb_new_cases = res_case_num - case_num

    filename = 'compare_'+ list_name + '_' + refversion + '_'+ niversion + '.csv'
    out_file = open(filename,"w")
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
                        is_result_better = 0
                        is_result_worse = 0
                        is_result_worse_20 = 0
                        is_result_changed = 0
                        diff_results[w] = compare_one_result(headers[w+1],ref_value,new_value, comparator)
                        if is_result_better == 1:
                            is_results_better = 1
                            if case not in better_cases:
                                better_cases.append(case)
                        if is_result_worse == 1:
                            is_results_worse = 1
                            if case not in worse_cases:
                                worse_cases.append(case)
                            if is_result_worse_20 == 1:
                                if case not in worse_cases_20:
                                    worse_cases_20.append(case)
                        if is_result_changed == 1:
                            is_results_changed = 1
                            if case not in changed_cases:
                                changed_cases.append(case)

                    else:
                        is_possible_crash = 1
                        if case not in crashed_cases:
                            crashed_cases.append(case)
                        diff_results[w] = "-"

                out_file.write("\n")

                out_file.write("%s\t" % "  ")
                for w in range(len(new_results)):
                    out_file.write("%s\t" % diff_results[w])
                out_file.write("\n")
            else:
                is_possible_crash = 1
                if case not in crashed_cases:
                    crashed_cases.append(case)
                
        field = field + 1

        out_file.write("\n")
    
    out_file.close()
    print "Comparison completed."

    summary = "Test results\nReference version: " + refversion \
                + "\nTested version: " + niversion \
                + "\nTest set: " + list_name \
                + "\n\nImproved cases (" + str(len(better_cases)) + "): " + ' '.join(better_cases) \
                + "\n\nDegraded cases (" + str(len(worse_cases)) + "): " + ' '.join(worse_cases) \
                + "\n\nCased degraded by more than 20% (" + str(len(worse_cases_20)) + "): " + ' '.join(worse_cases_20) \
                + "\n\nCrashed cases (" + str(len(crashed_cases)) + "): " + ' '.join(crashed_cases) \
                + "\n\nChanged cases (" + str(len(changed_cases)) + "): " + ' '.join(changed_cases) # + "\nNew cases: " + ' '.join(new_cases)
    if nb_new_cases > 0:
        summary = summary + "\n\nThere are " + str(nb_new_cases) + " new cases. Please update the reference results."

    print summary

    if send_mail == 1:
        print "Sending notification..."

        mail_body = summary
        mail_attachement = []
        mail_attachement.append(filename)

        email = mail.NIMail()
        email.send_mail(niversion + " test results for " + list_name, mailto.split(','), mail_body, files=mail_attachement)   
        print "Notification sent."

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
        print "Can not find statistics.html for project %s" % (project)
        return                            
    else:
        #print filename
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
        print "NO result file"
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
    print "Extracting results..."
    
    out_file = out_dir + "/" + final_out
    
    if caselist != "":
        list_name = string.split(caselist,"/")[-1]
        out_file = out_dir + "/" + "results_" + list_name + ".csv"

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
    print "Results extracted"

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
                if mpi:
                    command = mpi_path + '/bin/mpiexec -np ' + str(numproc) + ' ' + full_path_exe + '  ' + file +  ' -numproc ' + str(1) +  ' -print '
                else:
                    command = full_path_exe + '  ' + file + ' -numproc ' + str(numproc) + ' -print '
                os.system( command )
                os.chdir( cur_dir )
        
        os.system(" /bin/rm  " + out_dir+"/tmp/RUNNING_"+project)

#-----------------------------------------------------------------------
def run_list_of_cases():
    global out_dir
    global project
    global domain

    print "Running tests..."
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
            
            #command = "rsh " + hostname + " '. ./ENVIRONMENT && " + full_path_script + " " + full_path_exe + " -child -db " + DB_dir + " -list " + casefile_name + " -out_dir " + full_path_out_dir + " -numproc " + str(numproc) + "'"
            command = "rsh " + hostname + " " + full_path_script + " " + full_path_exe + " -child -db " + DB_dir + " -list " + casefile_name + " -out_dir " + full_path_out_dir + " -numproc " + str(numproc)
            if optim == 0:
                command = command + " -no_optim"
            os.system(command)

        #
        #... end of hostlist launching process --> exiting
        return

    #---------------------------------------------
    #... Run (or clean) each project in turn
    #
    for project in projects:
        run_project(project)

    print "Tests completed for ", caselist
    if child_process == 1:
        os.system('/bin/rm -rf '+ caselist)

#-----------------------------------------------------------------------

def run_daily_test():
    global out_dir
    global project
    global domain
    global big_sleep
    global child_process
    global niversion

    if niversion == "":
        niversion = executable[8:]

    # Run tests
    run_list_of_cases()
    if child_process == 1:
        return

    # Wait for completion of runs
    tmp_dir = out_dir + "/tmp"
    tests_completed = 0
    while len(hosts) != 0 and tests_completed == 0:
        time.sleep(big_sleep)
        if os.path.exists(tmp_dir) and len(os.listdir(tmp_dir)) == 0 or not os.path.exists(tmp_dir):
            tests_completed = 1
        
    print "All tests completed."
    
    # Extract results
    extract_project_list_from_args()
    extract_results()

    # Compare results with reference and mail the result
    compare_results(daily_comparator, 1)

    # Save new results in the reference results directory
    new_ref_dir = ref_path + niversion
    mkdir(new_ref_dir)
    chmodR(new_ref_dir, 0750)
    if os.path.exists(new_ref_dir):
        shutil.copy(result_files[1], new_ref_dir)

#----------------------------------------------------------------------------------------

def main():
    global out_dir
    global project
    global domain
    global child_process
    global result_files
    global list_name

    #
    # Adapt output dir name according to the hexpress version used
    #
    if out_dir_specified==0 and niversion != "":
        out_dir = out_dir + niversion
#    elif executable[0:8]=="hexpress":
#        out_dir = out_dir + executable[8:]
        
    out_dir = get_full_path(out_dir)

    if daily_test == 1:
        if caselist != "":
            list_name = string.split(caselist,"/")[-1]
        result_files=[]
        result_files.append(ref_path + refversion + "/results_" + list_name + ".csv")
        result_files.append(out_dir+"/results_"+list_name+".csv")
    
    mkdir(out_dir+"/tmp")

    if extract_result==1:
        extract_project_list_from_args()
        extract_results()
        return

    if compare_result==1:
        compare_results()
        return
    
    if daily_test == 1:
        run_daily_test()
        return
    
    if project !="":
        run_project(project)

    #------------------------------------------------------------------
    #... Run list of cases 
    #
    else:
        run_list_of_cases()

#--------------------------------------------------------------------------
#--------------------------------------------------------------------------
#... Execute the script

main()

