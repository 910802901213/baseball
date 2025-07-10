import bpy
import math
import os
import mathutils

obj = bpy.data.objects["baseball"]  # 你的棒球物件名
scene = bpy.context.scene

# 輸出資料夾
output_dir = bpy.path.abspath("//render_rotZ")
os.makedirs(output_dir, exist_ok=True)

# 設定輸出圖片格式和解析度
scene.render.image_settings.file_format = 'PNG'
scene.render.resolution_x = 640
scene.render.resolution_y = 640

original_matrix = obj.matrix_world.copy()

for i in range(5):
    angle_deg_X = i * (90)
    angle_rad_X = math.radians(angle_deg_X)
    rot_X = mathutils.Matrix.Rotation(angle_rad_X, 4, 'X')
    obj.matrix_world = rot_X @ original_matrix
    X_base = rot_X @ original_matrix
    bpy.context.view_layer.update()

    for j in range(5):
        angle_deg_Y = j * (90)
        angle_rad_Y = math.radians(angle_deg_Y)
        rot_Y = mathutils.Matrix.Rotation(angle_rad_Y, 4, 'Y')
        obj.matrix_world = rot_Y @ X_base 
        Y_base = rot_Y @ X_base 
        bpy.context.view_layer.update()

        for k in range(5):
                angle_deg_Z = k * (90)
                angle_rad_Z = math.radians(angle_deg_Z)
                rot_Z = mathutils.Matrix.Rotation(angle_rad_Z, 4, 'Z')
                obj.matrix_world = rot_Z @ Y_base
                bpy.context.view_layer.update()

                filename = f"worldX{angle_deg_X:03d}Y{angle_deg_Y:03d}Z{angle_deg_Z:03d}.png"
                scene.render.filepath = os.path.join(output_dir, filename)

                bpy.ops.render.render(write_still=True)

## 多次旋轉與拍攝
#for i in range(4):
#    angle_deg = i * 90
#    angle_rad = math.radians(angle_deg)

#    # 繞世界 Z 軸旋轉
#    rot = mathutils.Matrix.Rotation(angle_rad, 4, 'Z')
#    obj.matrix_world = rot @ obj.matrix_world

#    # 更新場景
#    bpy.context.view_layer.update()

#    # 設定輸出路徑
#    filename = f"worldZ_{angle_deg:03d}.png"
#    scene.render.filepath = os.path.join(output_dir, filename)

#    # 拍照儲存
#    bpy.ops.render.render(write_still=True)
