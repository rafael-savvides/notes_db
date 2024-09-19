"""
Provides MathJax support for rendering Markdown with LaTeX to html.
Source: https://github.com/miyuchina/mistletoe/blob/master/contrib/mathjax.py
Edited to allow inline math with $$. Source: https://tex.stackexchange.com/a/27656.
"""

import os
from mistletoe.html_renderer import HTMLRenderer
from mistletoe.latex_renderer import LaTeXRenderer

PATH_TO_MATHJAX_JS = os.getenv("PATH_TO_MATHJAX_JS", "")


class MathJaxRenderer(HTMLRenderer, LaTeXRenderer):
    """
    MRO will first look for render functions under HTMLRenderer,
    then LaTeXRenderer.
    """

    path_to_mathjax_js = (
        "https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.7/MathJax.js?config=TeX-MML-AM_CHTML"
        if not PATH_TO_MATHJAX_JS
        else PATH_TO_MATHJAX_JS
    )
    mathjax_src = (
        """<script type="text/x-mathjax-config">
    MathJax.Hub.Config({
        tex2jax: {
        inlineMath: [ ['$','$'] ],
        processEscapes: true
        }
    });
    </script>"""
        f'<script type="text/javascript" src="{path_to_mathjax_js}"></script>\n'
    )

    def render_math(self, token):
        return self.render_raw_text(token)

    def render_document(self, token):
        """
        Append CDN link for MathJax to the end of <body>.
        """
        return super().render_document(token) + self.mathjax_src
