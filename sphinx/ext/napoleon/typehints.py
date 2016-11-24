# -*- coding: utf-8 -*-
"""
    sphinx.ext.napoleon.typehints
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


    Functions for handling type hints.


    :copyright: Copyright 2007-2016 by the Sphinx team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""

import inspect

try:
    import typing

    get_type_hints = typing.get_type_hints

    def format_annotation(annotation, obj=None, link=True):
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
            try:
                qualname = annotation.__qualname__
            except AttributeError:
                qualname = annotation.__name__

            # builtin types don't need to be qualified with a module name
            if annotation.__module__ in ('builtins', '__builtin__'):
                if qualname == 'NoneType':
                    return '``None``'
                elif link:
                    return ':class:`{}`'.format(qualname)
                else:
                    return qualname

            role = 'class'
            params = None
            # Check first if we have an TypingMeta instance, because when mixing in another
            # meta class, some information might get lost.
            # For example, a class inheriting from both Tuple and Enum ends up not having the
            # TypingMeta metaclass and hence none of the Tuple typing information.
            if isinstance(annotation, typing.TypingMeta):
                # Since Any is a superclass of everything, make sure it gets handled normally.
                if annotation is typing.Any:
                    role = 'data'
                # Generic classes have type arguments
                elif isinstance(annotation, typing.GenericMeta):
                    params = annotation.__args__
                    # Make sure to format Generic[T, U, ...] correctly, because it only
                    # has parameters but nor argument values for them
                    if not params and issubclass(annotation, typing.Generic):
                        params = annotation.__parameters__
                # Tuples are not Generics, so handle their type parameters separately.
                elif issubclass(annotation, typing.Tuple):
                    role = 'data'
                    if annotation.__tuple_params__:
                        params = list(annotation.__tuple_params__)
                    # Tuples can have variable size with a fixed type, indicated by an Ellipsis:
                    # e.g. Tuple[T, ...]
                    if annotation.__tuple_use_ellipsis__:
                        params.append(Ellipsis)
                # Unions are not Generics, so handle their type parameters separately.
                elif issubclass(annotation, typing.Union):
                    role = 'data'
                    if annotation.__union_params__:
                        params = list(annotation.__union_params__)
                        # If the Union contains None, wrap it in an Optional, i.e.
                        # Union[T,None]   => Optional[T]
                        # Union[T,U,None] => Optional[Union[T, U]]
                        if type(None) in annotation.__union_set_params__:
                            qualname = 'Optional'
                            params.remove(type(None))
                            if len(params) > 1:
                                params = [typing.Union[tuple(params)]]
                # Callables are not Generics, so handle their type parameters separately.
                # They have the format Callable[arg_types, return_type].
                # arg_types is either a list of types or an Ellipsis for Callables with
                # variable arguments.
                elif issubclass(annotation, typing.Callable):
                    role = 'data'
                    if annotation.__args__ is not None or annotation.__result__ is not None:
                        if annotation.__args__ is Ellipsis:
                            args_value = Ellipsis
                        else:
                            args_value = '\\[{}]'.format(', '.join(format_annotation(a, obj, link)
                                                                   for a in annotation.__args__))
                        params = [args_value, annotation.__result__]
                # Type variables are formatted with a prefix character (~, +, -)
                # which have to be escaped.
                elif isinstance(annotation, typing.TypeVar):
                    return '\\' + repr(annotation)
                # Strings inside of type annotations are converted to _ForwardRef internally
                elif isinstance(annotation, typing._ForwardRef):
                    try:
                        try:
                            global_vars = obj is not None and obj.__globals__ or dict()
                        except AttributeError:
                            global_vars = dict()
                        # Evaluate the type annotation string and then format it
                        actual_type = eval(annotation.__forward_arg__, global_vars)
                        return format_annotation(actual_type, obj, link)
                    except Exception:
                        return annotation.__forward_arg__

            generic = '\\[{}]'.format(', '.join(format_annotation(p, obj, link)
                                                for p in params)) if params else ''
            format_str = ':{}:`~{}.{}`{}' if link else '{1}.{2}{3}'
            return format_str.format(role, annotation.__module__, qualname, generic)
        # _TypeAlias is an internal class used for the Pattern/Match types
        # It represents an alias for another type, e.g. Pattern is an alias for any string type
        elif isinstance(annotation, typing._TypeAlias):
            actual_type = format_annotation(annotation.type_var, obj, link)
            format_str = ':class:`~typing.{}`\\[{}]' if link else 'typing.{}\\[{}]'
            return format_str.format(annotation.name, actual_type)
        # Ellipsis is used in Callable/Tuple
        elif annotation is Ellipsis:
            return '...'

        return str(annotation)

except ImportError:

    def get_type_hints(obj, globals, locals):
        """Dummy replacement that returns an empty type hint dictionary."""
        return {}

    def format_annotation(annotation, obj=None, link=True):
        if inspect.isclass(annotation):
            try:
                qualname = annotation.__qualname__
            except AttributeError:
                qualname = annotation.__name__

            # builtin types don't need to be qualified with a module name
            if annotation.__module__ in ('builtins', '__builtin__'):
                if qualname == 'NoneType':
                    return '``None``'
                elif link:
                    return ':class:`{}`'.format(qualname)
                else:
                    return qualname

            format_str = ':obj:`~{}.{}`' if link else '{}.{}'
            return format_str.format(annotation.__module__, qualname)

        return str(annotation)

__all__ = ['get_type_hints']
