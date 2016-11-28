# -*- coding: utf-8 -*-
"""
    test_napoleon_typehints
    ~~~~~~~~~~~~~~~~~~~~~~~

    Tests for :mod:`sphinx.ext.napoleon.typehints` module.


    :copyright: Copyright 2007-2016 by the Sphinx team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""

from unittest import TestCase
from typing import (Any, Callable, Dict, Generic, Mapping, Optional, Pattern,
                    Tuple, Type, TypeVar, Union)

from sphinx.ext.napoleon import Config
from sphinx.ext.napoleon.typehints import format_annotation

T = TypeVar('T')
U = TypeVar('U', covariant=True)
V = TypeVar('V', contravariant=True)


class A:
    pass


class B(Generic[T]):
    pass


class C(Dict[T, int]):
    pass


ANNOTATION_EXAMPLES = [
    (str,                           ':class:`str`'),
    (int,                           ':class:`int`'),
    (type(None),                    '``None``'),
    (Any,                           ':data:`~typing.Any`'),
    (Generic[T],                    ':class:`~typing.Generic`\\[\\~T]'),
    (Mapping,                       ':class:`~typing.Mapping`\\[\\~KT, \\+VT_co]'),
    (Mapping[T, int],               ':class:`~typing.Mapping`\\[\\~T, :class:`int`]'),
    (Mapping[str, V],               ':class:`~typing.Mapping`\\[:class:`str`, \\-V]'),
    (Mapping[T, U],                 ':class:`~typing.Mapping`\\[\\~T, \\+U]'),
    (Mapping[str, bool],            ':class:`~typing.Mapping`\\[:class:`str`, :class:`bool`]'),
    (Dict,                          ':class:`~typing.Dict`\\[\\~KT, \\~VT]'),
    (Dict[T, int],                  ':class:`~typing.Dict`\\[\\~T, :class:`int`]'),
    (Dict[str, V],                  ':class:`~typing.Dict`\\[:class:`str`, \\-V]'),
    (Dict[T, U],                    ':class:`~typing.Dict`\\[\\~T, \\+U]'),
    (Dict[str, bool],               ':class:`~typing.Dict`\\[:class:`str`, :class:`bool`]'),
    (Tuple,                         ':data:`~typing.Tuple`'),
    (Tuple[str, bool],              ':data:`~typing.Tuple`\\[:class:`str`, :class:`bool`]'),
    (Tuple[int, int, int],          ':data:`~typing.Tuple`\\[:class:`int`, :class:`int`, '
                                    ':class:`int`]'),
    (Tuple[str, ...],               ':data:`~typing.Tuple`\\[:class:`str`, ...]'),
    (Union,                         ':data:`~typing.Union`'),
    (Union[str, bool],              ':data:`~typing.Union`\\[:class:`str`, :class:`bool`]'),
    (Optional[str],                 ':data:`~typing.Optional`\\[:class:`str`]'),
    (Optional[Union[int, str]],     ':data:`~typing.Optional`\\[:data:`~typing.Union`'
                                    '\\[:class:`int`, :class:`str`]]'),
    (Union[Optional[int], str],     ':data:`~typing.Optional`\\[:data:`~typing.Union`'
                                    '\\[:class:`int`, :class:`str`]]'),
    (Union[int, Optional[str]],     ':data:`~typing.Optional`\\[:data:`~typing.Union`'
                                    '\\[:class:`int`, :class:`str`]]'),
    (Callable,                      ':data:`~typing.Callable`'),
    (Callable[..., int],            ':data:`~typing.Callable`\\[..., :class:`int`]'),
    (Callable[[int], int],          ':data:`~typing.Callable`\\[\\[:class:`int`], :class:`int`]'),
    (Callable[[int, str], bool],    ':data:`~typing.Callable`\\[\\[:class:`int`, :class:`str`], '
                                    ':class:`bool`]'),
    (Callable[[int, str], None],    ':data:`~typing.Callable`\\[\\[:class:`int`, :class:`str`], '
                                    '``None``]'),
    (Callable[[T], T],              ':data:`~typing.Callable`\\[\\[\\~T], \\~T]'),
    (Pattern,                       ':class:`~typing.Pattern`\\[\\~AnyStr]'),
    (Pattern[str],                  ':class:`~typing.Pattern`\\[:class:`str`]'),
    (A,                             ':class:`~%s.A`' % __name__),
    (B,                             ':class:`~%s.B`\\[\\~T]' % __name__),
    (C,                             ':class:`~%s.C`\\[\\~T]' % __name__),
    (Type,                          ':class:`~typing.Type`\\[\\+CT]'),
    (Type[A],                       ':class:`~typing.Type`\\[:class:`~%s.A`]' % __name__),
    (Type['A'],                     ':class:`~typing.Type`\\[A]'),
    (Type['str'],                   ':class:`~typing.Type`\\[:class:`str`]'),
]


class FormatAnnotationTest(TestCase):
    def test_format_with_link(self):
        config = Config(napoleon_always_shorten=True)

        for annotation, result in ANNOTATION_EXAMPLES:
            self.assertEqual(result, format_annotation(annotation, config))