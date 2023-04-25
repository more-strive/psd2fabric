import json
import os
import uuid
import base64
from psd_tools import PSDImage

from io import BytesIO


def get_uuid(index):
    return str(uuid.uuid1()).split('-')[0] + str(index)


def parse():
    psd = PSDImage.load('./files/11背.psd')
    # print(psd.print_tree())
    for index, layer in enumerate(psd.layers):
        # print(layer, layer.kind, dir(layer))
        if not layer.visible:
            continue
        if layer.kind == 'group':
            check_group(layer)
        elif layer.kind == 'pixel':
            get_layer_image(layer)
        elif layer.kind == 'type':
            get_layer_text(layer, 'group-%s' % index)


def check_group(layer):
    for i in layer.layers:
        if not layer.visible:
            continue
        if i.kind == 'group':
            check_group(i)
        elif i.kind == 'pixel':
            get_layer_image(i)
        elif i.kind == 'type':
            print('text:', i, dir(i))
            get_layer_text(i, 'group-%s' % i)

def image_to_base64(image_path):
    """
        将图片转为 Base64流
    :param image_path: 图片路径
    :return:
    """
    with open(image_path, "rb") as file:
        base64_data = base64.b64encode(file.read())  # base64编码
    return base64_data

def get_layer_image(layer):
    image = layer.as_PIL()
    if not image:
        return
    print(layer.effects)
    # if image.mode == 'CMYK':
    #     from PIL import ImageChops
    #     image = ImageChops.invert(image)
    # image_path = os.path.join('./', '华氏')
    # if not os.path.exists(image_path):
    #     os.makedirs(image_path)
    # image_file = os.path.join(image_path, 'layer%s.png' % layer.layer_id)
    # image.save(image_file)
    output = BytesIO()
    image.save(output, format='png')
    byte_data = output.getvalue()
    base64_str = base64.b64encode(byte_data).decode()
    # print(base64_str)
    data = {
        "id": get_uuid(str(layer.layer_id) + '-image'),
        "type": 'image',
        "left": layer.left,
        'top': layer.top,
        'width': layer.width,
        'height': layer.height,
        "rotate": 0,
        "fixedRatio": True,
        "src": 'data:image/png;base64,' + base64_str,
    }
    # print(data)
    return data

def get_layer_text(layer, group_id):
    text_uuid = get_uuid(layer.layer_id)
    text_content = layer.text.split('\r')
    # print(layer.text_data)
    # for key, value in layer.text_data.items():
    #     print(key.decode(), value)
    text_data = ''
    for text in text_content:
        text_data += '<p>%s</p>' % text
    data = {
        "id": text_uuid,
        "type": 'text',
        "groupId": group_id,
        # "left": bbox[0],
        # "top": bbox[1] - 2,
        # "width": bbox[2] - bbox[0] + 4,
        # "height": bbox[3] - bbox[1] + 4,
        "left": layer.left,
        'top': layer.top,
        'width': layer.width,
        'height': layer.height,
        "rotate": 0,
        "content": text_data,
        "defaultFontName": '',
        "defaultColor": '',
        "style": {
            'fontSize': '%spx',
            'fontFamily': '',
            'lineHeight': 1
        }
    }
    return data


if __name__ == '__main__':
    parse()