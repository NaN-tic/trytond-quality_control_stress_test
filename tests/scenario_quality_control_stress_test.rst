====================================
Quality Control Stress Test Scenario
====================================

Imports::
    >>> import datetime
    >>> from dateutil.relativedelta import relativedelta
    >>> from decimal import Decimal
    >>> from operator import attrgetter
    >>> from proteus import config, Model, Wizard
    >>> today = datetime.date.today()

Create database::

    >>> config = config.set_trytond()
    >>> config.pool.test = True

Install quality_test module::

    >>> Module = Model.get('ir.module.module')
    >>> module, = Module.find(
    ...     [('name', '=', 'quality_control_stress_test')])
    >>> module.click('install')
    >>> Wizard('ir.module.module.install_upgrade').execute('upgrade')

Create company::

    >>> Currency = Model.get('currency.currency')
    >>> CurrencyRate = Model.get('currency.currency.rate')
    >>> currencies = Currency.find([('code', '=', 'USD')])
    >>> if not currencies:
    ...     currency = Currency(name='US Dollar', symbol=u'$', code='USD',
    ...         rounding=Decimal('0.01'), mon_grouping='[]',
    ...         mon_decimal_point='.')
    ...     currency.save()
    ...     CurrencyRate(date=today + relativedelta(month=1, day=1),
    ...         rate=Decimal('1.0'), currency=currency).save()
    ... else:
    ...     currency, = currencies
    >>> Company = Model.get('company.company')
    >>> Party = Model.get('party.party')
    >>> company_config = Wizard('company.company.config')
    >>> company_config.execute('company')
    >>> company = company_config.form
    >>> party = Party(name='Dunder Mifflin')
    >>> party.save()
    >>> company.party = party
    >>> company.currency = currency
    >>> company_config.execute('add')
    >>> company, = Company.find([])

Reload the context::

    >>> User = Model.get('res.user')
    >>> config._context = User.get_preferences(True, config.context)

Create product::

    >>> ProductUom = Model.get('product.uom')
    >>> unit, = ProductUom.find([('name', '=', 'Unit')])
    >>> ProductTemplate = Model.get('product.template')
    >>> Product = Model.get('product.product')
    >>> product = Product()
    >>> template = ProductTemplate()
    >>> template.name = 'product'
    >>> template.default_uom = unit
    >>> template.type = 'service'
    >>> template.list_price = Decimal('40')
    >>> template.cost_price = Decimal('25')
    >>> template.save()
    >>> product.template = template
    >>> product.save()

Create Quality Configuration::

    >>> Sequence = Model.get('ir.sequence')
    >>> sequence = Sequence.find([('code','=','quality.test')])[0]
    >>> Configuration = Model.get('quality.configuration')
    >>> configuration = Configuration()
    >>> configuration.name = 'Configuration'
    >>> Product = Model.get('product.product')
    >>> ConfigLine = Model.get('quality.configuration.line')
    >>> config_line = ConfigLine()
    >>> configuration.allowed_documents.append(config_line)
    >>> config_line.quality_sequence = sequence
    >>> models = Model.get('ir.model')
    >>> allowed_doc, = models.find([('model','=','product.product')])
    >>> config_line.document = allowed_doc
    >>> configuration.save()

Create Qualitative Proof::

    >>> Proof = Model.get('quality.proof')
    >>> QualityValue = Model.get('quality.qualitative.value')
    >>> Method = Model.get('quality.proof.method')
    >>> val1 = QualityValue(name='Val1')
    >>> val2 = QualityValue(name='Val2')
    >>> qlproof = Proof(name='Qualitative Proof', type='qualitative')
    >>> method1 = Method(name='Method 1')
    >>> qlproof.methods.append(method1)
    >>> method1.possible_values.append(val1)
    >>> method1.possible_values.append(val2)
    >>> qlproof.save()


Create Quantitative Proof::

    >>> Proof = Model.get('quality.proof')
    >>> Method = Model.get('quality.proof.method')
    >>> qtproof = Proof(name='Quantitative Proof', type='quantitative')
    >>> method2 = Method(name='Method 2')
    >>> qtproof.methods.append(method2)
    >>> qtproof.save()

Create Test Environaments::

    >>> TestEnvironment = Model.get('quality.stress_environment')
    >>> high_temperature = TestEnvironment(name='High Temperature')
    >>> high_temperature.save()
    >>> low_temperature = TestEnvironment(name='Low Temperature')
    >>> low_temperature.save()

Look For Values::

    >>> method1, = Method.find([('name', '=', 'Method 1')])
    >>> method2, = Method.find([('name', '=', 'Method 2')])
    >>> val1, = QualityValue.find([('name','=','Val1')])
    >>> val2, = QualityValue.find([('name','=','Val2')])

Create Template::

    >>> Template = Model.get('quality.template')
    >>> template=Template()
    >>> template.name = 'Template 1'
    >>> template.document = product
    >>> template.internal_description='Internal description'
    >>> template.external_description='External description'
    >>> template.environments.append(TestEnvironment(high_temperature.id))
    >>> template.environments.append(TestEnvironment(low_temperature.id))
    >>> ql_line = template.qualitative_lines.new()
    >>> ql_line.name = 'Line1'
    >>> ql_line.proof = qlproof
    >>> ql_line.method = method1
    >>> ql_line.environment = low_temperature
    >>> ql_line.valid_value = val1
    >>> ql_line.internal_description = 'quality line intenal description'
    >>> ql_line.external_description = 'quality line external description'
    >>> qt_line = template.quantitative_lines.new()
    >>> qt_line.name = 'Quantitative Line'
    >>> qt_line.proof = qtproof
    >>> qt_line.method = method2
    >>> ql_line.environment = low_temperature
    >>> qt_line.unit = unit
    >>> qt_line.unit_range = unit
    >>> qt_line.internal_description = 'quality line intenal description'
    >>> qt_line.external_description = 'quality line external description'
    >>> qt_line.min_value = Decimal('1.00')
    >>> qt_line.max_value = Decimal('2.00')
    >>> template.save()
    >>> template.reload()

Create And assing template to Test::

    >>> Test = Model.get('quality.test')
    >>> test=Test()
    >>> test.name = 'TEST/'
    >>> test.document = product
    >>> test.template = template
    >>> test.click('set_template')

Test values are assigned corretly::

    >>> len(test.environments)
    2
    >>> high_stress_test, low_stress_test = test.stress_tests
    >>> high_stress_test.environment == high_temperature
    True
    >>> high_stress_test.start
    >>> high_stress_test.end
    >>> low_stress_test.environment == low_temperature
    True
    >>> low_stress_test.start
    >>> low_stress_test.end
