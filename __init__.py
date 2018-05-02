# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import Pool
from . import quality


def register():
    Pool.register(
        quality.Environment,
        quality.Template,
        quality.QualitativeTemplateLine,
        quality.QuantitativeTemplateLine,
        quality.TemplateLine,
        quality.StressTest,
        quality.QualityTest,
        quality.QualitativeLine,
        quality.QuantitativeLine,
        quality.TestLine,
        module='quality_control_stress_test', type_='model')
