# import beamDetect
# import cv2
# from pathlib import Path
# import numpy as np

# def extract_feature(image):
#     resized = cv2.resize(image, (286, 286))     # 保證一致
#     mask = beamDetect.beamDetect(resized)
#     return mask.flatten().astype('float32') / 255.0

# if __name__ == "__main__":
#     image_folder = Path("C:/Users/samuel901213/Downloads/beam/render_20degreeTrim_accelerate")
#     feature_list = []
#     image_paths = []

#     for img_path in sorted(image_folder.glob("*.png")):
#         img = cv2.imread(str(img_path))
#         feature = extract_feature(img)
#         feature_list.append(feature)
#         image_paths.append(str(img_path))

#     np.save("features.npy", np.vstack(feature_list))
#     np.save("image_paths.npy", image_paths)  # 新增這個對應表
import cv2
import numpy as np
# img = cv2.imread("C:\Users\samuel901213\Downloads\beam\render_10degreeTrim_accelerate\worldX000Y000Z330_R144.npy", cv2.IMREAD_UNCHANGED)
image1 = np.load("C:\\Users\\samuel901213\\Downloads\\beam\\render_10degreeTrim_accelerate\\render_10degreeTrim_accelerate_npy\\worldX170Y250Z050_R143.npy")
print(image1.shape)