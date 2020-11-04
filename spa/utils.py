import importlib
import shutil

from django.core.exceptions import ObjectDoesNotExist
from django.utils.safestring import mark_safe

import main.models

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
import ast, json, os, random, string
import os.path
import filecmp
from PIL import Image
from django.utils.module_loading import import_string
from django.core.files.storage import default_storage, FileSystemStorage
from spa import settings
from main.const import IMG_EXT_WITH_DOT, IMAGE_SIZES, MAX_SIZE_UPLOADED, IMAGE_SIZES_INDEX, \
    MAX_SIZE_PRO_IMAGES, IMGCON_TYPES, IMAGE_SIZES_W, IMAGE_SIZES_H, MODE_SAVE_IMG_ZIP0
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.core.serializers.json import DjangoJSONEncoder
from cryptography.fernet import Fernet


# all image is save has ext = jpg
def handle_proccess_photo(file, obj, field, name, folder):
    if file == '' or obj.CONST_TYPE is None:
        return False
    if folder is None or not isinstance(folder, str):
        folder = obj.CONST_TYPE
    path = settings.MEDIA_ROOT + '/' + folder
    try:
        os.makedirs(path, exist_ok=True)
    except OSError:
        pass
    img = Image.open(file)
    if img.mode not in ('L', 'RGB'):
        img = img.convert('RGB')
    width, height = img.size  # Get dimensions
    # get orginal image ratio
    img_ratio = float(width) / height
    if img_ratio >= 1:
        sizes = IMAGE_SIZES_W
    else:
        sizes = IMAGE_SIZES_H
    for _size in sizes:
        size = sizes[_size]
        (x, y) = size
        real_ratio = x / y
        new_img = img.copy()
        if almost_equal(real_ratio, img_ratio):
            if width > x and height > y:
                new_img.thumbnail((x, y))
            else:
                new_img = new_img.resize((x, y), Image.ANTIALIAS)
        elif almost_gt(real_ratio, img_ratio):  # height of image > normal image
            real_height = (width * y) / x
            move_height = int((height - real_height) / 2)
            (left, top, right, bottom) = (0, move_height, width, height - move_height)
            new_img = new_img.crop((left, top, right, bottom))
            new_img = new_img.resize((x, y), Image.ANTIALIAS)
        else:
            real_width = (height * x) / y
            move_width = int((width - real_width) / 2)
            (left, top, right, bottom) = (move_width, 0, width - move_width, height)
            new_img = new_img.crop((left, top, right, bottom))
            new_img = new_img.resize((x, y), Image.ANTIALIAS)
        filename = name + "_{}x{}.".format(x, y) + 'jpg'
        full_path = path + "/" + filename
        if default_storage.exists(full_path):
            default_storage.delete(full_path)
        new_img.save(full_path)


def proccess_photo(request, obj, mode=MODE_SAVE_IMG_ZIP0):
    for i in range(1, MAX_SIZE_PRO_IMAGES):
        field = "file{}".format(i)
        xxx = request.FILES[field] if field in request.FILES else False
        if xxx and xxx != '' and obj.CONST_TYPE is not None and xxx.content_type in IMGCON_TYPES:
            folder = "{}/{}".format(obj.CONST_TYPE, obj.pk)
            # check files in folder. if >= max files is force exist
            path = settings.MEDIA_ROOT + '/' + folder
            if sum(len(files) for _, _, files in os.walk(path)) >= MAX_SIZE_PRO_IMAGES * len(IMAGE_SIZES_INDEX):
                break
            name = str(1) if mode is None or mode == MODE_SAVE_IMG_ZIP0 else str(i)
            handle_proccess_photo(xxx, obj, field, name, folder)

    file = request.FILES['file'] if 'file' in request.FILES else False
    if not file or file == '' or obj.CONST_TYPE is None or file.content_type not in IMGCON_TYPES:
        return False
    img = Image.open(file)
    if img.mode not in ('L', 'RGB'):
        img = img.convert('RGB')
    width, height = img.size  # Get dimensions
    # get orginal image ratio
    img_ratio = float(width) / height
    sizes = IMAGE_SIZES
    ext = 'jpg'
    path = settings.MEDIA_ROOT + '/' + obj.CONST_TYPE
    try:
        os.makedirs(path, exist_ok=True)
    except OSError:
        pass
    for size in sizes:
        new_img = img.copy()
        (x, y) = size
        real_ratio = x / y
        if almost_equal(real_ratio, img_ratio):
            if width > x and height > y:
                # keep ratio but shrink down
                new_img.thumbnail((x, y))
            else:
                new_img = new_img.resize((x, y), Image.ANTIALIAS)
        elif almost_gt(real_ratio, img_ratio):  # height of image > normal image
            real_height = (width * y) / x
            move_height = int((height - real_height) / 2)
            (left, top, right, bottom) = (0, move_height, width, height - move_height)
            new_img = new_img.crop((left, top, right, bottom))
            new_img = new_img.resize((x, y), Image.ANTIALIAS)
        else:
            real_width = (height * x) / y
            move_width = int((width - real_width) / 2)
            (left, top, right, bottom) = (move_width, 0, width - move_width, height)
            new_img = new_img.crop((left, top, right, bottom))
            new_img = new_img.resize((x, y), Image.ANTIALIAS)
        filename = str(obj.pk) + "_{}x{}.".format(x, y) + ext
        full_path = path + '/' + filename
        if default_storage.exists(full_path):
            default_storage.delete(full_path)
        new_img.save(full_path)
        if x == 640 or y == 480:
            filename = "{}.{}".format(str(obj.pk), ext)
            full_path = path + '/' + filename
            if default_storage.exists(full_path):
                default_storage.delete(full_path)
            new_img.save(full_path)
        # r=root, d=directories, f = files
        for r, d, f in os.walk(path):
            for _file in f:
                thumb = str(obj.pk) + "_{}x{}.".format(x, y)
                no_thumb = str(obj.pk) + "."
                if ((thumb in _file) or (no_thumb in _file)) and (ext not in _file) and os.path.exists(r + _file):
                    os.remove(r + _file)


