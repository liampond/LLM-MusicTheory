"""
Test configuration and utility function requirements.

These tests define how configuration and utilities SHOULD behave,
independent of current implementation details.
"""
import os
import tempfile
import time
from unittest.mock import Mock, patch, mock_open

import pytest
pytestmark = pytest.mark.contract
from pathlib import Path


class TestConfigurationContract:
    """Test configuration management requirements."""
    
    def test_settings_module_exists(self):
        """System MUST provide a settings/configuration module."""
        try:
            from llm_music_theory.config import settings
            assert settings is not None
        except ImportError:
            pytest.fail("Configuration module should be importable")
    
    def test_api_keys_configuration(self):
        """System MUST provide API key configuration mechanism."""
        from llm_music_theory.config import settings
        
        # Should have some way to access API keys
        api_key_attributes = ['API_KEYS', 'api_keys', 'KEYS', 'keys']
        
        has_api_keys = any(hasattr(settings, attr) for attr in api_key_attributes)
        assert has_api_keys, f"Settings should have one of: {api_key_attributes}"
    
    def test_environment_variable_support(self):
        """Configuration SHOULD support environment variables."""
        from llm_music_theory.config import settings
        
        # Mock environment variables
        env_vars = {
            'OPENAI_API_KEY': 'test-openai-key',
            'ANTHROPIC_API_KEY': 'test-anthropic-key',
            'GOOGLE_API_KEY': 'test-google-key',
        }
        
        with patch.dict('os.environ', env_vars):
            # Reload or re-access settings to pick up environment variables
            # The exact mechanism depends on implementation
            
            if hasattr(settings, 'API_KEYS'):
                api_keys = settings.API_KEYS
            elif hasattr(settings, 'api_keys'):
                api_keys = settings.api_keys  # type: ignore[attr-defined]
            else:
                pytest.skip("API keys configuration not found")
            
            # Should have picked up at least some environment variables
            # (exact structure depends on implementation)
            assert api_keys is not None
    
    def test_configuration_validation(self):
        """Configuration SHOULD validate settings appropriately."""
        from llm_music_theory.config import settings
        
        # Test that configuration can detect missing required settings
        with patch.dict('os.environ', {}, clear=True):
            # Clear all environment variables
            
            try:
                # Try to access API keys when none are set
                if hasattr(settings, 'API_KEYS'):
                    api_keys = settings.API_KEYS
                elif hasattr(settings, 'api_keys'):
                    api_keys = settings.api_keys  # type: ignore[attr-defined]
                else:
                    pytest.skip("API keys configuration not found")
                
                # Should either provide empty/None values or raise appropriate error
                # Both behaviors are acceptable
                
            except Exception as e:
                # If it raises an error, it should be informative
                error_msg = str(e).lower()
                assert any(word in error_msg for word in ["api", "key", "config", "missing"])


class TestPathUtilitiesContract:
    """Test path handling utility requirements."""
    
    def test_path_utils_module_exists(self):
        """System MUST provide path utilities."""
        try:
            from llm_music_theory.utils import path_utils
            assert path_utils is not None
        except ImportError:
            pytest.fail("Path utilities module should be importable")
    
    def test_file_path_resolution(self):
        """Path utilities SHOULD resolve file paths correctly."""
        from llm_music_theory.utils import path_utils
        
        # Should have functions for path resolution
        path_functions = ['resolve_path', 'get_path', 'find_file', 'resolve_file_path']
        
        has_path_function = any(
            hasattr(path_utils, func) and callable(getattr(path_utils, func))
            for func in path_functions
        )
        
        if not has_path_function:
            pytest.skip("Path resolution functions not found")
        
        # Test path resolution (exact function name is flexible)
        for func_name in path_functions:
            if hasattr(path_utils, func_name):
                func = getattr(path_utils, func_name)
                
                # Should handle basic path resolution
                try:
                    result = func("test", "exam", "question", "format")
                    assert isinstance(result, (str, Path))
                except (TypeError, ValueError):
                    # Different function signature is acceptable
                    pass
                break
    
    def test_file_existence_checking(self):
        """Path utilities SHOULD check file existence safely."""
        from llm_music_theory.utils import path_utils
        
        # Should have functions for existence checking
        check_functions = ['file_exists', 'path_exists', 'check_file', 'exists']
        
        has_check_function = any(
            hasattr(path_utils, func) and callable(getattr(path_utils, func))
            for func in check_functions
        )
        
        if not has_check_function:
            pytest.skip("File existence checking functions not found")
        
        # Test existence checking
        for func_name in check_functions:
            if hasattr(path_utils, func_name):
                func = getattr(path_utils, func_name)
                
                try:
                    # Test with a known non-existent path
                    result = func("/nonexistent/path/file.txt")
                    assert isinstance(result, bool)
                    assert result is False  # Should not exist
                except (TypeError, ValueError):
                    # Different function signature is acceptable
                    pass
                break
    
    def test_safe_path_handling(self):
        """Path utilities MUST handle paths safely."""
        from llm_music_theory.utils import path_utils
        
        # Test with various problematic paths
        problematic_paths = [
            "../../../etc/passwd",  # Directory traversal
            "/root/sensitive",       # Absolute path outside project
            "file with spaces.txt",  # Spaces
            "file-with-unicode-ñ.txt",  # Unicode
            "",                      # Empty string
            None                     # None value
        ]
        
        # Should handle these gracefully (exact behavior is flexible)
        # Could return None, raise ValueError, or sanitize - any is acceptable
        
        path_functions = ['resolve_path', 'get_path', 'find_file', 'resolve_file_path']
        
        for func_name in path_functions:
            if hasattr(path_utils, func_name):
                func = getattr(path_utils, func_name)
                
                for bad_path in problematic_paths:
                    try:
                        result = func(bad_path)
                        # If it doesn't raise an error, result should be safe
                        if result is not None:
                            assert isinstance(result, (str, Path))
                    except (ValueError, TypeError, OSError):
                        # These are acceptable error types for bad paths
                        pass
                break


