"""Defines a minimal model representing a dataset."""

import logging
import time

import lydata.utils as lyutils
import pandas as pd
from django.db import models
from github import Repository
from lydata.loader import LyDataset
from lydata.validator import cast_dtypes

from lyprox import loggers
from lyprox.accounts.models import Institution
from lyprox.settings import GITHUB_TOKEN, JOBLIB_MEMORY, LNLS
from lyprox.utils import cached_get_repo

logger = logging.getLogger(__name__)


def create_empty_modality_table(name: str, length: int) -> pd.DataFrame:
    """Create an empty, three-level header DataFrame for a modality."""
    columns = pd.MultiIndex.from_product([[name], ["ipsi", "contra"], LNLS])
    empty = pd.DataFrame([[None] * len(columns)] * length, columns=columns)
    empty[name, "core", "date"] = None
    return empty


def ensure_lnls_in_modalities(dataset: pd.DataFrame) -> pd.DataFrame:
    """Make sure every modality contains all LNLs."""
    dataset = dataset.copy()

    for modality in lyutils.get_default_modalities():
        empty = create_empty_modality_table(modality, len(dataset))
        updated = empty

        if modality in dataset.columns:
            original = dataset[[modality]]
            updated = lyutils.update_and_expand(left=original, right=empty)

        dataset = dataset.drop(columns=modality, errors="ignore")
        dataset = dataset.join(updated)

    return dataset


@JOBLIB_MEMORY.cache
def cached_load_dataframe(
    year: int,
    institution: str,
    subsite: str,
    repo_name: str,
    ref: str,
) -> pd.DataFrame:
    """Load an enhanced dataset into a pandas DataFrame using a persistent cache."""
    lydataset = LyDataset(
        year=year,
        institution=institution,
        subsite=subsite,
        repo_name=repo_name,
        ref=ref,
    )
    df = lydataset.get_dataframe(use_github=True, token=GITHUB_TOKEN)
    df = ensure_lnls_in_modalities(df)
    df = cast_dtypes(df)
    logger.info(f"Loaded dataset {lydataset} into DataFrame ({df.shape=}).")
    return df


class DatasetModel(loggers.ModelLoggerMixin, models.Model):
    """Minimal model representing a dataset.

    This is basically a Django representation of the `LyDataset` class.

    Its `DatasetModel.load_dataframe` method makes use of the function
    `cached_load_dataframe` to load the dataset into a pandas DataFrame.
    Note that this function uses `joblib` to cache the results of the function call
    in a persistent location given by the ``JOBLIB_CACHE_DIR`` setting.
    """

    year: int = models.IntegerField()
    institution: Institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    subsite: str = models.CharField(max_length=100)
    repo_name: str = models.CharField(max_length=100)
    ref: str = models.CharField(max_length=100)
    is_private: bool = models.BooleanField(default=False)
    last_pushed: models.DateTimeField = models.DateTimeField()
    last_saved: models.DateTimeField = models.DateTimeField(auto_now=True)

    class Meta:
        """Meta options for the `DatasetModel`."""

        unique_together = ("year", "institution", "subsite")

    def save(self, *args, **kwargs) -> None:
        """Update the ``is_private`` field based on the GitHub repository."""
        repo = self.get_repo()
        self.is_private = repo.private
        self.last_pushed = repo.pushed_at
        return super().save(*args, **kwargs)

    @property
    def name(self) -> str:
        """Return the name of the dataset."""
        return f"{self.year}-{self.institution.shortname.lower()}-{self.subsite}"

    def __str__(self):
        """Return the name of the dataset."""
        return self.name

    def get_repo(self) -> Repository:
        """Return the GitHub repository object."""
        return cached_get_repo(repo_id=self.repo_name)

    def get_kwargs(self) -> dict[str, int | str]:
        """Assemble ``kwargs`` from this model's field.

        These will both be used to call the `cached_load_dataframe` function as well
        as initialize a `LyDataset` object.
        """
        return {
            "year": self.year,
            "institution": self.institution.shortname.lower(),
            "subsite": self.subsite,
            "repo_name": self.repo_name,
            "ref": self.ref,
        }

    def get_lydataset(self) -> LyDataset:
        """Create a `LyDataset` from this model."""
        return LyDataset(**self.get_kwargs())

    def load_dataframe(self) -> pd.DataFrame:
        """Load the underlying table.

        This calls the `cached_load_dataframe` function with the assembled
        ``kwargs`` and returns the resulting `pd.DataFrame`.
        """
        kwargs = self.get_kwargs()
        is_in_cache = cached_load_dataframe.check_call_in_cache(**kwargs)

        msg_add = "from cache." if is_in_cache else "from GitHub."

        start_time = time.perf_counter()
        table = cached_load_dataframe(**kwargs)
        elapsed_time = time.perf_counter() - start_time
        logger.info(f"Fetched dataset {self} in {elapsed_time:.2f}s {msg_add}")
        return table
