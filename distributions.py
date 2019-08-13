__version__ = "0.2.1"

import re


def get_relevant_distribution(dcat_entry):
    """
    Given a DCAT entry, find the most relevant distribution
    for the intake catalog. Returns a tuple of
    (intake_driver_name, distribution). In general,
    we choose the more specific formats over the less specific
    formats. At present, they are ranked in the following order:

        GeoJSON
        Shapefile
        CSV

    If none of these are found, None.
    If there are no distributions, it returns None.
    """
    distributions = dcat_entry.get("distribution")
    if not distributions or not len(distributions):
        return None

    for d in distributions:
        if test_geojson(d):
            return "geojson", geojson_driver_args(d)
    for d in distributions:
        if test_shapefile(d):
            return "shapefile", shapefile_driver_args(d)
    for d in distributions:
        if test_csv(d):
            return "csv", csv_driver_args(d)

    return None


def test_geojson(distribution):
    """
    Test if a DCAT:distribution is GeoJSON.
    """
    return distribution.get("mediaType") == "application/vnd.geo+json"


def test_csv(distribution):
    """
    Test if a DCAT:distribution is CSV.
    """
    return distribution.get("mediaType") == "text/csv"


def test_shapefile(distribution):
    """
    Test if a DCAT:distribution is a Shapefile.
    """
    # TODO: can there be a more robust test here?
    url = distribution.get("downloadURL") or distribution.get("accessURL") or ""
    title = distribution.get("title") or ""
    return (
        title.lower() == "shapefile"
        or re.search("format=shapefile", url, re.I) is not None
    )


def geojson_driver_args(distribution):
    """
    Construct driver args for a GeoJSON distribution.
    """
    url = distribution.get("downloadURL") or distribution.get("accessURL")
    if not url:
        raise KeyError(f"A download URL was not found for {str(distribution)}")
    return {"urlpath": url}


def csv_driver_args(distribution):
    """
    Construct driver args for a GeoJSON distribution.
    """
    url = distribution.get("downloadURL") or distribution.get("accessURL")
    if not url:
        raise KeyError(f"A download URL was not found for {str(distribution)}")
    return {"urlpath": url, "csv_kwargs": {"blocksize": None, "sample": False}}


def shapefile_driver_args(distribution):
    """
    Construct driver args for a GeoJSON distribution.
    """
    url = distribution.get("downloadURL") or distribution.get("accessURL")
    if not url:
        raise KeyError(f"A download URL was not found for {str(distribution)}")
    args = {"urlpath": url, "geopandas_kwargs": {}}
    if distribution["mediaType"] == "application/zip":
        args["geopandas_kwargs"]["compression"] = "zip"
    return args

from typing import ClassVar

import requests
import yaml

from intake.catalog import Catalog
from intake.catalog.local import LocalCatalogEntry

from .distributions import get_relevant_distribution
from . import _version


class DCATCatalog(Catalog):
    """
    A Catalog that references a DCAT catalog at some URL
    and constructs an intake catalog from it, with opinionated
    choices about the drivers that will be used to load the datasets.
    In general, the drivers are in order of decreasing specificity:

    GeoJSON
    Shapefile
    CSV
    """

    name: ClassVar[str] = "dcat"
    version: ClassVar[str] = _version

    def __init__(self, url, name="catalog", items=None, metadata=None, **kwargs):
        """
        Initialize the catalog.

        Parameters
        ----------
        url: str
            A URL pointing to a DCAT catalog, usually named data.json
        name: str
            A name for the catalog
        items: Dict[str, str]
            A mapping of {name: id} of entries to include.
            The name is a human-redable name, and the id is the DCAT identifier.
            If `None` is given, then all entries are included.
        metadata: dict
            Additional information about the catalog
        """
        self.url = url
        self.name = name
        self._items = items
        super().__init__(name=name, metadata=metadata, **kwargs)

    def _load(self):
        """
        Load the catalog from the remote data source.
        """
        resp = requests.get(self.url)
        catalog = resp.json()
        self._entries = {
            entry["identifier"]: DCATEntry(entry)
            for entry in catalog["dataset"]
            if should_include_entry(entry, self._items)
        }

    def serialize(self):
        """
        Serialize the catalog to yaml.

        Returns
        -------
        A string with the yaml-formatted catalog.
        """
        output = {"metadata": self.metadata, "sources": {}}
        for key, entry in self.items():
            output["sources"][key] = yaml.safe_load(entry.yaml())["sources"][key]
        return yaml.dump(output)


