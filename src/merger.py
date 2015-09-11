'''
Created on Oct 31, 2014

'''
from PyPDF2 import PdfFileMerger, PdfFileReader
from os import listdir
from os.path import isfile, join
import re
from PyPDF2.pdf import PdfFileWriter
import StringIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


class Merger:
    files=[]
    output = ''
    footer_font_size = 10
    def set_footer_size(self,font_size):
        """
        Controlls the font size for footer text
        """
        self.footer_font_size = font_size
    def __init__(self,rootfolder,output):
        """
        Constructor overriden.
        :param rootfolder:
        :param output:
        :return:
        """
        self.rootfolder = rootfolder
        self.output = output
        
        
    def domerge(self):
        """
        Main merge method. It will merge all the pdfs in the input directory.
        :return:
        """
        print "Getting all pdf files in the folder"
        self.get_file_list()
        print "Going to start merge"
        pdfmerger = PdfFileMerger()
        writer = PdfFileWriter()
        outputStream = file(self.output, "wb")
  
        for filename in self.files:
            print "Going to merge %s"%filename
            reader = PdfFileReader(file(filename, 'rb'))
            page_num = 0
            for page in reader.pages:
#                 print page.artBox
#                 print page.bleedBox
#                 print page.cropBox
#                 print page.trimBox
                self.add_footer(page,filename,page_num)
                page_num +=1
                writer.addPage(page)
        writer.write(outputStream)
        outputStream.close()              
        print "Done merging"

    def add_footer(self,page,file_name,page_num):
        """
        Adds the source file name and page number as footer to given page.
        :param page:
        :param file_name:
        :param page_num:
        :return:
        """
        packet = StringIO.StringIO('')
        # create a new PDF with Reportlab
        can = canvas.Canvas(packet, pagesize=letter)
        string = "%s , Page %s"%(file_name,page_num+1)
        # print 'Going to add footer to %s'%file_name
        # print 'Footer string -->%s'%string
        # print string
        can.setFontSize(self.footer_font_size)
        can.drawString(0, 10, string.encode('UTF-8'))
        can.save()
        #move to the beginning of the StringIO buffer
        packet.seek(0)
        # print packet.getvalue()
        new_pdf = PdfFileReader(packet)
        page.mergePage(new_pdf.getPage(0))


    def get_file_list(self):
        for f in listdir(self.rootfolder):
            if isfile(join(self.rootfolder,f)):
                if f.endswith('.pdf') :
                    self.files.append(join(self.rootfolder,f))
#         self.files.sort()
#         self.files = sorted(self.files,self.sort_files)
        print self.sort_nicely(self.files)
        
    def tryint(self,s):
        try:
            return int(s)
        except:
            return s
    
    def alphanum_key(self,s):
        """ Turn a string into a list of string and number chunks.
            "z23a" -> ["z", 23, "a"]
        """
        return [ self.tryint(c) for c in re.split('([0-9]+)', s) ]
    
    def sort_nicely(self,l):
        """ Sort the given list in the way that humans expect.
        """
        l.sort(key=self.alphanum_key) 
        