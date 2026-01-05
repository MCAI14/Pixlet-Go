import os
import sys
import json
import mimetypes

try:
    import requests
except Exception:
    requests = None

"""
create_github_release.py

Usage:
  - Set environment variable `GITHUB_TOKEN` (do NOT paste token in chat).
  - Run: python create_github_release.py --repo OWNER/REPO --tag v0.1.0 --title "Pixlet Browser v0.1.0"

The script will create a release and upload `pixlet-installer.zip` from the repository root.
"""


def error(msg):
    print('ERROR:', msg, file=sys.stderr)
    sys.exit(1)


def get_token():
    token = os.environ.get('GITHUB_TOKEN')
    if not token:
        error('Environment variable GITHUB_TOKEN not set.')
    return token


def create_release(repo, tag, title, body='', draft=False, prerelease=False):
    token = get_token()
    url = f'https://api.github.com/repos/{repo}/releases'
    headers = {'Authorization': f'token {token}', 'Accept': 'application/vnd.github.v3+json'}
    payload = {
        'tag_name': tag,
        'name': title,
        'body': body,
        'draft': draft,
        'prerelease': prerelease
    }
    if requests is None:
        error('The "requests" package is required. Install with: python -m pip install requests')
    r = requests.post(url, headers=headers, data=json.dumps(payload))
    if r.status_code not in (200,201):
        error(f'Create release failed: {r.status_code} {r.text}')
    return r.json()


def upload_asset(upload_url_template, filepath, label=None):
    token = get_token()
    filename = os.path.basename(filepath)
    upload_url = upload_url_template.split('{')[0] + f'?name={filename}'
    if label:
        upload_url += f'&label={label}'
    mime_type, _ = mimetypes.guess_type(filename)
    if not mime_type:
        mime_type = 'application/octet-stream'
    headers = {'Authorization': f'token {token}', 'Content-Type': mime_type}
    with open(filepath, 'rb') as f:
        data = f.read()
    if requests is None:
        error('The "requests" package is required. Install with: python -m pip install requests')
    r = requests.post(upload_url, headers=headers, data=data)
    if r.status_code not in (200,201):
        error(f'Upload asset failed: {r.status_code} {r.text}')
    return r.json()


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Create GitHub release and upload pixlet-installer.zip')
    parser.add_argument('--repo', required=True, help='owner/repo')
    parser.add_argument('--tag', required=True, help='tag name (e.g. v0.1.0)')
    parser.add_argument('--title', required=True, help='release title')
    parser.add_argument('--body', default='', help='release notes/body')
    parser.add_argument('--file', default='pixlet-installer.zip', help='asset file to upload')
    args = parser.parse_args()

    filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), args.file)
    if not os.path.exists(filepath):
        error(f'Asset not found: {filepath}')

    print('Creating release...')
    rel = create_release(args.repo, args.tag, args.title, body=args.body)
    upload_url = rel.get('upload_url')
    if not upload_url:
        error('No upload_url returned by GitHub API')

    print('Uploading asset...')
    asset = upload_asset(upload_url, filepath)
    print('Upload successful. Asset URL:', asset.get('browser_download_url'))


if __name__ == '__main__':
    main()
