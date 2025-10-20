import pandas as pd
import numpy as np
import os
from os import listdir

def euclidean_distance(x1, y1, x2, y2):
	return np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

def compute_head_orientation(data):
	dx = data.loc[data['bodypart'] == 'ear_right', 'x'] - data.loc[data['bodypart'] == 'ear_left', 'x']
	dy = data.loc[data['bodypart'] == 'ear_right', 'y'] - data.loc[data['bodypart'] == 'ear_left', 'y']
	angle = np.arctan2(dy, dx)
	return angle

def compute_speed(data):
	dx = data.loc[data['bodyparts'] == 'body_center', 'x'].diff().fillna(0)
	dy = data.loc[data['bodyparts'] == 'body_center', 'y'].diff().fillna(0)
	return np.sqrt(dx ** 2 + dy ** 2)

def compute_rearing(data):
	speedThresh = 1.0
	bodyThresh = 20
	noseX = data.loc[data['bodyparts'] == 'nose', 'x']
	noseY = data.loc[data['bodyparts'] == 'nose', 'y']
	bodyX = data.loc[data['bodyparts'] == 'body_center', 'x']
	bodyY = data.loc[data['bodyparts'] == 'body_center', 'y']
	nose_to_body_distance = euclidean_distance(noseX, noseY, bodyX, bodyY)
	speed = compute_speed(data)
	# big distance and small speed
	isRearing = (speed < speedThresh) & (nose_to_body_distance > bodyThresh)
	return isRearing

def compute_grooming(data):
	thresh = 5
	noseX = data.loc[data['bodyparts'] == 'nose', 'x']
	noseY = data.loc[data['bodyparts'] == 'nose', 'y']
	bodyX = data.loc[data['bodyparts'] == 'body_center', 'x']
	bodyY = data.loc[data['bodyparts'] == 'body_center', 'y']
	nose_body_dist = euclidean_distance(noseX, noseY, bodyX, bodyY)
	nose_body_diff = nose_body_dist.diff().abs().fillna(0)
	isGrooming = (nose_body_diff > thresh)
	return isGrooming

def compute_approach(mouse1, mouse2):
	# Determină dacă mouse1 se apropie sau se îndepărtează de mouse2.
    # Returnează 1 = apropie, -1 = se îndepărtează, 0 = neutru
	thresh = 50
	bodyX1 = mouse1.loc[mouse1['bodypart'] == 'body_center', 'x']
	bodyY1 = mouse1.loc[mouse1['bodypart'] == 'body_center', 'y']
	bodyX2 = mouse2.loc[mouse2['bodypart'] == 'body_center', 'x']
	bodyY2 = mouse2.loc[mouse2['bodypart'] == 'body_center', 'y']
	dist = euclidean_distance(mouse1['body_x'], mouse1['body_y'], mouse2['body_x'], mouse2['body_y'])
	dist_diff = dist.diff().fillna(0)
	if dist_diff < -thresh:
		return 1
	elif dist_diff > thresh:
		return -1
	return 0

def compute_chasing(mouse1, mouse2):
	maxDistance = 50
	threshAngle = np.pi/6
	bodyX1 = mouse1.loc[mouse1['bodyparts'] == 'body_center', 'x']
	bodyY1 = mouse1.loc[mouse1['bodyparts'] == 'body_center', 'y']
	bodyX2 = mouse2.loc[mouse2['bodyparts'] == 'body_center', 'x']
	bodyY2 = mouse2.loc[mouse2['bodyparts'] == 'body_center', 'y']
	dx = bodyX2 - bodyX1
	dy = bodyY2 - bodyY1
	angle_to_other = np.arctan2(dy, dx)
	orientation_diff = np.abs(angle_to_other - mouse1['head_orientation'])
	following_flag = (euclidean_distance(bodyX1, bodyY1, bodyX2, bodyY2) < maxDistance) & (orientation_diff < threshAngle)
	return following_flag

def compute_contact(mouse1, mouse2):
	thresh = 10
	bodyX1 = mouse1.loc[mouse1['bodyparts'] == 'body_center', 'x']
	bodyY1 = mouse1.loc[mouse1['bodyparts'] == 'body_center', 'y']
	bodyX2 = mouse2.loc[mouse2['bodyparts'] == 'body_center', 'x']
	bodyY2 = mouse2.loc[mouse2['bodyparts'] == 'body_center', 'y']
	dist = euclidean_distance(bodyX1, bodyY1, bodyX2, bodyY2)

	if dist < thresh:
		return 1
	return 0

def compute_sniffingN2N(mouse1, mouse2):
	thresh = 15
	noseX1 = mouse1.loc[mouse1['bodyparts'] == 'nose', 'x']
	noseY1 = mouse1.loc[mouse1['bodyparts'] == 'nose', 'y']
	noseX2 = mouse2.loc[mouse2['bodyparts'] == 'nose', 'x']
	noseY2 = mouse2.loc[mouse2['bodyparts'] == 'nose', 'y']
	dist = euclidean_distance(noseX1, noseY1, noseX2, noseY2)

	if dist < thresh:
		return 1
	return 0

def compute_sniffingN2T(mouse1, mouse2):
	thresh = 20
	noseX1 = mouse1.loc[mouse1['bodyparts'] == 'nose', 'x']
	noseY1 = mouse1.loc[mouse1['bodyparts'] == 'nose', 'y']
	tailX2 = mouse2.loc[mouse2['bodyparts'] == 'tail_tip', 'x']
	tailY2 = mouse2.loc[mouse2['bodyparts'] == 'tail_tip', 'y']
	dist = euclidean_distance(noseX1, noseY1, tailX2, tailY2)

	if dist < thresh:
		return 1
	return 0