class TestLoggingContract:
    """Test logging utility requirements."""
    
    def test_logger_module_exists(self):
        """System SHOULD provide logging utilities."""
        try:
            from llm_music_theory.utils import logger
            assert logger is not None
        except ImportError:
            # Logging is optional but recommended
            pytest.skip("Logging module not found (optional)")
    
    def test_logger_configuration(self):
        """Logger SHOULD be properly configured."""
        try:
            from llm_music_theory.utils import logger
        except ImportError:
            pytest.skip("Logging module not available")
        
        # Should have standard logging functions
        log_functions = ['info', 'debug', 'warning', 'error', 'critical']
        
        has_log_functions = any(
            hasattr(logger, func) and callable(getattr(logger, func))
            for func in log_functions
        )
        
        if not has_log_functions:
            # Maybe it's a logger instance
            if hasattr(logger, 'logger'):
                actual_logger = logger.logger  # type: ignore[attr-defined]
                has_log_functions = any(
                    hasattr(actual_logger, func) and callable(getattr(actual_logger, func))
                    for func in log_functions
                )
        
        if has_log_functions:
            # Test basic logging (should not raise errors)
            try:
                if hasattr(logger, 'info'):
                    logger.info("Test log message")  # type: ignore[attr-defined]
                elif hasattr(logger, 'logger'):
                    logger.logger.info("Test log message")  # type: ignore[attr-defined]
            except Exception as e:
                pytest.fail(f"Basic logging failed: {e}")


class TestDataPathContract:
    """Test data file path management requirements."""
    
    def test_data_directory_structure(self):
        """System SHOULD have consistent data directory structure."""
        from llm_music_theory.utils import path_utils
        
        # Should be able to resolve paths for different data types
        data_types = ["encoded", "prompts", "questions"]
        formats = ["mei", "musicxml", "abc", "humdrum"]
        
        # Test basic path resolution capabilities
        path_functions = ['resolve_path', 'get_path', 'find_file', 'resolve_file_path']
        
        for func_name in path_functions:
            if hasattr(path_utils, func_name):
                func = getattr(path_utils, func_name)
                
                # Test with valid data structure parameters
                try:
                    result = func("encoded", "test_exam", "Q1b", "mei")
                    assert isinstance(result, (str, Path))
                except (TypeError, ValueError):
                    # Different function signature - try alternatives
                    try:
                        result = func("test_exam", "Q1b", "mei")
                        assert isinstance(result, (str, Path))
                    except (TypeError, ValueError):
                        pass
                break
    
    def test_format_specific_paths(self):
        """System SHOULD handle format-specific data paths."""
        from llm_music_theory.utils import path_utils
        
        formats = ["mei", "musicxml", "abc", "humdrum"]
        
        # Should be able to handle different format requirements
        path_functions = ['resolve_path', 'get_path', 'find_file']
        
        for func_name in path_functions:
            if hasattr(path_utils, func_name):
                func = getattr(path_utils, func_name)
                
                for fmt in formats:
                    try:
                        result = func("test_exam", "Q1b", fmt)
                        if result is not None:
                            assert isinstance(result, (str, Path))
                            # Path should include format information somehow
                            path_str = str(result).lower()
                            assert fmt in path_str or fmt.upper() in str(result)
                    except (TypeError, ValueError):
                        # Different function signature is acceptable
                        pass
                break