def encrypt(message: bytes, key: bytes) -> bytes:
    return Fernet(key).encrypt(message)


def decrypt(token: bytes, key: bytes) -> bytes:
    return Fernet(key).decrypt(token)


# First we create a little helper function, becase we will potentially have many PaginatedTypes
# and we will potentially want to turn many querysets into paginated results:
def get_paginator(qs, page_size, page, paginated_type, **kwargs):
    p = Paginator(qs, page_size)
    try:
        page_obj = p.page(page)
    except PageNotAnInteger:
        page_obj = p.page(1)
    except EmptyPage:
        page_obj = p.page(p.num_pages)
    return paginated_type(
        page=page_obj.number,
        pages=p.num_pages,
        has_next=page_obj.has_next(),
        has_prev=page_obj.has_previous(),
        objects=page_obj.object_list,
        **kwargs
    )


def almost_gt(a, b, decimal=2):
    return '{0:.{1}f}'.format(a, decimal) > '{0:.{1}f}'.format(b, decimal)


def almost_equal(a, b, decimal=2):
    return '{0:.{1}f}'.format(a, decimal) == '{0:.{1}f}'.format(b, decimal)


def almost_lt(a, b, decimal=2):
    return '{0:.{1}f}'.format(a, decimal) < '{0:.{1}f}'.format(b, decimal)


def rand_word(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))


def to_python(value):
    if value == "":
        return None
    try:
        if isinstance(value, str):
            return json.loads(json.dumps(value, sort_keys=True, indent=4))
    except ValueError:
        pass
    return value


def from_db_value(self, value, *args):
    return self.to_python(value)


def get_db_prep_save(self, value, *args, **kwargs):
    if value == "":
        return None
    if isinstance(value, dict):
        value = json.dumps(value, cls=DjangoJSONEncoder)
    return value


def convert_list_to_string(org_list, seperator=' '):
    """ Convert list to string, by joining all item in list with given separator.
        Returns the concatenated string """
    return seperator.join(org_list)


def is_json(value):
    result = True
    try:
        json_object = json.loads(json.dumps(value, sort_keys=True, indent=4))
        if isinstance(json_object, str):
            json_object = ast.literal_eval(json_object)
        if not isinstance(json_object, dict):
            result = False
    except ValueError as e:
        result = False
    return result


def get_list(vals, result):
    if isinstance(result, list):
        result = []
    for v in vals:
        if isinstance(v, list):
            result = get_list(v, result)  # result.extend(get_list(v))
        else:
            if v not in result:
                result.append(v)
    return result


# var: is value to add some positions of result
def add_to_list(variant, max_col, max_list, point, result):
    try:
        if point >= max_list:
            return result
        _item = result[str(point)]
        if not isinstance(_item, list):
            _item = []
        if variant not in _item:
            _item.append(variant)
        result[str(point)] = _item
    except IndexError:
        pass
    point += max_col
    if point >= max_list:
        return result
    else:
        return add_to_list(variant, max_col, max_list, point, result)


