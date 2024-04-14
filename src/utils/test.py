import tensorflow as tf

gpu = tf.config.list_physical_devices('CPU')
print(gpu)
print('--'*25)
print(len(gpu))