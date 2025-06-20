#!/usr/bin/python
#------------------------------------------------------
# import modules
import os
import sys
import time
import shutil
import string
import platform
import mail

# some initialization
executable      = ""
DB_dir          = "/develop/tests/hexpress/_test_cases/"

if sys.platform == "win32":
    DB_dir      = "C:/Users//michel/HEXPRESS_TEST_DB/_test_cases/"

out_dir         = "TEST_RESULTS"
niversion       = ""
refversion      = ""
ref_path        = "/develop/tests/hexpress/_reference_results/"
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

# daily test stuff
daily_test      = 0
list_name       = ""
mailto          = 'iouri.antonik@numeca.be'
child_process   = 0
big_sleep       = 300   # polling period in seconds for checking if the tests are done
is_result_better  = 0
is_result_worse   = 0
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
    print "   %s -niversion xxx [-list filename] [-hosts host1,host2,...] [-db db_dir] [-out_dir dir] [-daily_test [-mail_to]] " % (sys.argv[0])
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
    print "   -daily_test                 runs daily test and sends the notificatoin to the address specified by -mail_to"
    print "   -mail_to  <e-mail1>,<e-mail2> sends a notification about test results to the specified e-mail addresses"
   
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
    
    if arg == '-clean':
        cleanFlag=1
        
    if arg == '-help':
        print_usage()
        exit(0)

    if daily_test == 1:
        if caselist != "":
            list_name = string.split(caselist,"/")[-1]
        result_files=[]
        result_files.append(ref_path+refversion + "/results_"+list_name+".csv")
        #print "reference file: ", result_files[0]
        result_files.append(out_dir+"/results_"+list_name+".csv")
        #print "result file: ", result_files[1]

        

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
    #global projects

    if not os.path.isdir(DB_dir):
        sys.exit('ERROR: '+DB_dir+' directory does not exist !')
        
    if (caselist == ''):
        # ... No list filename specified
        # ...   => All project from CASES/ directory will be launched. 
        print 'All testcases from the database will be launched ...'
        print 
        
        for pj in os.listdir(DB_dir):
            if os.path.isdir(DB_dir+"/"+pj) and os.path.exists(DB_dir+"/"+pj+"/mesh.igg") or os.path.isdir(DB_dir+"/"+pj) and os.path.exists(DB_dir+"/"+pj+"/" + pj + ".igg") or os.path.exists(DB_dir+"/"+pj+"/script.py"):
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
    
#---------------------------------------------------------------------------------------

fields = [ ["HEXPRESS version",1],
           ["TIMER: blanking:","skip"],
           ["TIMER: adaptation:",1],
           ["Mesh Stat:",1],
           ["TIMER: CartToUMH Conversion:", 1],
           ["TIMER: body fitting:",1],
           ["Mesh Stat:",7],
           ["TIMER: buffer insertion:",1],
           ["Memory (MB):",1],
           ["TIMER: snapping:",1],
           ["Mesh Stat:",7],
           ["Surface optimization","skip"],
           ["Volume optimization","skip"],
           ["completed","skip"],
           ["concave",3],
           ["twisted",3],
           ["negative",3],
           ["TIMER: optimization:",1],
           ["Minimum Orthogonality:",1],
           ["Less than 5 degrees:",1],
           ["Maximum skewness:",1],
           ["Concave",6],
           ["Twisted",6],
           ["Negative",6],
           ["TIMER: viscous layer insertion:",1],
           ["Mesh Stat:","skip"],
           ["Mesh Stat:","skip"],
           ["Mesh Stat:",7],
           ["Minimum Orthogonality:",1],
           ["Less than 5 degrees:",1],
           ["Maximum skewness:",1],
           ]
#           ["TIMER: optimization:",1],
#           ["Number of concave cells after optimization:",1],
#           ["Number of twisted cells after optimization:",1],

