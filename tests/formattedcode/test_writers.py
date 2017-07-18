#
# Copyright (c) 2017 nexB Inc. and others. All rights reserved.
# http://nexb.com and https://github.com/nexB/scancode-toolkit/
# The ScanCode software is licensed under the Apache License version 2.0.
# Data generated with ScanCode require an acknowledgment.
# ScanCode is a trademark of nexB Inc.
#
# You may not use this software except in compliance with the License.
# You may obtain a copy of the License at: http://apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
# CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.
#
# When you publish or redistribute any data created with ScanCode or any ScanCode
# derivative work, you must accompany this data with the following acknowledgment:
#
#  Generated with ScanCode and provided on an "AS IS" BASIS, WITHOUT WARRANTIES
#  OR CONDITIONS OF ANY KIND, either express or implied. No content created from
#  ScanCode should be considered or used as legal advice. Consult an Attorney
#  for any legal advice.
#  ScanCode is a free software code scanning tool from nexB Inc. and others.
#  Visit https://github.com/nexB/scancode-toolkit/ for support and download.

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals

import codecs
from collections import OrderedDict
import json
import os
import re

import xmltodict

from commoncode import fileutils
from commoncode.testcase import FileDrivenTesting
from scancode.cli_test_utils import check_json_scan
from scancode.cli_test_utils import run_scan_click
from formattedcode.format_csv import flatten_scan


test_env = FileDrivenTesting()
test_env.test_data_dir = os.path.join(os.path.dirname(__file__), 'data')


"""
These CLI tests are dependent on py.test monkeypatch to  ensure we are testing the
actual command outputs as if using a real command line call.
"""

def test_json_pretty_print_option():
    test_dir = test_env.get_test_loc('json_format')
    result_file = test_env.get_temp_file('json')

    result = run_scan_click(['--copyright', '--format', 'json-pp', test_dir, result_file])
    assert result.exit_code == 0
    assert 'Scanning done' in result.output
    assert os.path.exists(result_file)
    assert len(open(result_file).read()) > 10
    assert len(open(result_file).readlines()) > 1


def test_json_output_option_is_minified():
    test_dir = test_env.get_test_loc('json_format')
    result_file = test_env.get_temp_file('json')

    result = run_scan_click(['--copyright', '--format', 'json', test_dir, result_file])
    assert result.exit_code == 0
    assert 'Scanning done' in result.output
    assert os.path.exists(result_file)
    assert len(open(result_file).read()) > 10
    assert len(open(result_file).readlines()) == 1


def test_paths_are_posix_paths_in_html_app_format_output():
    test_dir = test_env.get_test_loc('posix_path')
    result_file = test_env.get_temp_file(extension='html', file_name='test_html')

    result = run_scan_click(['--copyright', '--format', 'html-app', test_dir, result_file])
    assert result.exit_code == 0
    assert 'Scanning done' in result.output

    # the data we want to test is in the data.json file
    data_file = os.path.join(fileutils.parent_directory(result_file), 'test_html_files', 'data.json')
    assert 'copyright_acme_c-c.c' in open(data_file).read()


def test_paths_are_posix_in_html_format_output():
    test_dir = test_env.get_test_loc('posix_path')
    result_file = test_env.get_temp_file('html')

    result = run_scan_click(['--copyright', '--format', 'html', test_dir, result_file])
    assert result.exit_code == 0
    assert 'Scanning done' in result.output
    assert 'copyright_acme_c-c.c' in open(result_file).read()


def test_paths_are_posix_in_json_format_output():
    test_dir = test_env.get_test_loc('posix_path')
    result_file = test_env.get_temp_file('json')

    result = run_scan_click(['--copyright', '--format', 'json', test_dir, result_file])
    assert result.exit_code == 0
    assert 'Scanning done' in result.output
    assert 'copyright_acme_c-c.c' in open(result_file).read()


def test_html_format_with_custom_filename_fails_for_directory():
    test_dir = test_env.get_temp_dir('some_dir')
    result_file = test_env.get_temp_file('html')

    result = run_scan_click(['--format', test_dir, test_dir, result_file])
    assert result.exit_code != 0
    assert 'Invalid template file' in result.output


