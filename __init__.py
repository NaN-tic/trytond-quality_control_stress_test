# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import Pool
from .quality import *


def register():
    Pool.register(
        Environment,
        Template,
        QualitativeTemplateLine,
        QuantitativeTemplateLine,
        TemplateLine,
        StressTest,
        QualityTest,
        QualitativeLine,
        QuantitativeLine,
        module='quality_control_stress_test', type_='model')
