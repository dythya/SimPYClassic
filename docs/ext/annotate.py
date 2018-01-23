# coding=utf-8

import re

from docutils import nodes
from pygments.filter import simplefilter
from pygments.token import Comment


# Create the annotation token.
Annotation = Comment.Annotation

# Regular expression pattern for annotations.
annotation_pat = re.compile('(\\(\\w+\\))')


@simplefilter
def annotation_filter(self, lexer, stream, options):
    """Pygments filter for annotations in comments."""
    for ttype, value in stream:
        if ttype is Comment:
            tokens = annotation_pat.split(value)
            # Normal comments are even and labels are odd. Labels include
            # parenthesis at start/end and are stripped by slicing with [1:-1].

            # Special case for a single label in the comment: Drop the leading
            # hash (#).
            if len(tokens) == 3:
                # Strip '#' from the first token.
                if not tokens[0][1:].strip() and not tokens[-1].strip():
                    yield Annotation, tokens[1][1:-1]
                    continue

            for idx, token in enumerate(tokens):
                yield ((ttype, token) if idx % 2 == 0 else
                       (Annotation, token[1:-1]))
            continue
        yield ttype, value


class annotation(nodes.reference):
    pass


def annotation_role(name, rawtext, text, lineno, inliner, options={},
                    content=[]):
    return [annotation(rawtext, text)], []


def visit_annotation_html(self, node):
    # Use pygments generated css classes to highlight annotations in HTML
    # ouput.
    self.body.append('<span class="highlight"><span class="c-Annotation">')


def depart_annotation_html(self, node):
    self.body.append('</span></span>')


def visit_annotation_latex(self, node):
    # Use pygments generated LaTeX commands to highlight annotations.

    # Use a raisebox to lift annotation box a little bit, so that it appears
    # vertically centered in line.
    self.body.append(
        '\\raisebox{0.2ex}[0pt][0pt]{\\tt\\tiny\\PYG{c+cAnnotation}{')


def depart_annotation_latex(self, node):
    self.body.append('}}')


def setup(app):
    # FIXME Hack: Add our own custom filter for highlighting annotations.
    from sphinx.highlighting import lexers
    lexers['python'].add_filter(annotation_filter())

    # Add node and role for annotations.
    app.add_node(annotation,
                 html=(visit_annotation_html, depart_annotation_html),
                 latex=(visit_annotation_latex, depart_annotation_latex),
                 )
    app.add_role('an', annotation_role)
