**Chest X-ray based image classification**


This project was performed as part of Pattern Recognition and Algorithms coursework. 

Coding was completely done on Google Colabs and the notebook containing the code has been uploaded into this repository.
Dataset was downloaded from Kaggle. Due to size constraints, it was not uploaded to this repo.
The dataset was saved in my google drive and was then unzipped directly on to colab notebook.
The dataset was saved in my google drive and was then unzipped directly on to colab notebook 'termwork1.ipynb'.


This project implements a deep learning model using PyTorch to classify chest x-ray images as normal, viral pneumonia, or COVID-19.

Dataset
The COVID-19 Radiography Database from Kaggle is used. It contains normal, viral pneumonia and COVID-19 chest x-ray images.

Model
A pre-trained ResNet18 model is used as the base. The last fully connected layer is replaced to output 3 classes. Data transforms and custom dataset class implemented to load and preprocess the images.

Usage
The Jupyter notebook contains the full code. Main steps:

Install dependencies like PyTorch, torchvision, matplotlib etc.
Upload and extract dataset
Specify data directories and image transforms
Create custom dataset and dataloader
Initialize ResNet18 model
Train model using cross entropy loss and Adam optimizer
Evaluate on test data
Perform feature extraction from convolutional base
Fit SVM classifier for comparison
Evaluation

termwork1.ipynb: Main notebook with the implementation


Trained models and outputs are too large for GitHub and are available on request.

References
COVID-19 Radiography Database: https://www.kaggle.com/tawsifurrahman/covid19-radiography-database

