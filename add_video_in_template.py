import numpy as np
import cv2
import imageio
from types import SimpleNamespace
from PIL import ImageFont, ImageDraw, Image 

def add_sepia(img, k=1):
    matrix = [[0.272 - 0.349 * (1 - k), 0.534 - 0.534 *
               (1 - k), 0.131 + 0.869 * (1 - k)],
              [0.393 + 0.607 * (1 - k), 0.769 - 0.769 *
               (1 - k), 0.189 - 0.189 * (1 - k)],
              [0.349 - 0.349 * (1 - k), 0.686 + 0.314 *
               (1 - k), 0.168 - 0.168 * (1 - k)]]

    filt = cv2.transform(img, np.matrix(matrix))
    filt[np.where(filt > 255)] = 255
    return filt


def draw_text_scaled_to_rect(img, target_text, target_rect, font_name, thickness, color):
  
    # Use a truetype font  
    font = ImageFont.truetype(font_name, 10)
    ascent, descent = font.getmetrics()
    (width, baseline), (offset_x, offset_y) = font.font.getsize(target_text)  

    text_height = ascent + descent
    text_width = width
    target_rect_x = target_rect[0]
    target_rect_y = target_rect[1]
    target_rect_width = target_rect[2]
    target_rect_height = target_rect[3]
    scale_x = float(target_rect_width) / float(text_width)
    scale_y = float(target_rect_height) / float(text_height)
    scale = min(scale_x, scale_y)
    margin_x = 0 if scale == scale_x else int(target_rect_width *
                                              (scale_x - scale) / scale_x*0.5)
    margin_y = 0 if scale == scale_y else int(target_rect_height *
                                              (scale_y - scale) / scale_y*0.5)
    
    pil_im = Image.fromarray(img)  
    draw = ImageDraw.Draw(pil_im)
    font = ImageFont.truetype(font_name, int(10*scale))
     # Draw the text  
    draw.text((target_rect_x + margin_x, target_rect_y +
               target_rect_height - margin_y), target_text,fill='black', font=font) 
    result_img = np.array(pil_im)
    return result_img