headers = [ "CASE",
            "Version",
            "Adapt Time",
            "Nb Cells",
            "Convert to UMH Time", 
            "BodyFit Time",
            "Nb Cells",
            "BufInsert Time", 
            "Memory (MB)", 
            "Total Snap Time",
            "Nb Cells", 
            "Concave",
            "Twisted",
            "Negative",
            "Optim Time",
            "Min Ortho",
            "Less than 5 degrees", 
            "Max skewness",
            "Concave after VL", 
            "Twisted after VL", 
            "Negative after VL",
            "VL time", 
            "Nb Cells After VL",
            "Min Ortho After VL",
            "Less than 5 degrees After VL", 
            "Max skewness After VL",
            "Max Expansion Ratio after Opt", 
            "Max adjacent volume ratio after Opt", 
            "Max Expansion Ratio after VL", 
            "Max adjacent volume ratio after VL", 
            ]

fieldsFaceQuality = [ ["Mesh quality after optimization","skip"],
                      ["Expansion Ratio","skip"],
                      ["Maximum value",2],
                      ["Adjacent Volume Ratio","skip"],
                      ["Maximum value",2],
                      ["Mesh quality after viscous layer insertion","skip"],
                      ["Viscous layer insertion time:",1],
                      ["Expansion Ratio","skip"],
                      ["Maximum value",2],
                      ["Adjacent Volume Ratio","skip"],
                      ["Maximum value",2],
                      ["Fluent quality criteria","skip"],
                      ]              

#---------------------------------------------------------------------------------------

def compare_one_result(field_name,ref_value,new_value):
    global is_result_better
    global is_result_worse
    global is_result_changed
    #print "field,ref_value,new_value %s %s %s" % (field_name,ref_value,new_value)

    if ref_value=="-" or new_value=="-":
        return "-"
   
    if string.find(ref_value,"FAILED")!=-1 or string.find(new_value,"FAILED")!=-1 or string.find(ref_value,"Optimization")!=-1 or string.find(new_value,"Optimization")!=-1 or string.find(new_value,":")!=-1:
        return "-"

    if string.find(field_name,"Cells")!=-1:
        try:
            new_val = int(new_value)
            ref_val = int(ref_value)
        except:
            return "-"
        if new_val != ref_val:
            is_result_changed = 1

    elif string.find(field_name,"Negative")!=-1:
        try:
            new_val = int(new_value)
            ref_val = int(ref_value)
        except:
            return "-"
        if new_val > ref_val:
            is_result_worse = 1
            if ref_val >0 :
                percent = int((new_val/ref_val-1)*1000./10.)
                if percent>=1: return "worse("+`percent`+" %)"
        elif new_val < ref_val:
            is_result_better = 1

    elif string.find(field_name,"Mem")!=-1 or string.find(field_name,"time")!=-1:
        try:
            new_val = float(new_value)
            ref_val = float(ref_value)
        except:
            return "-"
        if new_val > ref_val:
            if ref_val >0 :
                percent = int((new_val/ref_val-1)*1000./10.)
                if percent>=1: return "worse("+`percent`+" %)"

    elif string.find(field_name,"Ortho")!=-1:
        new_val = float(new_value)
        ref_val = float(ref_value)
        if new_val < ref_val:
            if ref_val >0 :
                is_result_worse = 1
                percent = int((new_val/ref_val-1)*1000./10.)
                if percent>=1: return "worse("+`percent`+" %)"
        elif new_val > ref_val:
            is_result_better = 1

    elif string.find(field_name,"skewness")!=-1 or string.find(field_name,"Max Expansion Ratio")!=-1 or string.find(field_name,"Max adjacent volume ratio")!=-1:
        new_val = float(new_value)
        ref_val = float(ref_value)
        if new_val > ref_val:
            if ref_val >0 :
                is_result_worse = 1
                percent = int((new_val/ref_val-1)*1000./10.)
                if percent>=1: return "worse("+`percent`+" %)"
        elif new_val < ref_val:
            is_result_better = 1
                
    elif string.find(field_name,"concave")!=-1:
        neg_rs,concave_rs,skewed_rs = string.split(ref_value,"/")
        neg_ns,concave_ns,skewed_ns = string.split(new_value,"/")
        neg_r     = int(neg_rs)
        concave_r = int(concave_rs)
        skewed_r  = int(skewed_rs)
        neg_n     = int(neg_ns)
        concave_n = int(concave_ns)
        skewed_n  = int(skewed_ns)
        
        if neg_n>neg_r:
            is_result_worse = 1
            return "worse"
        elif neg_n==neg_r:
            if concave_n>concave_r:
                is_result_worse = 1
                return "worse"
            elif concave_n==concave_r:
                if skewed_n>skewed_r:
                    is_result_worse = 1
                    return "worse"
        
    return " - "
    
