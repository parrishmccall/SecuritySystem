import numpy as np
import tensorflow as tf
import cv2
from utils import label_map_util
from twilio.rest import Client
from time import sleep
from utils import visualization_utils as vis_util

account_sid = '*'
auth_token = "*"
client = Client(account_sid, auth_token)


cap = cv2.VideoCapture(0)

# What model to download.
MODEL_NAME = 'ssdlite_mobilenet_v2_coco_2018_05_09'

PATH_TO_CKPT = MODEL_NAME + '/frozen_inference_graph.pb'

# List of the strings that is used to add correct label for each box.
PATH_TO_LABELS = "*"

NUM_CLASSES = 90


detection_graph = tf.Graph()
with detection_graph.as_default():
  od_graph_def = tf.GraphDef()
  with tf.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
    serialized_graph = fid.read()
    od_graph_def.ParseFromString(serialized_graph)
    tf.import_graph_def(od_graph_def, name='')


label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=NUM_CLASSES, use_display_name=True)
category_index = label_map_util.create_category_index(categories)


with detection_graph.as_default():
  with tf.Session(graph=detection_graph) as sess:
    while True:
      ret, image_np = cap.read()
      # Expand dimensions since the model expects images to have shape: [1, None, None, 3]
      image_np_expanded = np.expand_dims(image_np, axis=0)
      image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')
      # Each box represents a part of the image where a particular object was detected.
      boxes = detection_graph.get_tensor_by_name('detection_boxes:0')
      # Each score represent how level of confidence for each of the objects.
      # Score is shown on the result image, together with the class label.
      scores = detection_graph.get_tensor_by_name('detection_scores:0')
      classes = detection_graph.get_tensor_by_name('detection_classes:0')
      num_detections = detection_graph.get_tensor_by_name('num_detections:0')
      # Actual detection.
      (boxes, scores, classes, num_detections) = sess.run(
          [boxes, scores, classes, num_detections],
          feed_dict={image_tensor: image_np_expanded})

      boxes = np.squeeze(boxes)
      scores = np.squeeze(scores)
      classes = np.squeeze(classes)
      
      # Alerts if person spotted
      for i, j in zip(scores, classes):
          if i > .6 and j ==1:
             client.messages.create(
                to="*",
                from_="*",
                body="Person Spotted"
              )
              sleep(2)


      # Visualization of the results of a detection.
      # vis_util.visualize_boxes_and_labels_on_image_array(
      #     image_np,
      #     boxes,
      #     classes.astype(np.int32),
      #     scores,
      #     category_index,
      #     use_normalized_coordinates=True,
      #     line_thickness=8)
      #
      # cv2.imshow('object detection', cv2.resize(image_np, (800,600)))
      if cv2.waitKey(25) & 0xFF == ord('q'):
        cv2.destroyAllWindows()
        break
