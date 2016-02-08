# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.model import ModelView, ModelSQL, fields
from trytond.pyson import Eval
from trytond.pool import Pool, PoolMeta
from trytond.modules.quality_control.quality import _STATES

__all__ = ['Environment', 'Template', 'QualitativeTemplateLine',
    'QuantitativeTemplateLine', 'TemplateLine', 'QualityTest', 'StressTest',
    'QualitativeLine', 'QuantitativeLine']
__metaclass__ = PoolMeta


class Environment(ModelSQL, ModelView):
    'Quality Stress Environament'
    __name__ = 'quality.stress_environment'

    template = fields.Many2One('quality.template', 'Quality Template',
        required=True, select=True, ondelete='CASCADE')
    name = fields.Char('Name', required=True)


class Template:
    __name__ = 'quality.template'

    environments = fields.One2Many('quality.stress_environment', 'template',
        'Stress Environments')


class QualitativeTemplateLine:
    __name__ = 'quality.qualitative.template.line'

    environment = fields.Many2One('quality.stress_environment',
        'Stress Environment',
        domain=[
            ('template', '=', Eval('template')),
            ],
        depends=['template'])


class QuantitativeTemplateLine(QualitativeTemplateLine):
    __name__ = 'quality.quantitative.template.line'


class TemplateLine(QualitativeTemplateLine):
    __name__ = 'quality.template.line'


class StressTest(ModelSQL, ModelView):
    'Quality Stress Test'
    __name__ = 'quality.stress_test'
    test = fields.Many2One('quality.test', 'Quality Test', required=True,
        ondelete='CASCADE')
    environment = fields.Many2One('quality.stress_environment',
        'Stress Environment', required=True)
    start = fields.DateTime('Start')
    end = fields.DateTime('End')

    def get_rec_name(self, name):
        return self.environment.rec_name

    @classmethod
    def search_rec_name(cls, name, clause):
        return [tuple('environment.rec_name',) + tuple(clause[1:])]


class QualityTest:
    __name__ = 'quality.test'
    stress_tests = fields.One2Many('quality.stress_test', 'test',
        'Stress Tests', states=_STATES, depends=['state'])

    def set_template_vals(self):
        pool = Pool()
        StressTest = pool.get('quality.stress_test')
        super(QualityTest, self).set_template_vals()
        StressTest.delete(StressTest.search([('test', '=', self.id)]))
        stress_tests = []
        for environment in self.template.environments:
            stress_tests.append({
                    'environment': environment.id,
                    'test': self.id,
                    })
        stress_tests = StressTest.create(stress_tests)
        mapping = dict((s.environment, s) for s in stress_tests)
        for ql, tl in zip(self.qualitative_lines,
                self.template.qualitative_lines):
            if tl.environment:
                ql.stress_test = mapping.get(tl.environment)
        for qn, tl in zip(self.quantitative_lines,
                self.template.quantitative_lines):
            if tl.environment:
                qn.stress_test = mapping.get(tl.environment)


class QualitativeLine:
    __name__ = 'quality.qualitative.test.line'

    stress_test = fields.Many2One('quality.stress_test',
        'Stress Environment',
        domain=[
            ('test', '=', Eval('test')),
            ],
        depends=['test'])


class QuantitativeLine(QualitativeLine):
    __name__ = 'quality.quantitative.test.line'
