import os, subprocess
from utils.util import getTopLevelPath

def convert_notebook_to_python(notebook_path, python_path, output_format = 'script'):
    assert 'script' == output_format
    command = f'jupyter nbconvert --to {output_format} "{notebook_path}" --output "{python_path}"'
    subprocess.run(command, shell = True)


top_folder = getTopLevelPath() + 'code/'

# Directory containing Python scripts
python_dir = top_folder + 'python/preprocess/'
# Directory to save Jupyter notebooks
notebook_dir = top_folder + 'notebooks/preprocess/'

# Find Python files in the directory
notebooks = [f for f in os.listdir(notebook_dir) if f.endswith('.ipynb')]

# Convert Python scripts to Jupyter notebooks
for notebook in notebooks:
    convert_notebook_to_python(notebook_dir + notebook, python_dir + notebook.replace('.ipynb', ''))