from setuptools import setup, find_packages

setup(
    name='perseids_collections_api',
    version="0.0.1",
    description='Perseids implementation of RDA Collections API',
    url='http://github.com/rdacollectionswg/tufts-implementation',
    author='Frederik Baumgardt',
    author_email='frederik.baumgardt@tufts.edu',
    license='MIT',
    packages=find_packages(exclude=["*.test", "*.test.*", "test.*", "test"]),
    install_requires=[
        "Flask>=0.12",
        "Werkzeug>=0.11.3",
        "Flask-Caching>=1.2.0",
        "flask-cors==2.0.0"
    ],
    include_package_data=True,
    test_suite="test",
    zip_safe=False
)
