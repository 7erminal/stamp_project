import decimal
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
import subprocess

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
        files_ = request.FILES.getlist('the_files')

        logger.info("List of files are")
        logger.info(files_)

        for f in files_:
            logger.info("File is ")
            logger.info(f)
            fs = FileSystemStorage()
            filename = fs.save(f.name.replace(" ","-"), f)
            logger.info("File name is ")
            logger.info(filename)
            uploaded_file_url = fs.url(filename)
            # logger.info("Base dir is ")
            # logger.info(BASE_DIR)
            # logger.info("Uploaded File url is ")
            # logger.info(uploaded_file_url)
            logger.info("Full path is ")
            logger.info(str(BASE_DIR) + uploaded_file_url)
            logger.info("Changing file permissions")
            os.chmod(str(BASE_DIR) +uploaded_file_url, 0o777)
            logger.info("Getting raw document")

        logger.info("About to call sh script to convert file to pdf")
        process = subprocess.Popen(['sh', './convert_to_pdf_script.sh'], stdout=subprocess.PIPE)
        process.wait()
        logger.info("Process code is "+str(process.returncode))

            # logger.info("Removing raw document since we now have the PDF file")
            # os.remove(str(BASE_DIR) +uploaded_file_url)

        # logger.info("PDF path is ")
        # logger.info(fs.url(filename+'.pdf'))

        

        logger.info("About to open stamp for processing")
        stamp = Image.open(str(BASE_DIR) + '/media/application_images/stamp.png')

        # Get the image dimensions
        img_width, img_height = stamp.size

        logger.info("Getting files ready")
        logger.info("Filename is "+filename)
        # Get our files ready
        output_file = PdfWriter()
        logger.info("About to loop through files in "+str(BASE_DIR)+'/temp_dir')
        # pathlist = Path(str(BASE_DIR)+'/temp_dir').rglob('*.asm')
        # logger.info(pathlist)
        for file in os.listdir(str(BASE_DIR)+'/temp_dir'):
            logger.info("Path is "+str(BASE_DIR)+'/temp_dir/'+str(file))
            input_file = PdfReader(open(str(BASE_DIR)+'/temp_dir/'+str(file), "rb"))

            # Create the watermark from an image
            c = canvas.Canvas('watermark.pdf')

            logger.info("Set page size")
            c.setPageSize((input_file.pages[0].mediabox.width, input_file.pages[0].mediabox.height))
            logger.info("Image height is "+str(img_height)+" and image width is "+str(img_width))
            logger.info("PDF Size width is "+str(input_file.pages[0].mediabox.width)+" and height is "+str(input_file.pages[0].mediabox.height))

            if request.POST['position'] == 'bl':
                # Bottom left
                c.drawImage(str(BASE_DIR) + '/media/application_images/stamp.png', 0, 0, 100, 100 * int(img_height) / int(img_width), mask='auto')

            if request.POST['position'] == 'tl':
                # Top left
                c.drawImage(str(BASE_DIR) + '/media/application_images/stamp.png', 0, int(input_file.pages[0].mediabox.height) - 120, 100, 100 * int(img_height) / int(img_width), mask='auto')

            if request.POST['position'] == 'tr':
                # Top right
                c.drawImage(str(BASE_DIR) + '/media/application_images/stamp.png', int(input_file.pages[0].mediabox.width) - 120, int(input_file.pages[0].mediabox.height) - 120, 100, 100 * int(img_height) / int(img_width), mask='auto')

            if request.POST['position'] == 'br':
                # Bottom right
                c.drawImage(str(BASE_DIR) + '/media/application_images/stamp.png', int(input_file.pages[0].mediabox.width) - 120, 0, 100, 100 * int(img_height) / int(img_width), mask='auto')


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
            with open(str(BASE_DIR)+'/temp_dir/'+str(file), "wb") as outputStream:
                output_file.write(outputStream)

            logger.info("PDF writing complete. About to delete surplus files")

            process2 = subprocess.Popen(['sh', './zip_files.sh'], stdout=subprocess.PIPE)
            process2.wait()

            os.remove('watermark.pdf')
        
        
    return FileResponse(open("pFiles.zip", 'rb'), as_attachment=True)
    return HttpResponseRedirect('/')