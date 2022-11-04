import json

import jinja2

with open("tea_breaks.json") as breaks_file:
    tea_breaks = breaks_file.read()

template = jinja2.Template(open("templates/index.html").read())

with open("out.html", "w+") as file:
    file.write(template.render(data=tea_breaks, json=json.loads(tea_breaks)))
