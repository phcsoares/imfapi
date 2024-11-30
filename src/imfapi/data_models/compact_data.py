from __future__ import annotations

from typing import Optional

import pandas as pd
from pydantic import BaseModel, Field, ConfigDict


class Name(BaseModel):
    model_config = ConfigDict(extra="ignore")
    text: str = Field(..., alias="#text")


class Obs(BaseModel):
    time_period: str = Field(..., alias="@TIME_PERIOD")
    obs_value: str = Field(..., alias="@OBS_VALUE")
    source_coverage_and_accounting_basis: Optional[str] = Field(
        default=None, alias="@SOURCE_COVERAGE_AND_ACCOUNTING_BASIS"
    )


class Series(BaseModel):
    freq: str = Field(..., alias="@FREQ")
    ref_area: str = Field(..., alias="@REF_AREA")
    indicator: str = Field(..., alias="@INDICATOR")
    unit_mult: str = Field(..., alias="@UNIT_MULT")
    time_format: str = Field(..., alias="@TIME_FORMAT")
    obs: list[Obs] = Field(..., alias="Obs")

    def to_pandas(self) -> pd.DataFrame:
        df = pd.DataFrame([obs.model_dump() for obs in self.obs])
        extra_fields = self.model_fields_set.copy()
        extra_fields.discard("obs")
        for field in sorted(extra_fields):
            df[field] = getattr(self, field)
        return df


class DataSet(BaseModel):
    model_config = ConfigDict(extra="ignore")
    series: Optional[list[Series]] = Field(default=None, alias="Series")

    def to_pandas(self) -> pd.DataFrame:
        if self.series is None:
            raise ValueError("The dataset is empty")
        return pd.concat([series.to_pandas() for series in self.series], ignore_index=True)


class CompactData(BaseModel):
    model_config = ConfigDict(extra="ignore")
    data_set: DataSet = Field(..., alias="DataSet")


class CompactDataModel(BaseModel):
    compact_data: CompactData = Field(..., alias="CompactData")
