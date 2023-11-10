import os

# Define the base directory
base_dir = "LIVE_DIALOGUE_OPTIONS"

# List of directories and sub-directories to be created
dirs = [
    os.path.join(base_dir, 'data', 'preprocessed_audio'),
    os.path.join(base_dir, 'data', 'raw_audio_samples'),
    os.path.join(base_dir, 'transcripts'),
    os.path.join(base_dir, 'demos'),
    os.path.join(base_dir, 'documentation'),
    os.path.join(base_dir, 'models', 'pretrained'),
    os.path.join(base_dir, 'models', 'trained'),
    os.path.join(base_dir, 'outputs', 'logs'),
    os.path.join(base_dir, 'outputs', 'results'),
    os.path.join(base_dir, 'src', 'dialogue_suggestions'),
    os.path.join(base_dir, 'src', 'diarization'),
    os.path.join(base_dir, 'src', 'audio'),
    os.path.join(base_dir, 'src', 'ui'),
    os.path.join(base_dir, 'utils'),
    os.path.join(base_dir, 'tests'),
    os.path.join(base_dir, 'assets'),
]

# Create directories
for dir_path in dirs:
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
        print(f"Created directory: {dir_path}")
    else:
        print(f"Directory already exists: {dir_path}")

# Create empty files (Note: This will overwrite if they already exist!)
files = [
    os.path.join(base_dir, 'config.py'),
    os.path.join(base_dir, 'src', 'audio', 'audio_manager.py'),
    os.path.join(base_dir, 'src', 'ui', 'ui_manager.py'),
    os.path.join(base_dir, 'src', 'main_app.py')
]

for file_path in files:
    with open(file_path, 'w') as f:
        pass
    print(f"Created file: {file_path}")

print("Directory structure created successfully!")

