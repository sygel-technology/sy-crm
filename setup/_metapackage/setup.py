import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo-addons-sygel-technology-sy-crm",
    description="Meta package for sygel-technology-sy-crm Odoo addons",
    version=version,
    install_requires=[
        'odoo-addon-crm_autoassign>=15.0dev,<15.1dev',
        'odoo-addon-crm_group_sale_salesman_extension>=15.0dev,<15.1dev',
        'odoo-addon-crm_sale_automatic_quotation>=15.0dev,<15.1dev',
        'odoo-addon-crm_sale_automatic_quotation_asynchronous_wizard>=15.0dev,<15.1dev',
        'odoo-addon-transfer_client_portfolio>=15.0dev,<15.1dev',
        'odoo-addon-transfer_client_portfolio_commissions>=15.0dev,<15.1dev',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 15.0',
    ]
)