# Function to check if an array is sub array of another array
def isSubArray(list_of_parent, list_of_child):
    (n, m) = (len(list_of_parent), len(list_of_child))
    # Two pointers to traverse the arrays
    (i, j) = (0, 0)
    # Traverse both arrays simultaneously
    while i < n and j < m:
        # If element matches
        # increment both pointers
        if list_of_parent[i] == list_of_child[j]:
            i += 1
            j += 1
            # If array B is completely
            # traversed
            if j == m:
                return True
            # If not,
        # increment i and reset j
        else:
            i = i - j + 1
            j = 0
    return False


def generate_uuid4_filename(filename):
    letters = string.ascii_lowercase
    basename = ''.join(random.choice(letters) for i in range(6))
    discard, ext = os.path.splitext(filename)
    return u'{0}{1}'.format(basename, ext)


def generate_slug(length=3):
    letters = string.ascii_lowercase
    basename = ''.join(random.choice(letters) for i in range(length))
    return u'{0}'.format(basename)


def generate_number(length=3):
    letters = string.ascii_lowercase
    basename = ''.join(random.choice(letters) for i in range(length))
    return u'{0}'.format(basename)


# CKEditor localization mapping


CKEDITOR_LOCALE_MAP = {
    'en-us': 'en',
    'vi': 'vi',
}


def get_ckeditor_language():
    """ Returns the UI language localization to be used with CKEditor """
    default_language_code = settings.LANGUAGE_CODE
    default_plugin_language = CKEDITOR_LOCALE_MAP.get(default_language_code, default_language_code)
    return default_plugin_language


# Allow for a custom storage backend defined in settings.
def get_storage_class():
    return import_string(getattr(settings, 'CKEDITOR_STORAGE_BACKEND', 'django.core.files.storage.DefaultStorage'))()


storage = get_storage_class()


# all image is save has ext = jpg
def handle_photo_formset(file, obj, name, folder):
    if file is None or file == '' or obj.CONST_TYPE is None:
        return False
    path = settings.MEDIA_ROOT + '/' + folder
    try:
        os.makedirs(path, exist_ok=True)
    except OSError:
        pass
    img = Image.open(file)
    if img.mode not in ('L', 'RGB'):
        img = img.convert('RGB')
    ext = 'jpg'
    width, height = img.size  # Get dimensions
    # get orginal image ratio
    img_ratio = float(img.size[0]) / img.size[1]
    (x, y) = IMAGE_SIZES_INDEX['big'] if img_ratio >= float(1) else IMAGE_SIZES_INDEX['hbig']
    real_ratio = x / y
    # define file output dimensions (ex 320x240)
    if almost_equal(real_ratio, img_ratio):
        if width > x and height > y:
            # keep ratio but shrink down
            img.thumbnail((x, y))
        else:
            img = img.resize((x, y), Image.ANTIALIAS)
    elif almost_gt(real_ratio, img_ratio):  # height of image > normal image
        real_height = (width * y) / x
        move_height = int((height - real_height) / 2)
        (left, top, right, bottom) = (0, move_height, width, height - move_height)
        img = img.crop((left, top, right, bottom))
        img = img.resize((x, y), Image.ANTIALIAS)
    else:
        real_width = (height * x) / y
        move_width = int((width - real_width) / 2)
        (left, top, right, bottom) = (move_width, 0, width - move_width, height)
        img = img.crop((left, top, right, bottom))
        img = img.resize((x, y), Image.ANTIALIAS)
    filename = "{}_{}x{}.{}".format(str(obj.pk), x, y, ext)
    full_path = path + '/' + filename
    if default_storage.exists(full_path):
        default_storage.delete(full_path)
    img.save(full_path)
    # r=root, d=directories, f = files
    for r, d, f in os.walk(path):
        for _file in f:
            thumb = str(obj.pk) + "_{}x{}.".format(x, y)
            no_thumb = str(obj.pk) + "."
            if ((thumb in _file) or (no_thumb in _file)) and (ext not in _file) and os.path.exists(r + _file):
                os.remove(r + _file)
    for size in IMAGE_SIZES_INDEX:
        (_x, _y) = IMAGE_SIZES_INDEX[size]
        new_img = img.copy()
        if _x == x or _y == y:
            continue
        else:
            filename = str(obj.pk) + "_{}x{}.".format(_x, _y) + ext
            resized_image = new_img.resize(IMAGE_SIZES_INDEX[size], Image.ANTIALIAS)
            full_path = path + '/' + filename
            if default_storage.exists(full_path):
                default_storage.delete(full_path)
            resized_image.save(full_path)


