import os

print("CC - experiments - all settings")
os.system("python final_experiments.py CC [0.0,0.1,0.2,0.3,0.4,0.50] 5 True True True")

print("MF - experiments - all settings")
os.system("python final_experiments.py MF [0.0,0.1,0.2,0.3,0.4,0.50] 5 True True True")

print("genre - experiments - all settings")
os.system("python final_experiments.py genre [0.0,0.1,0.2,0.3,0.4,0.50] 5 True True True")

print("BP - experiments - all settings")
os.system("python final_experiments.py BP [0.0,0.1,0.2,0.3,0.4,0.50] 5 True True True")

print("birthPlace - experiments - all settings")
os.system("python final_experiments.py birthPlace [0.0,0.1,0.2,0.3,0.4,0.50] 5 True True True")