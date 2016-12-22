import Image
import subprocess

import util
import errors

tesseract_exe_name = "tesseract" # Name of executable to be called at command line
scratch_image_name = "temp.bmp" # This file must be .bmp or other Tesseract-compatible format
scratch_text_name_root = "temp" # Leave out the .txt extension
cleanup_scratch_flag = False  # Temporary files cleaned up after OCR operation

def call_tesseract(input_filename, output_filename, bool_digits=False):
    """Calls external tesseract.exe on input file (restrictions on types),
    outputting output_filename+'txt'"""
    # args = [tesseract_exe_name, input_filename, output_filename]
    if bool_digits:
        # args = tesseract_exe_name+" "+input_filename+" "+output_filename+" -l eng -psm 7 nobatch eng_digits" # price
        args = tesseract_exe_name+" "+input_filename+" "+output_filename+" -l test_digits -psm 7 nobatch" # price
    else:
        args = tesseract_exe_name+" "+input_filename+" "+output_filename+" -l eng -psm 7 nobatch eng_characters" # English letters
        # args = tesseract_exe_name+" "+input_filename+" "+output_filename+" -l test_eng -psm 7 nobatch" # English letters
    # print args
    proc = subprocess.Popen(args, shell=True)
    retcode = proc.wait()
    if retcode != 0:
        errors.check_for_errors()

def image_to_string(im, cleanup = cleanup_scratch_flag, bool_digits=False):
    """Converts im to file, applies tesseract, and fetches resulting text.
    If cleanup=True, delete scratch files after operation."""
    try:
        util.image_to_scratch(im, scratch_image_name)
        call_tesseract(scratch_image_name, scratch_text_name_root, bool_digits)
        text = util.retrieve_text(scratch_text_name_root)
    finally:
        if cleanup:
            util.perform_cleanup(scratch_image_name, scratch_text_name_root)
    return text

def image_file_to_string(filename, cleanup = cleanup_scratch_flag, graceful_errors=True, bool_digits=False):
    """Applies tesseract to filename; or, if image is incompatible and graceful_errors=True,
    converts to compatible format and then applies tesseract.  Fetches resulting text.
    If cleanup=True, delete scratch files after operation."""
    try:
        try:
            call_tesseract(filename, scratch_text_name_root, bool_digits)
            text = util.retrieve_text(scratch_text_name_root)
        except errors.Tesser_General_Exception:
            if graceful_errors:
                im = Image.open(filename)
                text = image_to_string(im, cleanup, bool_digits)
            else:
                raise
    finally:
        if cleanup:
            util.perform_cleanup(scratch_image_name, scratch_text_name_root)
    return text
