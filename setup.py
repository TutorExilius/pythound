from setuptools import setup

install_requires = [
    'psutil==5.9.0',
]

setup(
    name='pythound',
    version='0.1.0',
    description='An async sound library for python.',
    license="MIT",
    author='Tutor Exilius',
    packages=['pythound'],
    author_email='tutorexilius@gmail.com',
    install_requires=install_requires,
)
