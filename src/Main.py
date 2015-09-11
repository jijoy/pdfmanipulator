'''
Created on Oct 31, 2014

'''
import sys
import os.path
from pdfmanipulator import do_highlight
from merger import Merger

def launchApp(argv):
    tmp_file = 'tmp.pdf'
    input_folder = argv[1]
    output_path = argv[2]
    is_highlighting = len(argv) > 3 #There are keywords for highlight
    merge_output = ''
    if is_highlighting :
        merge_output = tmp_file 
    else :
        merge_output = output_path
    m = Merger(input_folder,merge_output)
    m.domerge()
    if len(argv) > 3 :
        print 'There are keywords for highlighting'
        keywords = argv[3].split(',')
        print keywords
        do_highlight(merge_output,keywords,output_path)


def doValidation(argv):
    if len(argv) < 3:
        sys.exit('Usage: %s rootfolder output-file-path kewords,seperated,by,comma  .\n  keywords are optional' % argv[0])
    
    if not os.path.exists(argv[1]):
        sys.exit('ERROR: Root folder %s was not found!' % argv[1])
    
    if os.path.exists(argv[2]):
        sys.exit('ERROR: Output file %s already exists' % argv[2])

if __name__ == '__main__' :

    reload(sys)
    #sys.setdefaultencoding('ISO-8859-1')
    sys.setdefaultencoding('UTF-8')
    doValidation(sys.argv)
    launchApp(sys.argv)