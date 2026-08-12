+++
title = "Creating PDFs with LaTeX and Django"
date = "2019-10-01"
tags = ["python", "django", "latex"]
+++

When I started at my new job, the first task was: reports. It was a good way to learn the codebase, but when I opened the file that generated the PDFs, I found something really messed up. Every element (columns, rows, title…) had its position defined by hand, in centimeters. So a task that should have been quick was going to take much longer.

<!--more-->

But I remembered that LaTeX can easily create PDFs. Could I use it with Django? That way I could describe the structure of the document and leave the layout to LaTeX, instead of counting centimeters.

So I found [django-tex](https://github.com/weinbusch/django-tex), a simple Django app to render LaTeX templates and compile them into PDF files. You just need a local LaTeX installation and the Jinja2 templating engine for template rendering. In my case, [I forked the project](https://github.com/gabicavalcante/django-tex) and added some escape characters and filters for templates.

## Setup

- Install it. What's on PyPI is the original; use my fork if you want the extra filters:

```bash
pip install django-tex
# or: pip install git+https://github.com/gabicavalcante/django-tex
```

- Add `django_tex` to your `INSTALLED_APPS` setting:

```python
INSTALLED_APPS = [
    ...
    'django_tex',
]
```

- Add a second template backend for your `.tex` files. It sits alongside the HTML backend you already have, so keep both entries in `TEMPLATES`. `ROOT_PATH` below is just a variable pointing at the project root, so use whatever your `settings.py` already uses for paths:

```python
TEMPLATES = [
    {
        'NAME': 'tex',
        'BACKEND': 'django_tex.engine.TeXEngine',
        'APP_DIRS': True,
        'DIRS': [
            '%s/templates' % ROOT_PATH
        ],
    },
]
```

- Create a LaTeX template `test.tex` in your template directory:

```latex
\documentclass{article}
\begin{document}
\section{ {{- title -}} }
\end{document}
```

Both details in that `\section` line matter. The dashes in `{{- title -}}` strip the whitespace around the value, so you get `\section{Title}` instead of `\section{ Title }`. The spaces are what keep Jinja from reading `{{{` as the start of an expression followed by a stray brace.

## Rendering

There are two ways to get the PDF out. `compile_template_to_pdf` gives you the file as a bytes object:

```python
from django_tex.core import compile_template_to_pdf

template_name = 'test.tex'
context = {'title': 'Test PDF File'}
PDF = compile_template_to_pdf(template_name, context)
```

`render_to_pdf` wraps that in an `HttpResponse`, which is what you want from a view:

```python
from django_tex.shortcuts import render_to_pdf

def view(request):
    template_name = 'test.tex'
    context = {'title': 'Test PDF File'}
    return render_to_pdf(request, template_name, context,
                filename='test.pdf')
```

The default LaTeX interpreter is `lualatex`, but you can change it with the `LATEX_INTERPRETER` setting, for instance: `LATEX_INTERPRETER = 'pdflatex'`. Whichever one you pick has to be installed on the machine that runs the compile, which is worth remembering when you deploy.

I did end up refactoring the reports to LaTeX templates, and generating a PDF came down to a few seconds. The bigger win was that a new report became a template I could read, instead of a list of coordinates.