def test_html_format_with_custom_filename():
    test_dir = test_env.get_test_loc('posix_path')
    custom_template = test_env.get_test_loc('template/sample-template.html')
    result_file = test_env.get_temp_file('html')

    result = run_scan_click(['--format', custom_template, test_dir, result_file])
    assert result.exit_code == 0
    assert 'Custom Template' in open(result_file).read()


def test_scanned_path_is_present_in_html_app_output():
    test_dir = test_env.get_test_loc('html_app')
    result_file = test_env.get_temp_file('test.html')

    result = run_scan_click(['--copyright', '--format', 'html-app', test_dir, result_file])
    assert result.exit_code == 0
    assert 'Scanning done' in result.output

    result_content = open(result_file).read()
    assert '<title>ScanCode scan results for: %(test_dir)s</title>' % locals() in result_content
    assert '<div class="row" id = "scan-result-header">' % locals() in result_content
    assert '<strong>scan results for:</strong>' % locals() in result_content
    assert '<p>%(test_dir)s</p>' % locals() in result_content


def test_scan_output_does_not_truncate_copyright_json():
    test_dir = test_env.get_test_loc('basic/scan/')
    result_file = test_env.get_temp_file('test.json')

    result = run_scan_click(
        ['-clip', '--strip-root', '--format', 'json', test_dir, result_file])
    assert result.exit_code == 0
    assert 'Scanning done' in result.output

    expected = test_env.get_test_loc('basic/expected.json')
    check_json_scan(test_env.get_test_loc(expected), result_file, strip_dates=True)


def test_scan_output_does_not_truncate_copyright_json_stdout():
    test_dir = test_env.get_test_loc('basic/scan/')
    result_file = test_env.get_temp_file('test.json')

    result = run_scan_click(
        ['-clip', '--strip-root', '--format', 'json', test_dir, result_file])
    assert result.exit_code == 0
    assert 'Scanning done' in result.output

    expected = test_env.get_test_loc('basic/expected.json')
    check_json_scan(test_env.get_test_loc(expected), result_file, strip_dates=True)


def test_scan_html_output_does_not_truncate_copyright_html():
    test_dir = test_env.get_test_loc('basic/scan/')
    result_file = test_env.get_temp_file('test.html')

    result = run_scan_click(
        ['-clip', '--strip-root', '--format', 'html', '-n', '3',
         test_dir, result_file])
    assert result.exit_code == 0
    assert 'Scanning done' in result.output

    with open(result_file) as hi:
        result_content = hi.read()

    expected_template = r'''
        <tr>
          <td>%s</td>
          <td>1</td>
          <td>1</td>
          <td>copyright</td>
            <td>Copyright \(c\) 2000 ACME, Inc\.</td>
        </tr>
    '''

    expected_files = r'''
        copy1.c
        copy2.c
        subdir/copy1.c
        subdir/copy4.c
        subdir/copy2.c
        subdir/copy3.c
        copy3.c
    '''.split()

    # for this test we build regexes from a template so we can abstract
    # whitespaces
    for scanned_file in expected_files:
        exp = expected_template % (scanned_file,)
        exp = r'\s*'.join(exp.split())
        check = re.findall(exp, result_content, re.MULTILINE)
        assert check


def strip_variable_text(rdf_text):
    """
    Return rdf_text stripped from variable parts such as rdf nodeids
    """

    replace_nid = re.compile('rdf:nodeID="[^\"]*"').sub
    rdf_text = replace_nid('', rdf_text)

    replace_creation = re.compile('<ns1:creationInfo>.*</ns1:creationInfo>', re.DOTALL).sub
    rdf_text = replace_creation('', rdf_text)

    replace_pcc = re.compile('<ns1:packageVerificationCode>.*</ns1:packageVerificationCode>', re.DOTALL).sub
    rdf_text = replace_pcc('', rdf_text)
    return rdf_text


