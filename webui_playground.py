from functools import partial
import gradio as gr 
import time
import os 
from PIL import Image, ImageFont, ImageDraw, ImageFilter, ImageOps
from io import BytesIO
import base64
import re
import uuid
import argparse
import random
import sys

from frontend import draw_gradio_ui
from ui_functions import resize_image

from google.cloud import aiplatform

from google.protobuf import json_format
from google.protobuf.struct_pb2 import Value

"""
This file is here to play around with the interface without loading the whole model 
TBD - extract all the UI into this file and import from the main webui. 
"""

GFPGAN = True
RealESRGAN = True 
def run_goBIG():
    pass
def txt2img(endpoint_name, *args, **kwargs):
    print("endpoint_name",endpoint_name)
    aip_endpoint_name = (endpoint_name)
    endpoint = aiplatform.Endpoint(aip_endpoint_name)
    print(args)
    print(kwargs)
    seed = args[9]
    if seed == '':
        seed = random.randint(0, 6000000)
    seed = int(seed)
    print('seed:',seed)
    #Output should match output_txt2img_gallery, output_txt2img_seed, output_txt2img_params, output_txt2img_stats
    # info = f"""{args[0]} --seed {args[9]} --W {args[11]} --H {args[10]} -s {args[1]} -C {float(args[8])} --sampler {args[2]}  """.strip()
    args_and_names = {
        "seed": seed,
        "width": args[11],
        "height": args[10],
        "steps": args[1],
        "cfg_scale": str(args[8]),
        "sampler": args[2],
        'n_iter' : args[6],
        'n_samples' : args[7]
    }

    print("steps",args[1])
    
    full_string = f"{args[0]}\n"+ " ".join([f"{k}:" for k,v in args_and_names.items()])
    instances_list = [{"prompt": full_string}]
    instances = [json_format.ParseDict(s, Value()) for s in instances_list]
    
    parameters = {
        'scale' : args[8], 
        'seed' : seed, 
        'W' : args[11], 
        'H' : args[10], 
        'ddim_steps' : args[1],
        'n_samples' : args[7],
        'n_iter' : args[6]
        }
    parameters = json_format.ParseDict(parameters,Value())
    
    results = endpoint.predict(instances=instances,parameters=parameters)
    endpoint_images = results.predictions
    unique_id = str(uuid.uuid4())[:8]
    images = []
    os.makedirs("outputs/txt2img-samples",exist_ok=True)
    for i in range(len(endpoint_images)):
        img_path = f"outputs/txt2img-samples/{unique_id}-{i:05}.png"
        with open(img_path, "wb") as fh:
            fh.write(base64.b64decode(endpoint_images[i]))
        images.append(img_path)
    info = {
        'text': full_string,
        'entities': [{'entity':str(v), 'start': full_string.find(f"{k}:"),'end': full_string.find(f"{k}:") + len(f"{k} ")} for k,v in args_and_names.items()]
     }
    return images, int(time.time()) , info, 'random output'
def img2img(*args, **kwargs):
    images = [
    "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=387&q=80",
    "https://images.unsplash.com/photo-1554151228-14d9def656e4?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=386&q=80",
    "https://images.unsplash.com/photo-1542909168-82c3e7fdca5c?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxzZWFyY2h8MXx8aHVtYW4lMjBmYWNlfGVufDB8fDB8fA%3D%3D&w=1000&q=80",
    "https://images.unsplash.com/photo-1546456073-92b9f0a8d413?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=387&q=80",
    "https://images.unsplash.com/photo-1601412436009-d964bd02edbc?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=464&q=80",
    ]
    return images, 1234, 'random', 'random'

def run_GFPGAN(*args, **kwargs):
  time.sleep(.1)
  return "yo"
def run_RealESRGAN(*args, **kwargs):
  time.sleep(.2)
  return "yo"


class model():
  def __init__():
    pass

class opt():
    def __init__(self, name):
        self.name = name

    no_progressbar_hiding = True 

css_hide_progressbar = """
.wrap .m-12 svg { display:none!important; }
.wrap .m-12::before { content:"Loading..." }
.progress-bar { display:none!important; }
.meta-text { display:none!important; }
"""

css =  css_hide_progressbar
css = css + """
[data-testid="image"] {min-height: 512px !important};
#main_body {display:none !important};
#main_body>.col:nth-child(2){width:200%;}
"""

user_defaults = {}

# make sure these indicies line up at the top of txt2img()
txt2img_toggles = [
    'Create prompt matrix (separate multiple prompts using |, and get all combinations of them)',
    'Normalize Prompt Weights (ensure sum of weights add up to 1.0)',
    'Save individual images',
    'Save grid',
    'Sort samples by prompt',
    'Write sample info files',
    'jpg samples',
]
if GFPGAN is not None:
    txt2img_toggles.append('Fix faces using GFPGAN')