def save_photo_formset(data, obj):
    for i in range(1, MAX_SIZE_UPLOADED):
        field = "file{}".format(i)
        xxx = data[field] if field in data else False
        if xxx and obj.CONST_TYPE is not None:
            folder = "{}/{}".format(obj.CONST_TYPE, obj.pk)
            handle_photo_formset(xxx, obj, str(i), folder)

    file = data['file'] if 'file' in data else False
    # pdb.set_trace()
    if not file or file == '' or obj.CONST_TYPE is None:
        return False
    path = settings.MEDIA_ROOT + '/' + obj.CONST_TYPE
    try:
        os.makedirs(path, exist_ok=True)
    except OSError:
        pass

    img = Image.open(file)
    if img.mode not in ('L', 'RGB'):
        img = img.convert('RGB')
    ext = 'jpg'
    width, height = img.size  # Get dimensions
    # get orginal image ratio
    img_ratio = float(width) / height
    (x, y) = IMAGE_SIZES_INDEX['big'] if img_ratio >= float(1) else IMAGE_SIZES_INDEX['hbig']
    real_ratio = x / y
    # define file output dimensions (ex 320x240)
    if almost_equal(real_ratio, img_ratio):
        if width > x and height > y:
            # keep ratio but shrink down
            img.thumbnail((x, y))
        else:
            img = img.resize((x, y), Image.ANTIALIAS)
    elif almost_gt(real_ratio, img_ratio):  # height of image > normal image
        real_height = (width * y) / x
        move_height = int((height - real_height) / 2)
        (left, top, right, bottom) = (0, move_height, width, height - move_height)
        img = img.crop((left, top, right, bottom))
        img = img.resize((x, y), Image.ANTIALIAS)
    else:
        real_width = (height * x) / y
        move_width = int((width - real_width) / 2)
        (left, top, right, bottom) = (move_width, 0, width - move_width, height)
        img = img.crop((left, top, right, bottom))
        img = img.resize((x, y), Image.ANTIALIAS)
    filename = "{}_{}x{}.{}".format(str(obj.pk), x, y, ext)
    full_path = path + '/' + filename
    if default_storage.exists(full_path):
        default_storage.delete(full_path)
    img.save(full_path)
    filename = "{}.{}".format(str(obj.pk), ext)
    full_path = path + '/' + filename
    if default_storage.exists(full_path):
        default_storage.delete(full_path)
    img.save(full_path)
    # r=root, d=directories, f = files
    for r, d, f in os.walk(path):
        for _file in f:
            thumb = str(obj.pk) + "_{}x{}.".format(x, y)
            no_thumb = str(obj.pk) + "."
            if ((thumb in _file) or (no_thumb in _file)) and (ext not in _file) and os.path.exists(r + _file):
                os.remove(r + _file)
    for size in IMAGE_SIZES_INDEX:
        (_x, _y) = IMAGE_SIZES_INDEX[size]
        new_img = img.copy()
        if _x == x or _y == y:
            continue
        else:
            filename = str(obj.pk) + "_{}x{}.".format(_x, _y) + ext
            resized_image = new_img.resize(IMAGE_SIZES_INDEX[size], Image.ANTIALIAS)
            full_path = path + '/' + filename
            if default_storage.exists(full_path):
                default_storage.delete(full_path)
            resized_image.save(full_path)


def del_photo(request, obj):
    try:
        if obj.CONST_TYPE is None or obj.pk is None:
            return False
    except (ObjectDoesNotExist, IndexError, ValueError, TypeError, AttributeError):
        return False
    folder = "{}/{}".format(obj.CONST_TYPE, obj.pk)
    # check files in folder. if exist is force delete
    full_path = settings.MEDIA_ROOT + '/' + folder
    if default_storage.exists(full_path):
        shutil.rmtree(full_path)
        # default_storage.delete(full_path)
    folder = obj.CONST_TYPE
    path = settings.MEDIA_ROOT + '/' + folder
    if default_storage.exists(full_path):
        for ext in IMG_EXT_WITH_DOT:
            for sizes in IMAGE_SIZES:
                (x, y) = sizes
                filename = "{}_{}x{}{}".format(obj.pk, x, y, ext)
                full_path = path + "/" + filename
                if default_storage.exists(full_path):
                    default_storage.delete(full_path)
            filename = "{}{}".format(obj.pk, ext)
            full_path = path + "/" + filename
            if default_storage.exists(full_path):
                default_storage.delete(full_path)