class DCATEntry(LocalCatalogEntry):
    """
    A class representign a DCAT catalog entry, which knows how to pretty-print itself.
    """

    def __init__(self, dcat_entry):
        """
        Construct an Intake catalog entry from a DCAT catalog entry.
        """
        driver, args = get_relevant_distribution(dcat_entry)
        name = dcat_entry["identifier"]
        description = f"## {dcat_entry['title']}\n\n{dcat_entry['description']}"
        metadata = {"dcat": dcat_entry}
        super().__init__(name, description, driver, True, args=args, metadata=metadata)

    def _ipython_display_(self):
        """
        Print an HTML repr for the entry
        """
        dcat = self.metadata["dcat"]
        title = dcat.get("title") or "unknown"
        entry_id = dcat.get("identifier")
        description = dcat.get("description")
        issued = dcat.get("issued") or "unknown"
        modified = dcat.get("modified") or "unknown"
        license = dcat.get("license") or "unknown"
        organization = dcat.get("publisher")
        publisher = organization.get("name") or "unknown" if organization else "unknown"
        download = self._open_args.get("urlpath") or "unknown"

        info = f"""
            <p style="margin-bottom: 0.5em"><b>ID:</b><a href="{entry_id}"> {entry_id}</a></p>
            <p style="margin-bottom: 0.5em"><b>Issued:</b> {issued}</p>
            <p style="margin-bottom: 0.5em"><b>Last Modified:</b> {modified}</p>
            <p style="margin-bottom: 0.5em"><b>Publisher:</b> {publisher}</p>
            <p style="margin-bottom: 0.5em"><b>License:</b> {license}</p>
            <p style="margin-bottom: 0.5em"><b>Download URL:</b><a href="{download}"> {download}</a></p>
        """
        html = f"""
        <h3>{title}</h3>
        <div style="display: flex; flex-direction: row; flex-wrap: wrap; height:256px">
            <div style="flex: 0 0 384px; padding-right: 24px">
                {info}
            </div>
            <div style="flex: 1 1 0; height: 100%; overflow: auto">
                <p>
                    {description}
                </p>
            </div>
        </div>
        """

        return display(
            {
                "text/html": html,
                "text/plain": "\n".join([entry_id, title, description]),
            },
            raw=True,
        )


def should_include_entry(dcat_entry, items=None):
    """
    Return if a given DCAT entry should be included in the dataset.
    Returns True if we can find a driver to load it (GeoJSON,
    Shapefile, CSV), False otherwise.
    """
    vals = list(items.values()) if items else []
    if items is not None and dcat_entry["identifier"] not in vals:
        return False
    return get_relevant_distribution(dcat_entry) != None

import argparse
import sys
import yaml

from intake.cli.bootstrap import main as run
from intake.cli.util import Subcommand

from .catalog import DCATCatalog
from .util import mirror_data


class Mirror(Subcommand):
    """
    Mirror a catalog subset specified in a manifest to a remote bucket,
    and print the resulting subsetted catalog to stdout.


    If --dry-run is specified, then no upload happens, but the catalog is still printed.
    """

    name = "mirror"

    def initialize(self):
        """
        Initialize the subcommand by adding the argparser arguments.
        """
        self.parser.add_argument(
            "manifest",
            type=str,
            metavar="MANIFEST",
            help="Path to a manifest YAML file",
        )
        self.parser.add_argument(
            "--dry-run",
            help="If this flag is given, no upload occurs",
            action="store_true",
        )
        self.parser.add_argument(
            "--version", metavar="VERSION", type=str, help="Catalog version"
        )
        self.parser.add_argument(
            "--name", metavar="VERSION", type=str, help="Catalog name"
        )

    def invoke(self, args):
        """
        Invoke the command.
        """
        upload = not args.dry_run
        catalog = mirror_data(
            args.manifest, upload=upload, name=args.name, version=args.version
        )
        print(yaml.dump(catalog))


class Create(Subcommand):
    """
    Create an intake YAML catalog from a DCAT catalog and print it to stdout.
    """

    name = "create"

    def initialize(self):
        """
        Initialize the subcommand by adding the argparser arguments.
        """
        self.parser.add_argument("uri", metavar="URI", type=str, help="Catalog URI")
        self.parser.add_argument(
            "--version", metavar="VERSION", type=str, help="Catalog version"
        )
        self.parser.add_argument(
            "--name", metavar="VERSION", type=str, help="Catalog name"
        )

    def invoke(self, args):
        """
        Invoke the command.
        """
        version = args.version or None
        name = args.name or ""
        metadata = {"name": name, "version": version}
        catalog = DCATCatalog(args.uri, name=name, metadata=metadata)
        print(catalog.serialize())


subcommands = [Mirror, Create]


def main(argv=None):
    return run("Intake DCAT CLI", subcommands, argv or sys.argv)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
