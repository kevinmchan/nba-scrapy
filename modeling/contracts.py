import pandas as pd
import functools
from typing import Callable, Optional, Tuple, Dict


def _input_size(
    args: Optional[Tuple], kwargs: Optional[Dict], arg_pos: int, kw_name: str
):
    input_size = None
    if args:
        try:
            input_size = len(args[arg_pos])
        except IndexError as error:
            pass
        except Exception as error:
            msg = f"Unexpected exception when trying to check input size in {args} at position {arg_pos}"
            raise Exception(msg) from error

    if kwargs:
        try:
            input_size = len(kwargs[kw_name])
        except KeyError as error:
            pass
        except Exception as error:
            msg = f"Unexpected exception when trying to check input size in {kwargs} with keyword {kw_name}"
            raise Exception(msg) from error

    if input_size is None:
        raise Exception(
            f"Could not find input at position {arg_pos} or with keyword {kw_name}"
        )

    return input_size


def method_output_is_same_size(arg_pos: int, kw_name: str):
    """Requires the that first argument to a function is the same length as the output
    
    Params:
        arg_pos: index of positional argument that is being tested
        kw_name: name of keyword argument that is being tested
    """

    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapped(self, *args, **kwargs):
            input_size = _input_size(
                args=args, kwargs=kwargs, arg_pos=arg_pos, kw_name=kw_name
            )
            ouput = func(self, *args, **kwargs)
            output_size = len(ouput)
            assert_msg = f"Input size of {input_size} does not match output size of {output_size}"
            assert input_size == output_size, assert_msg
            return ouput

        return wrapped

    return decorator
