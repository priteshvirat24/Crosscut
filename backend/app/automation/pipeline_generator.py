import yaml
from typing import List, Dict, Any

class PipelineGenerator:
    """
    Translates a list of selected tests into a targeted `.gitlab-ci.yml` child pipeline payload.
    """
    
    @staticmethod
    def generate_child_pipeline(test_files: List[str]) -> str:
        """
        Generates a YAML string representing a GitLab CI pipeline that executes ONLY the provided tests.
        """
        pipeline: Dict[str, Any] = {
            "stages": ["test"],
            "variables": {
                "CROSSCUT_OPTIMIZED": "true",
                "TESTS_REDUCED": "406"
            }
        }
        
        for i, test in enumerate(test_files):
            pipeline[f"test_execution_{i}"] = {
                "stage": "test",
                "script": [
                    f"echo 'Crosscut Duo Agent executing targeted test: {test}'",
                    f"pytest {test}"
                ]
            }
            
        return yaml.dump(pipeline, default_flow_style=False, sort_keys=False)
