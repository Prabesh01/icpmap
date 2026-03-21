import os
import shutil

downloaded_dir="/home/prabesh/proj/icpmap/mst-automation/mst/y3/"
work_dir="/home/prabesh/icp/"

dir_map={
"app":"CS6004",
"cdl":"CS6W50NP",
"data":"CC6012",
"fyp":"Project"
}

for module in dir_map.keys():
	mst_path=os.path.join(work_dir,module,"mst")
	try: shutil.rmtree(mst_path)
	except: pass
	os.mkdir(mst_path)

def create_symlink(source,destination):
	# if os.path.islink(destination): os.unlink(destination)
	try: os.symlink(source,destination)
	except: print(f"err: {source} -> {destination}")

def process_folder(folder_path, assessment=False):
	if not os.listdir(folder_path): return
	if not assessment:
		folder_name=os.path.basename(os.path.dirname(folder_path))
	else:
		folder_name=os.path.basename(folder_path)
	destination_dir=None

	for dest in dir_map.keys():
		if dir_map[dest] in folder_name:
			destination_dir=dest
			break
	if not destination_dir:
		print(f"Unexpected: {folder_path}")
		return
	destination_path=os.path.join(work_dir,destination_dir,"mst")

	if assessment: destination_path=os.path.join(destination_path,"Assessment")
	else: destination_path=os.path.join(destination_path,os.path.basename(folder_path))

	create_symlink(folder_path, destination_path)

for folder in os.listdir(downloaded_dir):
	fol_path=os.path.join(downloaded_dir,folder)
	for subfolder in os.listdir(os.path.join(downloaded_dir,folder)):
		subfol_path=os.path.join(fol_path,subfolder)
		process_folder(subfol_path,assessment=True if folder=="Assessment" else False)