def compute_sniffing(prev_nose_x, prev_nose_y, nose_x, nose_y, prev_body_x, prev_body_y, body_x, body_y, nose_thresh=2, body_thresh=1):
	nose_dist = euclidean_distance(prev_nose_x, prev_nose_y, nose_x, nose_y)
	body_dist = euclidean_distance(prev_body_x, prev_body_y, body_x, body_y)
	return 1 if (nose_dist > nose_thresh and body_dist < body_thresh) else 0

def compute_locomotion(prev_body_x, prev_body_y, body_x, body_y):
	speed_thresh = 1.0
	dx = body_x - prev_body_x
	dy = body_y - prev_body_y
	speed = np.sqrt(dx ** 2 + dy ** 2)
	if speed > 5.0: # running
		return 1
	if speed < 5.0 & speed > 1.0: # walking
		return -1
	return 0

def compute_freezing(prev_body_x, prev_body_y, body_x, body_y):
	thresh = 0.5
	speed = euclidean_distance(prev_body_x, prev_body_y, body_x, body_y)
	return 1 if speed < thresh else 0

def miniDF(dir_path):
	dfs = []

	for filename in os.listdir(dir_path):
		if filename.endswith('.parquet'):
			file_path = os.path.join(dir_path, filename)
			df = pd.read_parquet(file_path)
			dfs.append(df)
	combinedDF = pd.concat(dfs, ignore_index=True)
	return combinedDF

if __name__ == "__main__":
	tracking_folder = 'train_tracking/' # what the model sees (the coordonates of the mice)
	annotations_folder = 'train_annotation/' # what the model needs to learn y (comportament labels)

	newDF = pd.DataFrame(columns=['video_frame', 'head_orientation', 'nose2nose', 'nose2tail', 'rearing', 'chasing', 'approach', 'contact', 'walking', 'running', 'freezing'])

	for dirpath, dirnames, filenames in os.walk(tracking_folder):
		# splitting the dataset in mini-batches
		# computing the dataset folder by folder
		for dir in dirnames:
			dir_path = os.path.join(dirpath, dir)
			ann_path = os.path.join(annotations_folder, dir)

			if not os.path.exists(ann_path):
				continue

			x_df = miniDF(dir_path)
			y_df = miniDF(ann_path)
			video_id = dir

			prevPositions = {}
			frames = x_df['video_frame'].unique()
			for frame in frames:
				frameData = x_df[x_df['video_frame'] == frame]

				for mouseID, mouseDF in frameData.groupby('mouse_id'):
					bx = float(mouseDF.loc[mouseDF['bodypart'] == 'body_center', 'x'])
					by = float(mouseDF.loc[mouseDF['bodypart'] == 'body_center', 'y'])
					nx = float(mouseDF.loc[mouseDF['bodypart'] == 'nose', 'x'])
					ny = float(mouseDF.loc[mouseDF['bodypart'] == 'nose', 'y'])
					tx = float(mouseDF.loc[mouseDF['bodypart'] == 'tail_tip', 'x'])
					ty = float(mouseDF.loc[mouseDF['bodypart'] == 'tail_tip', 'y'])

					if mouseID in prevPositions:
						prev = prevPositions[mouseID]
						action = compute_locomotion(prev['bx'], prev['by'], bx, by) # running sau walking
					else:
						action = "freezing" # altfel sta pe loc

					prevPositions[mouseID] = {'bx': bx, 'by': by}

					# get mouse status
					speed = compute_speed(mouseDF)

					newDF.append({'row_id': len(newDF), 'video_id': video_id, 'agent_id': mouseID, 'target_id': np.nan, 'action': action, 'start_frame': frame, 'stop_frame': frame, 'speed': com})

				miceID = frameData['mouse_id'].unique()
				nrOfMice = miceID.count()
				for i in nrOfMice - 1:
					m1 = frameData[frameData['mouse_id'] == miceID[i]]
					m2 = frameData[frameData['mouse_id'] == miceID[i + 1]]

					bx1, by1 = float(m1.loc[m1['bodypart'] == 'body_center', 'x']), float(m1.loc[m1['bodypart'] == 'body_center', 'y'])
					bx2, by2 = float(m2.loc[m2['bodypart'] == 'body_center', 'x']), float(m2.loc[m2['bodypart'] == 'body_center', 'y'])
					nx1, ny1 = float(m1.loc[m1['bodypart'] == 'nose', 'x']), float(m1.loc[m1['bodypart'] == 'nose', 'y'])
					nx2, ny2 = float(m2.loc[m2['bodypart'] == 'nose', 'x']), float(m2.loc[m2['bodypart'] == 'nose', 'y'])
					tx2, ty2 = float(m2.loc[m2['bodypart'] == 'tail_tip', 'x']), float(m2.loc[m2['bodypart'] == 'tail_tip', 'y'])

					if compute_approach(m1, m2):
						newDF.append({
					'row_id': len(newDF),
					'video_id': video_id,
					'agent_id': miceID[i],
					'target_id': miceID[i + 1],
					'action': 'contact',
					'start_frame': frame,
					'stop_frame': frame
				})
					if compute_chasing(m1, m2):
					if compute_contact(m1, m2):
					if compute_sniffingN2N(m1, m2):
					if compute_sniffingN2T(m1, m2):


		break  # doar primul folder pentru test

	print(newDF.head(10))
	print(y_df.shape[0])