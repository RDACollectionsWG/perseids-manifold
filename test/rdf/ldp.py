from unittest import TestCase
from src.utils.rdf.ldp import LDPModelExtension
from rdflib import URIRef

class LDPTest(TestCase):

    def test_add_container(self):
        ldp = LDPModelExtension()
        container = URIRef("container")
        member = URIRef("member")
        g = ldp.add_contains(container, member)
        self.assertIn((container, ldp.ns.contains, member), g)
        self.assertIn((member, ldp.ns.interactionModel, ldp.ns.BasicContainer), g)

    def test_add_member(self):
        ldp = LDPModelExtension()
        container = URIRef("container")
        member = URIRef("member")
        g = ldp.add_contains(container, member, False)
        self.assertIn((container, ldp.ns.contains, member), g)
        self.assertNotIn((member, ldp.ns.interactionModel, ldp.ns.BasicContainer), g)
