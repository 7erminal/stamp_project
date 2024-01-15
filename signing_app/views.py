from django.shortcuts import render
from django.http import HttpResponseRedirect, FileResponse
from django.core.files.storage import FileSystemStorage
import aspose.words as aw
from reportlab.pdfgen import canvas
from PyPDF2 import PdfWriter, PdfReader
from PIL import Image
import logging
import os
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent

# Get an instance of a logger
logger = logging.getLogger("django")

# Create your views here.
def index(request):
	# if request.user.is_authenticated:
	# 	queryset = modules.objects.filter(active=1,is_fillable=1)
	# 	return render(request, 'dataProcessor/index.html', {'modules' : queryset})
	# else:
	# 	return HttpResponseRedirect('/analytics/login/')
    return render(request, 'templates/index.html')

def upload(request):
    if request.method == "POST" and request.FILES['the_files']:
        logger.info("Begin... ")
        files_ = request.FILES['the_files']
        logger.info("File is ")
        logger.info(files_)
        fs = FileSystemStorage()
        filename = fs.save(files_.name.replace(" ","-"), files_)
        logger.info("File name is ")
        logger.info(filename)
        uploaded_file_url = fs.url(filename)
        logger.info("Base dir is ")
        logger.info(BASE_DIR)
        logger.info("Uploaded File url is ")
        logger.info(uploaded_file_url)
        logger.info("Full path is ")
        logger.info(str(BASE_DIR) + uploaded_file_url)
        # os.chmod(str(BASE_DIR) +uploaded_file_url, 0o777)
        doc = aw.Document(str(BASE_DIR) + uploaded_file_url)
        logger.info("About to save raw file")
        doc.save(filename+'.pdf')

        os.remove(str(BASE_DIR) +uploaded_file_url)

        # logger.info("PDF path is ")
        # logger.info(fs.url(filename+'.pdf'))

        # Create the watermark from an image
        c = canvas.Canvas('watermark.pdf')

        logger.info("About to open stamp for processing")
        stamp = Image.open(str(BASE_DIR) + '/media/application_images/stamp.png')

        # Get the image dimensions
        img_width, img_height = stamp.size

        logger.info("Getting files ready")
        # Get our files ready
        output_file = PdfWriter()
        input_file = PdfReader(open(str(BASE_DIR)+'/'+filename+'.pdf', "rb"))


        # Draw the image at x, y. I positioned the x,y to be where i like here

        logger.info("Set page size")
        c.setPageSize((input_file.pages[0].mediabox.width, input_file.pages[0].mediabox.height))

        if request.POST['position'] == 'bl':
            # Bottom left
            c.drawImage(str(BASE_DIR) + '/media/application_images/stamp.png', 0, 0, 100, 100 * img_height / img_width, mask='auto')

        if request.POST['position'] == 'tl':
            # Top left
            c.drawImage(str(BASE_DIR) + '/media/application_images/stamp.png', 0, input_file.pages[0].mediabox.height - 120, 100, 100 * img_height / img_width, mask='auto')

        if request.POST['position'] == 'tr':
            # Top right
            c.drawImage(str(BASE_DIR) + '/media/application_images/stamp.png', input_file.pages[0].mediabox.width - 120, input_file.pages[0].mediabox.height - 120, 100, 100 * img_height / img_width, mask='auto')

        if request.POST['position'] == 'br':
            # Bottom right
            c.drawImage(str(BASE_DIR) + '/media/application_images/stamp.png', input_file.pages[0].mediabox.width - 120, 0, 100, 100 * img_height / img_width, mask='auto')


        # Add some custom text for good measure
        # c.drawString(15, 720,"Hello World")
        c.save()

        # Get the watermark file you just created
        watermark = PdfReader('watermark.pdf')


        logger.info("Height of actual PDF is  ")
        logger.info(input_file.pages[0].mediabox.width)

        logger.info("Height of watermark PDF is  ")
        logger.info(watermark.pages[0].mediabox.width)


        # Number of pages in input document
        page_count = len(input_file.pages)

        logger.info("About to apply stamp on all pages of the file")
        # Go through all the input file pages to add a watermark to them
        for page_number in range(page_count):
            # print "Watermarking page {} of {}".format(page_number, page_count)
            # merge the watermark with the page
            input_page = input_file.pages[page_number]
            input_page.merge_page(watermark.pages[0])
            # add page from input file to output document
            output_file.add_page(input_page)
   
        logger.info("Stamp has been applied on all pages. \nAbout to write into pdf file")
        # finally, write "output" to document-output.pdf
        with open(filename+"edited-document-output.pdf", "wb") as outputStream:
            output_file.write(outputStream)

        logger.info("PDF writing complete. About to delete surplus files")
        os.remove(filename+'.pdf')
        os.remove('watermark.pdf')
    return FileResponse(open(filename+"edited-document-output.pdf", 'rb'), as_attachment=True)
    return HttpResponseRedirect('/')