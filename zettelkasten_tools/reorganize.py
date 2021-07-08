from . import handle_filenames as hf


def attach_missing_ids(file_name_list):
    command_list = []
    for filename in file_name_list:
        components = hf.get_filename_components(filename)
        if components[2] == '':
            oldfilename = filename
            file_id = hf.generate_id(filename)
            newfilename = components[0] + '_' + components[1][:-3] + \
                '_' + file_id + '.md'
            command_list.append(['rename', oldfilename, newfilename])
    return command_list
