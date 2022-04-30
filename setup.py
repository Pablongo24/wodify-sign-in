from setuptools import setup, find_packages

setup(
    name='wodify-auto-reserve',
    version='0.0.1',
    packages=find_packages(where='auto_reserve'),
    install_requires=[
        'python-dotenv==0.20.0',
        'selenium>=4.1'
    ],
    test_require=['pytest'],
    url='https://github.com/Pablongo24/wodify-sign-in',
    license='Apache License 2.0',
    author='Pablo Vega-Behar',
    author_email='pablo.vega.behar@gmail.com',
    description='Description Coming Soon'
)
