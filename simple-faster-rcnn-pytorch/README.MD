# Faster R-CNN Implementation of Multi-class Image Recognition of Food

## Before training

1. Install dependencies

    Install PyTorch>=0.4

    Install cupy (so GPU needed)
    ```Bash
    pip install cupy-cuda80
    ```
    Install other requirements
    ```Bash
    pip install -r requirements.txt
    ```

2. Prepare data
    
    Download images by using image scraping tool [Extreme Picture Finder](https://www.webimagedownloader.com/) and clean the noise manually.
    
    Use [labelImg](https://github.com/tzutalin/labelImg) to annotate all images manually.
    
    Our dataset is VOC format and can be downloaded in [dataset-for-food](https://drive.google.com/file/d/1SausE5LZ9h6imG8OhhEUBa3zXJZRfk7k/view?usp=sharing).  Need unzip all zipped file before using.


3. Prepare pretrained model

    Download caffe-pretrained model, convert it to the format compatible with torchvision and store it in a new folder /checkpoints.
    ```Bash
    python misc/convert_caffe_pretrain.py
    ```
    
4. Start visdom for visualization before training, so you may open browser, visit `http://<ip>:8097` and see the visualization of training procedure
    ```Bash
    python -m visdom.server &
    ```

## Begin training

Train the model and save the snapshots in /checkpoints folder.
    
    python train.py train --env='fasterrcnn-caffe' --plot-every=100 --caffe-pretrain
    
   
## Demo

Download the snapshot of model and test images in 'Demo_images'.

Use `demo.ipynb` to load snapshot and image and show the performance of that model.
