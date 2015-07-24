"""
Person.py
Writes to MongoDB Collection: links
"""

from . import abstract as abst
from . import schema
from . import time

import logging
logger = logging.getLogger(__name__)


class Person(abst.AbstractMongoRecord):
    """
    Homo Sapiens
    """
    collection = 'person'
    track_pkeys = True
    pkeys = ["key"]

    required_attrs = [
        "key",
        "names"
    ]
    optional_attrs = [
        "era",  # A key to a TimePeriod of type Era
        "generation",  # A key to a TimePeriod of type Generation
        "birthYear",
        "birthYearIsApprox",
        "birthPlace",
        "birthPlaceGeo"
        "deathYear",
        "deathYearIsApprox",
        "deathPlace",
        "deathPlaceGeo",
        "enBio",
        "heBio",
        "enWikiLink",
        "heWikiLink",
        "enJeLink",
        "sex",
        "rels"  # list of ... type and list of targets ... (two way?)
    ]

    def _normalize(self):
        super(self, Person)._normalize()
        self.names = self.name_group.titles
        if not self.key and self.primary_name("en"):
            self.key = self.primary_name("en")

    def _validate(self):
        super(self, Person)._validate()
        assert self.key

    # Names
    # This is the same as on TimePeriod, and very similar to Terms - abstract out
    def _init_defaults(self):
        self.name_group = None

    def _set_derived_attributes(self):
        if getattr(self, "names", None):
            self.set_names(self.names)

    def set_names(self, names):
        self.name_group = schema.TitleGroup(names)

    def all_names(self, lang=None):
        return self.name_group.all_titles(lang)

    def primary_name(self, lang=None):
        return self.name_group.primary_title(lang)

    def secondary_names(self, lang=None):
        return self.name_group.secondary_titles(lang)

    # Dates
    # A person may have an era, a generation, or a specific birth and death years, which each may be approximate.
    # They may also have none of these...
    def mostAccurateTimePeriod(self):
        if getattr(self, "birthYear", None) and getattr(self, "deathYear", None):
            return time.TimePeriod( {
                "start": self.birthYear,
                "startIsApprox": getattr(self, "birthYearIsApprox", False),
                "end": self.deathYear,
                "endIsApprox": getattr(self, "deathYearIsApprox", False)
            })
        elif getattr(self, "generation", None):
            return time.TimePerido().load({"symbol": self.generation})
        elif getattr(self, "era", None):
            return time.TimePerido().load({"symbol": self.era})
        else:
            return None


class PersonSet(abst.AbstractMongoSet):
    recordClass = Person


class PersonRelationship(abst.AbstractMongoRecord):
    collection = 'person_rel'

    required_attrs = [
        "from_key",
        "to_key",
        "type"
    ]
    optional_attrs = []

class PersonRelationshipSet(abst.AbstractMongoRecord):
    recordClass = PersonRelationship


"""
def process_index_title_change_in_gardens(indx, **kwargs):
    if indx.is_commentary():
        pattern = r'^{} on '.format(re.escape(kwargs["old"]))
    else:
        commentators = text.IndexSet({"categories.0": "Commentary"}).distinct("title")
        pattern = ur"(^{} \d)|(^({}) on {} \d)".format(re.escape(kwargs["old"]), "|".join(commentators), re.escape(kwargs["old"]))
        #pattern = r'(^{} \d)|( on {} \d)'.format(re.escape(kwargs["old"]), re.escape(kwargs["old"]))
    links = LinkSet({"refs": {"$regex": pattern}})
    for l in links:
        l.refs = [r.replace(kwargs["old"], kwargs["new"], 1) if re.search(pattern, r) else r for r in l.refs]
        try:
            l.save()
        except InputError: #todo: this belongs in a better place - perhaps in abstract
            logger.warning("Deleting link that failed to save: {} {}".format(l.refs[0], l.refs[1]))
            l.delete()


def process_index_delete_in_gardens(indx, **kwargs):
    if indx.is_commentary():
        pattern = ur'^{} on '.format(re.escape(indx.title))
    else:
        commentators = text.IndexSet({"categories.0": "Commentary"}).distinct("title")
        pattern = ur"(^{} \d)|^({}) on {} \d".format(re.escape(indx.title), "|".join(commentators), re.escape(indx.title))
    LinkSet({"refs": {"$regex": pattern}}).delete()
"""