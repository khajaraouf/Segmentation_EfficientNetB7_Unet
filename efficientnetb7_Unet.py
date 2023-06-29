from tensorflow.keras.layers import Conv2D, BatchNormalization, Activation, MaxPool2D, Conv2DTranspose, Concatenate, Input
from tensorflow.keras.models import Model
from tensorflow.keras.applications import EfficientNetB0
import tensorflow as tf

print("TF Version: ", tf.__version__)

"""Defining the Convolution Block"""
def conv_block(input, num_filters):
    x = Conv2D(num_filters, 3, padding="same", kernel_initializer="he_normal")(input)
    x = BatchNormalization()(x)
    x = Activation("relu")(x)

    x = Conv2D(num_filters, 3, padding="same", kernel_initializer="he_normal")(x)
    x = BatchNormalization()(x)
    x = Activation("relu")(x)

    return x

"""Defining the Transpose Convolution Block"""
def decoder_block(input, skip_features, num_filters):
    x = Conv2DTranspose(num_filters, (2, 2), strides=2, padding="same")(input)
    x = Concatenate()([x, skip_features])
    #x = Dropout(0.05)(x)
    x = conv_block(x, num_filters)
    return x

"""Building the EfficientNetB7_UNet"""
def build_efficientNetB7_unet(input_shape):
    """ Input """
    inputs = Input(shape=input_shape, name='input_image')

    """ Pre-trained EfficientNetB7 Model """
    effNetB7 = tf.keras.applications.EfficientNetB7(input_tensor=inputs, include_top=False, 
                                                    weights="imagenet")

    for layer in effNetB7.layers[:-61]:
        layer.trainable = False
    for l in effNetB7.layers:
        print(l.name, l.trainable)

    """ Encoder """
    s1 = effNetB7.get_layer("input_image").output                   ## (512 x 512)
    s2 = effNetB7.get_layer("block1a_activation").output            ## (256 x 256)
    s3 = effNetB7.get_layer("block2a_activation").output            ## (128 x 128)
    s4 = effNetB7.get_layer("block3a_activation").output            ## (64 x 64)
    s5 = effNetB7.get_layer("block4a_activation").output            ## (32 x 32)

    """ Bridge """
    b1 = effNetB7.get_layer("block7a_activation").output  ## (16 x 16)

    """ Decoder """
    d1 = decoder_block(b1, s5, 512)                     ## (32 x 32)
    d2 = decoder_block(d1, s4, 256)                     ## (64 x 64)
    d3 = decoder_block(d2, s3, 128)                     ## (128 x 128)
    d4 = decoder_block(d3, s2, 64)                     ## (256 x 256)
    d5 = decoder_block(d4, s1, 32)                      ## (512 x 512)

    """ Output """
    outputs = Conv2D(1, 1, padding="same", activation="sigmoid")(d5)

    model = Model(inputs, outputs, name="EfficientNetB7_U-Net")
    return model

if __name__ == "__main__":
    input_shape = (IMAGE_WIDTH, IMAGE_HEIGHT, CHANNELS)
    model = build_efficientNetB7_unet(input_shape)
    model.summary()