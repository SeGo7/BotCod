import subprocess

files = ["bot_pro.py", "bot_child.py"]
for file in files:
    subprocess.Popen(args=["start", "python", file], shell=True, stdout=subprocess.PIPE)
