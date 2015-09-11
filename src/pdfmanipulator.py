'''
Created on Nov 2, 2014

'''
from PyPDF2.generic import NameObject, DictionaryObject, ArrayObject,\
    FloatObject, NumberObject, TextStringObject
from datetime import datetime
from pdfminer.layout import LTTextBoxHorizontal, LAParams
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument, PDFTextExtractionNotAllowed
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfdevice import PDFDevice
from pdfminer.pdfpage import PDFPage
from pdfminer.converter import PDFPageAggregator
from PyPDF2.pdf import PdfFileReader, PdfFileWriter
YELLOW = [0.95, 0.9, 0.2]

class LocationKeeper:
    keyword =''
    bounds = []
    page_num = 1
    def __init__(self,keyword,bounds,page_num):
        self.keyword = keyword
        self.bounds= bounds
        self.page_num = page_num

def float_array(lst):
    return ArrayObject([FloatObject(i) for i in lst])   

def highlight_annotation(quadpoints, contents=None, author=None,
                         subject=None, color=YELLOW, alpha=1, flag=4):
    """Create a 'Highlight' annotation that covers the area given by quadpoints.
    
    Inputs: quadpoints  A list of rectangles to be highlighted as part of this
                        annotation.  Each is specified by a quadruple [x0,y0,x1,y1],
                        where (x0,y0) is the lower left corner of the rectangle and
                        (x1,y1) the upper right corner.
            
            contents    Strings giving the content, author, and subject of the
            author      annotation
            subject
            
            color       The color of the highlighted region, as an array of type
                        [g], [r,g,b], or [c,m,y,k].
            
            alpha       The alpha transparency of the highlight.
            
            flag        A bit flag of options.  4 means the annotation should be
                        printed.  See the PDF spec for more.
    
    Output: A DictionaryObject representing the annotation.
    
    """
    qpl = []
    print quadpoints
    for x0,y0,x1,y1 in quadpoints:
        qpl.extend([x0, y1, x1, y1, x0, y0, x1, y0])
    # The rectangle needs to contain the highlighted region for Evince
    # and Xpdf to display it.
    def quadpoints_col(i):
        return [pts[i] for pts in quadpoints]
    rect = [min(quadpoints_col(0)), min(quadpoints_col(1)),
            max(quadpoints_col(2)), max(quadpoints_col(3))]
    
    retval = _markup_annotation(rect, contents, author, subject, color, alpha, flag)
    retval[NameObject('/Subtype')] = NameObject('/Highlight')
    retval[NameObject('/QuadPoints')] = float_array(qpl)
    return retval
def _markup_annotation(rect, contents=None, author=None, subject=None,
                       color=None, alpha=1, flag=4):
    """Set shared properties of all markup annotations."""
    
    retval = DictionaryObject({ NameObject('/CA'): FloatObject(alpha),
                                NameObject('/F'): NumberObject(flag),
                                NameObject('/Rect'): float_array(rect),
                                NameObject('/Type'): NameObject('/Annot'),
                                NameObject('/CreationDate'): now(),
                                NameObject('/M'): now(),
                             })
    retval.popup = False  # Whether to add an explicit popup when adding to page
    if contents is not None:
        retval[NameObject('/Contents')] = TextStringObject(contents)
    if author is not None:
        retval[NameObject('/T')] = TextStringObject(author)
    if subject is not None:
        retval[NameObject('/Subj')] = TextStringObject(subject)
    if color is not None:
        retval[NameObject('/C')] = float_array(color)
    return retval

def now():
    # Python timezone handling is a messs, so just use UTC
    st = datetime.utcnow().strftime("D:%Y%m%d%H%M%SZ00'00")
    return TextStringObject(st)

def get_location(keyword,layout,x,y):
    """Takes , layout and keyword and returns bbox location."""
    keyword_length = len(keyword)
    locations = [] 
    
    print layout.bbox
    for obj in layout._objs:
        if isinstance(obj,LTTextBoxHorizontal) :
              for o in obj._objs :
                  arr = o._objs
                  index = 0
                  line_length = len(arr)
                  
                  for index in range(0,line_length):
