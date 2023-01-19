import pytest
    

def test_error_without_env_var() -> None:
    with pytest.raises(TypeError):
        import whylabs.helpers.client


class TestImport:
    @classmethod
    def setup_class(cls) -> None:
        import os
        os.environ["WHYLABS_API_KEY"] = "api_key"
    
    def test_import(self) -> None:
        import whylabs.helpers.client
