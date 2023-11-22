# -*- coding: utf-8 -*-
"""termwork1.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1zhYZXRFv85DIe-VMlNZoi3RWof0boC9P

## **INITIALIZATIONS - ALL CODES UNDER THIS TO BE RUN**

**Importing libraries**
"""

# Commented out IPython magic to ensure Python compatibility.
# %matplotlib inline

import os
import shutil
import random
import torch
import torchvision
import numpy as np

from PIL import Image
from matplotlib import pyplot as plt

torch.manual_seed(0)

print('Using PyTorch version', torch.__version__)

"""**Unzipping the dataset.zip file**"""

from google.colab import drive
drive.mount('/content/drive')

!unzip -uq "/content/drive/My Drive/dataset.zip"

"""**Creating custom Dataset**"""

class_names = ['normal', 'viral', 'covid']
root_dir = "/content/COVID-19 Radiography Database"
source_dirs = ['NORMAL', 'Viral Pneumonia', 'COVID-19']

if os.path.isdir(os.path.join(root_dir, source_dirs[1])):
    os.mkdir(os.path.join(root_dir, 'test'))

    for i, d in enumerate(source_dirs):
        os.rename(os.path.join(root_dir, d), os.path.join(root_dir, class_names[i]))

    for c in class_names:
        os.mkdir(os.path.join(root_dir, 'test', c))

    for c in class_names:
        images = [x for x in os.listdir(os.path.join(root_dir, c)) if x.lower().endswith('png')]
        selected_images = random.sample(images, 30)
        for image in selected_images:
            source_path = os.path.join(root_dir, c, image)
            target_path = os.path.join(root_dir, 'test', c, image)
            shutil.move(source_path, target_path)

class ChestXRayDataset(torch.utils.data.Dataset):
    def __init__(self, image_dirs, transform):
        def get_images(class_name):
            images = [x for x in os.listdir(image_dirs[class_name]) if x.lower().endswith('png')]
            print(f'Found {len(images)} {class_name} examples')
            return images

        self.images = {}
        self.class_names = ['normal', 'viral', 'covid']

        for class_name in self.class_names:
            self.images[class_name] = get_images(class_name)

        self.image_dirs = image_dirs
        self.transform = transform


    def __len__(self):
        return sum([len(self.images[class_name]) for class_name in self.class_names])


    def __getitem__(self, index):
        class_name = random.choice(self.class_names)
        index = index % len(self.images[class_name])
        image_name = self.images[class_name][index]
        image_path = os.path.join(self.image_dirs[class_name], image_name)
        image = Image.open(image_path).convert('RGB')
        return self.transform(image), self.class_names.index(class_name)

