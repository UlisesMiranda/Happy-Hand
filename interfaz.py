
# This file was generated by the Tkinter Designer by Parth Jadhav
# https://github.com/ParthJadhav/Tkinter-Designer
from cnn import Model, DataGatherer
from Auto_Correct_SpellChecker import Auto_Correct
import mediapipe as mp
from PIL import ImageTk, Image
import cv2
import numpy as np

from pathlib import Path

# from tkinter import *
# Explicit imports to satisfy Flake8
from tkinter import Tk, Canvas, Entry, Text, Button, PhotoImage,Frame,Label




OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / Path(r"D:\Documentos\a\build\assets\frame0")


def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)

# Hands capture
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands
cap = None

classifier = Model.load_classifier('grayscale_classifier.h5')


def draw_region(image, center):
    cropped_image = cv2.rectangle(image, (center[0] - 130, center[1] - 130),
        (center[0] + 130, center[1] + 130), (0, 0, 255), 2)
    return cropped_image[center[1]-130:center[1]+130, center[0]-130:center[0]+130], cropped_image

"""
Modelo
"""
def update_frame(image, vid_label):
    image_fromarray = Image.fromarray(image)
    imgtk = ImageTk.PhotoImage(image=image_fromarray)
    
    vid_label.imgtk = imgtk
    vid_label.config(image=imgtk)

""" def get_threshold(label_entrybox):
    value = label_entrybox.get('1.0', END)
    try:
        return float(value)
    except:
        return 0.95 """

def AddCharToWord(word, curr_char):
    temp_word = word
    if curr_char == 'space':
        temp_word = ""
    elif curr_char == 'del':
        temp_word = temp_word[0:-1]
        print('character has been deleted')
    elif curr_char != 'nothing':
        temp_word += curr_char.lower()
        print('character has been added: ', curr_char.lower())

    return [temp_word, curr_char]


def get_char(gesture):
    classes = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L',
           'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V',
           'W', 'X', 'Y', 'Z', 'del', 'nothing', 'space']

    return Model.predict(classes, classifier, gesture)

