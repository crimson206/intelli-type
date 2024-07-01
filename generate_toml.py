# region Pre-Defined

import os
from pydantic import BaseModel
from crimson.templator import format_insert

template = r'''[build-system]
requires = ["setuptools>=61.0.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "\[name_space\]-\[module_name\]"
version = "0.1.0"
description = "\[description\]"
readme = "README.md"
authors = [
  { name="\[name\]", email="\[email\]" },
]

classifiers = [
    "Programming Language :: Python :: 3",

    "Intended Audience :: Developers",
    "Topic :: Software Development :: Build Tools",

    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
]
dependencies = [
    "pydantic",
]
requires-python = ">=3.9"

[project.urls]
"Homepage" = "https://github.com/\[github_id\]/\[module_name\]"
"Bug Tracker" = "https://github.com/\[github_id\]/\[module_name\]/issues"
'''


class Kwargs(BaseModel):
    name: str = "Sisung Kim"
    email: str = "sisung.kim1@gmail.com"
    github_id: str = "crimson206"
    name_space: str
    module_name: str
    description: str


class Options(BaseModel):
    discussion: bool = False


def add_options(template: str, options: Options) -> str:

    if options.discussion:
        discussion_block = r'''"Discussion" = "https://github.com/\[github_id\]/\[module_name\]/discussions"'''
        template += discussion_block

    return template

# endregion

# ******************************************************
# region Utils


def create_skeleton(name_space:str, module_name:str):
    module_name = module_name.replace('-', '_')
    os.makedirs(f"src/{name_space}/{module_name}", exist_ok=True)
    with open(f"src/{name_space}/{module_name}/__init__.py", "w") as f:
        f.write("# Init file for the module")


setup_env_template = r'''\[bin_bash\]

read -p "Please enter the Python version you want to use (e.g., 3.9): " PYTHON_VERSION

conda create --name \[module_name\] python=$PYTHON_VERSION -y

conda activate \[module_name\]

pip install -r requirements.txt
pip install -r requirements_test.txt
pip install -r requirements_dev.txt

'''


def generate_setup_env_script(module_name, setup_env_template):
    with open("scripts/setup_env.sh", "w") as file:
        script = format_insert(
            setup_env_template,
            module_name=module_name,
            bin_bash="# !bin/bash"
        )
        file.write(script)

    print(f"Now, you can access the module name {module_name} in your terminal by $MODULE_NAME")
    print("To generate an conda env for your new module, run following command.")
    print("source scripts/setup_env.sh")


def generate_toml(pyproject_body):
    with open('pyproject.toml', "w") as file:
        file.write(pyproject_body)

# endregion

# ******************************************************
# region User Setup


options = Options(
    # Will you use the discussion session in your repo?
    discussion=False
)



# Define the general information of your package
kwargs = Kwargs(
    name_space="crimson-templator",
    module_name="requirements",
    description="requirements file templates.",
)

kwargs_skeleton = kwargs
kwargs_skeleton.name_space = kwargs_skeleton.name_space.replace('-', '/')

# endregion

# ******************************************************
# region Execution

template: str = add_options(
    template,
    options=options
)

pyproject_body: str = format_insert(
    template,
    **kwargs.model_dump()
)


generate_toml(
    pyproject_body=pyproject_body
)


create_skeleton(
    name_space=kwargs_skeleton.name_space,
    module_name=kwargs_skeleton.module_name
)

generate_setup_env_script(
    module_name=kwargs.module_name, 
    setup_env_template=setup_env_template
)

# endregion