def save_photo(request, obj):
    for i in range(1, MAX_SIZE_PRO_IMAGES):
        field = "file{}".format(i)
        xxx = request.FILES[field] if field in request.FILES else False
        if xxx and xxx != '' and obj.CONST_TYPE is not None and xxx.content_type in IMGCON_TYPES:
            folder = "{}/{}".format(obj.CONST_TYPE, obj.pk)
            # check files in folder. if >= max files is force exist
            path = settings.MEDIA_ROOT + '/' + folder
            if sum(len(files) for _, _, files in os.walk(path)) >= MAX_SIZE_PRO_IMAGES * len(IMAGE_SIZES_INDEX):
                break
            handle_uploaded_image(xxx, obj, field, str(i), folder)

    file = request.FILES['file'] if 'file' in request.FILES else False
    if not file or file == '' or obj.CONST_TYPE is None or file.content_type not in IMGCON_TYPES:
        return False
    img = Image.open(file)
    if img.mode not in ('L', 'RGB'):
        img = img.convert('RGB')
    width, height = img.size  # Get dimensions
    # get orginal image ratio
    img_ratio = float(width) / height
    sizes = IMAGE_SIZES
    ext = 'jpg'
    path = settings.MEDIA_ROOT + '/' + obj.CONST_TYPE
    try:
        os.makedirs(path, exist_ok=True)
    except OSError:
        pass
    for size in sizes:
        new_img = img.copy()
        (x, y) = size
        real_ratio = x / y
        if almost_equal(real_ratio, img_ratio):
            if width > x and height > y:
                # keep ratio but shrink down
                new_img.thumbnail((x, y))
            else:
                new_img = new_img.resize((x, y), Image.ANTIALIAS)
        elif almost_gt(real_ratio, img_ratio):  # height of image > normal image
            real_height = (width * y) / x
            move_height = int((height - real_height) / 2)
            (left, top, right, bottom) = (0, move_height, width, height - move_height)
            new_img = new_img.crop((left, top, right, bottom))
            new_img = new_img.resize((x, y), Image.ANTIALIAS)
        else:
            real_width = (height * x) / y
            move_width = int((width - real_width) / 2)
            (left, top, right, bottom) = (move_width, 0, width - move_width, height)
            new_img = new_img.crop((left, top, right, bottom))
            new_img = new_img.resize((x, y), Image.ANTIALIAS)
        filename = str(obj.pk) + "_{}x{}.".format(x, y) + ext
        full_path = path + '/' + filename
        if default_storage.exists(full_path):
            default_storage.delete(full_path)
        new_img.save(full_path)
        if x == 640 or y == 480:
            filename = "{}.{}".format(str(obj.pk), ext)
            full_path = path + '/' + filename
            if default_storage.exists(full_path):
                default_storage.delete(full_path)
            new_img.save(full_path)
        # r=root, d=directories, f = files
        for r, d, f in os.walk(path):
            for _file in f:
                thumb = str(obj.pk) + "_{}x{}.".format(x, y)
                no_thumb = str(obj.pk) + "."
                if ((thumb in _file) or (no_thumb in _file)) and (ext not in _file) and os.path.exists(r + _file):
                    os.remove(r + _file)


def handle_check_image_folder(request, obj, field, name, folder):
    pass


# all image is save has ext = jpg
def handle_uploaded_image(file, obj, field, name, folder):
    if file == '' or obj.CONST_TYPE is None:
        return False
    sizes = IMAGE_SIZES
    if folder is None or not isinstance(folder, str):
        folder = obj.CONST_TYPE
    path = settings.MEDIA_ROOT + '/' + folder
    try:
        os.makedirs(path, exist_ok=True)
    except OSError:
        pass
    img = Image.open(file)
    if img.mode not in ('L', 'RGB'):
        img = img.convert('RGB')
    width, height = img.size  # Get dimensions
    # get orginal image ratio
    img_ratio = float(width) / height
    for size in sizes:
        (x, y) = size
        real_ratio = x / y
        new_img = img.copy()
        if almost_equal(real_ratio, img_ratio):
            if width > x and height > y:
                new_img.thumbnail((x, y))
            else:
                new_img = new_img.resize((x, y), Image.ANTIALIAS)
        elif almost_gt(real_ratio, img_ratio):  # height of image > normal image
            real_height = (width * y) / x
            move_height = int((height - real_height) / 2)
            (left, top, right, bottom) = (0, move_height, width, height - move_height)
            new_img = new_img.crop((left, top, right, bottom))
            new_img = new_img.resize((x, y), Image.ANTIALIAS)
        else:
            real_width = (height * x) / y
            move_width = int((width - real_width) / 2)
            (left, top, right, bottom) = (move_width, 0, width - move_width, height)
            new_img = new_img.crop((left, top, right, bottom))
            new_img = new_img.resize((x, y), Image.ANTIALIAS)
        filename = name + "_{}x{}.".format(x, y) + 'jpg'
        full_path = path + "/" + filename
        if default_storage.exists(full_path):
            default_storage.delete(full_path)
        new_img.save(full_path)


