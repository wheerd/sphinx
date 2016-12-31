# -*- coding: utf-8 -*-
"""
    sphinx.ext.napoleon.typehints
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


    Functions for handling type hints.


    :copyright: Copyright 2007-2016 by the Sphinx team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""

import inspect
import sys

GenericMeta = []
Generic = []
Any = object()
TypeVar = []
Union = []
ForwardRef = []

try:
    import typing
    GenericMeta.append(typing.GenericMeta)
    Generic.append(typing.Generic)
    TypeVar.append(typing.TypeVar)
    Any = typing.Any
    ForwardRef.append(typing._ForwardRef)
    if hasattr(typing, '_Union'):
        Union.append(typing._Union)
except ImportError:
    pass

try:
    import backports.typing
    GenericMeta.append(backports.typing.GenericMeta)
    Generic.append(backports.typing.Generic)
    TypeVar.append(backports.typing.TypeVar)
    ForwardRef.append(backports.typing._ForwardRef)
    if hasattr(backports.typing, '_Union'):
        Union.append(backports.typing._Union)
except ImportError:
    pass

GenericMeta = tuple(GenericMeta)
Generic = tuple(Generic)
TypeVar = tuple(TypeVar)
Union = tuple(Union)
ForwardRef = tuple(ForwardRef)

try:
    from typing import get_type_hints
except ImportError:
    def get_type_hints(obj, globals, locals):
        """Dummy replacement that returns an empty type hint dictionary."""
        return {}

def format_annotation(annotation, config, obj=None):
    """Return the type annotation formatted in a reStructuredText format.

    Parameters
    ----------
    annotation : :obj:`type`
        The type annotation to format.
    obj: :obj:`object`, optional
        The original object for which the annotation is formatted.
        This is mainly used in case of string references in generic base classes.
        The namespace of the original object is needed in order to parse the reference.
    link: :obj:`bool`
        If ``True``, then link every class using reStructuredText roles.

    Returns
    -------
    unicode
        The formatted annotation.

    """
    if inspect.isclass(annotation):
        qualname = getattr(annotation, '__qualname__', annotation.__name__)
        module = annotation.__module__

        # builtin types don't need to be qualified with a module name
        if module in ('builtins', '__builtin__'):
            if qualname == 'NoneType':
                return '``None``'
            elif config.napoleon_link_types:
                return ':class:`{}`'.format(qualname)
            else:
                return qualname

        role = 'class'
        params = None
        if isinstance(annotation, GenericMeta):
            params = annotation.__args__
            # Make sure to format Generic[T, U, ...] correctly, because it only
            # has parameters but no argument values for them
            if not params and issubclass(annotation, Generic):
                params = annotation.__parameters__
            if module in ('typing', 'backports.typing'):
                if qualname in ('Callable', 'Tuple'):
                    role = 'data'
                if qualname == 'Callable' and params:
                    *params, r_type = params
                    if len(params) == 1 and params[0] == Ellipsis:
                        args_r = Ellipsis
                    else:
                        args_r = '\\[{}]'.format(', '.join(format_annotation(a, config, obj) for a in params))
                    params = [args_r, r_type]
        elif module in ('typing', 'backports.typing'):
            # Since Any is a superclass of everything, make sure it gets handled normally.
            if qualname == 'Any':
                role = 'data'
            # Tuples are not Generics, so handle their type parameters separately.
            elif qualname == 'Tuple':
                role = 'data'
                if annotation.__tuple_params__:
                    params = list(annotation.__tuple_params__)
                # Tuples can have variable size with a fixed type, indicated by an Ellipsis:
                # e.g. Tuple[T, ...]
                if annotation.__tuple_use_ellipsis__:
                    params.append(Ellipsis)
            # Unions are not Generics pre 3.6, so handle their type parameters separately.
            elif qualname == 'Union':
                role = 'data'
                params = getattr(annotation, '__union_params__', getattr(annotation, '__args__', None))
                if params:
                    params = list(params)
                    # If the Union contains None, wrap it in an Optional, i.e.
                    # Union[T,None]   => Optional[T]
                    # Union[T,U,None] => Optional[Union[T, U]]
                    if type(None) in params:
                        qualname = 'Optional'
                        params.remove(type(None))
                        if len(params) > 1:
                            generic = '\\[{}]'.format(', '.join(format_annotation(p, config, obj) for p in params))
                            link = _make_link('typing.Union', config, 'data')
                            params = [link + generic]
            # Callables are not Generics pre 3.6, so handle their type parameters separately.
            # They have the format Callable[arg_types, return_type].
            # arg_types is either a list of types or an Ellipsis for Callables with
            # variable arguments.
            elif qualname == 'Callable':
                role = 'data'
                if annotation.__args__ is not None or annotation.__result__ is not None:
                    if annotation.__args__ is Ellipsis:
                        args_r = Ellipsis
                    else:
                        args_r = '\\[{}]'.format(', '.join(format_annotation(a, config, obj) for a in annotation.__args__))
                    params = [args_r, annotation.__result__]
            # Type variables are formatted with a prefix character (~, +, -)
            # which have to be escaped.
            elif isinstance(annotation, TypeVar):
                return '\\' + repr(annotation)
            # Strings inside of type annotations are converted to _ForwardRef internally
            elif isinstance(annotation, ForwardRef):
                try:
                    global_vars = getattr(obj, '__globals__', None)
                    if global_vars is None and hasattr(obj, '__module__'):
                        module = sys.modules[obj.__module__]
                        global_vars = vars(module)
                    # Evaluate the type annotation string and then format it
                    actual_type = annotation._eval_type(global_vars or dict(), dict())
                    return format_annotation(actual_type, config, obj)
                except Exception:
                    return annotation.__forward_arg__

        generic = '\\[{}]'.format(', '.join(format_annotation(p, config, obj)
                                            for p in params)) if params else ''
        full_name = '{}.{}'.format(annotation.__module__, qualname)
        link = _make_link(full_name, config, role)

        return link + generic
    # Unions are not Generics, so handle their type parameters separately.
    elif isinstance(annotation, Union):
        params = None
        name = 'Union'
        if annotation.__args__:
            params = list(annotation.__args__)
            # If the Union contains None, wrap it in an Optional, i.e.
            # Union[T,None]   => Optional[T]
            # Union[T,U,None] => Optional[Union[T, U]]
            if type(None) in annotation.__args__:
                name = 'Optional'
                params.remove(type(None))
                if len(params) > 1:
                    generic = '\\[{}]'.format(', '.join(format_annotation(p, config, obj) for p in params))
                    link = _make_link('typing.Union', config, 'data')
                    params = [link + generic]
        generic = '\\[{}]'.format(', '.join(format_annotation(p, config, obj) for p in params)) if params else ''
        return ':data:`~typing.{}`{}'.format(name, generic)
    elif isinstance(annotation, ForwardRef):
        try:
            global_vars = getattr(obj, '__globals__', None)
            if global_vars is None and hasattr(obj, '__module__'):
                module = sys.modules[obj.__module__]
                global_vars = vars(module)
            # Evaluate the type annotation string and then format it
            actual_type = annotation._eval_type(global_vars, None)
            return format_annotation(actual_type, config, obj)
        except Exception:
            return annotation.__forward_arg__
    # _TypeAlias is an internal class used for the Pattern/Match types
    # It represents an alias for another type, e.g. Pattern is an alias for any string type
    elif isinstance(annotation, typing._TypeAlias):
        actual_type = format_annotation(annotation.type_var, config, obj)
        full_name = 'typing.{}'.format(annotation.name)
        link = _make_link(full_name, config, 'class')
        return '{}\\[{}]'.format(link, actual_type)
    # Ellipsis is used in Callable/Tuple
    elif annotation is Ellipsis:
        return '...'
    elif annotation is Any:
        return _make_link('typing.Any', config, 'data')
    elif isinstance(annotation, TypeVar):
        return '\\' + repr(annotation)

    return str(annotation)

def _make_link(full_name, config, role='obj'):
    if config.napoleon_link_types:
        if config.napoleon_always_shorten:
            link_name = '~{}'.format(full_name)
        else:
            link_name = _shorten_type_name(full_name, config.napoleon_shorten_prefixes)

        return ':{}:`{}`'.format(role, link_name)

    return full_name

def _shorten_type_name(name, prefixes):
    short_name = None
    for prefix in prefixes:
        if name.startswith(prefix):
            if prefix.endswith('.'):
                short_name = name[len(prefix):]
                if '.' not in short_name:
                    short_name = None
            if short_name:
                return '{} <{}>'.format(short_name, name)
            return '~{}'.format(name)
    return name


__all__ = ['get_type_hints', 'format_annotation']
