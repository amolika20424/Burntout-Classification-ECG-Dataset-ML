# -*- coding: utf-8 -*-
"""ml_hrv_project.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1-WYIAlzv-gPH-SQDZiojuhUBSfeUSRYH
"""

def heart_rate_feature_extraction(data, sampling_rate = 500):

    plt.style.use('bmh')

    cleaned = nk.ecg_clean(data, sampling_rate=sampling_rate, method="pantompkins1985") # cleaning ECG 
    pantompkins1985 = nk.ecg_findpeaks(cleaned, method="pantompkins1985") # find the R peaks
    hrv_df = pd.DataFrame(pantompkins1985)

    hrv_df["RR Intervals"] = hrv_df["ECG_R_Peaks"].diff()
    hrv_df.loc[0, "RR Intervals"]=hrv_df.loc[0]['ECG_R_Peaks'] # the first datapoint contain Nan we manually fix it

    # hrvana.plot_timeseries(hrv_df["RR Intervals"].values.tolist()) # visualise 90 RR intervals

    clean_rri = hrv_df['RR Intervals'].values/sampling_rate*1000 # Convert sample to ms
    clean_rri = hrvana.remove_outliers(rr_intervals=clean_rri, low_rri=300, high_rri=2000)
    clean_rri = hrvana.interpolate_nan_values(rr_intervals=clean_rri, interpolation_method="linear")
    clean_rri = hrvana.remove_ectopic_beats(rr_intervals=clean_rri, method="malik")
    clean_rri = hrvana.interpolate_nan_values(rr_intervals=clean_rri, interpolation_method="linear")

    # hrvana.plot_timeseries(clean_rri) # due to the size of the dataset, here we only show the 90 nnis
    # plt.title("NN intervals")
    # plt.title("NN Interval Over Time")
    # plt.ylabel("ms")
    # plt.xlabel("NN Interval Index")

    hrv_df["RR Intervals"] = clean_rri 
    hrv_df["RR Intervals"].isna().any()

    nn_epoch = hrv_df['RR Intervals'].values

    
    feature_list = []
    all_hr_features = {}
    all_hr_features.update(hrvana.get_time_domain_features(nn_epoch))
    all_hr_features.update(hrvana.get_frequency_domain_features(nn_epoch))
    all_hr_features.update(hrvana.get_poincare_plot_features(nn_epoch))
    all_hr_features.update(hrvana.get_csi_cvi_features(nn_epoch))
    all_hr_features.update(hrvana.get_geometrical_features(nn_epoch))
    feature_list.append(all_hr_features)
    hrv_feature_df = pd.DataFrame(feature_list)
    hrv_feature_df.isna().any()
    
    return hrv_feature_df  #Return cleaned updated rri_interval in ms.

