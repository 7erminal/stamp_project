#!/bin/bash

sudo rm -rf temp_dir
sudo mkdir temp_dir
cd temp_dir
sudo cp ../media/* .
#cd ..

# directory="temp_dir"

for file in *; do
	if [ $(head -c 4 "$file") = "%PDF" ]; then
    		echo "It's a PDF file. Skip"
		sudo rm "$file"
	else
		# soffice --headless --convert-to pdf:writer_pdf_Export --outdir . "$file"
		sudo libreoffice7.6 --headless --convert-to pdf:writer_pdf_Export --outdir . "$file"
		sudo rm "$file"
		sudo rm ../media/"$file"
	fi
done


