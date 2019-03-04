from setuptools import setup

setup(
    name='deep_rl',
    version='0.1.0',
    packages=['deep_rl',],
    author='Jonáš Kulhánek',
    author_email='jonas.kulhanek@live.com',
    license='MIT License',
    long_description=open('README.md').read(),
    install_requires = [
        'baselines @ git+https://github.com/openai/baselines.git',
        'gym'
    ]
)