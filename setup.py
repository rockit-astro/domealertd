#
# This file is part of domealertd.
#
# domealertd is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# domealertd is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with domealertd.  If not, see <http://www.gnu.org/licenses/>.

from distutils.core import setup

setup(name='warwick.observatory.domealert',
      version='0',
      packages=['warwick.observatory.domealert'],
      author='Paul Chote',
      description='Common backend code for the DomeAlert daemons',
      license='GNU GPLv3',
      author_email='p.chote@warwick.ac.uk',
      url='https://github.com/warwick-one-metre/domealertd',
      scripts=['domealertd'],
      data_files=[
            ('/etc/domealertd', ['onemetre.json', 'test.json'])
      ],
      install_requires=[
          'Pyro4>=4.75,<5',
          'jsonschema>=2.6.0,<3',
          'RPi.GPIO>=0.7'
      ]
)
