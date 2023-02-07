import os
import subprocess
import shutil
import pymeshlab as ml
import dearpygui.dearpygui as dpg

ms = ml.MeshSet()
pathToCompressonator = "compressonator\\"

path_to_input_sequence = ""
path_to_output_sequence = ""
last_image_path = ""
last_model_path = ""

input_sequence_list_models = []
input_sequence_list_images = []

is_pointcloud = False
input_valid = False
output_valid = False
is_running = False
is_stopped = False

image_processed_Index = 0
model_processed_Index = 0
total_file_count = 0

valid_model_types = ["obj", "3ds", "fbx", "glb", "gltf", "obj", "ply", "ptx", "stl", "xyz", "pts"]
valid_image_types = ["jpg", "jpeg", "png", "tiff", "dds", "bmp", "tga"]


def setup_converter():

    global is_running
    global total_file_count
    global model_processed_Index
    global image_processed_Index

    if(is_running == True):
        return False

    dpg.set_value(text_error_log_ID, "")
    dpg.set_value(text_info_log_ID, "")

    if(input_valid == False):
        dpg.set_value(text_error_log_ID, "Input files are not configured correctly")
        return False

    if(output_valid == False):
        dpg.set_value(text_error_log_ID, "Output folder is not configured correctly")
        return False

    dpg.set_value(progress_bar_ID, 0)

    model_processed_Index = 0
    image_processed_Index = 0
    total_file_count = len(input_sequence_list_images) + len(input_sequence_list_models)
    is_running = True



def convert_model(file):

    global is_pointcloud

    splitted_file = file.split(".")
    splitted_file.pop() # We remove the last element, which is the file ending
    file_name = ''.join(splitted_file)

    inputfile = path_to_input_sequence + "\\"+ file
    outputfile =  path_to_output_sequence + "\\" + file_name + ".ply"

    print(inputfile)
    print(outputfile)

    ms.load_new_mesh(inputfile)

    faceCount = len(ms.current_mesh().face_matrix())

    #File is a pointcloud
    if(faceCount == 0):
        ms.save_current_mesh(file_name=outputfile, binary=True, save_vertex_quality=False, save_vertex_color=True, save_vertex_coord=True, save_vertex_normal=False, save_vertex_radius=False, 
        save_face_quality=False, save_face_flag=False, save_face_color=False, save_wedge_color=False, save_wedge_texcoord=False, save_wedge_normal=False)
        
    #File is a mesh        
    else:
        if(ms.current_mesh().has_wedge_tex_coord == True):
            ms.current_mesh().compute_texcoord_transfer_wedge_to_vertex()

        ms.meshing_poly_to_tri()
        ms.save_current_mesh(file_name=outputfile, binary=True, save_vertex_quality=False, save_vertex_color=False, save_vertex_coord=True, save_vertex_normal=False, save_vertex_radius=False, 
        save_face_quality=False, save_face_flag=False, save_face_color=False, save_wedge_color=False, save_wedge_texcoord=False, save_wedge_normal=False, save_textures=False)
        

def convert_image(file):

    global last_image_path

    splitted_file = file.split(".")
    splitted_file.pop() # We remove the last element, which is the file ending
    file_name = ''.join(splitted_file)

    inputfile = path_to_input_sequence + "\\"+ file
    outputfile =  path_to_output_sequence + "\\" + file_name + ".dds"

    print(inputfile)
    print(outputfile)

    cmd = pathToCompressonator + "CompressonatorCLI.exe -fd DXT1 -EncodeWith GPU " + inputfile + " " + outputfile

    return_code = subprocess.call(cmd, shell=True)

    if(return_code != 0):
        shutil.copy2(last_image_path, outputfile) 

    else:
        last_image_path = outputfile



def validate_input_files(input_path):

        if(os.path.exists(input_path) == False):
            return "Folder does not exist!"

        files = os.listdir(input_path)
        print(input_path)
        
        #Sort the files into model and images
        for file in files:
            splitted_path = file.split(".")
            file_ending = splitted_path[len(splitted_path) - 1]

            if(file_ending in valid_model_types):
                input_sequence_list_models.append(file)
            
            elif(file_ending in valid_image_types):
                input_sequence_list_images.append(file)

        if(len(input_sequence_list_models) < 1 and len(input_sequence_list_images) < 1):
            return "No model/image files found in folder!"

        input_sequence_list_models.sort()
        input_sequence_list_images.sort()

        return True


#----------------------- UI Logic ---------------------------


#UI IDs for the DearPyGUI
text_input_Dir_ID = 0
text_output_Dir_ID = 0
text_error_log_ID = 0
text_info_log_ID = 0
progress_bar_ID = 0