def save_image(request, obj):
    import filecmp
    file_stores = {}
    for i in range(1, MAX_SIZE_UPLOADED):
        field = "file{}".format(i)
        xxx = request.FILES[field] if field in request.FILES else False
        if xxx and xxx != '' and obj.CONST_TYPE is not None:
            folder = "{}/{}".format(obj.CONST_TYPE, obj.pk)
            path = settings.MEDIA_ROOT + '/' + folder
            try:
                os.makedirs(path, exist_ok=True)
            except OSError:
                pass
            store = FileSystemStorage(path)
            ext = xxx.name.split(".")[-1].lower()
            # check files in folder. if >= max files is force exist
            if sum(len(files) for _, _, files in os.walk(path)) >= MAX_SIZE_UPLOADED:
                return file_stores
            real_name = "{}.{}".format(generate_slug(4), ext)
            fullname = path + "/" + real_name
            try:
                if os.path.exists(fullname):
                    # deepcode ignore PT: <please specify a reason of ignoring this>
                    os.remove(fullname)
                file_stored = store.save(real_name, xxx)
            except (OSError, SystemError):
                continue
            file_stores[i] = store.url(file_stored)
            # r=root, d=directories, f = files
            not_found = True
            for r, d, f in os.walk(path):
                for _file in f:
                    (_name, _ext) = _file.split(".")
                    if _ext != ext or real_name == _file:
                        continue
                    if filecmp.cmp(r + "/" + real_name, r + "/" + _file):
                        not_found = False
                        try:
                            os.remove(r + "/" + _file)
                            for f_rem in glob.glob("{}_*.{}".format(_name, _ext)):
                                os.remove(f_rem)
                        except (OSError, SystemError):
                            continue
            if not_found:
                handle_uploaded_image(request, obj, field, str(i), folder)
    return file_stores


def save_file(request, obj):
    file_stores = {}
    for i in range(1, int(MAX_SIZE_UPLOADED)):
        field = "file{}".format(i)
        xxx = request.FILES[field] if field in request.FILES else False
        if xxx and xxx != '' and obj.CONST_TYPE is not None:
            folder = "{}/{}".format(obj.CONST_TYPE, obj.pk)
            path = settings.MEDIA_ROOT + '/' + folder
            try:
                os.makedirs(path, exist_ok=True)
            except OSError:
                pass
            store = FileSystemStorage(path)
            ext = xxx.name.split(".")[-1].lower()
            # check files in folder. if >= max files is force exist
            if sum(len(files) for _, _, files in os.walk(path)) >= int(MAX_SIZE_UPLOADED):
                return file_stores
            real_name = "{}.{}".format(generate_slug(4), ext)
            fullname = path + "/" + real_name
            try:
                if os.path.exists(fullname):
                    # deepcode ignore PT: <please specify a reason of ignoring this>
                    os.remove(fullname)
                file_stored = store.save(real_name, xxx)
            except (OSError, SystemError):
                continue
            file_stores[i] = store.url(file_stored)
            # r=root, d=directories, f = files
            for r, d, f in os.walk(path):
                for _file in f:
                    _ext = _file.split(".")[-1].lower()
                    if _ext != ext or real_name == _file:
                        continue
                    if filecmp.cmp(r + "/" + real_name, r + "/" + _file):
                        try:
                            os.remove(r + "/" + _file)
                        except OSError:
                            pass
    return file_stores


def thumbnail(obj, typ='sm', *args, **kwargs):
    if typ is None or typ not in ['sm', 'mid', 'big']:
        typ = 'sm'
    if typ == 'sm':
        (x, y) = (32, 24)
    elif typ == 'mid':
        (x, y) = (320, 240)
    else:
        (x, y) = (640, 480)
    _name = "{}_{}x{}".format(str(obj.pk), x, y)
    real = settings.MEDIA_ROOT + '/' + obj.CONST_TYPE + '/'
    path = settings.MEDIA_URL + obj.CONST_TYPE + '/'
    found = False
    for ext in IMG_EXT_WITH_DOT:
        name = _name + ext
        if os.path.exists(real + name):
            thumb = name
            found = True
            break
    remain = 2
    if found and thumb is not None:
        thumb = path + thumb
        remain -= 1
        images = '<img src="{}" width="{}" height="{}"/>'.format(thumb, x, y)

    real = settings.MEDIA_ROOT + '/' + obj.CONST_TYPE + '/{}/'.format(str(obj.pk))
    path = settings.MEDIA_URL + obj.CONST_TYPE + '/{}/'.format(str(obj.pk))
    for r, d, f in os.walk(real):
        for file in f:
            thumb = "alt".format(x, y)
            if thumb in file and os.path.exists(r + file) and remain > 0:
                if remain == 2 or images is None:
                    images = '<img src="{}" width="{}" height="{}"/>'.format(path + file, x, y)
                else:
                    images += '<img src="{}" width="{}" height="{}"/>'.format(path + file, x, y)
                remain -= 1
                found = True
        if remain > 0:
            for file in f:
                thumb = "_{}x{}.".format(x, y)
                if thumb in file and os.path.exists(r + file) and remain > 0:
                    if remain == 2 or images is None:
                        images = '<img src="{}" width="{}" height="{}"/>'.format(path + file, x, y)
                    else:
                        images += '<img src="{}" width="{}" height="{}"/>'.format(path + file, x, y)
                    remain -= 1
                    found = True
    if not found or images is None:
        thumb = settings.MEDIA_URL + '/' + "noimage_{}x{}.jpg".format(x, y)
        images = '<img src="{}" width="{}" height="{}"/>'.format(thumb, x, y)
    return images


