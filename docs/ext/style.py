# coding=utf-8

from pygments.token import Comment
from sphinx.highlighting import SphinxStyle


class SimpyStyle(SphinxStyle):
    styles = SphinxStyle.styles
    styles.update({
        Comment.Annotation: ('noinherit bg:#ffff00 border:#ff8000 nobold '
                             'noitalic #000000')
    })