train_transform = torchvision.transforms.Compose([
    torchvision.transforms.Resize(size=(224, 224)),
    torchvision.transforms.RandomHorizontalFlip(),
    torchvision.transforms.ToTensor(),
    torchvision.transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

test_transform = torchvision.transforms.Compose([
    torchvision.transforms.Resize(size=(224, 224)),
    torchvision.transforms.ToTensor(),
    torchvision.transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

print(train_transform)

"""

**Prepare DataLoader**"""

train_dirs = {
    'normal': 'COVID-19 Radiography Database/normal',
    'viral': 'COVID-19 Radiography Database/viral',
    'covid': 'COVID-19 Radiography Database/covid'
}

train_dataset = ChestXRayDataset(train_dirs, train_transform)

test_dirs = {
    'normal': 'COVID-19 Radiography Database/test/normal',
    'viral': 'COVID-19 Radiography Database/test/viral',
    'covid': 'COVID-19 Radiography Database/test/covid'
}

test_dataset = ChestXRayDataset(test_dirs, test_transform)

batch_size = 6


dl_train = torch.utils.data.DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
dl_test = torch.utils.data.DataLoader(test_dataset, batch_size=batch_size, shuffle=True)

print('Number of training batches', len(dl_train))
print('Number of test batches', len(dl_test))

"""**Data Visualisation**"""

class_names = train_dataset.class_names


def show_images(images, labels, preds):
    plt.figure(figsize=(8, 4))
    acc=6
    for i, image in enumerate(images):
        plt.subplot(1, 6, i + 1, xticks=[], yticks=[])
        image = image.numpy().transpose((1, 2, 0))
        mean = np.array([0.485, 0.456, 0.406])
        std = np.array([0.229, 0.224, 0.225])
        image = image * std + mean
        image = np.clip(image, 0., 1.)
        plt.imshow(image)

        col = 'green'
        if preds[i] != labels[i]:
            col = 'red'
            acc-=1

        plt.xlabel(f'{class_names[int(labels[i].numpy())]}')
        plt.ylabel(f'{class_names[int(preds[i].numpy())]}', color=col)
    plt.tight_layout()
    plt.show()
    #print("Accuracy= "+str(acc/6))

images1, labels1 = next(iter(dl_train))
show_images(images1, labels1, labels1)
#print(images1)

images2, labels2 = next(iter(dl_test))
show_images(images2, labels2, labels2)

"""**Creating the model - IMPORTANT**"""

resnet18 = torchvision.models.resnet18(pretrained=True)
#print(resnet18)

resnet18.fc = torch.nn.Linear(in_features=512, out_features=3)

loss_fn = torch.nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(resnet18.parameters(), lr=3e-5)

def show_preds():
    resnet18.eval()
    images, labels = next(iter(dl_test))
    outputs = resnet18(images)
    _, preds = torch.max(outputs, 1)
    show_images(images, labels, preds)

"""# **Training using RESNET MODEL (NOT NECESSARY FOR TERMWORK)**

**Training the resnet18 model and classifying**
"""

def train(epochs):
    print('Starting training..')
    for e in range(0, epochs):
        print('='*20)
        print(f'Starting epoch {e + 1}/{epochs}')
        print('='*20)

        train_loss = 0.
        val_loss = 0.

        resnet18.train() # set model to training phase

        for train_step, (images, labels) in enumerate(dl_train):
            optimizer.zero_grad()
            outputs = resnet18(images)
            loss = loss_fn(outputs, labels)
            loss.backward()
            optimizer.step()
            train_loss += loss.item()
            if train_step % 20 == 0:
                print('Evaluating at step', train_step)

                accuracy = 0

                resnet18.eval() # set model to eval phase

                for val_step, (images, labels) in enumerate(dl_test):
                    outputs = resnet18(images)
                    loss = loss_fn(outputs, labels)
                    val_loss += loss.item()

                    _, preds = torch.max(outputs, 1)
                    accuracy += sum((preds == labels).numpy())

                val_loss /= (val_step + 1)
                accuracy = accuracy/len(test_dataset)
                print(f'Validation Loss: {val_loss:.4f}, Accuracy: {accuracy:.4f}')

                show_preds()

                resnet18.train()

                if accuracy >= 0.95:
                    print('Performance condition satisfied, stopping..')
                    return

        train_loss /= (train_step + 1)

        print(f'Training Loss: {train_loss:.4f}')
    print('Training complete..')

# Commented out IPython magic to ensure Python compatibility.
# %%time
# 
# train(epochs=1)

"""# **TERM WORK -1**

**Feature Extraction - Term work 1**
"""

import pandas as pd
df = pd.DataFrame()

feature_extractor = torch.nn.Sequential(*list(resnet18.children())[:-1])
for _ in range(len(dl_train)):
  images1, labels1 = next(iter(dl_train))
  output = feature_extractor(images1)
  output = output.reshape(output.shape[0],output.shape[1]*output.shape[2]*output.shape[3])
  #print(output)
  toNumpy = output.detach().numpy()
  #Appending each row (image wise)
  for i in range(batch_size):
    x = toNumpy[i].reshape(1,toNumpy[0].shape[0])
    #print(x)
    feat = pd.DataFrame(x)
    #print(feat)
    df = df.append(feat)

print(df)

#f=open('feature.txt','a')
#for i in range(batch_size):
#  np.savetxt(f, toNumpy[i])
#  print(toNumpy[i])
 # f.write("\n")

df.to_csv('train_features.csv')

df1 = pd.DataFrame()

#feature_extractor = torch.nn.Sequential(*list(resnet18.children())[:-1])
for _ in range(len(dl_test)):
  images2, labels2 = next(iter(dl_test))
  output1 = feature_extractor(images2)
  output1 = output1.reshape(output1.shape[0],output1.shape[1]*output1.shape[2]*output1.shape[3])
  #print(output)
  toNumpy = output1.detach().numpy()
  #Appending each row (image wise)
  for i in range(batch_size):
    x = toNumpy[i].reshape(1,toNumpy[0].shape[0])
    #print(x)
    feat = pd.DataFrame(x)
    #print(feat)
    df1 = df1.append(feat)

print(df1)

df1.to_csv('test_features.csv')

"""**Feature Map for 1 batch of training images - Term work 1**"""

images1, labels1 = next(iter(dl_train))
output = feature_extractor(images1)
output = output.reshape(output.shape[0],output.shape[1]*output.shape[2]*output.shape[3])
toNumpy = output.detach().numpy()
plt.imshow(toNumpy)
for i in range(batch_size):

  x = toNumpy[i].reshape(1,toNumpy[0].shape[0])
  plt.imshow(x)

show_images(images1,labels1,labels1)

feature_extractor = torch.nn.Sequential(*list(resnet18.children())[:-1])
for p in feature_extractor.parameters():
    p.requires_grad = False


out = feature_extractor(images1)
out = torch.squeeze(out, 0)
for i in range(batch_size):
  feature = out[i].numpy()
  feature = feature.reshape(feature.shape[0],1)
 # imshow(random.rand(8, 90), interpolation='nearest')
  plt.figure(figsize = (2,2))
  plt.imshow(feature, aspect='auto')
  plt.show()

"""**Testing for all 15 test batches - Term work 1**"""

for _ in range(len(dl_test)):
  show_preds()

"""**SVM Classifier - Term work 1**"""

batch_size_train = 1000
batch_size_test = 90


dl_train1 = torch.utils.data.DataLoader(train_dataset, batch_size=batch_size_train, shuffle=True)
dl_test1 = torch.utils.data.DataLoader(test_dataset, batch_size=batch_size_test, shuffle=True)

print('Number of training batches', len(dl_train1))
print('Number of test batches', len(dl_test1))

images1, labels1 = next(iter(dl_train1))
output = feature_extractor(images1)
output = output.reshape(output.shape[0],output.shape[1]*output.shape[2]*output.shape[3])
X_train = output.detach().numpy()
y_train = labels1.detach().numpy()
y_train = y_train.reshape(y_train.shape[0],1)

#Appending each row (image wise)

images2, labels2 = next(iter(dl_test1))
output = feature_extractor(images2)
output = output.reshape(output.shape[0],output.shape[1]*output.shape[2]*output.shape[3])
X_test = output.detach().numpy()
y_test = labels2.detach().numpy()
y_test = y_test.reshape(y_test.shape[0],1)

from sklearn import svm

#Create a svm Classifier
clf = svm.SVC(kernel='linear') #Kernel

#Train the model using the training sets
clf.fit(X_train, y_train)

#Predict the response for test dataset
y_pred = clf.predict(X_test)
y_pred = y_pred.reshape(y_pred.shape[0],1)
#print(y_pred.shape)
#print(y_pred)
#print(y_test.shape)
#Import scikit-learn metrics module for accuracy calculation
from sklearn import metrics

# Model Accuracy: how often is the classifier correct?
print("Upon usingg SVM classifier:")
print("Accuracy:",metrics.accuracy_score(y_test, y_pred))

"""**Feature Selection Using RFE - Term work 1**"""

from sklearn.feature_selection import RFE
selector = RFE(estimator=clf, n_features_to_select = 150, step=1)
selector = selector.fit(X_train, y_train)

selector.ranking_

selector.support_

y_fs_pred = selector.predict(X_test)
y_fs_pred = y_fs_pred.reshape(y_fs_pred.shape[0],1)
print("Accuracy:",metrics.accuracy_score(y_test, y_pred))

"""**Confusion Matrix - Term work 1**"""

from sklearn.metrics import confusion_matrix
confusion_matrix(y_test, y_fs_pred)

from sklearn.metrics import plot_confusion_matrix

titles_options = [("Confusion matrix, without normalization", None),
                  ("Normalized confusion matrix", 'true')]
for title, normalize in titles_options:
    disp = plot_confusion_matrix(selector, X_test, y_test,
                                 display_labels=class_names,
                                 cmap=plt.cm.Blues,
                                 normalize=normalize)
    disp.ax_.set_title(title)

    print(title)
    print(disp.confusion_matrix)

plt.show()

from sklearn.metrics import classification_report
print(classification_report(y_test, y_fs_pred, target_names=class_names))

"""**Plotting ROCs - Term work 1**"""

import matplotlib.pyplot as plt
from itertools import cycle

from sklearn import svm, datasets
from sklearn.metrics import roc_curve, auc
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import label_binarize
from sklearn.multiclass import OneVsRestClassifier
from scipy import interp
from sklearn.metrics import roc_auc_score

y_tr = label_binarize(y_train, classes=[0, 1, 2])
n_classes = y_tr.shape[1]

y_te = label_binarize(y_test, classes=[0, 1, 2])

print(n_classes)
print(y_te.shape)

# Learn to predict each class against the other
#random_state = np.random.RandomState(0)
classifier = OneVsRestClassifier(svm.SVC(kernel='linear', probability=True))
y_score = classifier.fit(X_train, y_tr).decision_function(X_test)
print(y_score)

# Compute ROC curve and ROC area for each class
fpr = dict()
tpr = dict()
roc_auc = dict()
for i in range(n_classes):
    fpr[i], tpr[i], _ = roc_curve(y_te[:, i], y_score[:, i])
    roc_auc[i] = auc(fpr[i], tpr[i])

# Compute micro-average ROC curve and ROC area
fpr["micro"], tpr["micro"], _ = roc_curve(y_te.ravel(), y_score.ravel())
roc_auc["micro"] = auc(fpr["micro"], tpr["micro"])

print(tpr)

plt.figure()
lw = 2
plt.plot(fpr[2], tpr[2], color='darkorange',
         lw=lw, label='ROC curve (area = %0.2f)' % roc_auc[2])
plt.plot([0, 1], [0, 1], color='navy', lw=lw, linestyle='--')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Receiver operating characteristic example')
plt.legend(loc="lower right")
plt.show()

# First aggregate all false positive rates
all_fpr = np.unique(np.concatenate([fpr[i] for i in range(n_classes)]))

# Then interpolate all ROC curves at this points
mean_tpr = np.zeros_like(all_fpr)
for i in range(n_classes):
    mean_tpr += interp(all_fpr, fpr[i], tpr[i])

# Finally average it and compute AUC
mean_tpr /= n_classes

fpr["macro"] = all_fpr
tpr["macro"] = mean_tpr
roc_auc["macro"] = auc(fpr["macro"], tpr["macro"])

# Plot all ROC curves
plt.figure()
plt.plot(fpr["micro"], tpr["micro"],
         label='micro-average ROC curve (area = {0:0.2f})'
               ''.format(roc_auc["micro"]),
         color='deeppink', linestyle=':', linewidth=4)

plt.plot(fpr["macro"], tpr["macro"],
         label='macro-average ROC curve (area = {0:0.2f})'
               ''.format(roc_auc["macro"]),
         color='navy', linestyle=':', linewidth=4)

colors = cycle(['aqua', 'darkorange', 'cornflowerblue'])
for i, color in zip(range(n_classes), colors):
    plt.plot(fpr[i], tpr[i], color=color, lw=lw,
             label='ROC curve of class {0} (area = {1:0.2f})'
             ''.format(i, roc_auc[i]))

plt.plot([0, 1], [0, 1], 'k--', lw=lw)
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Some extension of Receiver operating characteristic to multi-class')
plt.legend(loc="lower right")
plt.show()

y_prob = classifier.predict_proba(X_test)

macro_roc_auc_ovo = roc_auc_score(y_te, y_prob, multi_class="ovo",
                                  average="macro")
weighted_roc_auc_ovo = roc_auc_score(y_te, y_prob, multi_class="ovo",
                                     average="weighted")
macro_roc_auc_ovr = roc_auc_score(y_te, y_prob, multi_class="ovr",
                                  average="macro")
weighted_roc_auc_ovr = roc_auc_score(y_te, y_prob, multi_class="ovr",
                                     average="weighted")
print("One-vs-One ROC AUC scores:\n{:.6f} (macro),\n{:.6f} "
      "(weighted by prevalence)"
      .format(macro_roc_auc_ovo, weighted_roc_auc_ovo))
print("One-vs-Rest ROC AUC scores:\n{:.6f} (macro),\n{:.6f} "
      "(weighted by prevalence)"
      .format(macro_roc_auc_ovr, weighted_roc_auc_ovr))

"""# **TERM WORK - 2**

**Understanding the significane of C parameter - Term work 2**
"""

feature_extractor = torch.nn.Sequential(*list(resnet18.children())[:-1])

batch_size_train = 200
batch_size_test = 90


dl_train1 = torch.utils.data.DataLoader(train_dataset, batch_size=batch_size_train, shuffle=True)
dl_test1 = torch.utils.data.DataLoader(test_dataset, batch_size=batch_size_test, shuffle=True)

print('Number of training batches', len(dl_train1))
print('Number of test batches', len(dl_test1))

images1, labels1 = next(iter(dl_train1))
output = feature_extractor(images1)
output = output.reshape(output.shape[0],output.shape[1]*output.shape[2]*output.shape[3])
X_train = output.detach().numpy()
y_train = labels1.detach().numpy()
y_train = y_train.reshape(y_train.shape[0],1)

#Appending each row (image wise)

images2, labels2 = next(iter(dl_test1))
output = feature_extractor(images2)
output = output.reshape(output.shape[0],output.shape[1]*output.shape[2]*output.shape[3])
X_test = output.detach().numpy()
y_test = labels2.detach().numpy()
y_test = y_test.reshape(y_test.shape[0],1)

qwer = [0.001, 0.01, 0.1, 1, 10]
yval =[]

from sklearn import svm

for x in qwer:

  #Create a svm Classifier
  clf = svm.SVC(C=x,kernel='linear') #Kernel

  #Train the model using the training sets
  clf.fit(X_train, y_train)

  #Predict the response for test dataset
  y_pred = clf.predict(X_test)
  y_pred = y_pred.reshape(y_pred.shape[0],1)

  #Import scikit-learn metrics module for accuracy calculation
  from sklearn import metrics

  # Model Accuracy: how often is the classifier correct?
  yval.append(metrics.accuracy_score(y_test, y_pred))
  #print(metrics.accuracy_score(y_test, y_pred))

from pandas import DataFrame
Data ={'C Values': [0.001, 0.01, 0.1, 1.0, 10.0],'Accuracy': yval}
df = DataFrame(Data,columns=['C Values','Accuracy'])
print(df)

df.plot(x ='C Values', y='Accuracy', kind = 'scatter')
plt.show()

"""Using different Kernels"""

#Create a svm Classifier
clf = svm.SVC(kernel='linear') #Kernel

#Train the model using the training sets
clf.fit(X_train, y_train)

#Predict the response for test dataset
y_pred = clf.predict(X_test)
y_pred = y_pred.reshape(y_pred.shape[0],1)

#Import scikit-learn metrics module for accuracy calculation
from sklearn import metrics

# Model Accuracy: how often is the classifier correct?
print("Upon usingg SVM classifier:")
print("Accuracy:",metrics.accuracy_score(y_test, y_pred))

clf = svm.SVC(kernel='poly') #Kernel

#Train the model using the training sets
clf.fit(X_train, y_train)

#Predict the response for test dataset
y_pred = clf.predict(X_test)
y_pred = y_pred.reshape(y_pred.shape[0],1)

#Import scikit-learn metrics module for accuracy calculation
from sklearn import metrics

# Model Accuracy: how often is the classifier correct?
print("Upon usingg SVM classifier:")
print("Accuracy:",metrics.accuracy_score(y_test, y_pred))

#Create a svm Classifier
clf = svm.SVC(C=1.0,kernel='poly',degree = 1) #Kernel

#Train the model using the training sets
clf.fit(X_train, y_train)

#Predict the response for test dataset
y_pred = clf.predict(X_test)
y_pred = y_pred.reshape(y_pred.shape[0],1)

#Import scikit-learn metrics module for accuracy calculation
from sklearn import metrics

# Model Accuracy: how often is the classifier correct?
print("Upon usingg SVM classifier:")
print("Accuracy:",metrics.accuracy_score(y_test, y_pred))

clf = svm.SVC(kernel='poly', degree=5) #Kernel

#Train the model using the training sets
clf.fit(X_train, y_train)

#Predict the response for test dataset
y_pred = clf.predict(X_test)
y_pred = y_pred.reshape(y_pred.shape[0],1)

#Import scikit-learn metrics module for accuracy calculation
from sklearn import metrics

# Model Accuracy: how often is the classifier correct?
print("Upon usingg SVM classifier:")
print("Accuracy:",metrics.accuracy_score(y_test, y_pred))

#Create a svm Classifier
clf = svm.SVC(C=1.0,kernel='rbf') #Kernel

#Train the model using the training sets
clf.fit(X_train, y_train)

#Predict the response for test dataset
y_pred = clf.predict(X_test)
y_pred = y_pred.reshape(y_pred.shape[0],1)

#Import scikit-learn metrics module for accuracy calculation
from sklearn import metrics

# Model Accuracy: how often is the classifier correct?
print("Upon usingg SVM classifier:")
print("Accuracy:",metrics.accuracy_score(y_test, y_pred))

#Create a svm Classifier
clf = svm.SVC(C=1.0,kernel='sigmoid') #Kernel

#Train the model using the training sets
clf.fit(X_train, y_train)

#Predict the response for test dataset
y_pred = clf.predict(X_test)
y_pred = y_pred.reshape(y_pred.shape[0],1)

#Import scikit-learn metrics module for accuracy calculation
from sklearn import metrics

# Model Accuracy: how often is the classifier correct?
print("Upon usingg SVM classifier:")
print("Accuracy:",metrics.accuracy_score(y_test, y_pred))

"""**Understanding KNN Classification**

With different number of neighbours
"""

#using n_neighbours = 3
xv=[]
yv=[]
for i in range(3,33,3):
  xv.append(i)
  from sklearn.neighbors import KNeighborsClassifier
  neigh = KNeighborsClassifier(n_neighbors=i,weights='uniform')
  neigh.fit(X_train, y_train)
  yv.append(neigh.score(X_test, y_test))

Data = {'K Value': xv,
        'Accuracy': yv
       }

df = DataFrame(Data,columns=['K Value','Accuracy'])
df.plot(x ='K Value', y='Accuracy', kind = 'line')
plt.show()

print(df)

"""With different types of Weights"""

#using weights = uniform (default), n_neighbors=5
from sklearn.neighbors import KNeighborsClassifier
neigh = KNeighborsClassifier(n_neighbors=5,weights='uniform')
neigh.fit(X_train, y_train)

print("Mean Accuracy:",neigh.score(X_test, y_test))

#using weights = distance, n_neighbors=5
from sklearn.neighbors import KNeighborsClassifier
neigh = KNeighborsClassifier(n_neighbors=5,weights='distance')
neigh.fit(X_train, y_train)

print("Mean Accuracy:",neigh.score(X_test, y_test))