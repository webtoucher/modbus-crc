from setuptools import setup, find_packages

setup(name='modbus-crc',
      version='1.3',
      url='https://github.com/webtoucher/modbus-crc',
      license='BSD-3-Clause',
      author='Alexey Kuznetsov',
      author_email='mirakuru@webtoucher.ru',
      description='CRC-16 calculation for Modbus protocol',
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Intended Audience :: Developers',
          'Topic :: Software Development :: Libraries',
          'License :: OSI Approved :: BSD License',
          'Programming Language :: Python :: 3',
          'Operating System :: Microsoft :: Windows',
          'Operating System :: POSIX',
          'Operating System :: Unix',
          'Operating System :: MacOS',
      ],
      packages=['modbus_crc'],
      long_description=open('README.md').read(),
      long_description_content_type='text/markdown',
      zip_safe=False)
