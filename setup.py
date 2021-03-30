try:
    from setuptools import setup
    from setuptools import find_packages
except ImportError:
    from distutils.core import setup

setup(
    name='syslink_ats',
    version='1.0.0',
    packages=find_packages(),
    package_data={'': ['*.bin', '*.ctl', '*.dll', '*.exe', '*.ini', '*.ipynb', '*.json',
                       '*.lvclass', '*.lvlib', '*.lvproj', '*.pem', '*.seq', '*.tdms',
                       '*.txt', '*.vi', '*.vim', '*.vit', '*.xml']},
    url='',
    license='',
    author='sedwards',
    author_email='shawn.edwards@ni.com',
    description=''
)
