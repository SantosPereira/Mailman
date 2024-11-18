from setuptools import setup, find_packages

setup(
    name='mailman',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[  
        'click'
    ],
    include_package_data=True,
    description=' Multi package-manager manager',
    author='SantosPereira',
    author_email='pedrohenriquelemam@gmail.com',
    url='https://github.com/SantosPereira/Mailman',
)
