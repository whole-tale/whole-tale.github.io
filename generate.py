import yaml
import os
import glob
from markdown import Markdown
from jinja2 import Environment, FileSystemLoader
from shutil import copyfile

PATH = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_ENVIRONMENT = Environment(
    autoescape=False,
    loader=FileSystemLoader(os.path.join(PATH, "templates")),
    trim_blocks=False,
)
pages = {}


def render_template(template_filename, context):
    return TEMPLATE_ENVIRONMENT.get_template(template_filename).render(context)


def page(name, output_name=None):
    if output_name is None:
        output_name = name + ".html"

    def _page(func):
        pages[name] = (func, output_name)
        return func

    return _page


@page("index")
def index():
    data = yaml.safe_load(open("univs.yaml", "r"))
    data.update(yaml.safe_load(open("main.yaml", "r")))
    return data


@page("participate")
def participate():
    return yaml.safe_load(open("univs.yaml", "r"))


@page("maintenance")
def maintenance():
    return yaml.safe_load(open("univs.yaml", "r"))


@page("team")
def team():
    data = yaml.safe_load(open("univs.yaml", "r"))
    data.update(yaml.safe_load(open("team.yml", "r")))
    return data


@page("news")
def news():
    parser = Markdown(extensions=["pymdownx.tilde"])
    data = yaml.safe_load(open("univs.yaml", "r"))
    data["news"] = []
    for input_fname in sorted(glob.glob("_posts/*.md"), reverse=True):
        with open(input_fname, "r") as input_file:
            input_data = input_file.read()
        yaml_data, html_data = (_.strip() for _ in input_data.split("---\n") if _)
        post = yaml.safe_load(yaml_data)
        (year, month, day, title) = os.path.basename(input_fname)[:-3].split("-", 3)
        post["url"] = "/{}/{}/{}/{}.html".format(year, month, day, title)
        post["date"] = "{}/{}/{}".format(month, day, year)

        short_blurb = "\n\n".join(html_data.strip().split("\n\n", 2)[:2])
        post["content"] = parser.convert(short_blurb)

        data["news"].append(post)
    return data


def render_full_width_page(input_fname, output_fname):
    parser = Markdown(extensions=["pymdownx.tilde"])

    with open(input_fname, "r") as input_file:
        input_data = input_file.read()
    yaml_data, html_data = (_.strip() for _ in input_data.split("---\n") if _)

    context = yaml.safe_load(yaml_data)
    context["content"] = parser.convert(html_data)

    with open(output_fname, "w") as output_file:
        html = render_template("full-width.html", context)
        output_file.write(html)


def main():
    for name in sorted(pages):
        setup_func, template_name = pages[name]
        out_name = os.path.join(".", template_name)
        dir_name = os.path.dirname(out_name)
        if not os.path.isdir(dir_name):
            os.makedirs(dir_name)
        context = {"title": name}
        context.update(setup_func())
        with open("public/" + out_name, "w") as f:
            print(template_name)
            html = render_template(template_name, context)
            f.write(html)

    for post in sorted(glob.glob("_posts/*.md"), reverse=True):
        path_elements = os.path.basename(post).split("-", 3)
        full_input_name = os.path.join(*path_elements)
        os.makedirs("public/" + os.path.dirname(full_input_name), exist_ok=True)
        out_name = "public/" + full_input_name[:-2] + "html"
        render_full_width_page(post, out_name)

    os.makedirs("public/internship_projects", exist_ok=True)
    for project in glob.glob("_internship_projects/*.md"):
        out_name = (
            "public/internship_projects/" + os.path.basename(project)[:-2] + "html"
        )
        render_full_width_page(project, out_name)

    for image in glob.glob("_internship_projects/*.png"):
        copyfile(image, "public/" + image[1:])


if __name__ == "__main__":
    main()