def slider(obj, typ='sm', *args, **kwargs):
    if typ is None or typ not in ['sm', 'mid', 'big']:
        typ = 'sm'
    if typ == 'sm':
        (x, y) = (32, 24)
    elif typ == 'mid':
        (x, y) = (320, 240)
    else:
        (x, y) = (640, 480)
    _name = "{}_{}x{}".format(str(obj.pk), x, y)
    real = settings.MEDIA_ROOT + '/' + obj.CONST_TYPE + '/'
    path = settings.MEDIA_URL + obj.CONST_TYPE + '/'
    found = False
    for ext in IMG_EXT_WITH_DOT:
        name = _name + ext
        if os.path.exists(real + name):
            thumb = name
            found = True
            break
        # pdb.set_trace()
    images = ""
    remain = 5  # get 5 images
    if found and thumb is not None:
        images = '<img src="{}" width="{}" height="{}"/>'.format(path + thumb, 64, 48)
        remain -= 1

    real = settings.MEDIA_ROOT + '/' + obj.CONST_TYPE + '/{}/'.format(str(obj.pk))
    path = settings.MEDIA_URL + obj.CONST_TYPE + '/{}/'.format(str(obj.pk))
    for r, d, f in os.walk(real):
        for file in f:
            thumb = "_{}x{}.".format(x, y)
            if thumb in file and os.path.exists(r + file) and remain > 0:
                images += '<img src="{}" width="{}" height="{}"/>'.format(path + file, 64, 48)
                remain -= 1
    return mark_safe(images)


def preview(obj, typ='sm', *args, **kwargs):
    if typ is None or typ not in ['sm', 'mid', 'big']:
        typ = 'sm'
    if typ == 'sm':
        (x, y) = (32, 24)
    elif typ == 'mid':
        (x, y) = (320, 240)
    else:
        (x, y) = (640, 480)
    _name = "{}_{}x{}".format(str(obj.pk), x, y)
    real = settings.MEDIA_ROOT + '/' + obj.CONST_TYPE + '/'
    path = settings.MEDIA_URL + obj.CONST_TYPE + '/'
    found = False
    for ext in IMG_EXT_WITH_DOT:
        thumb = real + _name + ext
        if os.path.exists(thumb):
            thumb = str(obj.pk) + ext
            found = True
            break
    if found and thumb is not None:
        thumb = path + thumb
    else:
        thumb = settings.MEDIA_URL + "noimage.jpg"
    return mark_safe('<img src="{}" width="{}" height="{}"/>'.format(thumb, x, y))


# How to save file programmatically to Django
# https://medium.com/@jainmickey/how-to-save-file-programmatically-to-django-37c67d9664b5

def get_matrix(obj=None):
    if obj is None:
        return []
    if isinstance(obj, main.models.ProductAttribute):
        obj = main.models.Product.objects.get(pk=obj.product_id)
    if not isinstance(obj, main.models.Product):
        return []
    full_dict: List[List[int]] = []
    instObjs = main.models.ProductAttributeGroup.objects.filter(product_id=obj.product_id).order_by(
        '-attr_group_id__pk')
    flag = None
    item_list: List[int] = []
    for instObj in instObjs:
        if flag is None:
            flag = instObj.attr_group_id.pk
        if flag != instObj.attr_group_id.pk:
            flag = instObj.attr_group_id.pk
            if len(item_list) != 0:
                full_dict.append(item_list)
                item_list = []
        item_list.append(instObj.attribute_id.pk)
    if len(item_list) != 0:
        full_dict.append(item_list)
    return full_dict


