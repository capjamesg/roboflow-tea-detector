import json

import jinja2

with open("coffee_breaks.json") as breaks_file:
    coffee_breaks = breaks_file.read()

template = jinja2.Template(open("index.html").read())

with open("out.html", "w+") as file:
    file.write(template.render(data=coffee_breaks, json=json.loads(coffee_breaks)))