def load_and_clean_rdf(location):
    """
    Return plain Python nested data for the SPDX RDF file at location
    suitable for comparison. The file content is cleaned from variable
    parts such as dates, generated UUIDs and versions

    NOTE: we use plain dicts to avoid ordering issues in XML. the SPDX
    tool and lxml do not seem to return a consistent ordering that is
    needed for tests.
    """
    content = codecs.open(location, encoding='utf-8').read()
    content = strip_variable_text(content)
    data = xmltodict.parse(content, dict_constructor=dict)
    return sort_nested(data)


def sort_nested(data):
    """
    Return a new dict with any nested list sorted recursively.
    """
    if isinstance(data, dict):
        new_data = {}
        for k, v in data.items():
            if isinstance(v, list):
                v = sorted(v)
            if isinstance(v, dict):
                v = sort_nested(v)
            new_data[k] = v
        return new_data
    elif isinstance(data, list):
        new_data = []
        for v in sorted(data):
            if isinstance(v, list):
                v = sort_nested(v)
            if isinstance(v, dict):
                v = sort_nested(v)
            new_data.append(v)
        return new_data


def check_rdf_scan(expected_file, result_file, regen=False):
    """
    Check that expected and result_file are equal.
    Both are paths to SPDX RDF XML files, UTF-8 encoded.
    """
    import json
    result = load_and_clean_rdf(result_file)
    if regen:
        expected = result
        with codecs.open(expected_file, 'w', encoding='utf-8') as o:
            json.dump(expected, o, indent=2)
    else:
        with codecs.open(expected_file, 'r', encoding='utf-8') as i:
            expected = sort_nested(json.load(i))
    assert expected == result


def load_and_clean_tv(location):
    """
    Return a mapping for the SPDX TV file at location suitable for
    comparison. The file content is cleaned from variable parts such as
    dates, generated UUIDs and versions
    """
    content = codecs.open(location, encoding='utf-8').read()
    content = [l for l in content.splitlines(False)
        if l and l.strip() and not l.startswith(('Creator: ', 'Created: ',))]
    return '\n'.join(content)


def check_tv_scan(expected_file, result_file, regen=False):
    """
    Check that expected and result_file are equal.
    Both are paths to plain spdx tv text files, UTF-8 encoded.
    """
    result = load_and_clean_tv(result_file)
    if regen:
        with codecs.open(expected_file, 'w', encoding='utf-8') as o:
            o.write(result)

    expected = load_and_clean_tv(expected_file)
    assert expected == result


def test_spdx_rdf_basic():
    test_file = test_env.get_test_loc('spdx_basic/test.txt')
    result_file = test_env.get_temp_file('rdf')
    expected_file = test_env.get_test_loc('spdx_basic/expected.rdf')
    result = run_scan_click(['--format', 'spdx-rdf', test_file, result_file])
    assert result.exit_code == 0
    check_rdf_scan(expected_file, result_file)


def test_spdx_tv_basic():
    test_dir = test_env.get_test_loc('spdx_basic/test.txt')
    result_file = test_env.get_temp_file('tv')
    expected_file = test_env.get_test_loc('spdx_basic/expected.tv')
    result = run_scan_click(['--format', 'spdx-tv', test_dir, result_file])
    assert result.exit_code == 0
    check_tv_scan(expected_file, result_file)


def test_spdx_rdf_with_known_licenses():
    test_dir = test_env.get_test_loc('spdx_license_known/scan')
    result_file = test_env.get_temp_file('rdf')
    expected_file = test_env.get_test_loc('spdx_license_known/expected.rdf')
    result = run_scan_click(['--format', 'spdx-rdf', test_dir, result_file])
    assert result.exit_code == 0
    check_rdf_scan(expected_file, result_file)


def test_spdx_rdf_with_license_ref():
    test_dir = test_env.get_test_loc('spdx_license_ref/scan')
    result_file = test_env.get_temp_file('rdf')
    expected_file = test_env.get_test_loc('spdx_license_ref/expected.rdf')
    result = run_scan_click(['--format', 'spdx-rdf', test_dir, result_file])
    assert result.exit_code == 0
    check_rdf_scan(expected_file, result_file)


def test_spdx_tv_with_known_licenses():
    test_dir = test_env.get_test_loc('spdx_license_known/scan')
    result_file = test_env.get_temp_file('tv')
    expected_file = test_env.get_test_loc('spdx_license_known/expected.tv')
    result = run_scan_click(['--format', 'spdx-tv', test_dir, result_file])
    assert result.exit_code == 0
    check_tv_scan(expected_file, result_file)


