#!/bin/bash

sudo rm -rf temp_dir
sudo mkdir temp_dir
sudo cd temp_dir
sudo cp media/* .
#cd ..

directory="temp_dir"

for file in "$directory"/*; do
	if [ $(head -c 4 "$file") = "%PDF" ]; then
    		echo "It's a PDF file. Skip"
		sudo rm media/"$file"
	else
		# soffice --headless --convert-to pdf:writer_pdf_Export --outdir . "$file"
		sudo libreoffice7.6 --headless --convert-to pdf:writer_pdf_Export --outdir . "$file"
		sudo rm "$directory"/"$file"
		sudo rm media/"$file"
	fi
done


