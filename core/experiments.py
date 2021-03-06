from . import PersistentList
from fastapi import APIRouter
from fastapi.responses import ORJSONResponse
from .models import NewExperiment as RealItem, Sorting
from .fakers import NewExperiment as FakeItem
from rapidfuzz.process import extract

app = APIRouter()

real_items = PersistentList(RealItem)
fake_items = PersistentList(FakeItem)
fake_items.extend(real_items)


async def get_title_map():
    return {item: item.title for item in fake_items.list}


async def sort(it, key: Sorting):
    if key is Sorting.cost_ascending:
        return sorted(it, key=lambda item: item.salary)
    elif key is Sorting.cost_descending:
        return sorted(it, key=lambda item: item.salary, reverse=True)
    elif key is Sorting.duration_ascending:
        return sorted(it, key=lambda item: item.duration)
    elif key is Sorting.duration_descending:
        return sorted(it, key=lambda item: item.duration, reverse=True)
    elif key is Sorting.smart_ascending:
        return list(it)[::-1]
    elif key is Sorting.smart_descending:
        return list(it)


@app.get("/query/fake/{text}", response_class=ORJSONResponse)
async def query_fake_items_by_title(text: str, n: int = 3, key: Sorting = Sorting.smart_descending):
    """fuzzy matching using title"""
    return (await sort((i[2] for i in extract(text, await get_title_map(), limit=n)), key))[:n]


async def get_description_map():
    return {item: item.description for item in fake_items.list}


@app.get("/search/fake/{text}", response_class=ORJSONResponse)
async def search_fake_items_by_description(text: str, n: int = 3, key: Sorting = Sorting.smart_descending):
    """fuzzy matching using description"""
    return (await sort((i[2] for i in extract(text, await get_description_map(), limit=n)), key))[:n]


#####################################################################


@app.post("/new/fake", response_class=ORJSONResponse)
async def new_fake_experiment_item(item: FakeItem):
    """
    add a fake ExperimentItem to the fake database
    - the unfilled parameters will be default(fake) values
    """
    fake_items.append(item.to_item())
    return item.to_item().id


@app.delete("/fake", response_class=ORJSONResponse)
async def clear_all_fake_experiments():
    """clear the fake database"""
    return fake_items.clear()


@app.get("/fake/random/{n}", response_class=ORJSONResponse)
async def get_random_fake_items(n: int):
    """
    get many fake experimentItems as you want

    in case you require more than you posted,
    I promise you get something random rather than errors
    """
    for _ in range(n - len(fake_items)):
        await new_fake_experiment_item(FakeItem())
    return fake_items.sample(n)


#####################################################################


@app.post("/new", response_class=ORJSONResponse)
async def new_experiment_item(item: RealItem):
    real_items.append(item.to_item())
    return item.to_item().id


@app.delete("/", response_class=ORJSONResponse)
async def clear_all_experiments():
    return real_items.clear()


@app.get("/random/{n}", response_class=ORJSONResponse)
async def get_random_items(n: int):
    return real_items.sample(n)
