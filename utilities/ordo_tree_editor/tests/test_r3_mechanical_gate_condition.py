from pathlib import Path
import sys

HERE = Path(__file__).resolve()
EDITOR = HERE.parents[1]
if str(EDITOR) not in sys.path:
    sys.path.insert(0, str(EDITOR))
import editor_service as es


def test_simple_one_of_and_not_empty_passes():
    c='state.parse_validation_status is one of VALID and state.parse_validation_report_ref is not empty'
    state={'parse_validation_status':'VALID','parse_validation_report_ref':'reports/runtime/parse_validation.json'}
    result, reason, extra = es._evaluate_mechanical_condition(c,state)
    assert result == 'pass'
    assert extra['condition_result'] is True


def test_simple_one_of_false_routes_fail_not_unresolved():
    c='state.parse_validation_status is one of VALID and state.parse_validation_report_ref is not empty'
    state={'parse_validation_status':'INVALID','parse_validation_report_ref':'reports/runtime/parse_validation.json'}
    result, reason, extra = es._evaluate_mechanical_condition(c,state)
    assert result == 'fail'
    assert extra['condition_result'] is False


def test_one_of_multiple_values():
    c='state.language_validation_status is one of VALID, VALID_WITH_WARNINGS and state.language_validation_report_ref is not empty'
    state={'language_validation_status':'VALID_WITH_WARNINGS','language_validation_report_ref':'reports/runtime/language_validation.json'}
    assert es._evaluate_mechanical_condition(c,state)[0] == 'pass'


def test_missing_path_is_unresolved_fail_closed():
    c='state.parse_validation_status is one of VALID and state.parse_validation_report_ref is not empty'
    result, reason, extra = es._evaluate_mechanical_condition(c,{'parse_validation_status':'VALID'})
    assert result == 'unresolved'
    assert 'parse_validation_report_ref' in extra['missing_required_inputs']


def test_unsupported_syntax_is_unresolved_not_eval():
    result, reason, extra = es._evaluate_mechanical_condition('state.x magically becomes VALID',{'x':'VALID'})
    assert result == 'unresolved'
    assert extra['unsupported_clauses']