import pandas as pd
def return_hrv_participant_wise(data: pd.DataFrame(), sampling_rate = 500):

    hrv = pd.DataFrame()

    # for each_column in data.columns:
    list_of_leads = ['II', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6']
    for each_column in list_of_leads:
      
        try:
            df1 = heart_rate_feature_extraction(np.array(data[each_column]), sampling_rate = sampling_rate)
            # df1 =norm_api.Ecg_analysis().Neurokit2().heart_rate_feature_extraction(np.array(data[each_column]), sampling_rate = sampling_rate)
            

            df1.columns = each_column + "_"  + df1.columns
            hrv = pd.concat([hrv, df1], axis = 1)

            hrv.reset_index(inplace = True, drop =True)
            
        except:
            continue

    return hrv

!pip install neurokit2
!pip install hrv-analysis
!pip install pyhrv

import pandas as pd
import neurokit2 as nk  # This package can process ECG
import hrvanalysis as hrvana # RR interval processing package
import pandas as pd
import numpy as np
import pandas as pd
from matplotlib import style
import matplotlib.pyplot as plt
import hrvanalysis as hrvana # RR interval processing package
import numpy as np
import neurokit2 as nk  # This package can process ECG
import pyhrv.tools as tools
from pyhrv.hrv import hrv

from google.colab import drive
drive.mount('/content/drive')

RM_1001 = pd.read_excel("/content/drive/MyDrive/ecg_dataset/Visit 1/Group 1/1001 Rm/1001_Rm.xls")
RM_1001 = RM_1001.drop([0, 5007]) ## dropping nan values
RM_1001

!pip install pywavelets

import numpy as np
import pywt
from sklearn.cluster import KMeans

def DWPT(ecg_data):
    coeffs = pywt.dwt(ecg_data, 'db1', level=4)
    return coeffs

def cluster_ecg_data(ecg_data):
    coeffs = DWPT(ecg_data)
    kmeans = KMeans(n_clusters=2, random_state=0).fit(coeffs)
    return kmeans.labels_

# Example usage
ecg_data = np.random.rand(1000)
labels = cluster_ecg_data(ecg_data)
print(labels)

df = return_hrv_participant_wise(RM_1001)
df.shape

df

df['II_tinn']

df.dropna(axis=1, how = 'all', inplace=True) # drop columns with all missing values
df.dropna(axis=0, how = 'any', inplace=True) # drop rows with any missing values

df.shape

df

col_names = df.columns.to_list()
## 30 hrv features per lead extracted
col_names

"""Making complete dataset

"""

class df_holder:
    def __init__(self, df): 
        self.df = df

df__ = pd.read_pickle("/content/drive/MyDrive/class_dataset.pkl")
df__.loc[1001,'V1_df'].df

_lr,_lc = 3,4
_leads = [
    [['I'],['avR'],['V1'],['V4']],
    [['II'],['avL'],['V2'],['V5']],
    [['III'],['avF'],['V3'],['V6']]
]

df__1001 = df__.loc[1001,'V1_df'].df


fig,ax = plt.subplots(_lr,_lc, figsize=(_lr*7,_lc*4))
#fig.set_dpi(150)
for i in range(0,3):
    for j in range(0,4):
        _key = _leads[i][j][0]
        ax[i,j].set_title(_key)
        ax[i,j].plot(df__1001[_key], color='black', linewidth=0.6)
        ax[i,j].set_ylim((-1500,1500))
        ax[i,j].set_xlim((0,5000))
        ax[i,j].hlines(0,0,5000,color='black',linestyle='dotted')


plt.show()

from scipy import signal

df = df__.loc[1001,'V1_df'].df

fig,ax = plt.subplots(_lr,_lc, figsize=(_lr*7,_lc*4))
for i in range(0,3):
    for j in range(0,4):
        _key = _leads[i][j][0]
        ax[i,j].set_title(_key)
        sos = signal.butter(5, 0.3, 'hp', fs=2000, output='sos')
        sig = df[_key]
        sig = sig.drop([0, 5007])
        clean_sig = nk.ecg_clean(sig, 500)
        filtd=signal.sosfilt(sos, sig)
        ax[i,j].plot(sig, label='Raw Signal')
        ax[i,j].plot(clean_sig, label='Cleaned Signal')
        ax[i,j].legend(['Raw Signal', 'Cleaned Signal'])

plt.show()

dfs = ['V1_df', 'V2_df', 'V3_df']
hrv_dataset = df__
for ind in df__.index:
    for df_visit in dfs:
        ndf = df__.loc[ind, df_visit].df
        ndf = ndf.drop([0, 5007])
        ndf_hrv = return_hrv_participant_wise(ndf)
        hrv_dataset.loc[ind, df_visit+'HRV'] = df_holder(ndf_hrv)



    # ndf_hrv.dropna(axis=1, how = 'all', inplace=True) # drop columns with all missing values
    # ndf_hrv.dropna(axis=0, how = 'any', inplace=True) # drop rows with any missing values

hrv_dataset

hrv_dataset.columns.to_list()

hrv_dataset = hrv_dataset.drop(['V1_path',
 'V2_path',
 'V3_path'], axis = 1)

hrv_dataset = hrv_dataset.drop(['V1_path',
 'V2_path',
 'V3_path',
 'V1_df',
 'V2_df',
 'V3_df'], axis = 1)

hrv_dataset.loc[1001, 'V1_df'].df

hrv_dataset.loc[1001, 'V1_df'].df.values.tolist()[1]

hrv_dataset.rename(columns = {'V1_dfHRV': 'V1_df', 'V2_dfHRV': 'V2_df', 'V3_dfHRV': 'V3_df'}, inplace = True)
hrv_dataset

lds = {"id":[],"v":[]}
for i in hrv_dataset.loc[1001, "V1_df"].df.columns.tolist():
    lds[i]=[]

for i in hrv_dataset.loc[1001, "V1_dfHRV"].df.columns.tolist():
    lds[i]=[]

n_ds = pd.DataFrame(lds)


for i in hrv_dataset.index:
    row = [i, hrv_dataset.loc[i, "V1"]]
    row.extend(hrv_dataset.loc[i, "V1_df"].df.values.tolist()[0])
    row.extend(hrv_dataset.loc[i, "V1_dfHRV"].df.values.tolist()[0])
    n_ds.loc[len(n_ds)] = row
    row = [i, hrv_dataset.loc[i, "V2"]]
    row.extend(hrv_dataset.loc[i, "V2_df"].df.values.tolist()[0])
    row.extend(hrv_dataset.loc[i, "V2_dfHRV"].df.values.tolist()[0])
    n_ds.loc[len(n_ds)] = row
    row = [i, hrv_dataset.loc[i, "V3"]]
    row.extend(hrv_dataset.loc[i, "V3_df"].df.values.tolist()[0])
    row.extend(hrv_dataset.loc[i, "V3_dfHRV"].df.values.tolist()[0])
    n_ds.loc[len(n_ds)] = row

n_ds

n_ds.dropna(axis=1, how = 'all', inplace=True) # drop columns with all missing values
n_ds.dropna(axis=0, how = 'any', inplace=True) # drop rows with any missing values

n_ds

n_ds.to_pickle('complete_data.pkl')

li = n_ds.columns.to_list()[2:]
len(li)

"""Clustering"""

import pandas as pd

n_ds = pd.read_pickle('/content/drive/MyDrive/ecg_dataset/complete_data.pkl')
n_ds = n_ds.rename(columns={'v': 'target'})

n_ds

# Commented out IPython magic to ensure Python compatibility.
# importing required libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
# %matplotlib inline
from sklearn.cluster import KMeans
from sklearn.datasets import load_digits
from sklearn.feature_selection import SelectKBest, chi2
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, silhouette_score
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA

df = n_ds.loc[:, 'v':'V6_triangular_index']
desired_class_df = df[df['v'] == 1]
duplicated_df = pd.concat([df] + [desired_class_df] * 2)

# count the number of samples in each class again to verify the class imbalance has been corrected
new_class_count = duplicated_df['v'].value_counts()
print(new_class_count)

from sklearn.cluster import KMeans

X = n_ds.loc[:, 'II_mean_nni':'V6_triangular_index']
wcss = [] 
for i in range(1, 11): 
    kmeans = KMeans(n_clusters = i, init = 'k-means++', random_state = 42)
    kmeans.fit(X) 
    wcss.append(kmeans.inertia_)  
      
plt.plot(range(1, 11), wcss) 
plt.xlabel('Number of clusters')
plt.ylabel('WCSS') 
plt.show()

duplicated_df

acc = []

dis = []
k = list(range(1,211))
def k2acc(df, K):

    data = df.loc[:, 'II_mean_nni':'V6_triangular_index']
    for k in K:
        
        data = df.loc[:, 'II_mean_nni':'V6_triangular_index']
        scaler = StandardScaler()

        data_scaled = scaler.fit_transform(data)
        pca = PCA(n_components = k)
        pC = pca.fit_transform(data_scaled)
        principalDf = pd.DataFrame(data = pC
             , columns = list(range(1,k+1)))
        data_scaled = principalDf

        pd.DataFrame(data_scaled).describe()
        kmeans = KMeans(n_clusters = 3, init='k-means++', n_init='auto', random_state = 42)
        kmeans.fit(data_scaled)
        pred = kmeans.predict(data_scaled)

        dis.append(silhouette_score(data_scaled, pred))
        acc.append(accuracy_score(df['target'].astype(int), pred))

k2acc(n_ds, k)

plt.plot(k, acc)

# Setting up labels and title
plt.xlabel('Value of k (k features selected)')
plt.ylabel('Acuuracy')
plt.title('k vs accuracy')

# Displaying the plot
plt.show()

plt.plot(k, dis)

# Setting up labels and title
plt.xlabel('Value of k (k features selected)')
plt.ylabel('Silhoutte score')
plt.title('k vs silhoutte score')

# Displaying the plot
plt.show()

## k = 7 is best
print(dis)
index = dis.index(max(dis))

index+1

from sklearn.datasets import load_digits
from sklearn.feature_selection import SelectKBest, chi2
data = n_ds.loc[:, 'II_mean_nni':'V6_triangular_index']
# X_new = SelectKBest(chi2, k=index+1).fit_transform(data, n_ds['v'])
# X_new.shape

# standardizing the data
from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()

# data= X_new
data_scaled = scaler.fit_transform(data)

# statistics of scaled data
pd.DataFrame(data_scaled).describe()

pca = PCA(n_components = 1)
pC = pca.fit_transform(data_scaled)
tm=[]
for i in range(1, index+2):
    tm.append(str(i))
principalDf = pd.DataFrame(data = pC, columns = ['feature'])
data_scaled = principalDf

# k means using 2 clusters and k-means++ initialization
from sklearn.cluster import KMeans
kmeans = KMeans(n_clusters = 3, init='k-means++')
kmeans.fit(data_scaled)
pred = kmeans.predict(data_scaled)
print(data_scaled)
print(pred)

fig = plt.figure(figsize = (8,8))
ax = fig.add_subplot(1,1,1) 
ax.set_xlabel('Principal Component 1', fontsize = 15)
ax.set_ylabel('Principal Component 2', fontsize = 15)
ax.set_title('2 component PCA', fontsize = 20)

#targets = ['Iris-setosa', 'Iris-versicolor', 'Iris-virginica']
colors = ['r', 'g']
# for target, color in zip(pred,colors):
for i in data_scaled.index:
    ax.scatter(data_scaled.loc[i, 'pc1']
                , data_scaled.loc[i, 'pc2']
                , c = colors[data_scaled.loc[i,'target']]
                )
ax.grid()

fig = plt.figure(figsize = (8,8))
ax = fig.add_subplot(1,1,1) 
ax.set_xlabel('Principal Component 1', fontsize = 15)
ax.set_ylabel('Principal Component 2', fontsize = 15)
ax.set_title('2 component PCA', fontsize = 20)

#targets = ['Iris-setosa', 'Iris-versicolor', 'Iris-virginica']
colors = ['r', 'g']
# for target, color in zip(pred,colors):
for i in data_scaled.index:
    ax.scatter(data_scaled.loc[i, 'pc1']
                , data_scaled.loc[i, 'pc2']
                , c = colors[data_scaled.loc[i,'cluster']]
                )
ax.grid()

# inertia on the fitted data
kmeans.inertia_

frame = pd.DataFrame(data_scaled)
frame['cluster'] = pred
frame['target'] = n_ds['target'].astype(int)
frame['cluster'].value_counts()
'''
0    464
1    142
Name: target

1    230
0    226
2    150
Name: cluster

'''

frame['target'].value_counts()

frame

from sklearn.metrics import accuracy_score, silhouette_score
print('Accuracy:', accuracy_score(frame['target'], frame['cluster']))
print('Silhoutte score:', silhouette_score(data_scaled, frame['cluster']))

from sklearn.metrics import pairwise_distances
labels = kmeans.labels_
centroids = kmeans.cluster_centers_

# compute pairwise distances between centroids
distances = pairwise_distances(centroids)
distances

# spectral clustering
from numpy import unique
from numpy import where
from sklearn.datasets import make_classification
from sklearn.cluster import SpectralClustering
from matplotlib import pyplot


# define the model
model = SpectralClustering(n_clusters=3)
# fit model and predict clusters
yhat = model.fit_predict(data_scaled)
# retrieve unique clusters
print(yhat)
clusters = unique(yhat)
print('Clusters', clusters)
print(pd.DataFrame(yhat).value_counts())

from sklearn.metrics import accuracy_score, silhouette_score
print('Accuracy:', accuracy_score(yhat, data_scaled['v']))
print('Silhoutte score:', silhouette_score(data_scaled['v'], yhat))

# gaussian mixture clustering
from numpy import unique
from numpy import where
from sklearn.datasets import make_classification
from sklearn.mixture import GaussianMixture
from matplotlib import pyplot
model = GaussianMixture(n_components=2)
# fit the model
model.fit(data_scaled)
# assign a cluster to each example
yhat = model.predict(data_scaled)
print(yhat)
clusters = unique(yhat)
print('Clusters', clusters)
print(pd.DataFrame(yhat).value_counts())

from sklearn.metrics import accuracy_score, silhouette_score
print('Accuracy:', accuracy_score(yhat, frame['target']))
print('Silhoutte score:', silhouette_score(frame['target'], yhat))

# optics clustering
from numpy import unique
from numpy import where
from sklearn.datasets import make_classification
from sklearn.cluster import OPTICS
from matplotlib import pyplot

model = OPTICS(eps=0.8, min_samples=10)
# fit model and predict clusters
yhat = model.fit_predict(data_scaled)
# retrieve unique clusters
yhat += 1
clusters = unique(yhat)
print('Clusters', clusters)
print(pd.DataFrame(yhat).value_counts())

# from sklearn.metrics import accuracy_score, silhouette_score
# print('Accuracy:', accuracy_score(yhat, frame['target']))
# print('Silhoutte score:', silhouette_score(data_scaled, yhat))

"""SVM"""

from sklearn import svm
clf = svm.SVC()
clf.fit(data_scaled, n_ds['v'])

svm_pred = clf.predict(data_scaled)

svm_pred

from sklearn import metrics
print("Accuracy:",metrics.accuracy_score(frame['cluster'], svm_pred))

"""
# Classifiers
"""