def test_spdx_tv_with_license_ref():
    test_dir = test_env.get_test_loc('spdx_license_ref/scan')
    result_file = test_env.get_temp_file('tv')
    expected_file = test_env.get_test_loc('spdx_license_ref/expected.tv')
    result = run_scan_click(['--format', 'spdx-tv', test_dir, result_file])
    assert result.exit_code == 0
    check_tv_scan(expected_file, result_file)


def test_spdx_rdf_with_known_licenses_with_text():
    test_dir = test_env.get_test_loc('spdx_license_known/scan')
    result_file = test_env.get_temp_file('rdf')
    expected_file = test_env.get_test_loc('spdx_license_known/expected_with_text.rdf')
    result = run_scan_click(['--format', 'spdx-rdf', '--license-text', test_dir, result_file])
    assert result.exit_code == 0
    check_rdf_scan(expected_file, result_file)


def test_spdx_rdf_with_license_ref_with_text():
    test_dir = test_env.get_test_loc('spdx_license_ref/scan')
    result_file = test_env.get_temp_file('rdf')
    expected_file = test_env.get_test_loc('spdx_license_ref/expected_with_text.rdf')
    result = run_scan_click(['--format', 'spdx-rdf', '--license-text', test_dir, result_file])
    assert result.exit_code == 0
    check_rdf_scan(expected_file, result_file)


def test_spdx_tv_with_known_licenses_with_text():
    test_dir = test_env.get_test_loc('spdx_license_known/scan')
    result_file = test_env.get_temp_file('tv')
    expected_file = test_env.get_test_loc('spdx_license_known/expected_with_text.tv')
    result = run_scan_click(['--format', 'spdx-tv', '--license-text', test_dir, result_file])
    assert result.exit_code == 0
    check_tv_scan(expected_file, result_file)


def test_spdx_tv_with_license_ref_with_text():
    test_dir = test_env.get_test_loc('spdx_license_ref/scan')
    result_file = test_env.get_temp_file('tv')
    expected_file = test_env.get_test_loc('spdx_license_ref/expected_with_text.tv')
    result = run_scan_click(['--format', 'spdx-tv', '--license-text', test_dir, result_file])
    assert result.exit_code == 0
    check_tv_scan(expected_file, result_file)


def test_spdx_tv_tree():
    test_dir = test_env.get_test_loc('basic/scan')
    result_file = test_env.get_temp_file('tv')
    expected_file = test_env.get_test_loc('basic/expected.tv')
    result = run_scan_click(['--format', 'spdx-tv', test_dir, result_file])
    assert result.exit_code == 0
    check_tv_scan(expected_file, result_file)


def test_spdx_rdf_tree():
    test_dir = test_env.get_test_loc('basic/scan')
    result_file = test_env.get_temp_file('rdf')
    expected_file = test_env.get_test_loc('basic/expected.rdf')
    result = run_scan_click(['--format', 'spdx-rdf', test_dir, result_file])
    assert result.exit_code == 0
    check_rdf_scan(expected_file, result_file)


def load_scan(json_input):
    """
    Return a list of scan results loaded from a json_input, either in
    ScanCode standard JSON format or the data.json html-app format.
    """
    with codecs.open(json_input, 'rb', encoding='utf-8') as jsonf:
        scan = jsonf.read()

    scan_results = json.loads(scan, object_pairs_hook=OrderedDict)
    scan_results = scan_results['files']
    return scan_results


def check_json(result, expected_file, regen=False):
    if regen:
        with codecs.open(expected_file, 'wb', encoding='utf-8') as reg:
            reg.write(json.dumps(result, indent=4, separators=(',', ': ')))
    expected = json.load(
        codecs.open(expected_file, encoding='utf-8'), object_pairs_hook=OrderedDict)
    assert expected == result


