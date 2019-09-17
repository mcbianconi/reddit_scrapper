import os

IMG_WIDTH=1920

IMG_HEIGHT=1080

NUM_THREADS = 8

OUTPUT_DIR = os.path.join(os.getcwd(), "output")




if not os.path.exists(OUTPUT_DIR):
    os.mkdir(OUTPUT_DIR)