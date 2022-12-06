import cv2
from PIL import Image, ImageFilter


def scale_image(image, new_width=90, new_height=32):
    (original_width, original_height) = image.size
    aspect_ratio = original_height / float(original_width)
    if new_height == 0:
        new_height = int(aspect_ratio * new_width)

    new_image = image.resize((new_width, new_height))
    return new_image


def convert_to_grayscale(image):
    return image.convert('L')


def map_pixels_to_ascii_chars(image, chars):
    image = image.filter(ImageFilter.SHARPEN)
    pixels_of_such_value = [0] * 256

    pixels_in_image = list(image.getdata())

    for pixel_value in pixels_in_image:
        pixels_of_such_value[pixel_value] += 1
    non_null_values = len(pixels_in_image) - pixels_of_such_value[0]

    values_per_char = non_null_values / len(chars)

    char_by_value = list([0] * 256)
    i = 1
    processed_values = 0
    if non_null_values > 0:
        for i in range(1, 256, 1):
            char_by_value[i] = int(processed_values / values_per_char - 0.001)
            processed_values += pixels_of_such_value[i]
    for i in range(0, 16):
        char_by_value[i] = 0
    for i in range(241, 256):
        char_by_value[i] = -1

    pixels_to_chars = list()
    for pixel_value in pixels_in_image:
        pixels_to_chars.append(chars[char_by_value[pixel_value]])

    return "".join(pixels_to_chars)


def convert_image_to_ascii(image, new_width, new_height, chars):
    image = scale_image(image, new_width, new_height)
    image = convert_to_grayscale(image)

    pixels_to_chars = map_pixels_to_ascii_chars(image, chars)
    len_pixels_to_chars = len(pixels_to_chars)

    image_ascii = [pixels_to_chars[index: index + new_width] for index in
                   range(0, len_pixels_to_chars, new_width)]

    return "\n".join(image_ascii)


def get_frames_count(video_capture):
    return int(video_capture.get(7))


def get_framerate(video_capture):
    return video_capture.get(5)


def print_video_capture_info(video_capture):
    print("Resolution: \t", int(video_capture.get(3)), 'x', int(video_capture.get(4)))
    print("Framerate: \t", get_framerate(video_capture))
    print('Frames: \t', get_frames_count(video_capture))


def print_arguments():
    print('Usage:')
    print('     python ....py -v my_video.mp4 -w 120 -h 40 -o 120')
    print('Supported arguments:')
    print('    -v:  video filename,                     default: video.mp4')
    print('    -w:  frame width                         default: 90')
    print('    -h:  frame height, 0 means keep aspect   default: 32')
    print('    -s:  video frames per ASCII art          default: 1')
    print('    -i:  only print video info               default: false')
    print('    -nb: no block characters                 default: false')
    print('    -l:  length in frames, 0 means whole     default: 0')
    print('    -o:  offset from in frames               default: 0')


def read_args():
    import sys
    if len(sys.argv) < 2:
        print_arguments()
        exit()

    video_file = 'video.mp4'
    width = 90
    height = 32
    step = 1
    info_only = False
    no_block_chars = False
    length = 0
    offset = 0
    flag = ''
    for arg in sys.argv:
        if arg[0] == '-':
            if arg == '-i':
                info_only = True
            elif arg == '-nb':
                no_block_chars = True
            else:
                flag = arg
                continue
        if not len(flag) == 0:
            if flag == '-v':
                video_file = arg
            elif flag == '-w':
                width = int(arg)
            elif flag == '-h':
                height = int(arg)
            elif flag == '-s':
                step = int(arg)
            elif flag == '-l':
                length = int(arg)
            elif flag == '-o':
                offset = int(arg)
            else:
                print('Unknown parameter:', flag)
                print_arguments()
                exit()
            flag = ''
    if not len(flag) == 0:
        print("Parameter value expected:", flag)
        exit()
    return video_file, width, height, step, info_only, no_block_chars, length, offset


def video_to_ascii_frames(video_file, width, height, step, info_only, no_block_chars, length, offset):
    video = cv2.VideoCapture(video_file)
    if info_only:
        print_video_capture_info(video)
        exit()

    chars = '@MGC0%t;:,. ' if no_block_chars else '█▓▒@░MGC0%t;:,. '

    fps = get_framerate(video)
    last_frame = get_frames_count(video) - 1
    if not length == 0:
        last_frame = min(last_frame, offset + length)

    frames = []
    for frame_i in range(offset, last_frame, step):
        print('Process ASCII frame #', frame_i, '/', last_frame)
        video.set(1, frame_i)
        success, image_data = video.read()

        if not success:
            print("Failed to read frame #", frame_i)

        image = Image.fromarray(image_data, "RGB")
        image_ascii = convert_image_to_ascii(image, width, height, chars)
        frames.append(image_ascii)

    return frames


if __name__ == '__main__':
    video_file, width, height, step, info_only, no_block_chars, length, offset = read_args()
    frames = video_to_ascii_frames(video_file, width, height, step, info_only, no_block_chars, length, offset)

    f = open(video_file + '.txt', 'w', encoding="utf-8")
    f.write('SPLIT'.join(frames))
    f.close()
