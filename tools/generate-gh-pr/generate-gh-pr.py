"""Create a GitHub PR for each line of new carbon footprint data."""
import argparse
import csv
import textwrap
import typing
from typing import Iterator, List, Optional

import github

from tools.parsers.lib import data


def _iterate_on_data(csv_filename: str) -> Iterator[data.DeviceCarbonFootprint]:
    with open(csv_filename, 'rt', encoding='utf-8') as new_data_file:
        reader = csv.DictReader(new_data_file)
        for new_row in reader:
            yield data.DeviceCarbonFootprint.from_text(new_row)


def main(string_args: Optional[List[str]] = None) -> None:
    argparser = argparse.ArgumentParser(
        description='Create a new GitHub PR for new carbon footprint data',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        exit_on_error=False)
    argparser.add_argument('--access_token', help='GitHub access token', required=True)
    argparser.add_argument(
        '--github_repo', help='GitHub repository org and name', default='Boavizta/environmental-footprint-data')
    argparser.add_argument(
        'new_data_csv', help='Path to a CSV with new data to submit')
    args = argparser.parse_args(string_args)

    github_client = github.Github(args.access_token)
    repo = github_client.get_repo(args.github_repo)

    for device in _iterate_on_data(args.new_data_csv):
        change_name = f'Add new {device.get("Name")} {device.get("Category")}'
        newbranch = change_name.replace(' ', '-')
        try:
            repo.get_git_ref(f'heads/{newbranch}')
            continue
        except github.UnknownObjectException:
            pass
        repo.create_git_ref(f'refs/heads/{newbranch}', repo.get_branch('main').commit.sha)
        contents = repo.get_contents('boavizta-data-us.csv', ref='main')
        newcontent = contents.decoded_content.decode() + "\n" + device.as_csv_row(csv_format='us')

        repo.update_file(
            contents.path, f'{change_name} - us format',
            contents.decoded_content.decode().splitlines()[0] + '\n'.join(sorted((contents.decoded_content.decode() + "\n" + device.as_csv_row(csv_format='us')).splitlines()[1:])),
            contents.sha, branch=newbranch)
        contents = repo.get_contents('boavizta-data-fr.csv', ref='main')
        repo.update_file(
            contents.path, f'{change_name} - fr format',
            contents.decoded_content.decode().splitlines()[0] + '\n'.join(sorted((contents.decoded_content.decode() + "\n" + device.as_csv_row(csv_format='fr')).splitlines()[1:])),
            contents.sha, branch=newbranch)
        body = textwrap.dedent(f'''\
            SUMMARY
            {change_name}

            PDF_SOURCE_LINK
            {device.get('Sources')}
        ''')
        repo.create_pull(title=change_name, body=body, head=newbranch, base='main')


if __name__ == '__main__':
    main()