def check_csvs(
        result_file, expected_file,
        ignore_keys=('date', 'file_type', 'mime_type',),
        regen=False):
    """
    Load and compare two CSVs.
    `ignore_keys` is a tuple of keys that will be ignored in the comparisons.
    """
    result_fields, results = load_csv(result_file)
    if regen:
        import shutil
        shutil.copy2(result_file, expected_file)
    expected_fields, expected = load_csv(expected_file)
    assert expected_fields == result_fields
    # then check results line by line for more compact results
    for exp, res in zip(sorted(expected), sorted(results)):
        for ign in ignore_keys:
            exp.pop(ign, None)
            res.pop(ign, None)
        assert exp == res


def load_csv(location):
    """
    Load a CSV file at location and return a tuple of (field names, list of rows as
    mappings field->value).
    """
    with codecs.open(location, 'rb', encoding='utf-8') as csvin:
        reader = unicodecsv.DictReader(csvin)
        fields = reader.fieldnames
        values = sorted(reader)
        return fields, values


def test_flatten_scan_minimal():
    test_json = test_env.get_test_loc('csv/minimal.json')
    scan = load_scan(test_json)
    headers = OrderedDict([
        ('info', []),
        ('license', []),
        ('copyright', []),
        ('email', []),
        ('url', []),
        ('package', []),
        ])
    result = list(flatten_scan(scan, headers))
    expected_file = test_env.get_test_loc('csv/minimal.json-expected')
    check_json(result, expected_file)


def test_flatten_scan_full():
    test_json = test_env.get_test_loc('csv/full.json')
    scan = load_scan(test_json)
    headers = OrderedDict([
        ('info', []),
        ('license', []),
        ('copyright', []),
        ('email', []),
        ('url', []),
        ('package', []),
        ])
    result = list(flatten_scan(scan, headers))
    expected_file = test_env.get_test_loc('csv/full.json-expected')
    check_json(result, expected_file)


def test_csv_minimal():
    test_dir = test_env.get_test_loc('csv/srp')
    result_file = test_env.get_temp_file('csv')
    expected_file = test_env.get_test_loc('csv/minimal.csv')
    result = run_scan_click(['--copyright', '--format', 'csv', test_dir, result_file])
    assert result.exit_code == 0
    assert 'Scanning done' in result.output
    assert open(expected_file).read() == open(result_file).read()


def test_csv_full():
    test_dir = test_env.get_test_loc('basic/scan')
    result_file = test_env.get_temp_file('csv')
    expected_file = test_env.get_test_loc('basic/expected.csv')
    result = run_scan_click(['--copyright', '--format', 'csv', test_dir, result_file])
    assert result.exit_code == 0
    assert open(expected_file).read() == open(result_file).read()


def test_key_ordering():
    test_json = test_env.get_test_loc('csv/key_order.json')
    scan = load_scan(test_json)
    headers = OrderedDict([
        ('info', []),
        ('license', []),
        ('copyright', []),
        ('email', []),
        ('url', []),
        ('package', []),
        ])
    result = list(flatten_scan(scan, headers))
    expected_file = test_env.get_test_loc('csv/key_order.expected.json')
    check_json(result, expected_file)


def test_json_with_no_keys_does_not_error_out():
    # this scan has no results at all
    test_json = test_env.get_test_loc('csv/no_keys.json')
    scan = load_scan(test_json)
    headers = OrderedDict([
        ('info', []),
        ('license', []),
        ('copyright', []),
        ('email', []),
        ('url', []),
        ('package', []),
        ])
    result = list(flatten_scan(scan, headers))
    expected_headers = OrderedDict([
        ('info', []),
        ('license', []),
        ('copyright', []),
        ('email', []),
        ('url', []),
        ('package', []),
        ])
    assert expected_headers == headers
    assert [] == result


def test_can_process_package_license_when_license_value_is_null():
    test_json = test_env.get_test_loc('csv/package_license_value_null.json')
    scan = load_scan(test_json)
    headers = OrderedDict([
        ('info', []),
        ('license', []),
        ('copyright', []),
        ('email', []),
        ('url', []),
        ('package', []),
        ])
    result = list(flatten_scan(scan, headers))
    expected_file = test_env.get_test_loc('csv/package_license_value_null.json-expected')
    check_json(result, expected_file)