#---------------------------------------------------------------------------------------

def compare_results(send_mail=0):
    global is_result_better
    global is_result_worse
    global is_result_changed
    global list_name
    results_ref = {}
    other_res = {}

    better_cases = []
    worse_cases = []
    crashed_cases = []
    new_cases = []
    changed_cases = []

    is_results_better = 0
    is_results_worse = 0
    is_results_changed = 0
    is_possible_crash = 0

    print "Comparing results..."
    
    # Open reference result file
    #
    fref = open(result_files[0],"r")

    #.... Read reference file......

    # skip first line (header)
    theaders = fref.readline()
    case_list = []
    for lines in fref.readlines():
        splitted_line = string.split(lines)
        case          = splitted_line[0]    # first field of line is always case name

        #results_ref[case] = splitted_line[1:-1]
        results_ref[case] = splitted_line[1:]
        case_list.append(case)
        
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

            #other_res[file][case] = splitted_line[1:-1]
            other_res[file][case] = splitted_line[1:]


    filename = out_dir + "/compare.csv"
    out_file = open(filename,"w")
    #print "YA comparison file: ", filename
    out_file.write(theaders)

    field = 1
    for case in case_list:
        #print "YA_comparing case: ", case
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
                        is_result_changed = 0
                        diff_results[w] = compare_one_result(headers[w+1],ref_value,new_value)
                        if is_result_better == 1:
                            is_results_better = 1
                            if case not in better_cases:
                                better_cases.append(case)
                        if is_result_worse == 1:
                            is_results_worse = 1
                            if case not in worse_cases:
                                worse_cases.append(case)
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

    if send_mail == 1:
        print "Sending notification..."

        mail_body = "Test results\nReference version: " + refversion \
                     + "\nTested version: " + niversion \
                     + "\nTest set: " + list_name \
                     + "\n\nImproved cases (" + str(len(better_cases)) + "): " + ' '.join(better_cases) \
                     + "\n\nDegraded cases (" + str(len(worse_cases)) + "): " + ' '.join(worse_cases) \
                     + "\n\nChanged cases (" + str(len(changed_cases)) + "): " + ' '.join(changed_cases) \
                     + "\n\nCrashed cases (" + str(len(crashed_cases)) + "): " + ' '.join(crashed_cases) \
                     + "\n\nNew cases: " + ' '.join(new_cases)
        mail_attachement = []
        mail_attachement.append(filename)

        email = mail.NIMail()
        email.send_mail("Hexpress " + niversion + " test results for " + list_name, mailto.split(','), mail_body, files=mail_attachement)   
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
    global fields
    global lines
    
    #... Opening .rep file for data extraction
    #
    filename = out_dir + "/" + project + "/mesh.rep"

    values = []
    values.append(project)              # same project name

    if os.path.exists(filename) == 0:   # no result file associated with project
        if os.path.exists(out_dir + "/" + project + "/mesh.igg"):
            print "Found .igg but not .rep file for project %s" % (project) 
        return                            # means case has crashed or been interrupted
    else:
        f     = open(filename,"r")
        lines = f.readlines()
        f.close()

        meshing_failed = 0
        for line in lines:
            for failure in "Initial mesh : FAILED","Adaptation : FAILED","Snapping : FAILED","Optimization : FAILED":
                if string.find(line,failure)!=-1:
                    meshing_failed = failure
            
        for w in range(len(fields)):
            field = fields[w]

            next_field = "lulu"
            if w < len(fields)-1:
                next_field = fields[w+1]
            val = get_field_value(field[0],field[1],next_field[0])
            
            if val != None and val != "skip":
                values.append(val)
            elif val == "skip":
                pass
            elif val == None and meshing_failed != 0:
                values.append(meshing_failed)
                break
            elif val != "skip":
                values.append("-")
            else:
                pass


    # Surface mesh qulity parameters

    filename = out_dir + "/" + project + "/mesh.qualityReport"
    faceQualityValues=[]

    if os.path.exists(filename) == 0:   # no result file associated with project
        if os.path.exists(out_dir + "/" + project + "/mesh.igg"):
            print "Found .igg but not .qualityReport file for project %s" % (project)
        return                            # means case has crashed or been interrupted
    else:
        f     = open(filename,"r")
        lines = f.readlines()
        f.close()

      
        meshing_failed = 0
            
        for w in range(len(fieldsFaceQuality)):
            field = fieldsFaceQuality[w]

            next_field = "lulu"
            if w < len(fieldsFaceQuality)-1:
                next_field = fieldsFaceQuality[w+1]

            val = get_field_value(field[0],field[1],next_field[0])
            if (field[0] == "Viscous layer insertion time:"): # to stop reading if no VL inserted
                if (val == None):
                   values.append("-")
                   values.append("-")
                   break
                else:
                   continue

            if val != None and val != "skip":
                values.append(val)
            elif val == "skip":
                pass
            elif val == None and meshing_failed != 0:
                values.append(meshing_failed)
                break
            elif val != "skip":
                values.append("-")
            else:
                pass

    for i in range(len(values)):
        of.write("%s\t" % values[i])
    of.write("\n")

