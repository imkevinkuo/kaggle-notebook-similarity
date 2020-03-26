import os
import sys
import subprocess

# Download the notebook you want to check for plagiarism and place it in the same folder as this script.

COMPETITON_ARG = "--competition house-prices-advanced-regression-techniques"
NB_KERNEL_ARG = "--kernel-type notebook"
SP_KERNEL_ARG = "--kernel-type script"
LIST_KERNELS_CMD = f"kaggle kernels list --page-size 100 --language python -v"

PULL_KERNEL_CMD = "kaggle kernels pull"
NBCONVERT_ARGS = "--TemplateExporter.exclude_markdown=True --no-prompt"


def download_scripts(page_num):
    sp_out = subprocess.Popen(f"{LIST_KERNELS_CMD} {COMPETITON_ARG} {SP_KERNEL_ARG} --page {page_num}".split(),
                              stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT)

    stdout, stderr = sp_out.communicate()
    lines = stdout.splitlines()[1:]

    if len(lines) <= 2:
        return -1

    kernel_names = []
    for line in lines:
        line_str = line.decode('utf-8')
        if len(line_str) > 0 and ',' in line_str:
            kernel_names.append(line_str.split(',')[0])

    if not os.path.isdir("scripts"):
        os.mkdir("scripts")
    existing_scripts = os.listdir("scripts")
    # Downloads scripts
    for kernel_name in kernel_names:
        author_name, script_name = kernel_name.split("/")
        if f"{author_name}-{script_name}.py" not in existing_scripts:
            os.system(f"{PULL_KERNEL_CMD} {kernel_name} --path scripts")
            script_path = os.path.join("scripts", f"{script_name}.py")
            script_path_new = os.path.join("scripts", f"{author_name}-{script_name}.py")
            os.rename(script_path, script_path_new)
        else:
            print(f"File {script_name} already exists.")
    return 0


def download_notebooks(page_num):
    nb_out = subprocess.Popen(f"{LIST_KERNELS_CMD} {COMPETITON_ARG} {NB_KERNEL_ARG} --page {page_num}".split(),
                              stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT)

    stdout, stderr = nb_out.communicate()
    lines = stdout.splitlines()[1:]

    if len(lines) <= 2:
        return -1

    kernel_names = []
    for line in lines:
        line_str = line.decode('utf-8')
        if len(line_str) > 0 and ',' in line_str:
            kernel_names.append(line_str.split(',')[0])

    if not os.path.isdir("notebooks"):
        os.mkdir("notebooks")
    existing_notebooks = os.listdir("notebooks")
    # Downloads notebooks, strips all annotations, and converts to a .py script file.
    for kernel_name in kernel_names:
        author_name, notebook_name = kernel_name.split("/")
        if f"{author_name}-{notebook_name}.ipynb" not in existing_notebooks:
            os.system(f"{PULL_KERNEL_CMD} {kernel_name} --path notebooks")
            try:
                notebook_path = os.path.join("notebooks", f"{notebook_name}.ipynb")
                notebook_path_new = os.path.join("notebooks", f"{author_name}-{notebook_name}.ipynb")
                # To avoid UnicodeDecodeError, remove all non-UTF-8 characters
                content = ""
                with open(notebook_path, encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                with open(notebook_path, 'w') as f:
                    f.write(content)
                os.rename(notebook_path, notebook_path_new)
                os.system(f"jupyter nbconvert --to script {notebook_path_new} --output-dir=scripts {NBCONVERT_ARGS}")
            except:
                print(f"Could not convert {notebook_name}")
        else:
            print(f"File {notebook_name} already exists.")
    return 0


def check_scripts(reference_nb_name):
    os.system(f"jupyter nbconvert --to script {reference_nb_name} {NBCONVERT_ARGS}")
    reference_script_name = f"{reference_nb_name.split('.')[0]}.py"

    candidate_script_names = os.listdir("scripts")
    print(f"ref: {reference_script_name}")
    for script_name in candidate_script_names:
        candidate_script_path = os.path.join("scripts", script_name)
        total_lines, matching_lines = 0, 0
        for zipline in zip(open(reference_script_name), open(candidate_script_path)):
            total_lines += 1
            if zipline[0] == zipline[1]:
                matching_lines += 1
        line_info = f"({matching_lines}/{total_lines})".ljust(12)
        print(f"Similarity score: {matching_lines / total_lines:.2f} {line_info} {script_name}")


if __name__ == "__main__":
    if len(sys.argv) == 3:
        page = int(sys.argv[2])
        if page > 0:
            download_notebooks(page)
        else:
            print("Page must be greater than 0.")
    elif len(sys.argv) == 2:
        page = 1
        while download_notebooks(page) == 0:
            page += 1
        page = 1
        while download_scripts(page) == 0:
            page += 1
        check_scripts(sys.argv[1])
    else:
        print(
            "This script downloads Jupyter Notebooks from the Kaggle 'house-prices-advanced-regression-techniques' competition and compares them to a reference notebook.")
        print("Usage: python main.py <reference_notebook_filename> <page_number>")
        print("Omitting page_number will make the script check against as many notebooks and scripts as possible.")
