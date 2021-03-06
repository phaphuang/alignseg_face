import os
import os.path as osp
import numpy as np
import random
import collections
import torch
import torchvision
import cv2
from torch.utils import data
from glob import glob
from torch.utils.data import DataLoader

class CelebADataSet(data.Dataset):
    def __init__(self, root, max_iters=None, crop_size=(321, 321), mean=(128, 128, 128), scale=True, mirror=True, ignore_label=255):
        self.root = root
        self.crop_h, self.crop_w = crop_size
        self.mean = mean
        self.ignore_label = ignore_label
        self.scale = scale
        self.is_mirror = mirror

        img_lists = glob(osp.join(self.root, "CelebA-HQ-img/*"))
        #label_lists = glob(osp.join(root, "mask/*"))

        self.files = []

        image_ids = len(img_lists)
        #print(image_ids)

        for id in range(image_ids):
            img_file = osp.join(self.root, "CelebA-HQ-img/%s.jpg" % str(id))
            label_file = osp.join(self.root, "mask/%s.png" % str(id))
            self.files.append({
                "img": img_file,
                "label": label_file,
                "name": str(id)
            })

    def __len__(self):
        return len(self.files)
    
    def generate_scale_label(self, image, label):
        f_scale = 0.5 + random.randint(0, 11) / 10.0
        image = cv2.resize(image, None, fx=f_scale, fy=f_scale, interpolation = cv2.INTER_LINEAR)
        label = cv2.resize(label, None, fx=f_scale, fy=f_scale, interpolation = cv2.INTER_NEAREST)
        return image, label
    
    def __getitem__(self, index):
        datafiles = self.files[index]
        image = cv2.imread(datafiles["img"], cv2.IMREAD_COLOR)
        label = cv2.imread(datafiles["label"], cv2.IMREAD_GRAYSCALE)
        size = image.shape
        name = datafiles["name"]
        if self.scale:
            image, label = self.generate_scale_label(image, label)
        image = np.asarray(image, np.float32)
        image -= self.mean
        img_h, img_w = label.shape
        pad_h = max(self.crop_h - img_h, 0)
        pad_w = max(self.crop_w - img_w, 0)
        if pad_h > 0 or pad_w > 0:
            img_pad = cv2.copyMakeBorder(image, 0, pad_h, 0, pad_w, cv2.BORDER_CONSTANT, value=(0.0, 0.0, 0.0))
            label_pad = cv2.copyMakeBorder(label, 0, pad_h, 0, pad_w, cv2.BORDER_CONSTANT, value=(self.ignore_label,))
        else:
            img_pad, label_pad = image, label
        
        img_h, img_w = label_pad.shape
        h_off = random.randint(0, img_h - self.crop_h)
        w_off = random.randint(0, img_w - self.crop_w)
        # roi = cv2.Rect(w_off, h_off, self.crop_w, self.crop_h);
        image = np.asarray(img_pad[h_off : h_off+self.crop_h, w_off : w_off+self.crop_w], np.float32)
        label = np.asarray(label_pad[h_off : h_off+self.crop_h, w_off : w_off+self.crop_w], np.float32)
        #image = image[:, :, ::-1]  # change to BGR
        image = image.transpose((2, 0, 1))
        if self.is_mirror:
            flip = np.random.choice(2) * 2 - 1
            image = image[:, :, ::flip]
            label = label[:, ::flip]

        return image.copy(), label.copy(), np.array(size), name

if __name__ == '__main__':

    root_path = "../CelebAMask-HQ"

    dataset = CelebADataSet(root=root_path)

    #file_list = glob("../CelebAMask-HQ/CelebA-HQ-img/*")

    #print(file_list[0].split("\\")[-1].split(".")[0])
    #print(len())

    is_shuffle = True

    train_loader = DataLoader(dataset,
                            batch_size=4,
                            drop_last=False,
                            shuffle=is_shuffle)
    print(len(next(iter(train_loader)))) # 30000 / 4 = 7500


    
