from __future__ import annotations

from typing import Optional

import pandas as pd
from pydantic import BaseModel, Field, ConfigDict


class Name(BaseModel):
    model_config = ConfigDict(extra="ignore")
    text: str = Field(..., alias="#text")

    def __str__(self) -> str:
        return self.text


class Description(BaseModel):
    model_config = ConfigDict(extra="ignore")
    text: str = Field(..., alias="#text")

    def __str__(self) -> str:
        return self.text


class CodeItem(BaseModel):
    model_config = ConfigDict(extra="ignore")
    value: str = Field(..., alias="@value")
    description: Description = Field(..., alias="Description")

    def to_pandas(self) -> pd.DataFrame:
        return pd.DataFrame([[self.value, self.description.text]], columns=["value", "description"])


class CodeListItem(BaseModel):
    model_config = ConfigDict(extra="ignore")
    code_list_item_id: str = Field(..., alias="@id")
    name: Name = Field(..., alias="Name")
    code: list[CodeItem] = Field(..., alias="Code")
    description: Optional[Description] = Field(default=None, alias="Description")

    def to_pandas(self) -> pd.DataFrame:
        df = pd.concat([code.to_pandas() for code in self.code], ignore_index=True)
        extra_fields = self.model_fields_set.copy()
        extra_fields.discard("code")
        for field in sorted(extra_fields):
            val = getattr(self, field)
            if not isinstance(val, int | float | str) and val is not None:
                val = str(val)
            df[field] = val
        return df


class CodeLists(BaseModel):
    code_list: list[CodeListItem] = Field(..., alias="CodeList")

    def to_pandas(self) -> pd.DataFrame:
        return pd.concat([cl.to_pandas() for cl in self.code_list], ignore_index=True)


class TextFormat(BaseModel):
    text_type: str = Field(..., alias="@textType")


class ConceptItem(BaseModel):
    model_config = ConfigDict(extra="ignore")
    concept_item_id: str = Field(..., alias="@id")
    name: Name = Field(..., alias="Name")
    # TextFormat: Optional[TextFormat] = None
    description: Optional[Description] = Field(default=None, alias="Description")


class ConceptScheme(BaseModel):
    model_config = ConfigDict(extra="ignore")
    concept_scheme_id: str = Field(..., alias="@id")
    name: Name = Field(..., alias="Name")
    concept: list[ConceptItem] = Field(..., alias="Concept")


class Concepts(BaseModel):
    concept_scheme: ConceptScheme = Field(..., alias="ConceptScheme")


class DimensionItem(BaseModel):
    concept_ref: str = Field(..., alias="@conceptRef")
    concept_version: str = Field(..., alias="@conceptVersion")
    concept_scheme_ref: str = Field(..., alias="@conceptSchemeRef")
    concept_scheme_agency: str = Field(..., alias="@conceptSchemeAgency")
    codelist: str = Field(..., alias="@codelist")
    codelist_version: str = Field(..., alias="@codelistVersion")
    codelist_agency: str = Field(..., alias="@codelistAgency")
    is_frequency_dimension: Optional[str] = Field(None, alias="@isFrequencyDimension")


class TimeDimension(BaseModel):
    concept_ref: str = Field(..., alias="@conceptRef")
    concept_version: str = Field(..., alias="@conceptVersion")
    concept_scheme_ref: str = Field(..., alias="@conceptSchemeRef")
    concept_scheme_agency: str = Field(..., alias="@conceptSchemeAgency")


class PrimaryMeasure(BaseModel):
    model_config = ConfigDict(extra="ignore")
    # conceptRef: str = Field(..., alias='@conceptRef')
    # conceptVersion: str = Field(..., alias='@conceptVersion')
    # conceptSchemeRef: str = Field(..., alias='@conceptSchemeRef')
    # conceptSchemeAgency: str = Field(..., alias='@conceptSchemeAgency')
    text_format: TextFormat = Field(..., alias="TextFormat")


class AttributeItem(BaseModel):
    model_config = ConfigDict(extra="ignore")
    # conceptRef: str = Field(..., alias='@conceptRef')
    # conceptVersion: str = Field(..., alias='@conceptVersion')
    # conceptSchemeRef: str = Field(..., alias='@conceptSchemeRef')
    # conceptSchemeAgency: str = Field(..., alias='@conceptSchemeAgency')
    # codelist: Optional[str] = Field(None, alias='@codelist')
    # codelistVersion: Optional[str] = Field(None, alias='@codelistVersion')
    # codelistAgency: Optional[str] = Field(None, alias='@codelistAgency')
    # attachmentLevel: str = Field(..., alias='@attachmentLevel')
    # assignmentStatus: str = Field(..., alias='@assignmentStatus')
    text_format: Optional[TextFormat] = Field(default=None, alias="TextFormat")
    # isTimeFormat: Optional[str] = Field(None, alias='@isTimeFormat')


class Components(BaseModel):
    model_config = ConfigDict(extra="ignore")
    # Dimension: List[DimensionItem]
    # TimeDimension: TimeDimension
    # PrimaryMeasure: PrimaryMeasure
    attribute: list[AttributeItem] = Field(..., alias="Attribute")


class AnnotationText(BaseModel):
    model_config = ConfigDict(extra="ignore")
    text: str = Field(..., alias="#text")


class AnnotationItem(BaseModel):
    model_config = ConfigDict(extra="ignore")
    annotation_title: str = Field(..., alias="AnnotationTitle")
    annotation_text: AnnotationText = Field(..., alias="AnnotationText")


class Annotations(BaseModel):
    annotation: list[AnnotationItem] = Field(..., alias="Annotation")


class KeyFamily(BaseModel):
    model_config = ConfigDict(extra="ignore")
    key_family_id: str = Field(..., alias="@id")
    name: Name = Field(..., alias="Name")
    components: Components = Field(..., alias="Components")
    annotations: Annotations = Field(..., alias="Annotations")


class KeyFamilies(BaseModel):
    key_family: KeyFamily = Field(..., alias="KeyFamily")


class Structure(BaseModel):
    model_config = ConfigDict(extra="ignore")
    code_lists: CodeLists = Field(..., alias="CodeLists")
    concepts: Concepts = Field(..., alias="Concepts")
    key_families: KeyFamilies = Field(..., alias="KeyFamilies")


class DataStructureModel(BaseModel):
    model_config = ConfigDict(extra="ignore")
    structure: Structure = Field(..., alias="Structure")