#--------------------------------------------------------------------------

def extract_results():
    global projects
    global list_name
    print "Extracting results..."
    
    out_file = out_dir + "/" + final_out
    
    if caselist != "":
        if (list_name == ""):
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
    print "Results extracted."

#----------------------------------------------------------------------------------------

def _run_domain(in_domain,output_mesh_file):

    print " INPUT file %s " % (in_domain)
    print " OUTPUT file %s " % (output_mesh_file)

    HXP.import_domain(in_domain)

    # Regenerate the mesh. Perform only next action if previous has succeeded
    # 
    if HXP.generate_initial_mesh() == "0":
        if HXP.adapt_mesh() == "0":
            if HXP.snap_mesh() == "0":
                HXP.output_quality()
                num_beg_cells = HXP.get_number_of_negative_cells()
                if optim == 1 and num_beg_cells<500:
                    HXP.regularize_mesh()
    
    HXP.output_quality()

    HXP.saveAs_project(output_mesh_file)

#----------------------------------------------------------------------------------------

def run_domain(domain):

    in_dom  = DB_dir  + "/" + domain + "/domain_original.dom"
    out_d   = out_dir + "/" + project

    if cleanFlag == 1:
        if os.path.isdir(out_d):
            print 'Cleaning directory: '+ out_d
            os.system('/bin/rm -rf '+out_d)
    else:
        print "Running %s" % (project)

        # Execute hexpress on the single domain
        #
        executable = "hexpress"
        full_path_exe = get_full_path(executable)

        command = full_path_exe + ' -batch' + ' -script ' + ' _python/_igg/HXP_test.py ' + ' -dom ' + in_dom + ' -out ' + out_d
        if optim == 0:
            command = command + " -no_optim"
        os.system( command )

#-----------------------------------------------------------------------

def run_project(project):
    print "Running %s" % (project)

    ref_project_dir  = DB_dir       + "/" + project
    out_mesh_dir     = out_dir      + "/" + project
    project_name     = out_mesh_dir + "/mesh.igg"
    project_rep      = out_mesh_dir + "/mesh.rep"
            
    if  os.path.exists(project_rep) :
        print "Result file already exists, skipping %s " % project
        return

    mkdir(out_mesh_dir)
    chmodR(out_mesh_dir,0750)    

    for ext in [ '.igg', '.bcs', '.dom' ]:
        src1_file  = os.path.join( ref_project_dir, 'mesh'+ext )
        src2_file  = os.path.join( ref_project_dir, project+ext )
        dest_file  = os.path.join( out_mesh_dir, 'mesh'+ext )
        #print "YA_run_project, src1_file: ", src1_file
        #print "YA_run_project, src2_file: ", src2_file
        #print "YA_run_project, dest_file: ", dest_file
        if os.path.exists( src1_file ):
            shutil.copy( src1_file, out_mesh_dir )
        elif os.path.exists(src2_file):
            shutil.copy( src2_file, dest_file )


    chmodR(out_mesh_dir,0750)     
 
    if cleanFlag == 1:
        if os.path.isdir(out_d):
            print 'Cleaning directory: '+ out_d
            os.system('/bin/rm -rf '+out_d)
    else:
        # Execute hexpress on the single .igg project
        #
        full_path_exe = get_full_path(executable)
        
        tmp_out = out_dir + "/tmp/RUNNING_"+project
        
        fout = open(tmp_out,"w")
        fout.write(hostname)
        fout.close()

        #command = full_path_exe + ' -batch -print -project ' + project_name + " >& tmp_out "
        command = full_path_exe + ' -batch -print -save_rep_only -project ' + project_name 
        #command = full_path_exe + ' -numproc 4 -batch -print -save_rep_only -project ' + project_name 
        os.system( command )
        
        os.system(" /bin/rm  " + out_dir+"/tmp/RUNNING_"+project)

