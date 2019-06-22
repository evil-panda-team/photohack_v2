import numpy as np
import cv2
import imageio

templates_folder = 'templates/'
animations_folder = 'animations/'
gifs_folder = 'results/gifs/'
template_name = 'template_header.jpg'
animation_name = 'telka.mp4'
gif_name = 'newspaper.gif'


scale_factor = 4
x_pos = 0.5
y_pos = 0.3
x_scale = 1
y_scale = 1

cv2.namedWindow("output", cv2.WINDOW_NORMAL)
cv2.namedWindow("template", cv2.WINDOW_NORMAL)

# Load an color image in grayscale
template = cv2.imread('{}{}'.format(templates_folder,
                                    template_name), cv2.IMREAD_COLOR)
template = cv2.resize(template, None, fx=1/scale_factor, fy=1/scale_factor)
newspaper = np.ones((template.shape[0]*5, template.shape[1], 3), np.uint8)*255
newspaper[0:template.shape[0], 0:template.shape[1], :] = template

position = [int(x_pos*newspaper.shape[0]), int(y_pos*newspaper.shape[0])]

cv2.imshow('template', newspaper)
cv2.waitKey(0)
cv2.destroyAllWindows()

print(template.shape)
cap = cv2.VideoCapture('{}{}'.format(animations_folder,
                                     animation_name))

# Check if camera opened successfully
if (cap.isOpened() == False):
    print("Error opening video stream or file")
else:
    anim_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    anim_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

images = []
# Read until video is completed
with imageio.get_writer('{}{}'.format(gifs_folder,
                                      gif_name), mode='I', fps=25) as writer:
    while(cap.isOpened()):
        ret, frame = cap.read()
        if ret == True:
            if x_scale == 1 and y_scale == 1:
                anim_frame = frame
            else:
                desired_size = [int(x_scale * frame[0]),
                                int(y_scale * frame[1])]
                anim_frame = cv2.resize(
                    frame, tuple(desired_size))
            anim_shape = anim_frame.shape
            anim_h, anim_w = anim_shape[1], anim_shape[0]
            newspaper[position[0]:position[0]+anim_w,
                      position[1]: position[1]+anim_h] = anim_frame

            newspaper = cv2.cvtColor(newspaper, cv2.COLOR_BGR2RGB)
            cv2.imshow('output', newspaper)
            writer.append_data(newspaper)
            # Press Q to exit
            if cv2.waitKey(25) & 0xFF == ord('q'):
                break
        else:
            break

# When everything done, release the video capture object
cap.release()
