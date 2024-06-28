#!/usr/bin/env python

from inspect import getmembers, isclass

from sqlalchemy_data_model_visualizer import generate_data_model_diagram, add_web_font_and_interactivity

from app.db import models as app_models

#models = [x for x in dir(models) if isinstance(x, models.SQLModel) and x.__name__ != 'SQLModel']
models = list(val for name, val in getmembers(app_models, lambda x: isclass(x) and issubclass(x, app_models.SQLModel)) if name != 'SQLModel')
print(repr(models))

# Suppose these are your SQLAlchemy data models defined above in the usual way, or imported from another file:
output_file_name = 'my_data_model_diagram'
generate_data_model_diagram(models, output_file_name)
add_web_font_and_interactivity('my_data_model_diagram.svg', 'my_interactive_data_model_diagram.svg')
