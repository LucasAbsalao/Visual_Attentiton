import cv2
import numpy as np 
import math
from matplotlib import pyplot as plt
import os
from show import showAndDestroy, plot_img, exhibit


def lab_mean(img):
    L,a,b = cv2.split(img)
    titles = ["L","a","b"]
    #exhibit(1,3,titles,[L,a,b])
    Lmean = np.mean(L)
    amean = np.mean(a)
    bmean = np.mean(b)

    Imean = np.array(np.round([Lmean, amean, bmean]),dtype = np.uint8)
    
    return Imean


def gaussian_smoothing(img, kernel):
    result = cv2.filter2D(img,-1,kernel)
    result = cv2.GaussianBlur(img,(5,5),0)
    plt.imshow(result)
    plt.show()
    return result


def euclidean_distance(vector1,vector2):
    vector = (vector1-vector2)
    #print(vector1, vector2, vector)
    soma = np.float32(0)
    for x in vector:
        soma += x**2
    return math.sqrt(soma)

def saliency_map(img, Imean):
    img32f = np.float32(img)
    Imean32f = np.float32(Imean)

    Iwhc = [[euclidean_distance(Imean32f,element) for element in row] for row in img32f]
    Iwhc = np.array(Iwhc, dtype=np.uint8)
    return Iwhc

def k_means_gray(img):
    vectorized = img.reshape((-1))
    vectorized = np.float32(vectorized)

    k=6
    attempts = 10
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 0.95)

    ret, label, center = cv2.kmeans(vectorized,k,None,criteria,attempts,cv2.KMEANS_PP_CENTERS)

    center = np.uint8(center)
    res = center[label.flatten()]
    result_image = res.reshape((img.shape))

    return result_image

def segment_mean(img):
    return 2*(np.uint8(np.round(np.mean(img))))

def write_images(path_folder,name_folder,images):
    os.system('mkdir ' + path_folder)
    write_img = []
    for image in images:
        write_img.append(cv2.cvtColor(image, cv2.COLOR_RGB2BGR))

    cv2.imwrite(path_folder+name_folder+'_imagem_original.png', write_img[0])
    cv2.imwrite(path_folder+name_folder+'_saliency_map.png', write_img[1])
    cv2.imwrite(path_folder+name_folder+'_threshold_otsu.png', write_img[2])
    cv2.imwrite(path_folder+name_folder+'_kmeans_saliency_map.png', write_img[3])
    cv2.imwrite(path_folder+name_folder+'_kmeans_image.png', write_img[4])


PATH_IMAGES = 'images/'
PATH_OUTPUT = 'kmeans_saliency/'
path = PATH_IMAGES + 'stop.jpg'

name_folder = (path.split('/')[-1]).split('.')[0]
path_folder = PATH_OUTPUT + name_folder + '/'

img = cv2.imread(path)

img_lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
Imean = lab_mean(img_lab)


#Figura que representa a média das features do vetor no espaço Lab
Imean_rgb = cv2.cvtColor(np.array([[Imean]]), cv2.COLOR_LAB2RGB)
img_mean = np.full((img_lab.shape), Imean_rgb, dtype = np.uint8)
plt.imshow(img_mean)
plt.show()


#Smoothing da imagem com gaussiana 5x5 e criação do mapa de saliência
kernel=np.array([1,4,6,4,1])/16  
img_lab_smooth = gaussian_smoothing(img_lab,kernel)
saliency_img = saliency_map(img_lab_smooth,Imean)


#Imagem gerada utilizando a técnica de OTSU
img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
ret, thresh = cv2.threshold(saliency_img,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
attention_img_otsu = cv2.bitwise_and(img, img, mask=thresh)


plt.figure(figsize=(6.4*5,4.8*5), constrained_layout=False)
titles = ['Imagem Original', 'Mapa de Saliência', 'Imagem Final Otsu']
images = [img, saliency_img, attention_img_otsu]
exhibit(1,3,titles,images)


#Imagem gerada usando Kmeans
segment_saliency = k_means_gray(saliency_img)
segment_m = segment_mean(saliency_img)
print(segment_m)
ret, thresh = cv2.threshold(segment_saliency, segment_m, 255, cv2.THRESH_BINARY)
attention_img_kmeans = cv2.bitwise_and(img,img,mask=thresh)

plt.figure(figsize=(6.4*5,4.8*5), constrained_layout=False)
titles = ['Imagem Original', 'Mapa de Saliência Kmeans', 'Imagem Final Kmeans']
images = [img, segment_saliency, attention_img_kmeans]
exhibit(1,3,titles,images)

images = [img, saliency_img, attention_img_otsu, segment_saliency,attention_img_kmeans]
write_images(path_folder, name_folder,images)