def make_gif(params_paths, params_text, params_transform, scale_factor=3, scenario=2, show_result=False):
    ns_paths = SimpleNamespace(**params_paths)
    ns_text = SimpleNamespace(**params_text)
    ns_transforms = SimpleNamespace(**params_transform)

    print(ns_paths.templates_folder)
    if scenario == 1:
        template_name = 'template4.jpg'
        position = [230, 430]
        desired_size = [580, 380]
    elif scenario == 2:
        template_name = 'template3_cropped.jpg'
        position = [425, 165]
        desired_size = [470, 420]
        text_box_params = {'ltp': [236, 33],
                           'rbp': [421, 754],
                           'color': [216, 226, 234]}

    position = [int(x/scale_factor) for x in position]
    desired_size = [int(x/scale_factor) for x in desired_size]
    text_box_params['ltp'] = [int(x/scale_factor)
                              for x in text_box_params['ltp']]
    text_box_params['rbp'] = [int(x/scale_factor)
                              for x in text_box_params['rbp']]
    if show_result:
        cv2.namedWindow("output", cv2.WINDOW_NORMAL)
        cv2.namedWindow("template", cv2.WINDOW_NORMAL)

    # Load an color image in grayscale
    template = cv2.imread('{}{}'.format(ns_paths.templates_folder,
                                        template_name), cv2.IMREAD_COLOR)

    template = cv2.resize(template, None, fx=1/scale_factor, fy=1/scale_factor)

    # Add text on template
    text_box_ltp = text_box_params['ltp']
    text_box_rbp = text_box_params['rbp']
    template[text_box_ltp[0]:text_box_rbp[0],
             text_box_ltp[1]:text_box_rbp[1], :] = text_box_params['color']

    target_rect_line1 = [text_box_ltp[1], text_box_ltp[0]-int((text_box_rbp[0]-text_box_ltp[0])/2),
                         text_box_rbp[1]-text_box_ltp[1],
                         int((text_box_rbp[0]-text_box_ltp[0])/2)]
    target_rect_line2 = [text_box_ltp[1], text_box_ltp[0],
                         text_box_rbp[1]-text_box_ltp[1],
                         int((text_box_rbp[0]-text_box_ltp[0])/2)]

    template = draw_text_scaled_to_rect(template, ns_text.headline_text, target_rect_line1,
                             ns_paths.fonts_folder + ns_text.font, ns_text.thickness_line_1, ns_text.color)
    template = draw_text_scaled_to_rect(template, ns_text.sub_headline_text, target_rect_line2,
                             ns_paths.fonts_folder + ns_text.font, ns_text.thickness_line_2, ns_text.color)
    if show_result:
        cv2.imshow('template', template)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    # print(template.shape)
    cap = cv2.VideoCapture('{}{}'.format(ns_paths.animations_folder,
                                         ns_paths.animation_name))

    # Check if camera opened successfully
    if (cap.isOpened() == False):
        print("Error opening video stream or file")
    else:
        anim_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        anim_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    t_rows, t_cols, t_channels = template.shape
    # Read until video is completed
    with imageio.get_writer('{}{}'.format(ns_paths.gifs_folder,
                                          ns_paths.gif_name), mode='I', fps=25) as writer:
        angle_curr = ns_transforms.angle_start
        scale_curr = ns_transforms.scale_start
        angle_direction = 1
        scale_direction = 1
        while(cap.isOpened()):
            ret, frame = cap.read()
            if ret == True:
                angle_curr %= 360
                anim_frame = cv2.resize(
                    frame, tuple(desired_size))
                if ns_transforms.sepia:
                    anim_frame = add_sepia(
                        anim_frame, ns_transforms.sepia_scale)
                anim_shape = anim_frame.shape
                anim_h, anim_w = anim_shape[1], anim_shape[0]
                template[position[0]:position[0]+anim_w,
                         position[1]: position[1]+anim_h] = anim_frame

                output = cv2.cvtColor(template, cv2.COLOR_BGR2RGB)
                if ns_transforms.rotate or ns_transforms.scale or ns_transforms.skew:

                    if angle_curr < ns_transforms.angle_stop:
                        angle_curr += (angle_direction * ns_transforms.angle_step)
                    elif ns_transforms.angle_reverse:
                        angle_direction *= -1
                        angle_curr += (angle_direction * ns_transforms.angle_step)
                    if scale_curr < ns_transforms.scale_stop:
                        scale_curr += (scale_direction * ns_transforms.scale_step)
                    elif ns_transforms.scale_reverse:
                        scale_direction *= -1
                        scale_curr += (scale_direction * ns_transforms.scale_step)
                    angle_t = angle_curr if ns_transforms.rotate else 0
                    scale_t = scale_curr if ns_transforms.scale else 1
                    R = cv2.getRotationMatrix2D(
                        (int(t_cols/2), int(t_rows/2)
                         ), angle_t,
                        scale_t)
                    if ns_transforms.skew:
                        pts1 = np.float32([[0,0],[0,t_cols],[t_rows,0],[t_rows,t_cols]])
                        pts2 = np.float32([[0,0],[0,t_cols-angle],[t_rows,0],[t_rows,t_cols]])
                        # M = cv2.getPerspectiveTransform(pts1,pts2)
                        # R = np.matrix(M) * np.matrix(R)
                    output = cv2.warpAffine(output, R, (t_cols, t_rows))
                if show_result:
                    cv2.imshow('output', output)
                writer.append_data(output)

                # Press Q to exit
                if cv2.waitKey(25) & 0xFF == ord('q'):
                    break
            else:
                break
    cap.release()


def main():
    # Image transformation
    params_transform = {
        'rotate': True,
        'scale': True,
        'skew': False,
        'sepia': False,
        'sepia_scale': 0.4,
        'angle_start': 0,
        'angle_stop': 35,
        'angle_step': 0.2,
        'angle_reverse': True,
        'scale_start': 0.7,
        'scale_stop': 1.2,
        'scale_step': 0.005,
        'scale_reverse': True
    }

    # Paths
    params_paths = {
        'templates_folder': 'templates/',
        'animations_folder': 'animations/',
        'gifs_folder': 'results/gifs/',
        'animation_name': 'vlad_2.mp4',
        'gif_name': 'newspaper_vlad2.gif',
        'fonts_folder': 'fonts/'
    }

    # Text lines params
    params_text = {
        'thickness_line_1': 2,
        'thickness_line_2': -1,
        'color': (0, 0, 0),
        'font': 'Mugglenews.ttf',
        'headline_text': 'SENSATION!',
        'sub_headline_text': 'EVIL PANDA MADE CRAZY THING AGAIN!'
    }

    # Select one of the scenarios
    scenario = 2
    scale_factor = 3
    show_result = True

    make_gif(params_paths, params_text, params_transform,
             scale_factor=scale_factor, scenario=scenario, show_result=show_result)


if __name__ == '__main__':
    main()