#                      print arr[index].get_text()
#                      print index
                     word = ''
                     if arr[index].get_text().lower() == keyword[0].lower() :
                        if index+keyword_length <= line_length :
                             for j in arr[index:index+keyword_length]:
                                  word += j.get_text()
#                              print 'Word %s'%word
#                              print '%s,%s'%(index,index+keyword_length)
                             if word.lower() == keyword.lower():
                                 print 'Found -->%s'%word
                                 print arr[index:index+keyword_length]
                                 x0 = arr[index].bbox[0]
                                 x0+=x
                                 y0 = arr[index].bbox[1]
                                 y0+=y
                                 x1 = arr[index+keyword_length-1].bbox[2]
                                 x1+=x
                                 y1 = arr[index+keyword_length-1].bbox[3]
                                 y1+=y
                                 print x0
                                 print y0
                                 print x1
                                 print y1
                                 locations.append([x0,y0,x1,y1]) 
    return locations    
                             
def calculate_locations(filename,keywords):
    locations = []
    fp = open(filename, 'rb')
    parser = PDFParser(fp)
    # Create a PDF document object that stores the document structure.
    # Supply the password for initialization.
    document = PDFDocument(parser)
    # Check if the document allows text extraction. If not, abort.
    if not document.is_extractable:
        raise PDFTextExtractionNotAllowed
    # Create a PDF resource manager object that stores shared resources.
    rsrcmgr = PDFResourceManager()
    # Create a PDF device object.
    device = PDFDevice(rsrcmgr)
    # Create a PDF interpreter object.
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    # Process each page contained in the document.
    for page in PDFPage.create_pages(document):
        interpreter.process_page(page)    
    #Set parameters for analysis.
    laparams = LAParams()
    # Create a PDF page aggregator object.
    device = PDFPageAggregator(rsrcmgr, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    pages = PDFPage.create_pages(document)
    pagenum = 0
    reader = PdfFileReader(file(filename,"rb"))
    for page in pages:
        interpreter.process_page(page)
        # receive the LTPage object for the page.
        layout = device.get_result()    
        page = reader.getPage(pagenum)
        x = page.trimBox[0].as_numeric()
        y = page.trimBox[1].as_numeric()
        #Handling special case
        if  (x > 0 and y < 0):
                x = 0
#         print "At page = %s  X  = %s , y = %s"%(pagenum,x,y)
        for keyword in keywords:    
            print '********************************'
            co_ordinates = get_location(keyword,layout,x,y)
            print'Keyword %s , location %s'%(keyword,co_ordinates)
            print '********************************'
            if co_ordinates != None :
                for location in co_ordinates:
                    print "PageNum-->%s"%pagenum
                    l = LocationKeeper(keyword,location,pagenum)
                    locations.append(l)
        pagenum+=1
    return locations

def do_highlight(filename,keywords,output_file):
     locations = calculate_locations(filename,keywords)
     reader = PdfFileReader(file(filename, 'rb'))
     lnk = DictionaryObject()
     writer = PdfFileWriter()
     num = 0
     for page in reader.pages:
         for l in locations :
            if l.page_num == num :
                annot1 = highlight_annotation([l.bounds],
                            'Comments', 
                            'Author', 'Comments.')   
                popup_ref = writer._addObject(annot1)
                print l.page_num
                if "/Annots" in page:
                    page['/Annots'].append(popup_ref)
                    annots = page['/Annots']
                else:
                    page[NameObject('/Annots')] = ArrayObject([popup_ref])
                    annots = page['/Annots']
                annots_ref = writer._addObject(annots)
         num+=1
         writer.addPage(page) 
        # finally, write "output" to document-output.pdf
     outputStream = file(output_file, "wb")
     writer.write(outputStream) 
     outputStream.close()
                