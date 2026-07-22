#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
游迹织梦 - 姿势识别打卡程序
三种姿势: 姆巴佩庆祝、比耶、双手叉腰
使用 MediaPipe Pose + Hands (solutions API)

运行方式: python main.py
按 q 退出, 按 s 手动拍照
"""

import cv2
import mediapipe as mp
import numpy as np
import time
import os
import requests
from datetime import datetime

# ============================================================
# 配置
# ============================================================
SERVER_URL = "http://118.24.77.181:8000"  # 后端地址
CAMERA_INDEX = 0                           # 摄像头编号
HOLD_FRAMES = 15                           # 连续检测到多少帧才算成功
COOLDOWN_SEC = 5                           # 拍照后冷却时间(秒)
SAVE_DIR = "photos"                        # 本地照片保存目录

os.makedirs(SAVE_DIR, exist_ok=True)

# ============================================================
# MediaPipe 初始化
# ============================================================
mp_pose = mp.solutions.pose
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

pose = mp_pose.Pose(
    static_image_mode=False,
    model_complexity=1,
    min_detection_confidence=0.6,
    min_tracking_confidence=0.6
)
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    min_detection_confidence=0.6,
    min_tracking_confidence=0.6
)


# ============================================================
# 工具函数
# ============================================================

def landmark_to_np(landmark, w, h):
    """将 MediaPipe landmark 转为 (x, y) 像素坐标"""
    return np.array([landmark.x * w, landmark.y * h])


def distance(a, b):
    """两点欧氏距离"""
    return np.linalg.norm(a - b)


def finger_states(hand_landmarks, w, h):
    """
    判断五根手指是否伸直
    返回: [thumb, index, middle, ring, pinky]  True=伸直
    """
    lm = hand_landmarks.landmark
    pts = np.array([[lm[i].x * w, lm[i].y * h] for i in range(21)])

    states = [False] * 5

    # 拇指: tip(4) 与 mcp(2) 的水平距离 > ip(3) 与 mcp(2) 的水平距离
    if abs(pts[4][0] - pts[2][0]) > abs(pts[3][0] - pts[2][0]):
        states[0] = True

    # 其余四指: tip 的 y < pip 的 y (坐标系向下)
    tips = [8, 12, 16, 20]
    pips = [6, 10, 14, 18]
    for i, (tip, pip) in enumerate(zip(tips, pips)):
        if pts[tip][1] < pts[pip][1]:
            states[i + 1] = True

    return states


# ============================================================
# 三种姿势检测
# ============================================================

def detect_mbappe(pose_lm, w, h):
    """
    姆巴佩庆祝: 双手交叉环抱胸前
    判据: 左手腕靠近右肩 且 右手腕靠近左肩
    """
    lm = pose_lm.landmark
    l_wrist = landmark_to_np(lm[mp_pose.PoseLandmark.LEFT_WRIST], w, h)
    r_wrist = landmark_to_np(lm[mp_pose.PoseLandmark.RIGHT_WRIST], w, h)
    l_shoulder = landmark_to_np(lm[mp_pose.PoseLandmark.LEFT_SHOULDER], w, h)
    r_shoulder = landmark_to_np(lm[mp_pose.PoseLandmark.RIGHT_SHOULDER], w, h)
    l_elbow = landmark_to_np(lm[mp_pose.PoseLandmark.LEFT_ELBOW], w, h)
    r_elbow = landmark_to_np(lm[mp_pose.PoseLandmark.RIGHT_ELBOW], w, h)

    shoulder_width = distance(l_shoulder, r_shoulder)
    if shoulder_width < 1:
        return False, 0

    # 左手腕靠近右肩
    lw_near_rs = distance(l_wrist, r_shoulder) / shoulder_width
    # 右手腕靠近左肩
    rw_near_ls = distance(r_wrist, l_shoulder) / shoulder_width

    # 肘部在胸口区域
    chest_y = (l_shoulder[1] + r_shoulder[1]) / 2
    elbows_ok = l_elbow[1] > chest_y * 0.8 and r_elbow[1] > chest_y * 0.8

    score = 0
    if lw_near_rs < 1.2:
        score += 35
    if rw_near_ls < 1.2:
        score += 35
    if elbows_ok:
        score += 20
    score += int(max(0, (1.0 - min(lw_near_rs, rw_near_ls)) * 10))

    return score >= 60, min(100, score)


def detect_peace(pose_lm, hand_lms_list, w, h):
    """
    比耶: 至少一只手 食指+中指伸直, 其余弯曲
    """
    if not hand_lms_list:
        return False, 0

    best_score = 0
    for hand_lm in hand_lms_list:
        states = finger_states(hand_lm, w, h)
        # 食指和中指伸直, 无名指和小指弯曲
        if states[1] and states[2] and not states[3] and not states[4]:
            score = 85
            if not states[0]:  # 拇指也弯曲更标准
                score = 95
            best_score = max(best_score, score)

    return best_score >= 85, best_score


def detect_arms_akimbo(pose_lm, w, h):
    """
    双手叉腰:
    - 双手放在腰部两侧
    - 手肘向外张开
    - 手臂弯曲
    """
    lm = pose_lm.landmark
    
    # 获取关键点
    l_shoulder = landmark_to_np(lm[mp_pose.PoseLandmark.LEFT_SHOULDER], w, h)
    r_shoulder = landmark_to_np(lm[mp_pose.PoseLandmark.RIGHT_SHOULDER], w, h)
    l_elbow = landmark_to_np(lm[mp_pose.PoseLandmark.LEFT_ELBOW], w, h)
    r_elbow = landmark_to_np(lm[mp_pose.PoseLandmark.RIGHT_ELBOW], w, h)
    l_wrist = landmark_to_np(lm[mp_pose.PoseLandmark.LEFT_WRIST], w, h)
    r_wrist = landmark_to_np(lm[mp_pose.PoseLandmark.RIGHT_WRIST], w, h)
    l_hip = landmark_to_np(lm[mp_pose.PoseLandmark.LEFT_HIP], w, h)
    r_hip = landmark_to_np(lm[mp_pose.PoseLandmark.RIGHT_HIP], w, h)
    
    shoulder_width = distance(l_shoulder, r_shoulder)
    if shoulder_width < 1:
        return False, 0
    
    # 计算腰部位置（肩膀和臀部的中间）
    waist_y = (l_shoulder[1] + r_shoulder[1] + l_hip[1] + r_hip[1]) / 4
    
    # 判断手腕是否在腰部附近
    # 允许的误差范围：肩宽的0.3倍
    waist_tolerance = shoulder_width * 0.3
    
    l_wrist_near_waist = abs(l_wrist[1] - waist_y) < waist_tolerance
    r_wrist_near_waist = abs(r_wrist[1] - waist_y) < waist_tolerance
    
    # 判断手肘是否向外张开
    # 手肘的x坐标应该在手腕和肩膀之间（或更外侧）
    l_elbow_out = l_elbow[0] < l_wrist[0] and l_elbow[0] < l_shoulder[0]
    r_elbow_out = r_elbow[0] > r_wrist[0] and r_elbow[0] > r_shoulder[0]
    
    # 计算分数
    score = 0
    
    # 双手都在腰部附近
    if l_wrist_near_waist:
        score += 35
    if r_wrist_near_waist:
        score += 35
    
    # 双手手肘向外张开
    if l_elbow_out:
        score += 15
    if r_elbow_out:
        score += 15
    
    # 额外奖励：手腕在身体两侧（x坐标在肩膀外侧）
    if l_wrist[0] < l_shoulder[0]:
        score += 5
    if r_wrist[0] > r_shoulder[0]:
        score += 5
    
    return score >= 70, min(100, score)


# ============================================================
# 上传
# ============================================================

def upload_photo(filepath, user_id="demo_user", spot_id="demo_spot"):
    """上传照片到服务器"""
    try:
        url = f"{SERVER_URL}/api/upload_photo"
        with open(filepath, "rb") as f:
            files = {"photo": (os.path.basename(filepath), f, "image/jpeg")}
            data = {"user_id": user_id, "spot_id": spot_id}
            resp = requests.post(url, files=files, data=data, timeout=10)
        if resp.status_code == 200:
            print(f"  [上传成功] {resp.json()}")
        else:
            print(f"  [上传失败] HTTP {resp.status_code}")
    except Exception as e:
        print(f"  [上传异常] {e}")


# ============================================================
# 主循环
# ============================================================

def main():
    print("=" * 50)
    print("  游迹织梦 - 姿势识别打卡")
    print("  三种姿势: 姆巴佩 / 比耶 / 双手叉腰")
    print("=" * 50)
    print()

    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        print("错误: 无法打开摄像头")
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    hold_count = {"mbappe": 0, "peace": 0, "akimbo": 0}
    last_photo_time = 0
    photo_count = 0

    print("按 q 退出, 按 s 手动拍照")
    print()

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        h, w = frame.shape[:2]
        clean_frame = frame.copy()  # 用于保存的干净照片
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb.flags.writeable = False

        # 检测
        pose_result = pose.process(rgb)
        hand_result = hands.process(rgb)

        pose_detected = None
        score = 0

        if pose_result.pose_landmarks:
            pose_lm = pose_result.pose_landmarks
            hand_lms_list = hand_result.multi_hand_landmarks if hand_result.multi_hand_landmarks else []

            # 检测三种姿势
            is_mbappe, s1 = detect_mbappe(pose_lm, w, h)
            is_peace, s2 = detect_peace(pose_lm, hand_lms_list, w, h)
            is_akimbo, s3 = detect_arms_akimbo(pose_lm, w, h)

            # 选择得分最高的
            candidates = []
            if is_mbappe:
                candidates.append(("mbappe", s1))
            if is_peace:
                candidates.append(("peace", s2))
            if is_akimbo:
                candidates.append(("akimbo", s3))

            if candidates:
                candidates.sort(key=lambda x: -x[1])
                best_name, best_score = candidates[0]
                hold_count[best_name] += 1
                for k in hold_count:
                    if k != best_name:
                        hold_count[k] = 0

                if hold_count[best_name] >= HOLD_FRAMES:
                    pose_detected = best_name
                    score = best_score
            else:
                for k in hold_count:
                    hold_count[k] = 0

            # 绘制骨架
            mp_draw.draw_landmarks(frame, pose_lm, mp_pose.POSE_CONNECTIONS)

        # 绘制手部关键点
        if hand_result.multi_hand_landmarks:
            for hl in hand_result.multi_hand_landmarks:
                mp_draw.draw_landmarks(frame, hl, mp_hands.HAND_CONNECTIONS)

        # 拍照
        now = time.time()
        if pose_detected and (now - last_photo_time) > COOLDOWN_SEC:
            last_photo_time = now
            photo_count += 1

            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"pose_{pose_detected}_{ts}_{photo_count:04d}.jpg"
            filepath = os.path.join(SAVE_DIR, filename)
            cv2.imwrite(filepath, clean_frame)
            print(f"  拍照! 姿势={pose_detected} 分数={score} -> {filepath}")

            # 照片已保存到本地 photos/ 目录

            for k in hold_count:
                hold_count[k] = 0

        # ---- 画面标注 ----
        labels = {
            "mbappe": ("Mbappe", (0, 0, 255)),
            "peace": ("Peace", (0, 255, 0)),
            "akimbo": ("Akimbo", (255, 0, 255)),
        }
        y_offset = 30
        for key, (name, color) in labels.items():
            count = hold_count[key]
            bar_w = int(count / HOLD_FRAMES * 200)
            cv2.putText(frame, name, (10, y_offset),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            cv2.rectangle(frame, (120, y_offset - 15), (120 + bar_w, y_offset + 5),
                          color, -1)
            y_offset += 35

        if pose_detected:
            names = {"mbappe": "MBAPPE!", "peace": "PEACE!", "akimbo": "AKIMBO!"}
            cv2.putText(frame, names.get(pose_detected, ""),
                        (w // 2 - 100, h - 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)

        cv2.putText(frame, f"Photos: {photo_count}", (w - 200, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        cv2.imshow("Pose Check-in", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break
        elif key == ord("s"):
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = os.path.join(SAVE_DIR, f"manual_{ts}.jpg")
            cv2.imwrite(filepath, clean_frame)
            print(f"  手动拍照 -> {filepath}")

    cap.release()
    cv2.destroyAllWindows()
    print(f"\n结束, 共拍摄 {photo_count} 张照片")


if __name__ == "__main__":
    main()
