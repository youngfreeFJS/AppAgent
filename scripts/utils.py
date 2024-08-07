import os
import base64
import cv2
import pyshine as ps

from colorama import Fore, Style


def print_with_color(text: str, color=""):
    if color == "red":
        print(Fore.RED + text)
    elif color == "green":
        print(Fore.GREEN + text)
    elif color == "yellow":
        print(Fore.YELLOW + text)
    elif color == "blue":
        print(Fore.BLUE + text)
    elif color == "magenta":
        print(Fore.MAGENTA + text)
    elif color == "cyan":
        print(Fore.CYAN + text)
    elif color == "white":
        print(Fore.WHITE + text)
    elif color == "black":
        print(Fore.BLACK + text)
    else:
        print(text)
    print(Style.RESET_ALL)


def draw_bbox_multi(img_path, output_path, elem_list, record_mode=False, dark_mode=False):
    imgcv = cv2.imread(img_path)
    count = 1
    for elem in elem_list:
        try:
            top_left = elem.bbox[0]
            bottom_right = elem.bbox[1]
            left, top = top_left[0], top_left[1]
            right, bottom = bottom_right[0], bottom_right[1]
            label = str(count)
            if record_mode:
                if elem.attrib == "clickable":
                    color = (250, 0, 0)
                elif elem.attrib == "focusable":
                    color = (0, 0, 250)
                else:
                    color = (0, 250, 0)
                imgcv = ps.putBText(imgcv, label, text_offset_x=(left + right) // 2 + 10, text_offset_y=(top + bottom) // 2 + 10,
                                    vspace=10, hspace=10, font_scale=1, thickness=2, background_RGB=color,
                                    text_RGB=(255, 250, 250), alpha=0.5)
            else:
                text_color = (10, 10, 10) if dark_mode else (255, 250, 250)
                bg_color = (255, 250, 250) if dark_mode else (10, 10, 10)
                imgcv = ps.putBText(imgcv, label, text_offset_x=(left + right) // 2 + 10, text_offset_y=(top + bottom) // 2 + 10,
                                    vspace=10, hspace=10, font_scale=1, thickness=2, background_RGB=bg_color,
                                    text_RGB=text_color, alpha=0.5)
        except Exception as e:
            print_with_color(f"ERROR: An exception occurs while labeling the image\n{e}", "red")
        count += 1
    cv2.imwrite(output_path, imgcv)
    return imgcv


def draw_grid(img_path, output_path):
    def get_unit_len(n):
        for i in range(1, n + 1):
            if n % i == 0 and 120 <= i <= 180:
                return i
        return -1

    image = cv2.imread(img_path)
    height, width, _ = image.shape
    color = (255, 116, 113)
    unit_height = get_unit_len(height)
    if unit_height < 0:
        unit_height = 120
    unit_width = get_unit_len(width)
    if unit_width < 0:
        unit_width = 120
    thick = int(unit_width // 50)
    rows = height // unit_height
    cols = width // unit_width
    for i in range(rows):
        for j in range(cols):
            label = i * cols + j + 1
            left = int(j * unit_width)
            top = int(i * unit_height)
            right = int((j + 1) * unit_width)
            bottom = int((i + 1) * unit_height)
            cv2.rectangle(image, (left, top), (right, bottom), color, thick // 2)
            cv2.putText(image, str(label), (left + int(unit_width * 0.05) + 3, top + int(unit_height * 0.3) + 3), 0,
                        int(0.01 * unit_width), (0, 0, 0), thick)
            cv2.putText(image, str(label), (left + int(unit_width * 0.05), top + int(unit_height * 0.3)), 0,
                        int(0.01 * unit_width), color, thick)
    cv2.imwrite(output_path, image)
    return rows, cols


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def get_image_megabyte_size(image_path: str) -> int:
    '''
    Get image size (Megabyte).
    '''
    return  os.stat(image_path).st_size / 1000 / 1000


def compress_image_size(image_path: str, expect_megabyte: int) -> str:
    '''
    Compress image size.
    Compress image size to reduce prompt volume, and decrease AI(openai, qwen, etc...) interface RT.

    Args:
        image_path (str): image original abs path.
        expect_megabyte (int): expect compress size in mega byte.

    Returns:
        str: compressed image path.

    Example:

        ```
        ls -al '/Users/.../github/appAgentFork/AppAgent/apps/X/demos/self_explore_2024-07-19_11-49-26'  total 8440
        drwxr-xr-x@ 6 youngfreefjs  staff      192  7 19 11:49 .
        drwxr-xr-x@ 4 youngfreefjs  staff      128  7 19 11:50 ..
        -rw-r--r--@ 1 youngfreefjs  staff    92927  7 19 11:49 1.xml
        -rw-r--r--@ 1 youngfreefjs  staff  1703275  7 19 11:49 1_before.png
        -rw-r--r--@ 1 youngfreefjs  staff  1995296  7 19 11:49 1_before_labeled.png
        -rw-r--r--@ 1 youngfreefjs  staff   459612  7 19 11:50 1_before_labeled_compression.jpg
        ```
    '''

    quality: int = 95
    
    image_reader = cv2.imread(image_path)

    compressed_image_path: str = os.path.splitext(image_path)[0]+'_compression.jpg'

    while quality > 10:
        cv2.imwrite(compressed_image_path, image_reader, [cv2.IMWRITE_JPEG_QUALITY, quality])
        current_megabyte_size: int = get_image_megabyte_size(compressed_image_path)
        print_with_color(f'compress image size to: {get_image_megabyte_size(compressed_image_path)} MB.')
        if get_image_megabyte_size(compressed_image_path) <= expect_megabyte:
            break
        quality -= 10 if current_megabyte_size >= 6.5 else 5
    open(compressed_image_path, 'rb')
    return compressed_image_path
