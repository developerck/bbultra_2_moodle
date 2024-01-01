from setuptools import setup

setup(
    name='bbultra2moodle',
    version='1.0.0',
    description='Blackboard ultra course to Moodle',
    packages=['bbultra2moodle','bbultra2moodle.conv'],
    package_data={'bbultra2moodle': ['moodle.xml.template']},
    include_package_data=True,
    zip_safe=False,
    author='Chandra K',
    author_email='',
    url='',
    license='GPL v3',
    platforms=['any'],
    keywords=['blackboard','bbultra', 'moodle', 'migration', 'lms'],
    install_requires=['lxml', 'jinja2'],
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.7',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: GNU General Public License (GPL)'
    ],
    long_description=' Blackboard ultra course to Moodle Course',
    entry_points={
        "console_scripts": [
            "bbultra2moodle = bbultra2moodle.main:main",
        ]
    },
)
