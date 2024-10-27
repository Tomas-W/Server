import os
from PIL import Image
from rembg import remove


def resize_image(input_path, output_path, size):
    with Image.open(input_path) as img:
        img = img.convert("RGB")
        img = img.resize(size, Image.LANCZOS)
        img.save(output_path)

def process_images(root_folder):
    sizes = [(400, 400), (300, 300), (200, 200), (100, 100), (50, 50)]
    
    for foldername, subfolders, filenames in os.walk(root_folder):
        for filename in filenames:
            if filename.lower().endswith(('.png')):
                input_path = os.path.join(foldername, filename)
                
                for size in sizes:                   
                    name, ext = os.path.splitext(filename)
                    output_filename = f"{name}{int(size[0]/10)}{ext}"
                    output_path = os.path.join(foldername, output_filename)
                    
                    resize_image(input_path, output_path, size)


def remove_background_by_folder(folder_path):
    for file in os.listdir(folder_path):
        if file.lower().endswith("5.png") or file.lower().endswith("0.png"):
            input_image_path = os.path.join(folder_path, file)
            
            with open(input_image_path, "rb") as input_file:
                input_image = input_file.read()

            output_image = remove(input_image)

            output_file_path = os.path.join(folder_path, file.split(".")[0] + "0.png")
            with open(output_file_path, "wb") as output_file:
                output_file.write(output_image)


def remove_background_by_file(input_image_path):
    with open(input_image_path, "rb") as input_file:
        input_image = input_file.read()

    output_image = remove(input_image)

    with open(os.path.join(input_image_path), "wb") as output_file:
        output_file.write(output_image)


def remove_images_with_suffix(folder_path):
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith("0.png"):
                file_path = os.path.join(root, file)
                os.remove(file_path)


def rename_images_with_suffix(folder_path):
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".png"):
                file_path = os.path.join(root, file)
                new_file_name = file[:-8] + ".png"
                new_file_path = os.path.join(root, new_file_name)
                os.rename(file_path, new_file_path)