"""VIDEO"""
def frame_video_stream(names, curr_char, prev_char, word, sentence, *args):
    kwargs = dict(zip(names, args))
    
    threshold = 0.97
    curr_char = curr_char
    prev_char = prev_char
    
    success, frame = cap.read()
    
    # Flip the image horizontally for a later selfie-view display, and convert
    frame = cv2.flip(frame, 1)
    frame = cv2.resize(frame, (700, 700))
    
    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    update_frame(image, kwargs['vid_label'])
    
    image.flags.writeable = False
    results = kwargs['hands'].process(image)

    # Draw the hand annotations on the image.
    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    image_height, image_width, _ = image.shape

    if results.multi_hand_landmarks:
        
        for hand_landmarks in results.multi_hand_landmarks:
            x = [landmark.x for landmark in hand_landmarks.landmark]
            y = [landmark.y for landmark in hand_landmarks.landmark]

            
            center = np.array([np.mean(x) * image_width, np.mean(y) * image_height]).astype('int32')
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            cropped_img, full_img = draw_region(image, center)

            update_frame(full_img, kwargs['vid_label'])

            try:
                # Transform the cropped hand into gray image
                gray = cv2.cvtColor(cropped_img, cv2.COLOR_BGR2GRAY)
                gray = DataGatherer().edge_detection(gray)

                # We obtain the char prediction and its prob
                curr_char, pred = get_char(gray)
                
                # We show the prediction and its probability
                char = cv2.putText(full_img, curr_char, (center[0]-135, center[1]-135), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
                char_prob = cv2.putText(full_img, '{0:.2f}'.format(np.max(pred)), (center[0]+60, center[1]-135), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)

                update_frame(full_img, kwargs['vid_label'])

                kwargs['cc_box'].delete('1.0', 'end')
                kwargs['cc_box'].insert('end', curr_char)


                # compare the current char with the previous one and if matched, then won't add the current char
                # also we use the threshold to prevent the meaningless characters to be added to the word
                if (curr_char != prev_char) and (np.max(pred) > threshold):
                    
                    # save the curr char in the complete word
                    temp = AddCharToWord(word, curr_char)
                    
                    
                    if (temp[0] == "") and (temp[1] != "del"):
                        corrected_word = Auto_Correct(word) 
                        sentence += corrected_word + " "
                        kwargs['sent_box'].insert('end', corrected_word + " ")
                        kwargs['ow_box'].delete('1.0', 'end')
                        kwargs['cw_box'].delete('1.0', 'end')
                        kwargs['cw_box'].insert('end', corrected_word)
                    word = temp[0]
                    kwargs['ow_box'].delete('1.0', 'end')
                    kwargs['ow_box'].insert('end', word)

                    prev_char = curr_char
            except:
                print("Algo salio mal")
                pass
    kwargs['vid_label'].after(1, frame_video_stream, names, curr_char, prev_char, word, sentence, *args)


def pipe_cam(vid_label):
    
    curr_char = None
    prev_char = None
    word = ""
    sentence = ""
    
    # Threshold for the word accuracy
    threshold = float(0.98)

    # Probability format
    float_formatter = "{:.5f}".format
    np.set_printoptions(formatter={'float_kind':float_formatter})
    
    # Videoa capture
    global cap
    cap = cv2.VideoCapture(0)

    # GUI characteristics
    labels_num = 5
    labels = ['UMBRAL', 'LETRA DETECTADA', 'PALABRA ORIGINAL', 'PALABRA CORREGIDA', 'ORACION']

    #Labels, entryboxes = gui.create_labels(labels_num, labels, 'nw', 0, 0, y_spacing=0.1, #create_entrybox_per_label=1)

    """  entryboxes['PALABRA ORIGINAL_entrybox'].config(width=18)
    entryboxes['PALABRA CORREGIDA_entrybox'].config(width=18)
    entryboxes['ORACION_entrybox'].config(width=18, height=8)
    entryboxes['UMBRAL_entrybox'].insert('end', threshold)
    
    th_entrybox = entryboxes['UMBRAL_entrybox']
    cc_entrybox = entryboxes['LETRA DETECTADA_entrybox']
    ow_entrybox = entryboxes['PALABRA ORIGINAL_entrybox']
    cw_entrybox = entryboxes['PALABRA CORREGIDA_entrybox']
    sent_entrybox = entryboxes['ORACION_entrybox'] """

    #Exit_program_btn = gui.create_buttons(1, ['SALIR'], 'center', 0.5, 0.9, command=lambda: exit_app(gui, #cap))

    names = ['vid_label', 'hands', 'cc_box',  'sent_box']
    
    with mp_hands.Hands(min_detection_confidence=0.4, min_tracking_confidence=0.5, max_num_hands=1) as hands:
        
            frame_video_stream(names, curr_char, prev_char, word, sentence, vid_label,
                               hands, letra_detectada, sent_entrybox)
            
            window.mainloop()
            

def create_frame(width, height, anchor, relx, rely, background='white'):
        global window
        frame = Frame(window, bg=background, width=width, height=height)
        frame.place(anchor=anchor, relx=relx, rely=rely)
        return frame

window = Tk()

window.geometry("1138x720")
window.configure(bg = "#F5FDF8")



canvas = Canvas(
    window,
    bg = "#F5FDF8",
    height = 720,
    width = 1138,
    bd = 0,
    highlightthickness = 0,
    relief = "ridge"
)


canvas.place(x = 0, y = 0)



image_image_1 = PhotoImage(
    file=relative_to_assets("image_1.png"))

gui_frame = create_frame(700, 700, 'ne', 1, 0, 'green')
vid_label = Label(gui_frame)
vid_label.grid()

xd = canvas.create_image(
    821.6666259765625,
    296.0,
    image=image_image_1
)

entry_image_1 = PhotoImage(
    file=relative_to_assets("entry_1.png"))
entry_bg_1 = canvas.create_image(
    316.7642364501953,
    357.955322265625,
    image=entry_image_1
)
sent_entrybox = Text(
    bd=0,
    bg="#FFFFFF",
    fg="#000716",
    highlightthickness=0
)
sent_entrybox.place(
    x=165.756103515625,
    y=27.0,
    width=302.0162658691406,
    height=659.91064453125
)

canvas.create_text(
    164.60975646972656,
    70.25201416015625,
    anchor="nw",
    text="Tu mensaje aparecera aqui...\n",
    fill="#858383",
    font=("Inter", 16 * -1)
)

canvas.create_rectangle(
    566.0,
    608.0,
    1080.0,
    692.0,
    fill="#B80090",
    outline="")

canvas.create_text(
    583.0,
    633.0,
    anchor="nw",
    text="Palabra detectada: ",
    fill="#FFFFFF",
    font=("OpenSansRoman CondensedBold", 32 * -1)
)

letra_detectada = canvas.create_text(
    952.0,
    626.0,
    anchor="nw",
    text="A",
    fill="#FFFFFF",
    font=("OpenSansRoman CondensedBold", 36 * -1)
)

canvas.create_rectangle(
    14.0,
    27.0,
    95.86991882324219,
    688.91064453125,
    fill="#FFFFFF",
    outline="")

button_image_1 = PhotoImage(
    file=relative_to_assets("button_1.png"))
button_1 = Button(
    image=button_image_1,
    borderwidth=0,
    highlightthickness=0,
    command=lambda: print("button_1 clicked"),
    relief="flat"
)
button_1.place(
    x=25.0,
    y=41.0,
    width=62.0,
    height=104.0
)

button_image_2 = PhotoImage(
    file=relative_to_assets("button_2.png"))
button_2 = Button(
    image=button_image_2,
    borderwidth=0,
    highlightthickness=0,
    command=lambda: print("button_2 clicked"),
    relief="flat"
)
button_2.place(
    x=32.536590576171875,
    y=264.11376953125,
    width=48.658538818359375,
    height=54.83740234375
)

button_image_3 = PhotoImage(
    file=relative_to_assets("button_3.png"))
button_3 = Button(
    image=button_image_3,
    borderwidth=0,
    highlightthickness=0,
    command=lambda: print("button_3 clicked"),
    relief="flat"
)
button_3.place(
    x=30.219512939453125,
    y=343.6666259765625,
    width=48.658538818359375,
    height=54.83740234375
)

button_image_4 = PhotoImage(
    file=relative_to_assets("button_4.png"))
button_4 = Button(
    image=button_image_4,
    borderwidth=0,
    highlightthickness=0,
    command=lambda: print("button_4 clicked"),
    relief="flat"
)
button_4.place(
    x=30.99188232421875,
    y=410.86181640625,
    width=48.658538818359375,
    height=54.83740234375
)

button_image_5 = PhotoImage(
    file=relative_to_assets("button_5.png"))
button_5 = Button(
    image=button_image_5,
    borderwidth=0,
    highlightthickness=0,
    command=lambda: print("button_5 clicked"),
    relief="flat"
)
button_5.place(
    x=30.99188232421875,
    y=626.349609375,
    width=48.658538818359375,
    height=54.83740234375
)

pipe_cam(vid_label)
window.resizable(False, False)
window.mainloop()