import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo-addons-sygel-technology-sy-crm",
    description="Meta package for sygel-technology-sy-crm Odoo addons",
    version=version,
    install_requires=[
        'odoo-addon-crm_lead_hide_add_property>=16.0dev,<16.1dev',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 16.0',
    ]
)
