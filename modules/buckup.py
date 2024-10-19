import json
import os
import pickle

def buckup(data, filepath):
  with open(filepath, "w") as f:
    json.dump(data, f, indent=4)

def load_buckup(filepath):
  if os.path.exists(filepath):
    with open(filepath, "r") as f:
      data = json.load(f)

    return data
  else:
    return []
  
def buckup_job(text, filepath):
  with open(filepath, "w") as f:
    f.write(text)

def load_buckup_job(filepath):
  if os.path.exists(filepath):
    with open(filepath, "r") as f:
      data = f.read()

    return data
  else:
    return "あなたは高性能AIです"
  
def buckup_queue(data, filepath):
  with open(filepath, "wb") as f:
    pickle.dump(data, f)
    
def load_buckup_queue(filepath):
  if os.path.exists(filepath):
    with open(filepath, "rb") as f:
      data = pickle.load(f)

      return data
  else:
    return None