from . import handle_filenames as hf


def attach_missing_ids(file_name_list):
    """Generates a list of commands to attach missing ids by renaming files

    :param file_name_list: List of files in a given directory which might
        contain filenames with missing ids.
    :type file_name_list: list of strings
    :return: list of commands. Each command is a list with three components.
        the command (i.e. rename), the old filename and the new filename.
    :rtype: list of list of strings
    """
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
