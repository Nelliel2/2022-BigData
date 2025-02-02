import os
import matplotlib.pyplot as plt
import pandas as pd
import pathlib
import tensorflow as tf
from tensorflow import keras
from keras import layers


data_dir = pathlib.Path('_lab-6\\movies_posters')
genres = pd.read_csv('_lab-6\\movies_dataset.csv')

genres_set = set(genres['genres_list'])
genres_dict = dict(zip(genres_set, range(len(genres_set))))
path = 'Смирнова Анна Николаевна\\_lab-6\\Data\\'

img_height = 56
img_width = 38
batch_size = 32

def load_imgs(data_dir=data_dir):
    image_count = len(list(data_dir.glob('*/*.jpg')))
    list_ds = tf.data.Dataset.list_files(str(data_dir/'*'), shuffle=True)
    #list_ds = list_ds.shuffle(image_count, reshuffle_each_iteration=False)
    return list_ds, image_count

def get_label(file_path, genres=genres):
    parts = tf.strings.split(file_path, sep=os.path.sep)
    img_id = tf.strings.split(parts[-1], '.')[-2]
    # g_list = list(genres[genres['id'] == img_id['genres_list']])
    # g_indeces = [genres_dict[x] for x in g_list]
    return int(genres.loc[genres['id'] == img_id, 'genres_list'].iloc[0][:4])

def get_id(file_path):
    parts = tf.strings.split(file_path, sep=os.path.sep)
    img_id = tf.strings.split(parts[-1], '.')[-2]
    return img_id

def decode_img(img, img_height=img_height, img_width=img_width):
    img = tf.io.decode_jpeg(img, channels=3)
    return tf.image.resize(img, [img_height, img_width])

def process_path(file_path):
    label = get_label(file_path)
    img = tf.io.read_file(file_path)
    img = decode_img(img)
    return img, label

train_ds = tf.keras.utils.image_dataset_from_directory(
    data_dir,
    validation_split=0.2,
    subset="training",
    seed=123,
    image_size=(img_height, img_width),
    batch_size=batch_size,
    label_mode='categorical')

val_ds = tf.keras.utils.image_dataset_from_directory(
    data_dir,
    validation_split=0.2,
    subset="validation",
    seed=123,
    image_size=(img_height, img_width),
    batch_size=batch_size,
    label_mode='categorical')

def get_model():
    try: 
        model = keras.models.load_model(filepath = path + 'my_model')
    except:
        model = tf.keras.models.Sequential([
            tf.keras.layers.Normalization(input_shape=(img_height, img_width, 3),
                                        mean=510, variance=255),
            tf.keras.layers.Conv2D(filters=512, kernel_size=(4, 4),
                                padding='same', activation='relu',
                                strides=(2, 2)),
            tf.keras.layers.MaxPool2D(pool_size=2, strides=None,
                                    padding='valid',
                                    data_format='channels_last'),
            tf.keras.layers.Conv2D(filters=256, kernel_size=(4, 4),
                                padding='same', activation='relu',
                                strides=(2, 2)),
            tf.keras.layers.MaxPool2D(pool_size=2, strides=None,
                                    padding='valid',
                                    data_format='channels_last'),
            tf.keras.layers.Conv2D(filters=256, kernel_size=(3, 3),
                                padding='same', activation='relu',
                                strides=(1, 1)),
            tf.keras.layers.Flatten(),
            tf.keras.layers.Dropout(.5),
            tf.keras.layers.Dense(64, activation='sigmoid'),
            tf.keras.layers.Dense(32, activation='sigmoid'),
            tf.keras.layers.Dense(10, activation='softmax')
        ])
    return model

def fit_model(model):
    model.compile(optimizer='adam', loss='categorical_crossentropy',
                metrics=tf.keras.metrics.CategoricalAccuracy(),
                run_eagerly=True)

    # Define the checkpoint callback that saves the model's weights at every epoch
    epoch = 0
    PATH = path + f'checkpoint_{epoch}.ckpt'

    cp_callback = tf.keras.callbacks.ModelCheckpoint(
                                filepath=PATH,
                                save_weights_only=True, # If False, full model
                                save_freq='epoch')

    model.summary()
    input("Press enter to start")


    hist = model.fit(train_ds,
                    validation_freq=[2, 5, 9],
                    epochs=3,
                    callbacks=[cp_callback], 
                    use_multiprocessing=True)

    model.save(filepath = path + 'my_model')
    metrics_df = pd.DataFrame(hist.history)
    print(metrics_df)
    metrics_df.to_csv(path + 'metrics_df')  
    return(metrics_df)

def plt_model():
    df = pd.read_csv(path + 'metrics_df')
    df["loss"].plot()
    plt.savefig(path + 'loss')
    plt.show()
    df["categorical_accuracy"].plot()
    plt.savefig(path + 'categorical_accuracy')
    plt.show()

model = get_model()
fit_model(model)
plt_model()