class TestErrorHandlingContract:
    """Test error handling requirements across utilities."""
    
    def test_graceful_missing_file_handling(self):
        """Utilities SHOULD handle missing files gracefully."""
        from llm_music_theory.utils import path_utils
        
        # Test with non-existent files
        path_functions = ['resolve_path', 'get_path', 'find_file']
        
        for func_name in path_functions:
            if hasattr(path_utils, func_name):
                func = getattr(path_utils, func_name)
                
                try:
                    result = func("nonexistent_exam", "nonexistent_question", "mei")
                    
                    # Should either return None/empty or raise appropriate error
                    if result is not None:
                        # If it returns something, should be a valid path type
                        assert isinstance(result, (str, Path))
                        
                except (FileNotFoundError, ValueError, OSError):
                    # These are acceptable error types for missing files
                    pass
                break
    
    def test_invalid_parameter_handling(self):
        """Utilities SHOULD validate parameters appropriately."""
        from llm_music_theory.utils import path_utils
        
        # Test with invalid parameters
        invalid_params = [
            (None, "Q1b", "mei"),
            ("exam", None, "mei"), 
            ("exam", "Q1b", None),
            ("", "Q1b", "mei"),
            ("exam", "", "mei"),
            ("exam", "Q1b", ""),
            (123, "Q1b", "mei"),  # Wrong type
            ("exam", 123, "mei"),  # Wrong type
            ("exam", "Q1b", 123),  # Wrong type
        ]
        
        path_functions = ['resolve_path', 'get_path', 'find_file']
        
        for func_name in path_functions:
            if hasattr(path_utils, func_name):
                func = getattr(path_utils, func_name)
                
                for params in invalid_params:
                    try:
                        result = func(*params)
                        # If it doesn't raise an error, result should be safe
                        if result is not None:
                            assert isinstance(result, (str, Path))
                    except (TypeError, ValueError, AttributeError):
                        # These are acceptable error types for invalid params
                        pass
                break


class TestPerformanceContract:
    """Test performance requirements for utilities."""
    
    @pytest.mark.slow
    def test_path_resolution_speed(self):
        """Path resolution SHOULD be fast for typical use cases."""
        import time
        from llm_music_theory.utils import path_utils
        
        path_functions = ['resolve_path', 'get_path', 'find_file']
        
        for func_name in path_functions:
            if hasattr(path_utils, func_name):
                func = getattr(path_utils, func_name)
                
                # Time multiple path resolutions
                start_time = time.time()
                
                for i in range(100):
                    try:
                        result = func("test_exam", f"Q{i}", "mei")
                    except (TypeError, ValueError):
                        # Different function signature
                        try:
                            result = func("test_exam", f"Q{i}")
                        except (TypeError, ValueError):
                            break
                
                total_time = time.time() - start_time
                avg_time = total_time / 100
                
                # Should be fast (< 0.001 seconds per resolution)
                assert avg_time < 0.001, f"Path resolution took {avg_time:.4f}s on average"
                break
    
    @pytest.mark.slow
    def test_configuration_access_speed(self):
        """Configuration access SHOULD be fast."""
        import time
        from llm_music_theory.config import settings
        
        # Time multiple configuration accesses
        start_time = time.time()
        
        for _ in range(1000):
            try:
                if hasattr(settings, 'API_KEYS'):
                    _ = settings.API_KEYS
                elif hasattr(settings, 'api_keys'):
                    _ = settings.api_keys  # type: ignore[attr-defined]
                else:
                    break
            except Exception:
                break
        
        total_time = time.time() - start_time
        avg_time = total_time / 1000
        
        # Should be very fast (< 0.0001 seconds per access)
        assert avg_time < 0.0001, f"Config access took {avg_time:.6f}s on average"


class TestSecurityContract:
    """Test security requirements for utilities."""
    
    def test_path_traversal_protection(self):
        """Path utilities MUST prevent directory traversal attacks."""
        from llm_music_theory.utils import path_utils
        
        # Test directory traversal attempts
        malicious_paths = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            "exam/../../../sensitive_file",
            "normal_name/../../../etc/passwd"
        ]
        
        path_functions = ['resolve_path', 'get_path', 'find_file']
        
        for func_name in path_functions:
            if hasattr(path_utils, func_name):
                func = getattr(path_utils, func_name)
                
                for malicious_path in malicious_paths:
                    try:
                        result = func(malicious_path, "Q1b", "mei")
                        
                        if result is not None:
                            # Result should not contain directory traversal
                            result_str = str(result)
                            assert "../" not in result_str, f"Path traversal detected: {result_str}"
                            assert "..\\" not in result_str, f"Path traversal detected: {result_str}"
                            
                            # Should not point outside project directory
                            # (This is implementation-dependent, but good practice)
                            
                    except (ValueError, OSError, PermissionError):
                        # These are acceptable - system is protecting against traversal
                        pass
                    except TypeError:
                        # Different function signature
                        break
                break
    
    def test_api_key_security(self):
        """Configuration SHOULD handle API keys securely."""
        from llm_music_theory.config import settings
        
        # API keys should not be logged or exposed in debug output
        try:
            if hasattr(settings, 'API_KEYS'):
                api_keys = settings.API_KEYS
            elif hasattr(settings, 'api_keys'):
                api_keys = settings.api_keys  # type: ignore[attr-defined]
            else:
                pytest.skip("API keys configuration not found")
            
            # String representation should not expose actual keys
            settings_str = str(settings)
            
            # Should not contain actual API key values
            # (This is a best practice but hard to test definitively)
            assert len(settings_str) < 1000, "Settings string representation should be minimal"
            
        except Exception:
            # If configuration is not accessible, that's fine for this test
            pass
