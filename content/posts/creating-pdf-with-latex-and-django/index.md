+++
title = "Creating Pdf with Latex and Django"
date = "2019-10-01"
+++

When I started in my new job, the first task was: reports. It was great because I didn’t know the software, but when I open the file that created PDFs, I found something really messed up. I needed define each position of every thing (columns, rows, title…) in my document, and define that in centimetres. So, a task that should take some time, would take much more.

But I remembered that Latex can easily created PDF, could I use it with Django? So I found [django-tex](https://github.com/weinbusch/django-tex), a simple Django app to render LaTeX templates and compile them into PDF files. You just need a local Latex installations and jinja2 templating engine for templates rendering. In my case, [I did a fork of the project](https://github.com/gabicavalcante/django-tex) and included some escape character and filters for templates.

- Add `django_tex` to your `INSTALLED_APPS` setting:

```python
INSTALLED_APPS = [
    ...
    'django_tex',
]
```

- Configure the `settings.py` and make Latex file as your template:

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

- Use `compile_template_to_pdf` in your code to get the PDF file as a bytes object

```python
from django_tex.core import compile_template_to_pdf

template_name = 'teste.tex'
context = {'title': 'Arquivo PDF Test'}
PDF = compile_template_to_pdf(template_name, context)
```

Or use `render_to_pdf` to get a `HTTPResponse` containing the PDF file.

```python
from django_tex.shortcuts import render_to_pdf

def view(request):
    template_name = 'teste.tex'
    context = {'title': 'Arquivo PDF Teste'}
    return render_to_pdf(request, template_name, context,
                filename='teste.pdf')
```

The default LaTeX interpreter is set to `lualatex`. This but you can change by the setting `LATEX_INTERPRETER`, for instance: `LATEX_INTERPRETER = 'pdflatex'`. To work properly, the interpreter needs to be installed on your system.
