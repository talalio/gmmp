#!/usr/bin/python3

from bs4 import BeautifulSoup
import requests
import os
import io
import sys
import img2pdf
import argparse

def get_images(link: str, save: bool = False, img_dir: str = None) -> list:
    headers =  {
        "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:110.0) Gecko/20100101 Firefox/110.0"
    }

    slide_page = requests.get(link, headers=headers, allow_redirects=False)
    bs = BeautifulSoup(slide_page.content, features='html.parser')

    image_elements = bs.find_all('img', attrs={'class':'slide-image'})
    images_sources = [img.attrs['src'] for img in image_elements]
    images_objects = [requests.get(image).content for image in images_sources]

    if save:
        try:
            os.chdir(img_dir)
        except FileNotFoundError:
            os.mkdir(img_dir)
            os.chdir(img_dir)

        for (img_no, image) in enumerate(images_objects):
            with open(f'img{img_no}.jpg', 'wb') as imgf:
                imgf.write(image)
        print(f"[+] Images saved to : {img_dir}")

    return [io.BytesIO(image) for image in images_objects]


def to_pdf(images_objects: list, output_file_name: str):
    if len(output_file_name.split('.')) > 0:
        if output_file_name.split('.')[-1] != 'pdf':
            output_file_name += '.pdf'

    with open(output_file_name, 'wb') as of:
       of.write(img2pdf.convert(images_objects))
       print(f"[+] File saved to {output_file_name}")


def main():
    parser = argparse.ArgumentParser(prog="GMMP", description="Download presentations from websites")
    parser.add_argument('-u', dest="url", help='url to the slidepresentation', required=True)
    parser.add_argument('-o', dest="output", help='output file path', required=True)
    parser.add_argument('-im', dest="images_dir", help="save downloaded image to a directory")

    args = parser.parse_args()

    link = args.url
    output_file = args.output
    images = get_images(link, args.images_dir != None, args.images_dir)
    to_pdf(images, output_file)
    sys.exit(0)


if __name__ == '__main__':
    main()
