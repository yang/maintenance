from setuptools import setup, find_packages

setup(
  name = 'maintenance',
  version = '0.1',
  packages = find_packages(),
  install_requires = [
    'psutil==1.0.1',
    'pync==1.1',
    'bitrot==0.5.1',
  ],
  description = 'General maintenance tools',
  entry_points = {
    'console_scripts': [
      'maintenance = maintenance:main',
    ]
  },
)
