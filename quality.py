# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.model import ModelView, ModelSQL, fields
from trytond.pyson import Eval, If, Bool
from trytond.pool import Pool, PoolMeta
from trytond.modules.quality_control.quality import _STATES

__all__ = ['Environment', 'EnvironmentTemplate', 'Template',
    'QualitativeTemplateLine', 'QuantitativeTemplateLine', 'EnvironmentTest',
    'StressTest', 'QualityTest', 'QualitativeLine', 'QuantitativeLine']
__metaclass__ = PoolMeta


class Environment(ModelSQL, ModelView):
    'Quality Stress Environament'
    __name__ = 'quality.stress_environment'

    name = fields.Char('Name', required=True)


class EnvironmentTemplate(ModelSQL):
    'Quality Stress Environment - Quality Template'
    __name__ = 'quality.stress_environment-quality.template'
    environment = fields.Many2One('quality.stress_environment',
        'Stress Environment', required=True, select=True, ondelete='CASCADE')
    template = fields.Many2One('quality.template', 'Quality Template',
        required=True, select=True, ondelete='CASCADE')


class Template:
    __name__ = 'quality.template'

    environments = fields.Many2Many(
        'quality.stress_environment-quality.template', 'template',
        'environment', 'Stress Environments')


class QualitativeTemplateLine:
    __name__ = 'quality.qualitative.template.line'

    environment = fields.Many2One('quality.stress_environment',
        'Stress Environment',
        domain=[
            If(Bool(Eval('template_environments')),
                ('id', 'in', Eval('template_environments', [])),
                ()),
            ],
        depends=['template_environments'])
    template_environments = fields.Function(fields.Many2Many(
            'quality.stress_environment', None, None, 'Stress Environments'),
        'on_change_with_template_environments')

    @fields.depends('template')
    def on_change_with_template_environments(self, name=None):
        if self.template:
            return [x.id for x in self.template.environments]
        return []


class QuantitativeTemplateLine(QualitativeTemplateLine):
    __name__ = 'quality.quantitative.template.line'


class EnvironmentTest(ModelSQL):
    'Quality Stress Environment - Quality Test'
    __name__ = 'quality.stress_environment-quality.test'
    environment = fields.Many2One('quality.stress_environment',
        'Stress Environment', required=True, select=True, ondelete='CASCADE')
    test = fields.Many2One('quality.test', 'Quality Test',
        required=True, select=True, ondelete='CASCADE')


class StressTest(ModelSQL, ModelView):
    'Quality Stress Test'
    __name__ = 'quality.stress_test'
    test = fields.Many2One('quality.test', 'Quality Test', required=True,
        ondelete='CASCADE')
    environment = fields.Many2One('quality.stress_environment',
        'Stress Environment', required=True)
    start = fields.DateTime('Start')
    end = fields.DateTime('End')


class QualityTest:
    __name__ = 'quality.test'
    environments = fields.Many2Many('quality.stress_environment-quality.test',
        'test', 'environment', 'Stress Environments', states=_STATES,
        depends=['state'])
    stress_tests = fields.One2Many('quality.stress_test', 'test',
        'Stress Tests', states=_STATES, depends=['state'])

    def set_template_vals(self):
        pool = Pool()
        StressTest = pool.get('quality.stress_test')
        super(QualityTest, self).set_template_vals()
        environments, stress_tests = [], []
        for environment in self.template.environments:
            environments.append(environment)
            stress_tests.append(StressTest(environment=environment))
        self.environments = environments
        self.stress_tests = stress_tests


class QualitativeLine:
    __name__ = 'quality.qualitative.test.line'

    environment = fields.Many2One('quality.stress_environment',
        'Stress Environment',
        domain=[
            If(Bool(Eval('test_environments')),
                ('id', 'in', Eval('test_environments', [])),
                ()),
            ],
        depends=['test_environments'])
    test_environments = fields.Function(fields.Many2Many(
            'quality.stress_environment', None, None, 'Stress Environments'),
        'on_change_with_test_environments')

    @fields.depends('test')
    def on_change_with_test_environments(self, name=None):
        if self.test:
            return [x.id for x in self.test.environments]
        return []

    def set_template_line_vals(self, template_line):
        super(QualitativeLine, self).set_template_line_vals(template_line)
        self.environment = template_line.environment


class QuantitativeLine(QualitativeLine):
    __name__ = 'quality.quantitative.test.line'
