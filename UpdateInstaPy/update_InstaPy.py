import os
import re
import json
from shutil import copyfile

# Settings
##############################################
requirements_location = '../App/requirements.txt'
requirements_location_backup = '../App/requirements.txt_backup'
copyfile(requirements_location, requirements_location_backup)
instapy_requirements_location = '../InstaPy/requirements.txt'
requirement_line_regex = '(.*?)[<>=]{2}(.*)'
##############################################


# All functions
##############################################

# Do git
#def do_git():


# Compare versions x.x.x....
def get_latest_version(version_1='', version_2=''):
    latest_version = None
    if version_1 == version_2:
        return version_1
    if version_1 == '':
        return version_2
    if version_2 == '':
        return version_1
    _version_1 = version_1.split('.')
    _version_2 = version_2.split('.')
    len1 = len(_version_1)
    len2 = len(_version_2)
    version_len = len1 if len1 <= len2 else len2
    i = 0
    while i < version_len:
        number_1 = int(_version_1[i])
        number_2 = int(_version_2[i])
        if number_1 > number_2:
            latest_version = version_1
            break
        elif number_1 < number_2:
            latest_version = version_2
            break
        i = i + 1
    if latest_version is None:
        latest_version = version_2 if len1 < len2 else version_1
    return latest_version

# Make dict from requirements file
def requirements_to_dict(file_lines):
    p = re.compile(requirement_line_regex)
    result = {}
    for line in file_lines:
        error_line = 'Failed to match dependency: {}'.format(line)
        m = p.match(line)
        if m is None:
            print('{}, m = {}'.format(error_line, m))
            continue
        groups = m.groups()
        if len(groups) < 2:
            print('{}, groups = {}'.format(error_line, len(groups)))
            continue
        dependency = groups[0]
        version = groups[1]
        if not dependency or dependency == '' or not version or version == '':
            print('{}, d = {}, v = {}'.format(error_line, dependency, version))
            continue
        result[dependency] = version
    if len(result) != len(file_lines):
        print('ERROR: Some line had errors')
        exit()
    return result

# Read file
def read_file(file_path):
    data_to_return = []
    file_location = os.path.join(file_path)
    if not os.path.exists(file_location):
        print('{} doesn\' exist'.format(file_path))
        return data_to_return
    try:
        with open(file_location, 'r') as file_object:
            data_to_return = file_object.read().splitlines()
    except Exception as exc:
        print('Failed to open or read the file {}'.format(file_path))
    return data_to_return

# Check requirements
def get_final_latest_requirements(requirements_1_lines, requirements_2_lines):
    latest_requirements = {}
    requirements_1_dict = requirements_to_dict(requirements_1_lines)
    requirements_2_dict = requirements_to_dict(requirements_2_lines)
    for requirement, version in requirements_1_dict.items():
        version_1 = version
        version_2 = requirements_2_dict.get(requirement, '')
        latest_requirements[requirement] = get_latest_version(version_1, version_2)
    for requirement, version in requirements_2_dict.items():
        if requirement in latest_requirements:
            continue
        version_1 = version
        version_2 = requirements_1_dict.get(requirement, '')
        latest_requirements[requirement] = get_latest_version(version_1, version_2)
    return latest_requirements

def write_to_file(file_path, lines):
    file_location = os.path.join(file_path)
    if not os.path.exists(file_location):
        print('{} doesn\'t exist'.format(file_path))
        return data_to_return
    try:
        with open(file_location, 'w+') as file_object:
            file_object.write('\n'.join(lines) + '\n')
    except Exception as exc:
        print('Failed to open the file {} for writing'.format(file_path))

def write_new_requirements(latest_requirements):
    new_lines = []
    for requirement, version in latest_requirements.items():
        new_lines.append('{}=={}'.format(requirement, version))
    new_lines = sorted(new_lines, key=lambda s: s.lower())
    write_to_file(requirements_location, new_lines)

def comment_out_stuff():
    # - comment the line "from .clarifai_util import check_image"
    pass
##############################################

def update_requirements_from_instapy():
    requirements_lines = read_file(requirements_location)
    instapy_requirements_lines = read_file(instapy_requirements_location)
    latest_requirements = get_final_latest_requirements(requirements_lines, instapy_requirements_lines)
    write_new_requirements(latest_requirements)

def start():
    update_requirements_from_instapy()

start()
print('Done')