if RealESRGAN is not None:
    txt2img_toggles.append('Upscale images using RealESRGAN')

txt2img_defaults = {
    'prompt': '',
    'ddim_steps': 50,
    'toggles': [1, 2, 3],
    'sampler_name': 'PLMS',
    'ddim_eta': 0.0,
    'n_iter': 2,
    'batch_size': 2,
    'cfg_scale': 7.5,
    'seed': '42',
    'height': 512,
    'width': 512,
    'fp': None,
    'submit_on_enter': 'No',
    'variant_amount': 0,
    'variant_seed': ''
}

if 'txt2img' in user_defaults:
    txt2img_defaults.update(user_defaults['txt2img'])

txt2img_toggle_defaults = [txt2img_toggles[i] for i in txt2img_defaults['toggles']]

sample_img2img = "assets/stable-samples/img2img/sketch-mountains-input.jpg"
sample_img2img = sample_img2img if os.path.exists(sample_img2img) else None

# make sure these indicies line up at the top of img2img()
img2img_toggles = [
    'Create prompt matrix (separate multiple prompts using |, and get all combinations of them)',
    'Normalize Prompt Weights (ensure sum of weights add up to 1.0)',
    'Loopback (use images from previous batch when creating next batch)',
    'Random loopback seed',
    'Save individual images',
    'Save grid',
    'Sort samples by prompt',
    'Write sample info files',
    'jpg samples',
]
if GFPGAN is not None:
    img2img_toggles.append('Fix faces using GFPGAN')
if RealESRGAN is not None:
    img2img_toggles.append('Upscale images using RealESRGAN')

img2img_mask_modes = [
    "Keep masked area",
    "Regenerate only masked area",
]

img2img_resize_modes = [
    "Just resize",
    "Crop and resize",
    "Resize and fill",
]

img2img_defaults = {
    'prompt': '',
    'ddim_steps': 50,
    'toggles': [1, 4, 5],
    'sampler_name': 'PLMS',
    'ddim_eta': 0.0,
    'n_iter': 1,
    'batch_size': 1,
    'cfg_scale': 5.0,
    'denoising_strength': 0.75,
    'mask_mode': 0,
    'resize_mode': 0,
    'seed': '',
    'height': 512,
    'width': 512,
    'fp': None,
}

if 'img2img' in user_defaults:
    img2img_defaults.update(user_defaults['img2img'])

img2img_toggle_defaults = [img2img_toggles[i] for i in img2img_defaults['toggles']]
img2img_image_mode = 'sketch'


css_hide_progressbar = """
.wrap .m-12 svg { display:none!important; }
.wrap .m-12::before { content:"Loading..." }
.progress-bar { display:none!important; }
.meta-text { display:none!important; }
"""

styling = """
[data-testid="image"] {min-height: 512px !important}
* #body>.col:nth-child(2){width:250%;max-width:89vw}
#generate{width: 100%; }
#prompt_row input{
 font-size:20px
 }
input[type=number]:disabled { -moz-appearance: textfield;+ }
"""

def main(args):

    txt2img_partial = partial(txt2img,args.aip_endpoint_name)

    demo = draw_gradio_ui(opt,
                        user_defaults=user_defaults,
                        txt2img=txt2img_partial,
                        img2img=img2img,
                        txt2img_defaults=txt2img_defaults,
                        txt2img_toggles=txt2img_toggles,
                        txt2img_toggle_defaults=txt2img_toggle_defaults,
                        show_embeddings=hasattr(model, "embedding_manager"),
                        img2img_defaults=img2img_defaults,
                        img2img_toggles=img2img_toggles,
                        img2img_toggle_defaults=img2img_toggle_defaults,
                        img2img_mask_modes=img2img_mask_modes,
                        img2img_resize_modes=img2img_resize_modes,
                        sample_img2img=sample_img2img,
                        RealESRGAN=RealESRGAN,
                        GFPGAN=GFPGAN,
                        run_GFPGAN=run_GFPGAN,
                        run_RealESRGAN=run_RealESRGAN
                            )

    demo.launch(share=False, debug=False, enable_queue=False, auth=('tester','test@12345'),server_name='0.0.0.0', server_port=args.port)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--port",
        type=int,
        help="port to run the gradio app"
    )
    parser.add_argument(
        "--aip-endpoint-name",
        type=str,
        help="vertex endpoint name. Ex: projects/{project_id}/locations/us-central1/endpoints/{endpoint_id}"        
    )
    args = parser.parse_args()
    main(args)