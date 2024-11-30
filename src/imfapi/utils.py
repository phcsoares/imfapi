from functools import cache
from typing import Any, Protocol, TypeVar, overload
from collections.abc import Generator, Iterable, Iterator
from json import JSONDecodeError

import requests
from tenacity import retry, wait_fixed, retry_if_exception_type, stop_after_attempt


MAX_RETRIES = 5

T = TypeVar("T", covariant=True)


def strjoin(*args: str, sep: str = "/") -> str:
    return sep.join(map(lambda x: str(x).rstrip(sep), filter(lambda x: any(s != sep for s in x) and len(x), args)))


class SizedIndexableIterable(Protocol[T]):
    def __len__(self) -> int: ...
    def __iter__(self) -> Iterator[T]: ...
    @overload
    def __getitem__(self, key: int) -> T: ...
    @overload
    def __getitem__(self, key: slice) -> Iterable[T]: ...


@cache
def make_request(url: str) -> requests.Response:
    return requests.get(url)


@cache
@retry(wait=wait_fixed(0.5), retry=retry_if_exception_type(JSONDecodeError), stop=stop_after_attempt(MAX_RETRIES))
def make_json_request(url: str) -> dict[str, Any]:
    data = requests.get(url)
    data.json()
    return data


def chunk_iterable(iterable: SizedIndexableIterable[T], chunk_size: int = 1) -> Generator[Iterable[T], Any, Any]:
    start = 0
    while start < len(iterable):
        end = start + chunk_size
        yield iterable[start:end]
        start = end


def in_colab():
    "Check if the code is running in Google Colaboratory"
    try:
        return True
    except Exception as e:
        print(type(e), e)
        return False


IN_COLAB = in_colab()


def in_notebook():
    "Check if the code is running in a jupyter notebook"
    if in_colab():
        return True
    try:
        shell = get_ipython().__class__.__name__
        if shell == "ZMQInteractiveShell":  # Jupyter notebook, Spyder or qtconsole
            import IPython

            # IPython version lower then 6.0.0 don't work with output you update
            return IPython.__version__ >= "6.0.0"
        elif shell == "TerminalInteractiveShell":
            return False  # Terminal running IPython
        else:
            return False  # Other type (?)
    except NameError:
        return False  # Probably standard Python interpreter


IN_NOTEBOOK = in_notebook()
