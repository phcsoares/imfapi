import os
import time
from typing import (
    Literal,
    TypeVar,
)
from pydantic import BaseModel, Field
from pydantic.dataclasses import dataclass

import pandas as pd
from joblib import Parallel, delayed

# from tqdm import tqdm
from tqdm.notebook import tqdm
# from fastprogress import master_bar

from imfapi._constants import JSON_RESTFUL_ENDPOINT, DATAFLOW, DATA_STRUCTURE
from imfapi.data_models.data_structure import DataStructureModel
from imfapi.utils import chunk_iterable, make_request, make_json_request, strjoin


T = TypeVar("T", covariant=True)


_TIME_WINDOW = 5
_MAX_REQUESTS_AT_ONCE = 10


class DataBase(BaseModel):
    name: str
    database_id: str
    structure: DataStructureModel = Field(repr=False)

    @property
    def dimensions(self) -> pd.DataFrame:
        return self.structure.structure.code_lists.to_pandas()


@dataclass
class IMFData:
    databases_to_load: Literal["main", "all"] = "main"
    database_ids: list[str] = Field(default_factory=list, init=False, repr=False)
    databases: list[DataBase] = Field(default_factory=list, init=False, repr=False)

    # def model_post_init(self, __context: Any):
    def __post_init__(self):
        self._load_database_ids()

    def populate_indicators(self):
        self._load_database_indicators()

    def _load_database_ids(self):
        response = make_request(strjoin(JSON_RESTFUL_ENDPOINT, DATAFLOW))
        data_json = response.json()
        df = pd.json_normalize(data_json["Structure"]["Dataflows"]["Dataflow"])
        self._df = df
        self._all_database_ids = sorted(df["KeyFamilyRef.KeyFamilyID"].map(str))

        database_ids = self._all_database_ids[:]
        if self.databases_to_load == "main":
            database_ids = [
                db_id
                for db_id in self._all_database_ids
                if not any([s.isnumeric() for s in db_id]) and "DISCONTINUED" not in db_id
            ]
        self.database_ids = database_ids

    def _make_databases(self) -> list[DataBase]:
        databases = []
        for db_json in self._indicators_json:
            db_id = db_json["Structure"]["KeyFamilies"]["KeyFamily"]["@id"]
            name = self._df.loc[(self._df["KeyFamilyRef.KeyFamilyID"] == db_id), "Name.#text"].iloc[0]
            database = DataBase(name=name, database_id=db_id, structure=db_json)
            databases.append(database)
            setattr(self, db_id, database)
        return databases

    def _load_database_indicators(self):
        indicators_json = []
        for ids in tqdm(chunk_iterable(iterable=self.database_ids, chunk_size=_MAX_REQUESTS_AT_ONCE)):
            indicators_json.extend(
                Parallel(n_jobs=min(os.cpu_count(), _MAX_REQUESTS_AT_ONCE), prefer="threads")(
                    delayed(make_json_request)(strjoin(JSON_RESTFUL_ENDPOINT, DATA_STRUCTURE, db_id)) for db_id in ids
                )
            )
            if len(self.database_ids) > _MAX_REQUESTS_AT_ONCE:
                time.sleep(_TIME_WINDOW + 0.1)
        self._indicators_json = indicators_json
        self.databases = self._make_databases()
