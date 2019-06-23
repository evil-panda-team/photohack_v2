# -*- coding: utf-8 -*-

from run_vlad import create_mp4

if __name__ == "__main__":
    input_img_path = 'img/buzova.jpg'
    csv_path = 'csv/vlad_scream.csv'
    create_mp4(input_img_path, csv_path)