dpg.create_context()

def input_files_confirm_callback(sender, app_data):

    global input_valid
    global path_to_input_sequence

    new_input_path = app_data["file_path_name"]
    input_valid = False

    dpg.set_value(text_error_log_ID, "")

    input_sequence_list_images.clear()
    input_sequence_list_models.clear()

    res = validate_input_files(new_input_path)

    if(res == True):
        path_to_input_sequence = new_input_path
        dpg.set_value(text_input_Dir_ID, path_to_input_sequence)
        dpg.set_value(text_info_log_ID, "Input files set!")
        input_valid = True

    else:
        path_to_input_sequence = ""
        input_valid = False
        dpg.set_value(text_info_log_ID, "")
        dpg.set_value(text_error_log_ID, res)



def output_files_confirm_callback(sender, app_data):

    global output_valid
    global path_to_output_sequence

    new_output_path = app_data["file_path_name"]
    output_valid = False

    dpg.set_value(text_info_log_ID, "")
    dpg.set_value(text_error_log_ID, "")


    if(os.path.exists(new_output_path) == True):
        path_to_output_sequence = new_output_path
        dpg.set_value(text_output_Dir_ID, path_to_output_sequence)
        dpg.set_value(text_info_log_ID, "Output folder set!")
        output_valid = True

    else:
        path_to_output_sequence = ""
        dpg.set_value(text_info_log_ID, "")
        dpg.set_value(text_error_log_ID, "Error: Output directory is not valid!")
        output_valid = False

def cancel_processing_callback():
    global is_stopped
    is_stopped = True

def show_input():
    dpg.show_item("file_input_dialog_id")
    dpg.set_item_pos(item="file_input_dialog_id", pos=[0,0])

def show_output():
    dpg.show_item("file_output_dialog_id")
    dpg.set_item_pos(item="file_output_dialog_id", pos=[0,0])


dpg.create_viewport(height=500, width=500, title="Geometry Sequence Converter")
dpg.setup_dearpygui()

with dpg.window(label="Geometry Sequence Converter", tag="main_window", min_size= [500, 500]):
    
    dpg.add_file_dialog(directory_selector=True, show=False, callback=input_files_confirm_callback, tag="file_input_dialog_id", min_size=[500, 430])
    dpg.add_file_dialog(directory_selector=True, show=False, callback=output_files_confirm_callback, tag="file_output_dialog_id", min_size=[500, 430], default_path=path_to_input_sequence)

    dpg.add_text("Input sequence folder:")
    dpg.add_same_line()
    dpg.add_button(label="Select folder", callback=lambda:show_input())
    text_input_Dir_ID = dpg.add_text(path_to_input_sequence, wrap=500)
    dpg.add_spacer()

    dpg.add_text("Output sequence folder:")
    dpg.add_same_line()
    dpg.add_button(label="Select folder", callback=lambda:show_output())
    text_output_Dir_ID = dpg.add_text(path_to_output_sequence, wrap=500)
    dpg.add_spacer()

    dpg.add_text("Progress:")
    dpg.add_same_line()
    progress_bar_ID = dpg.add_progress_bar(default_value=0, width=400)
    dpg.add_spacer(height=10)
    dpg.add_button(label="Start", callback=lambda:setup_converter())
    dpg.add_same_line()
    dpg.add_button(label="Cancel", callback=lambda:cancel_processing_callback())
    dpg.add_spacer(height=20)

    text_error_log_ID = dpg.add_text("", color=[255, 0, 0], wrap=500)
    dpg.add_same_line()
    text_info_log_ID = dpg.add_text("", color=[255, 255, 255], wrap=500)

dpg.show_viewport()
dpg.set_primary_window("main_window", True)

while dpg.is_dearpygui_running():
    
    if(is_running):

        if(image_processed_Index < len(input_sequence_list_images)):
            convert_image(input_sequence_list_images[image_processed_Index])
            image_processed_Index += 1

        if(model_processed_Index < len(input_sequence_list_models)):
            convert_model(input_sequence_list_models[model_processed_Index])
            model_processed_Index += 1

        processed_file_count = image_processed_Index + model_processed_Index
        dpg.set_value(progress_bar_ID, processed_file_count / total_file_count)

        if(processed_file_count == total_file_count):
            is_running = False
            dpg.set_value(text_info_log_ID, "Finished!")
            dpg.set_value(progress_bar_ID, 0)

    if(is_stopped):
        is_running = False
        is_stopped = False
        dpg.set_value(text_info_log_ID, "Canceled!")
        dpg.set_value(progress_bar_ID, 0)


    dpg.render_dearpygui_frame()

dpg.destroy_context()
