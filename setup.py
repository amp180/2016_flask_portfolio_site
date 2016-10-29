from setuptools import setup

setup(
    name='flask portfolio site',
    version='1.0',
    long_description=__doc__,
    packages=['flask_portfolio_site'],
    include_package_data=True,
    zip_safe=False,
    install_requires = [
        'Flask==0.11.1',
        'Flask-Admin',
        'Flask-Login<0.3.2',
        'Flask-Security',
        'Flask-SQLAlchemy',
        'lxml',
        'passlib',
        'Pillow',
        'requests',
        'requests-cache',
        'SQLAlchemy',
        'pytz'
    ]
)
