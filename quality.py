# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from itertools import chain
from trytond.model import ModelView, ModelSQL, fields
from trytond.pyson import Eval
from trytond.pool import Pool, PoolMeta
from trytond.modules.quality_control.quality import _STATES

__all__ = ['Environment', 'Template', 'QualitativeTemplateLine',
    'QuantitativeTemplateLine', 'TemplateLine', 'QualityTest', 'StressTest',
    'QualitativeLine', 'QuantitativeLine', 'TestLine']


class Environment(ModelSQL, ModelView):
    'Quality Stress Environament'
    __name__ = 'quality.stress_environment'

    template = fields.Many2One('quality.template', 'Quality Template',
        required=True, select=True, ondelete='CASCADE')
    name = fields.Char('Name', required=True)


class Template(metaclass=PoolMeta):
    __name__ = 'quality.template'

    environments = fields.One2Many('quality.stress_environment', 'template',
        'Stress Environments')

    @classmethod
    def copy(cls, templates, default=None):
        pool = Pool()
        TemplateLine = pool.get('quality.template.line')
        if default is None:
            default = {}
        lines = list(chain(*(t.lines for t in templates)))
        new_templates = super(Template, cls).copy(templates, default)
        new_lines = list(chain(*(t.lines for t in new_templates)))
        new_environments = dict(((l.template, l.name), l)
            for t in new_templates for l in t.environments)
        to_write = []
        for old_line, new_line in zip(lines, new_lines):
            if old_line.environment:
                to_write.extend(([new_line], {
                        'environment': new_environments.get((new_line.template,
                                    old_line.environment.name)),
                        }))
        if to_write:
            TemplateLine.write(*to_write)
        return new_templates


class QualitativeTemplateLine(metaclass=PoolMeta):
    __name__ = 'quality.qualitative.template.line'

    environment = fields.Many2One('quality.stress_environment',
        'Stress Environment',
        domain=[
            ('template', '=', Eval('template')),
            ],
        depends=['template'])

    @classmethod
    def copy(cls, lines, default=None):
        if default is None:
            default = {}
        default['environment'] = None
        return super(QualitativeTemplateLine, cls).copy(lines, default)


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


class QualityTest(metaclass=PoolMeta):
    __name__ = 'quality.test'

    stress_tests = fields.One2Many('quality.stress_test', 'test',
        'Stress Tests', states=_STATES, depends=['state'])

    def apply_template_values(self):
        pool = Pool()
        StressTest = pool.get('quality.stress_test')
        super(QualityTest, self).apply_template_values()
        StressTest.delete(StressTest.search([('test', '=', self.id)]))
        stress_tests = []
        templates = [t for t in self.templates]
        templates_qualitative_lines = []
        templates_quantitative_lines = []
        for template in templates:
            for environment in template.environments:
                stress_tests.append({
                        'environment': environment.id,
                        'test': self.id,
                        })
            templates_qualitative_lines.extend(
                [ql for ql in template.qualitative_lines])
            templates_quantitative_lines.extend(
                [ql for ql in template.quantitative_lines])

        stress_tests = StressTest.create(stress_tests)
        mapping = dict((s.environment, s) for s in stress_tests)
        for ql, tl in zip(self.qualitative_lines, templates_qualitative_lines):
            if tl.environment:
                ql.stress_test = mapping.get(tl.environment)
        for qn, tl in zip(self.quantitative_lines,
                templates_quantitative_lines):
            if tl.environment:
                qn.stress_test = mapping.get(tl.environment)

    @classmethod
    def copy(cls, tests, default=None):
        pool = Pool()
        TestLine = pool.get('quality.test.line')
        if default is None:
            default = {}
        lines = list(chain(*(t.lines for t in tests)))
        new_tests = super(QualityTest, cls).copy(tests, default)
        new_lines = list(chain(*(t.lines for t in new_tests)))
        new_stress_tests = dict(((l.test, l.environment.name), l)
            for t in new_tests for l in t.stress_tests)
        to_write = []
        for old_line, new_line in zip(lines, new_lines):
            if old_line.stress_test:
                to_write.extend(([new_line], {
                        'stress_test': new_stress_tests.get((new_line.test,
                                    old_line.stress_test.environment.name)),
                        }))
        if to_write:
            TestLine.write(*to_write)
        return new_tests


class QualitativeLine(metaclass=PoolMeta):
    __name__ = 'quality.qualitative.test.line'

    stress_test = fields.Many2One('quality.stress_test',
        'Stress Environment',
        domain=[
            ('test', '=', Eval('test')),
            ],
        depends=['test'])

    @classmethod
    def copy(cls, lines, default=None):
        if default is None:
            default = {}
        default['stress_test'] = None
        return super(QualitativeLine, cls).copy(lines, default)


class QuantitativeLine(QualitativeLine):
    __name__ = 'quality.quantitative.test.line'


class TestLine(QualitativeLine):
    __name__ = 'quality.test.line'
