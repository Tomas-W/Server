
# from datetime import datetime, timedelta
# import random
from PIL import Image
# from rembg import remove


# def random_dates(count=20):
#     start_date = datetime.now() - timedelta(weeks=3)
#     end_date = datetime.now()
#     return sorted(datetime.fromtimestamp(random.randint(int(start_date.timestamp()), int(end_date.timestamp()))).strftime("%d %b %H:%M") for _ in range(count))


def resize_image(input_path, output_path, size):
    with Image.open(input_path) as img:
        img = img.convert("RGBA")
        img = img.resize(size, Image.LANCZOS)
        img.save(output_path)
        
# if __name__ == "__main__":
#     for root, dirs, files in os.walk("C:/Coding/Projects/Server/backups/images/bakery smaller/New folder"):
#         for image in files:
#             input_path = os.path.join(root, image)
#             relative_path = os.path.relpath(root, "C:/Coding/Projects/Server/backups/images/bakery smaller/New folder")
#             output_dir = os.path.join("C:/Coding/Projects/Server/backups/images/bakery smaller/New folder/new", relative_path)
#             os.makedirs(output_dir, exist_ok=True)
#             output_path = os.path.join(output_dir, image)
#             resize_image(input_path, output_path, (200, 200))

# def process_images(root_folder):
#     sizes = [(400, 400), (300, 300), (200, 200), (100, 100), (50, 50)]
    
#     for foldername, subfolders, filenames in os.walk(root_folder):
#         for filename in filenames:
#             if filename.lower().endswith(('.png')):
#                 input_path = os.path.join(foldername, filename)
                
#                 for size in sizes:                   
#                     name, ext = os.path.splitext(filename)
#                     output_filename = f"{name}{int(size[0]/10)}{ext}"
#                     output_path = os.path.join(foldername, output_filename)
                    
#                     resize_image(input_path, output_path, size)


# def remove_background_by_folder(folder_path):
#     for file in os.listdir(folder_path):
#         if file.lower().endswith("5.png") or file.lower().endswith("0.png"):
#             input_image_path = os.path.join(folder_path, file)
            
#             with open(input_image_path, "rb") as input_file:
#                 input_image = input_file.read()

#             output_image = remove(input_image)

#             output_file_path = os.path.join(folder_path, file.split(".")[0] + "0.png")
#             with open(output_file_path, "wb") as output_file:
#                 output_file.write(output_image)

# def remove_background_by_file(input_image_path):
#     with open(input_image_path, "rb") as input_file:
#         input_image = input_file.read()

#     output_image = remove(input_image)

#     with open(os.path.join(input_image_path), "wb") as output_file:
#         output_file.write(output_image)


# def remove_images_with_suffix(folder_path):
#     for root, dirs, files in os.walk(folder_path):
#         for file in files:
#             if file.endswith("0.png"):
#                 file_path = os.path.join(root, file)
#                 os.remove(file_path)


# def rename_images_with_suffix(folder_path):
#     for root, dirs, files in os.walk(folder_path):
#         for file in files:
#             if file.endswith(".png"):
#                 file_path = os.path.join(root, file)
#                 new_file_name = file[:-8] + ".png"
#                 new_file_path = os.path.join(root, new_file_name)
#                 os.rename(file_path, new_file_path)
