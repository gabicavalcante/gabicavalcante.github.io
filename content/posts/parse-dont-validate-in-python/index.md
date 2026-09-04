+++
title = "Parse, don't validate, in Python"
description = "Alexis King's \"Parse, don't validate\" in Python: refinement types instead of checks, where DRF hands the precision back, and where the lack of private constructors stops you."
date = "2026-08-28"
draft = true
tags = ["python", "django"]
+++

There is a comment I have written more than once, and I suspect you have too. A function reaches into a list, or a dict, or an optional field, and just above the line sits some version of `# the caller already checked this`. That comment is a note saying the type system used to know something and has forgotten it. Alexis King's [Parse, don't validate](https://lexi-lambda.github.io/blog/2019/11/05/parse-don-t-validate/) is about where that knowledge goes and how to stop losing it. The post is Haskell. The idea travels to Python mostly intact, and the places where it does not are the part worth reading.

<!--more-->

This is my study guide after reading it. Go read the original too. Links to everything are at the end.

## The function that cannot be written

```python
def first(items: list[int]) -> int:
    return items[0]
```

The signature promises an `int` back for every list you pass. Hand it `[]` and you get `IndexError`. Haskell refuses to compile the equivalent without a warning about the missing case. Python takes it happily, and the hole stays invisible in the signature, which is where anyone reading the code will look.

There are two ways out. Weaken the return type:

```python
def first(items: list[int]) -> int | None: ...
```

Honest, and now every caller handles `None`, including the callers that already know the list has something in it.

Or strengthen the argument type:

```python
def first(items: NonEmpty[int]) -> int: ...
```

This one is total. Every input has an answer. The empty case did not vanish, it moved to whoever constructs the `NonEmpty`, once, at the edge of the system.

Here is a `NonEmpty` small enough to fit in a post. The generic syntax needs Python 3.12.

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class NonEmpty[T]:
    head: T
    tail: tuple[T, ...] = ()


def first(items: NonEmpty[int]) -> int:
    return items.head
```

## Two functions, one difference

```python
def validate_non_empty[T](items: list[T]) -> None:
    if not items:
        raise ValueError("list cannot be empty")


def parse_non_empty[T](items: list[T]) -> NonEmpty[T]:
    match items:
        case [head, *tail]:
            return NonEmpty(head, tuple(tail))
        case _:
            raise ValueError("list cannot be empty")
```

Same work. Same failure. The difference is the return type, and that difference is the whole article.

`None` is the type that carries no information. The validator learned something about `items` and then threw it away, so the knowledge now lives in the reader's head and in a comment, neither of which a type checker can see. `NonEmpty[T]` is a refinement of the input, so the knowledge rides along with the value and every function downstream can rely on it without asking again.

King's definition is worth memorizing: "a parser is just a function that consumes less-structured input and produces more-structured output." By that definition `int()`, `datetime.fromisoformat()`, and a DRF field's `to_internal_value` are all parsers. `assert isinstance(x, int)` is not.

## What the validator costs you later

```python
def load_config(config_dirs: list[str]) -> Config:
    validate_non_empty(config_dirs)
    ...
    cache_dir = first(config_dirs)  # safe, and nothing in the code says why
```

That is fine today. It costs you three things over time.

Redundant checks, first. If `first` returns `int | None` you write the `if` again here, and in the next function, and the one after that, all of them provably dead.

Then the branches you write to satisfy the checker, the ones ending in `raise AssertionError("should never happen")`. Every one of those is a place where you knew more than the code could express.

The third is the one that actually bites. Delete the `validate_non_empty` line during a refactor and nothing breaks. Not the type checker, not the tests that pass non-empty lists, nothing until a user sends an empty list in production. There is no link between the check and the use for anything to notice.

## Shotgun parsing

King borrows the term from a LangSec paper: "a programming antipattern whereby parsing and input-validating code is mixed with and spread across processing code, throwing a cloud of checks at the input, and hoping, without any systematic justification, that one or another would catch all the 'bad' cases."

In Django it usually looks like this:

```python
def handle_signup(payload: dict) -> None:
    user = User.objects.create(email=payload["email"])   # already acted
    if "@" not in payload["email"]:                      # checked, too late
        raise ValidationError("bad email")
    send_welcome_email(user)
```

The paper's own line about why this hurts: "Late-discovered errors in an input stream will result in some portion of invalid input having been processed, with the consequence that program state is difficult to accurately predict." A half-written row, a sent email, a charged card.

Parsing at the boundary splits the program in two. Everything that can fail because of bad input happens before anything happens at all.

## The rules, in Python

King gives six pieces of advice. Each one has a Python shape.

### Make illegal states unrepresentable

The version I meet most often is a boolean next to an optional.

```python
@dataclass
class User:
    email: str
    is_verified: bool
    verified_at: datetime | None
```

Four combinations, two of them nonsense: verified with no timestamp, unverified with one. Nothing stops either from being written, so every function that touches this has to decide what to do about them, and different functions will decide differently.

```python
from typing import assert_never


@dataclass(frozen=True)
class Unverified:
    email: str


@dataclass(frozen=True)
class Verified:
    email: str
    verified_at: datetime


type User = Unverified | Verified


def badge(user: User) -> str:
    match user:
        case Unverified():
            return "not verified"
        case Verified(verified_at=when):
            return f"verified on {when:%Y-%m-%d}"
        case _:
            assert_never(user)
```

`assert_never` earns its place here. Add a third state to the union and mypy fails this function at the `case _` line, which is how you find every place that needs updating without grepping for it.

### Push the burden of proof upward

A checker that returns nothing is optional. A parser that returns the thing you need is not.

```python
def check_no_duplicate_keys(pairs: list[tuple[str, int]]) -> None: ...   # skippable

def index_by_key(pairs: list[tuple[str, int]]) -> dict[str, int]: ...    # unskippable
```

Nobody forgets to call the second one, because the rest of the function needs what it returns. That is the trick in one line: make the proof the only route to the value.

### Let your datatypes inform your code

King puts it as a warning against sticking a `Bool` in a record somewhere, which is the `is_verified` field above. The order matters. Decide what shape the data has, then write functions over that shape, rather than adding a field every time a function needs to remember something.

### Parse in more than one pass

Avoiding shotgun parsing does not mean everything has to happen in one function. `bytes` to JSON to `dict` to a domain object is three passes and perfectly clean. Reading an already-parsed `type` field to decide how to parse the rest is fine too. What you must not do is act on the data while it is still half parsed.

### Avoid denormalized representations, especially mutable ones

Two copies of the same fact is an illegal state waiting to happen, because they can disagree. A `total` field next to the line items that compute it will drift the first time somebody updates one without the other. When you do need the duplicate for performance, keep it behind an interface that updates both, so there is one place to get it wrong instead of forty.

### Fake a parser with an abstract type

This is where Python's ceiling shows up.

```python
@dataclass(frozen=True)
class Email:
    value: str

    @classmethod
    def parse(cls, raw: str) -> "Email":
        if "@" not in raw:
            raise ValueError(f"not an email: {raw}")
        return cls(raw)
```

`Email.parse` is a real parser. `Email("garbage")` is also still legal, passes mypy, and produces an `Email` that is not one. Python has no private constructors, so the guarantee holds by convention and code review rather than by construction. Leading underscores and `__init_subclass__` tricks make it awkward rather than impossible.

Pydantic buys you the rest, because its validators run inside `__init__`, so the only door into the type is guarded:

```python
from pydantic import BaseModel, EmailStr


class Signup(BaseModel):
    email: EmailStr
    display_name: str
```

`Signup(email="garbage", display_name="x")` raises. That is a genuine smart constructor, paid for with a dependency and a runtime cost on every instantiation. Worth it at the boundary. Rarely worth it for a type that only ever gets built by code you already control.

King wrote a follow-up on exactly this gap, [Names are not type safety](https://lexi-lambda.github.io/blog/2020/11/01/names-are-not-type-safety/), which is the thing to read before reaching for `typing.NewType`. `NewType` gives you a distinct name for mypy and no runtime check at all, so `UserId = NewType("UserId", int)` documents intent and stops an argument mix-up, and it proves nothing about the value.

## Where Django hands the precision back

DRF parses well and then drops the result on the floor.

```python
serializer = OrderSerializer(data=request.data)
serializer.is_valid(raise_exception=True)
create_order(serializer.validated_data)
```

`validated_data` is a `dict[str, Any]`. Every field was checked, coerced and normalized, and then packed back into the least precise type in the language. Inside `create_order` you are writing `data["customer_id"]` again with no guarantee the key exists, no type on what comes out, and no help from mypy if you rename a field in the serializer.

The fix is small. Do not let the parse decay at the boundary.

```python
@dataclass(frozen=True)
class OrderRequest:
    customer_id: UUID
    items: NonEmpty[LineItem]


class OrderCreateView(APIView):
    def post(self, request):
        serializer = OrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = create_order(OrderRequest(**serializer.validated_data))
        return Response(OrderSerializer(order).data, status=201)


def create_order(request: OrderRequest) -> Order: ...
```

`create_order` now states what it needs, and every function it calls can too. The serializer keeps doing the work it is good at, and the dict stops at the view. If you are starting fresh and this appeals to you, Django Ninja does it out of the box, because it is Pydantic all the way down and hands the view a typed object instead of a dict.

## Where I stop

Not every value deserves its own type. A `NonEmpty` for a list that gets built and consumed inside the same twenty lines is ceremony, and a codebase where every string is wrapped in something is genuinely worse to read than one that is not. The cost is real and it lands on the next person.

The two signals I use to decide: the same check appearing in more than one function, and a comment explaining why a check is unnecessary here. Both mean a fact about the data is being carried by hand. That fact wants to live in the type, parsed once, at the edge.

## References

- [Parse, don't validate](https://lexi-lambda.github.io/blog/2019/11/05/parse-don-t-validate/), Alexis King, 2019
- [Names are not type safety](https://lexi-lambda.github.io/blog/2020/11/01/names-are-not-type-safety/), Alexis King, 2020
- [The Seven Turrets of Babel: a taxonomy of LangSec errors](https://langsec.org/papers/langsec-cwes-secdev2016.pdf), Momot, Bratus, Hallberg and Patterson, SecDev 2016
- [Effective ML revisited](https://blog.janestreet.com/effective-ml-revisited/), Yaron Minsky, where "make illegal states unrepresentable" comes from
- [PEP 695](https://peps.python.org/pep-0695/) for the type parameter syntax, and the [typing docs on NewType](https://docs.python.org/3/library/typing.html#newtype)
- [Pydantic](https://docs.pydantic.dev/latest/) and [Django Ninja](https://django-ninja.dev/)