def get_max_combined(obj=None):
    max_combined = 0
    if obj is None:
        return max_combined
    if isinstance(obj, main.models.ProductAttribute):
        obj = main.models.Product.objects.get(pk=obj.product_id)
    if not isinstance(obj, main.models.Product):
        return max_combined
    matrix = get_matrix(obj)
    if matrix is not None and len(matrix) > 0:
        for i in range(len(matrix)):
            if max_combined == 0:
                max_combined = len(matrix[i])
            else:
                max_combined = max_combined * len(matrix[i])
    else:
        max_combined = 0
    return max_combined


def double_replace(result, sta_pointer, dyn_pointer, cur, rep):
    for x in range(sta_pointer):
        list_item = result[str(x)]
        new_list = list_item[:]  # copying a list using slicing
        if rep in new_list and cur not in new_list:
            new_list.remove(rep)
            new_list.append(cur)
        result[str(dyn_pointer)] = new_list
        dyn_pointer += 1
    return result


def get_list_combined(obj=None):
    items = {}
    if obj is None:
        return items
    if isinstance(obj, main.models.ProductAttribute):
        obj = main.models.Product.objects.get(pk=obj.product_id)
    if not isinstance(obj, main.models.Product):
        return items
    matrix = get_matrix(obj)
    max_combined = 0
    if matrix is not None and len(matrix) > 0:
        for i in range(len(matrix)):
            if max_combined == 0:
                max_combined = len(matrix[i])
            else:
                max_combined = max_combined * len(matrix[i])
    else:
        max_combined = 0

    if max_combined > 0:
        for i in range(max_combined):
            item = {str(i): []}
            items.update(item)
        static_pointer = 0
        # dynamic_pointer = 0
        row_first = True
        item_fist = True
        for i in range(len(matrix)):
            if row_first:
                row_first = False
                for j in range(len(matrix[i])):
                    current = matrix[i][j]
                    _item = [current]
                    items[str(j)] = _item
            else:
                _first = None
                for j in range(len(matrix[i])):
                    current = matrix[i][j]
                    if item_fist:
                        item_fist = False
                        _first = matrix[i][j]
                        for p in range(static_pointer):
                            _item = items[str(p)]
                            if current not in _item:
                                _item.append(current)
                            items[str(p)] = _item
                    else:
                        dynamic_pointer = j * static_pointer
                        if current != _first:
                            items = double_replace(items, static_pointer, dynamic_pointer, current, _first)
                    # dynamic_pointer = j * static_pointer if j > 0 else static_pointer
                item_fist = True
            static_pointer = static_pointer * len(matrix[i]) if static_pointer > 0 else len(matrix[i])
    return items


def proccessConfig(obj=None):
    config = {}
    if obj is not None and isinstance(obj, main.models.Product):
        _config = get_list_combined(obj)
        if _config is not None and len(_config) > 0:
            config = _config
    return json.dumps(config, cls=DjangoJSONEncoder)


def str_to_class(module_name, name_of_class):
    """Return a class instance from a string reference"""
    try:
        module_ = importlib.import_module(module_name)
        try:
            cls = getattr(module_, name_of_class)()
        except AttributeError:
            try:
                cls = globals()[name_of_class]
            except AttributeError:
                pass
    except ImportError:
        pass
    return cls or None


def get_attributes(obj):
    if obj is None or not isinstance(obj, main.models.ProductAttribute):
        return []
    if obj is not None and isinstance(obj, int):
        try:
            obj = main.models.ProductAttribute.objects.get(pk=obj)
        except ObjectDoesNotExist:
            return []
    attributes = [attribute.pk for attribute in obj.attributes.all()]
    attributes.sort()
    return attributes


def get_list_attributes(obj):
    items = {}
    if obj is None or not isinstance(obj, main.models.Product):
        return items
    if obj is not None and isinstance(obj, int):
        try:
            obj = main.models.Product.objects.get(pk=obj)
        except ObjectDoesNotExist:
            return items
    pro_atts = main.models.ProductAttribute.objects.filter(product_id=obj)
    for pro_att in pro_atts:
        attributes = [attribute.pk for attribute in pro_att.attributes.all()]
        attributes.sort()
        item = {str(pro_att.pk): attributes}
        items.update(item)
    return items


def check_exist_in_dict(my_list, my_dict):
    rs = False
    if not isinstance(my_list, list) or not isinstance(my_dict, dict) or not my_list:
        return rs
    my_list.sort()
    for key in my_dict:
        same_list = my_dict.get(key)
        if isinstance(same_list, list) and len(same_list) > 0:
            same_list.sort()
            if my_list == same_list:
                rs = True
                break
            if isSubArray(same_list, my_list) or isSubArray(my_list, same_list):
                rs = True
                break
    return rs
