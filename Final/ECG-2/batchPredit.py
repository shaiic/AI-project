import tensorflow as tf
import numpy as np
import os
import time
import cv2

# 模型目录
CHECKPOINT_DIR = './runs/1566440950/checkpoints'
INCEPTION_MODEL_FILE = 'model/tensorflow_inception_graph.pb'

# inception-v3模型参数
BOTTLENECK_TENSOR_NAME = 'pool_3/_reshape:0'  # inception-v3模型中代表瓶颈层结果的张量名称
JPEG_DATA_TENSOR_NAME = 'DecodeJpeg/contents:0'  # 图像输入张量对应的名称

#类别字典
class_dict = {
    0: 'abnormal',
    1: 'normal',
}

start1 = time.time()
# 评估
checkpoint_file = r'C:\Users\zengy\Desktop\tensorflow\bak\runs\1566440950\checkpoints\model-100.0%-4650.meta'
with tf.Graph().as_default() as graph:
    with tf.Session().as_default() as sess:
        # 读取训练好的inception-v3模型
        with tf.gfile.FastGFile(INCEPTION_MODEL_FILE, 'rb') as f:
            graph_def = tf.GraphDef()
            graph_def.ParseFromString(f.read())

        # 加载inception-v3模型，并返回数据输入张量和瓶颈层输出张量
        bottleneck_tensor, jpeg_data_tensor = tf.import_graph_def(
            graph_def,
            return_elements=[BOTTLENECK_TENSOR_NAME, JPEG_DATA_TENSOR_NAME])

        # 加载元图和变量
        saver = tf.train.import_meta_graph(checkpoint_file)
        saver.restore(sess, checkpoint_file)
        print('加载时间：', time.time() - start1)
        start2 = time.time()

        imgPath = r'./test/'  #待预测图片路径
        extensions = {'jpg', 'jpeg', 'JPG', 'JPEG', 'png', 'PNG'}

        # 批量检测图片
        for data in os.listdir(imgPath):
            if not data.split('.')[-1] in extensions:
                continue
            file_path = os.path.join(imgPath, data)
            # 读取数据
            image_data = tf.gfile.FastGFile(file_path, 'rb').read()

            # 使用inception-v3处理图片获取特征向量
            bottleneck_values = sess.run(bottleneck_tensor,
                                         {jpeg_data_tensor: image_data})
            # 将四维数组压缩成一维数组，由于全连接层输入时有batch的维度，所以用列表作为输入
            bottleneck_values = [np.squeeze(bottleneck_values)]

            # 通过名字从图中获取输入占位符
            input_x = graph.get_operation_by_name(
                'BottleneckInputPlaceholder').outputs[0]

            # 我们想要评估的tensors
            predictions = graph.get_operation_by_name(
                'evaluation/ArgMax').outputs[0]

            # 收集预测值
            # all_predictions = []
            # all_predictions = sess.run(predictions,
            #                            {input_x: bottleneck_values})

            confidence = graph.get_tensor_by_name(
                'final_training_ops/Softmax:0')
            all_confidence = []
            all_confidence = sess.run(confidence, {input_x: bottleneck_values})
            result = all_confidence[0]
            # index = sess.run(tf.argmax(all_confidence, 1))
            # confidence = result #预测值的置信度

            if result[1] > 0.72:
                index = 1
            else:
                index = 0
            text = class_dict[index]
            # 图片绘制结果
            img = cv2.imread(file_path)
            shape = img.shape
            cv2.putText(img,
                        text,
                        org=(10, 30),
                        fontFace=cv2.FONT_HERSHEY_COMPLEX,
                        fontScale=0.8,
                        color=(0, 0, 255),
                        thickness=2)
            # cv2.namedWindow("image")
            # cv2.imshow('image', img)
            # cv2.waitKey(0)  # 显示 10000 ms 即 10s 后消失
            # cv2.destroyAllWindows()
            save_path = r'./test/result/'
            cv2.imwrite(save_path + 'new_{}'.format(data), img)


            # 打印出预测结果
            # temp = all_predictions[0]
            # print(temp)
            # print(type(temp))

            # index = str(all_predictions)[1]
            # index = int(index)

            print('{}  预测结果为：{}  置信度:{}'.format(file_path, class_dict[index],
                                                result))
            with open(save_path + 'result.txt', 'a+') as f:
                f.write('{}  预测结果为：{}  置信度:{}\n'.format(
                    file_path, class_dict[index], result))
        print('预测时间：', time.time() - start2)
