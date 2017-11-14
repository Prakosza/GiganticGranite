def cls(path):
    import sys
    import os
    import dlib
    import glob
    import cv2
    import pickle
    predictor_path = "shape_predictor_5_face_landmarks.dat"
    face_rec_model_path = "dlib_face_recognition_resnet_model_v1.dat"
    detector = dlib.get_frontal_face_detector()
    sp = dlib.shape_predictor(predictor_path)
    facerec = dlib.face_recognition_model_v1(face_rec_model_path)
    descriptors = []
    for f in glob.glob(os.path.join(path, "*.jpg")):
        img = cv2.imread(f)
        dets = detector(img, 1)
        for k, d in enumerate(dets):
            shape = sp(img, d)
            face_descriptor = facerec.compute_face_descriptor(img, shape)
            descriptors.append(face_descriptor)
    labels = dlib.chinese_whispers_clustering(descriptors, 0.5)
    num_classes = len(set(labels))
    biggest_class = None
    biggest_class_length = 0
    for i in range(0, num_classes):
        class_length = len([label for label in labels if label == i])
        if class_length > biggest_class_length:
            biggest_class_length = class_length
            biggest_class = i
    faces = []
    for i, label in enumerate(labels):
        if label == biggest_class:
            faces.append(i)
    pickle.dump(faces, open(os.path.join(path, os.path.basename(path)+".p"),"wb"), pickle.HIGHEST_PROTOCOL)
    print(os.path.join(path, os.path.basename(path)+".p"))




