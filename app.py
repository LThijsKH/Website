from flask import Flask, render_template, request, url_for, g
from flask_frozen import Freezer
import json
from datetime import datetime

app = Flask(__name__)

def split_list(images, columns=3):
    cols = [[] for _ in range(columns)]
    heights = [0.0] * columns
    for img in images:
        # 2:3 portrait images are visually taller
        weight = 1 / img["aspect_ratio"]
        shortest_col = heights.index(min(heights))
        cols[shortest_col].append(img)
        heights[shortest_col] += weight
    return cols

images = []

with open("static/data/strings.json") as f:
    STRINGS = json.load(f)

def bilingual(path):
    def register(view):
        app.add_url_rule(path, view_func=view, defaults={"lang": "en"})
        app.add_url_rule("/fr" + path, view_func=view, defaults={"lang": "fr"})
        return view
    return register

@app.url_value_preprocessor
def pull_lang(endpoint, values):
    g.lang = (values or {}).pop("lang", "en")

@app.url_defaults
def add_lang(endpoint, values):
    if "lang" not in values and app.url_map.is_endpoint_expecting(endpoint, "lang"):
        values["lang"] = g.get("lang", "en")

@app.context_processor
def inject_strings():
    lang = g.get("lang", "en")
    return {"lang": lang, "STRINGS": STRINGS[lang]}

@bilingual("/")
def landing():
    # TODO: Sort by date
    lang = g.lang
    if lang == "fr":
        with open("static/data/projects_fr.json") as f:
            featured_projects = [
                p for p in json.load(f) if p.get("featured")
            ]
        with open("static/data/cv_fr.json") as f:
            cv = json.load(f)
    else:
        with open("static/data/projects.json") as f:
            featured_projects = [
                p for p in json.load(f) if p.get("featured")
            ]
        with open("static/data/cv.json") as f:
            cv = json.load(f)
    return render_template("index.html", cv=cv, projects=featured_projects)

@bilingual("/photos/")
def photos():
    global images
    if images == []:
        with open("static/data/photos.json") as f:
            images = sorted(
                json.load(f),
                key=lambda img: datetime.strptime(
                    img["date"],
                    "%Y:%m:%d %H:%M:%S"
                ),
                reverse=True
            )

    col1, col2, col3 = split_list(images)
    return render_template("photos.html", images=images, col1=col1, col2=col2, col3=col3, total_i=len(images))

@bilingual("/photo/<slug>/")
def photo(slug):
    global images
    if images == []:
        with open("static/data/photos.json") as f:
            images = sorted(
                json.load(f),
                key=lambda img: datetime.strptime(
                    img["date"],
                    "%Y:%m:%d %H:%M:%S"
                ),
                reverse=True
            )

    img_data = []
    for img in images:
        img_data.append({
            "slug": img["slug"],
            "route": url_for(
                "photo",
                slug=img["slug"]
            )
        })
    
    for img in images:
        if img["slug"] == slug:
            return render_template("photo.html", img=img, img_data=img_data)
    return not_found(404)

@bilingual('/projects/')
def projects():
    lang=g.lang
    if lang == "fr":
        with open("static/data/projects_fr.json") as f:
            projects = json.load(f)
    else:
        with open("static/data/projects.json") as f:
                projects = json.load(f)
    return render_template('projects.html', projects=projects)

@bilingual("/404.html")
def not_found_page():
    return render_template("404.html")

@app.errorhandler(404)
def not_found(e):
  return render_template("404.html"), 404

# Setup that uses frozen flask to generate static pages in /build for cloudflare pages
freezer = Freezer(app)

@freezer.register_generator
def both_languages():
    for rule in app.url_map.iter_rules():
        if rule.defaults and rule.arguments == {"lang"}:
            yield rule.endpoint, {"lang": rule.defaults["lang"]}
    with open("static/data/photos.json") as f:
        for img in json.load(f):
            yield "photo", {"slug": img["slug"], "lang": "fr"}

app.config['FREEZER_STATIC_IGNORE'] = [ 
    'img/photos/Originals/*', 
]

app.config['FREEZER_REMOVE_EXTRA_FILES'] = ['True']

app.config["FREEZER_BASE_URL"] = "https://leotkh.com"

if __name__ == '__main__':
    freezer.freeze()  # This will generate static files in a build/ directory