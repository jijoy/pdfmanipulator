from pyPdf import PdfFileWriter, PdfFileReader
import StringIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter


# read your existing PDF
file_name = "D:\\Work\\pdfmanipulator\\docs\\Sampleism login notes.pdf"
existing_pdf = PdfFileReader(file(file_name, "rb"))
output = PdfFileWriter()
# add the "watermark" (which is the new pdf) on the existing page

count=1
position = 10
str = "ABCDEFG"
for num in range(0,existing_pdf.getNumPages()):
    page = existing_pdf.getPage(num)
    packet = StringIO.StringIO('')
    # create a new PDF with Reportlab
    can = canvas.Canvas(packet, pagesize=letter)
    string = "%s , Page %s"%(file_name,num+1)

    can.drawString(0, 0, string)
    can.save()
    count = count +1
    #move to the beginning of the StringIO buffer
    packet.seek(0)
    # print packet.getvalue()
    new_pdf = PdfFileReader(packet)
    page.mergePage(new_pdf.getPage(0))
    output.addPage(page)
# finally, write "output" to a real file
outputStream = file("D:\\Work\\pdfmanipulator\\docs\\destination.pdf", "wb")
output.write(outputStream)
outputStream.close()