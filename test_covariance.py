
from flext_core.result import FlextResult

def test_covariance() -> FlextResult[object]:
    result_str: FlextResult[str] = FlextResult[str].ok('test')
    result_obj: FlextResult[object] = result_str
    return result_obj
