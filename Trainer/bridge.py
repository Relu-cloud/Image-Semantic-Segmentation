import sys

import numpy as np

sys.path.extend([r'D:\dl_project\dl_project_cnn\DataInput', r'D:\dl_project\dl_project_cnn\Models' \
                    , r'D:\dl_project\dl_project_cnn\Trainer', r'D:\dl_project\dl_project_cnn\Utils'])

import configparser

from DataInput.Dataset import BasicDataset
from torch.utils.data import DataLoader
from glob import glob
from os.path import *
from torchvision import transforms
from PIL import Image
import matplotlib.pyplot as plt

from torch import optim
from Utils.lr_scheduler import *

from Utils.metrics import *
from Utils.loss import *
from Utils.visualizer import *
from Utils.saver import *

import logging

logging.getLogger().setLevel(logging.INFO)
from tqdm import tqdm

import torch
import torch.nn as nn
from Utils.loss import *
from Utils.metrics import *
from Utils.loss import *
from Utils.visualizer import *
from Utils.saver import *

import os
import time


def bridge(net,
          config_path
          ):
    '''record the start time'''
    start_time = time.clock()

    '''read the config file'''
    cf = configparser.ConfigParser()
    cf.read(config_path)
    secs = cf.sections()
    batch_size = int(cf.get(secs[0], 'batch_size'))
    root_path = cf.get(secs[0], 'root_path')
    lr_base = float(cf.get(secs[0], 'lr_base'))
    epochs = int(cf.get(secs[0], 'epochs'))
    interval_step = int(cf.get(secs[0], 'interval_step'))
    val_step = int(cf.get(secs[0], 'val_step'))
    dir_checkpoint = cf.get(secs[0], 'dir_checkpoint')

    save_path = r'F:/dataset/M_road/val/image_no_use/'
    '''read input data, using BasicDataset and Dataloader'''
    trans = transforms.ToTensor()
    trans_back = transforms.ToPILImage()

    image_dataset = glob(join(root_path, 'val', 'image','*.png'))
    # image_dataset = [r'F:\dataset\M_road\train\image\10078690_15_3.png']
    # name_list = [os.path.basename(file) for file in image_dataset]
    # logging.info(f'name loaded!')
    # image_list = [trans(Image.open(fp=file)) for file in image_dataset] # CHW Tensor
    # logging.info(f'Image loaded!')

    net.cuda()
    net.eval()
    for file in tqdm(image_dataset):
        name = os.path.basename(file)
        image = trans(Image.open(fp=file)).unsqueeze(0).cuda()
        with torch.no_grad():
            # pred = (torch.sigmoid(net(image)) > 0.3).type(torch.float32).data.cpu()
            pred = torch.sigmoid(net(image))
        pred_img = trans_back(pred[0])  # PIL
        pred_img.save(save_path+name)

def save_pred(fp_sig, fp_pred):
    sig_set = glob(join(fp_sig, '*.png'))
    for file in tqdm(sig_set):
        name = os.path.basename(file)
        image = (transforms.ToTensor()(Image.open(fp=file)) > 0.8).type(torch.float32)
        image = transforms.ToPILImage()(image)
        image.save(fp_pred+name)

def loss_com(fp_pred, fp_label):
    pred_set = glob(join(fp_pred, '*.png'))
    label_set = glob(join(fp_label, '*.png'))
    loss = []
    num=0
    for predf, labelf in tqdm(zip(pred_set, label_set)):
        name = os.path.basename(predf)
        image = transforms.ToTensor()(Image.open(fp=predf).convert('L'))
        img = image.numpy().flatten()
        label = transforms.ToTensor()(Image.open(fp=labelf).convert('L'))
        lab = label.numpy().flatten()
        hist = np.bincount(
            2 * lab.astype(int) + img.astype(int),
            minlength=  4,
        ).reshape(2, 2)
        precision_cls = np.diag(hist) / hist.sum(axis=0)
        # iou = np.diag(hist) / (hist.sum(axis=1) + hist.sum(axis=0) - np.diag(hist))
        if not np.isnan(precision_cls[1]) and  precision_cls[1]>0.8:
            num+=1
            transforms.ToPILImage()(image).save(r'F:\dataset\M_road\train\image_filt/' + name)
            transforms.ToPILImage()(label).save(r'F:\dataset\M_road\train\label_filt/' + name)
    print(num)

def iou_com(fp_pred, fp_label):
    train_metricer = StreamSegMetrics(n_classes=2)
    pred_set = glob(join(fp_pred, '*.png'))
    label_set = glob(join(fp_label, '*.png'))
    loss = []
    num = 0
    for predf, labelf in tqdm(zip(pred_set, label_set)):
        image = np.array(Image.open(fp=predf).convert('L'))/255
        label = np.array(Image.open(fp=labelf).convert('L'))/255
        train_metricer.update(image, label)
    metric_dict = train_metricer.get_results()
    print(metric_dict)


if __name__ == '__main__':
    fp_sig = r'F:\dataset\M_road\train\image_sig'
    fp_pred = r'F:\dataset\M_road\val\first_pred/'
    fp_label = r'F:\dataset\M_road\val\label/'
    # save_pred(fp_sig, fp_pred)
    iou_com(fp_pred, fp_label)