#-----------------------------------------------------------------------

def run_script(project):
    print "Running Script %s" % (project)

    ref_project_dir  = DB_dir       + "/" + project
    out_mesh_dir     = out_dir      + "/" + project
    project_name     = out_mesh_dir + "/script.py"

    mkdir(out_mesh_dir)
    chmodR(out_mesh_dir,0750)     

    for file in [ 'script.py' ]:
        src_file  = os.path.join( ref_project_dir, file )
        if os.path.exists( src_file ):
            shutil.copy( src_file, out_mesh_dir )
               
    chmodR(out_mesh_dir,0750)     

    if cleanFlag == 1:
        if os.path.isdir(out_d):
            print 'Cleaning directory: '+ out_d
            os.system('/bin/rm -rf '+out_d)
    else:
        # Execute hexpress on the single .igg project
        #
        full_path_exe = get_full_path(executable)
        
        tmp_out = out_dir + "/tmp/RUNNING_"+project
        
        fout = open(tmp_out,"w")
        fout.write(hostname)
        fout.close()

        cur_dir = os.getcwd()

        # Change current dir so that saving in py script takes place underneath the ouput test dir
        os.chdir(out_mesh_dir)
        
        # command = full_path_exe + ' -batch -print -project ' + project_name + " >& tmp_out "
        command = full_path_exe + ' -batch -print -save_rep_only -script ' + project_name
        print command
        os.system( command )
        
        os.system(" /bin/rm  " + out_dir+"/tmp/RUNNING_"+project)

        # back to original dir
        os.chdir(cur_dir)

#-----------------------------------------------------------------------
def run_list_of_cases():
    global out_dir
    global project
    global domain
    global caselist

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
            
            command = "rsh " + hostname + " " + full_path_script + " " + full_path_exe + " -child -db " + DB_dir + " -list " + casefile_name + " -out_dir " + full_path_out_dir
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
        if os.path.exists( DB_dir + "/" + project + "/script.py" ):
            run_script(project)
        else:
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

    # Compare results with reference
    if caselist != "":
        list_name = string.split(caselist,"/")[-1]
    result_files=[]
    result_files.append(ref_path+list_name+refversion+"/results_"+list_name+".csv")
    result_files.append(out_dir+"/results_"+list_name+".csv")
    compare_results(1)

    # Save new results in the reference results directory
    new_ref_dir = ref_path + niversion
    mkdir(new_ref_dir)
    chmodR(new_ref_dir,0750)    
    if os.path.exists(new_ref_dir):
        shutil.copy(result_files[1], new_ref_dir)


#----------------------------------------------------------------------------------------

def main():
    global out_dir
    global project
    global domain
    global child_process
    
    out_dir = get_full_path(out_dir)
    #print "YA_main, out_dir: ", out_dir
    
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
    
    #------------------------------------------------------------------
    #... Run single domain  (.dom file specified from the input line )
    
    if domain !="":
        #... extract last dir containing domain
        project_dir   = string.split(domain,"/")[-2]
        out_mesh_dir  = out_dir + "/" + project_dir 
        out_mesh_file = out_mesh_dir + "/mesh.igg"

        # Create output directory
        #
        mkdir(out_mesh_dir)

        #... Proceed to launch if a result file (.igg) does not exist yet
        if  os.path.exists(out_mesh_file) :
            print "Result file already exists, skipping %s " % domain
        else:   
            _run_domain(domain,out_mesh_file)
        
    elif project !="":  # (.igg specified from the input line: hexpress -project mesh.igg)
        if os.path.exists( DB_dir + "/" + project + "/script.py" ):
            run_script(project)
        else:
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

