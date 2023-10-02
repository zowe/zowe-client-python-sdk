"""
Sphinx extension to automatically generate .rst files for each class
"""

import glob
import os
import re
import shutil

CLASS_TEMPLATE = """{{header}}

.. autoclass:: {{fullname}}
   :members:
"""
INDEX_TEMPLATE = """{{header}}

.. toctree::
   :maxdepth: {{maxdepth}}

   {{filelist}}
"""


def render_template(template, context):
    for key, value in context.items():
        value = str(value)
        if key == "header":
            value += f"\n{'=' * len(value)}"
        template = template.replace("{{" + key + "}}", value)
    return template


def main():
    sdk_dirs = [path for path in glob.iglob("src/*") if os.path.isdir(path)]
    sdk_names = []
    if os.path.isdir("docs/source/classes"):
        shutil.rmtree("docs/source/classes")
    os.mkdir("docs/source/classes")

    for sdk_dir in sorted(sdk_dirs):
        sdk_name = os.path.basename(sdk_dir)
        if sdk_name == "__pycache__" or sdk_name.endswith(".egg-info"):
            continue
        pkg_name = f"zowe.{sdk_name}_for_zowe_sdk"
        print(f"building class docs for {pkg_name}... ", end="")
        os.mkdir(f"docs/source/classes/{sdk_name}")
        py_files = glob.glob(f"src/{sdk_name}/{pkg_name.replace('.', '/')}/*.py")
        rst_names = []
        parent_rst_names = []

        for py_file in sorted(py_files):
            py_name = os.path.basename(py_file)
            if py_name == "__init__.py":
                continue
            with open(py_file, "r", encoding="utf-8") as f:
                py_contents = f.read()
            class_names = re.findall(r"^class (\w+)\b", py_contents, re.MULTILINE)
            if len(class_names) == 1:
                rst_name = f"{py_name[:-3]}.rst"
                rst_contents = render_template(
                    CLASS_TEMPLATE, {"fullname": f"{sdk_name}.{pkg_name}.{class_names[0]}", "header": class_names[0]}
                )
                with open(f"docs/source/classes/{sdk_name}/{rst_name}", "w", encoding="utf-8") as f:
                    f.write(rst_contents)
                rst_names.append(rst_name)
            elif len(class_names) > 1:
                module_name = py_name[:-3]
                os.mkdir(f"docs/source/classes/{sdk_name}/{module_name}")
                child_rst_names = []
                for class_name in sorted(class_names):
                    rst_name = f"{class_name.lower()}.rst"
                    rst_contents = render_template(
                        CLASS_TEMPLATE,
                        {"fullname": f"{sdk_name}.{pkg_name}.{module_name}.{class_name}", "header": class_name},
                    )
                    with open(f"docs/source/classes/{sdk_name}/{module_name}/{rst_name}", "w", encoding="utf-8") as f:
                        f.write(rst_contents)
                    child_rst_names.append(rst_name)
                rst_name = f"{module_name}/index.rst"
                rst_contents = render_template(
                    INDEX_TEMPLATE,
                    {
                        "filelist": "\n   ".join(name[:-4] for name in child_rst_names),
                        "header": f"{module_name.replace('_', ' ').title()} classes",
                        "maxdepth": 2,
                    },
                )
                with open(f"docs/source/classes/{sdk_name}/{rst_name}", "w", encoding="utf-8") as f:
                    f.write(rst_contents)
                parent_rst_names.append(rst_name)

        rst_contents = render_template(
            INDEX_TEMPLATE,
            {
                "filelist": "\n   ".join(name[:-4] for name in rst_names + parent_rst_names),
                "header": pkg_name,
                "maxdepth": 2,
            },
        )
        with open(f"docs/source/classes/{sdk_name}/index.rst", "w", encoding="utf-8") as f:
            f.write(rst_contents)
        sdk_names.append(sdk_name)
        print("done")

    rst_contents = render_template(
        INDEX_TEMPLATE,
        {"filelist": "\n   ".join(f"{name}/index" for name in sdk_names), "header": "Classes", "maxdepth": 3},
    )
    with open(f"docs/source/classes/index.rst", "w", encoding="utf-8") as f:
        f.write(rst_contents)


def setup(app):
    old_cwd = os.getcwd()
    os.chdir(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../.."))
    try:
        main()
    finally:
        os.chdir(old_cwd)
