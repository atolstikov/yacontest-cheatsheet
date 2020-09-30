from flake8.api import legacy as flake8
import sys


if __name__ == '__main__':
    ignored_errors = ['W', 'E126']
    excluded_files = ['check.py']
    line_length = 121

    style_guide = flake8.get_style_guide(ignore=ignored_errors,
                                         excluded=excluded_files,
                                         max_line_length=line_length)
    report = style_guide.check_files('solution.py')
    if report.get_statistics('E'):
        print('Код не соответствует стандарту PEP8\nили в нем есть синтаксические ошибки')
        sys.exit(1)
