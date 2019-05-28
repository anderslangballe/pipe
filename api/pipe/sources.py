import os
import re
from logging import getLogger


def load_sources():
    sources = dict()
    source_env = os.getenv('SOURCES')
    if not source_env:
        return sources
    source_names = [item.strip() for item in source_env.split(',')]

    for source in source_names:
        endpoint = os.getenv('ENDPOINT_{}'.format(source.upper()))

        if endpoint:
            sources[source] = endpoint

    return sources


def replace_contents(contents, source_directory, sources, fragment_separator):
    # Keep track of whether we have replaced fragment with actual content
    # Used to determine whether a separator is needed
    has_replaced = False

    # For each fragment, replace the contents with the contents of the fragment
    fragment_matches = re.findall(r'%FILE_([A-Z]+)\.([a-z]+)%', contents)
    for source, extension in fragment_matches:
        replace_content = ''
        if source in sources:
            fragment_location = os.path.join(source_directory, '{}.{}'.format(source, extension))

            if os.path.isfile(fragment_location):
                with open(fragment_location, 'r') as f:
                    replace_content = f.read()

                # Check if we need to insert an operator
                if has_replaced and fragment_separator:
                    replace_content = '{}{}'.format(fragment_separator, replace_content)
                else:
                    has_replaced = True
            else:
                getLogger(__name__).error('Unable to find fragment {}'.format(fragment_location))

        # Replace the fragment
        contents = contents.replace('%FILE_{}.{}%'.format(source, extension), replace_content)

    # Having replaced all fragments, we can now replace endpoints
    endpoint_matches = re.findall(r'%ENDPOINT_([A-Z]+)%', contents)
    for endpoint in endpoint_matches:
        contents = contents.replace('%ENDPOINT_{}%'.format(endpoint), sources.get(endpoint, ''))

    return contents


def fill_template(sources, files, source_directory, target_directory, fragment_separator=None):
    # For convention, capitalise source names
    sources = {source.upper(): endpoint for source, endpoint in sources.items()}

    # Remove and re-create corresponding files
    for file in files:
        source_path = os.path.join(source_directory, file)
        target_path = os.path.join(target_directory, file)

        # Get template contents
        with open(source_path, 'r') as f:
            template_contents = replace_contents(f.read(), source_directory, sources, fragment_separator)

        # Ensure that target directory exists
        os.makedirs(target_directory, exist_ok=True)

        # Overwrite target file
        with open(target_path, 'w') as f:
            f.write(template_contents)
