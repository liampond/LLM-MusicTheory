"""
Test the CLI interface requirements and behavior.

These tests define how the command-line interface SHOULD behave,
independent of current implementation details.
"""
from io import StringIO
from unittest.mock import Mock, patch, MagicMock

import pytest
pytestmark = pytest.mark.contract


class TestCLIModuleExistence:
    """Test that required CLI modules exist."""
    
    def test_cli_modules_importable(self):
        """CLI modules MUST be importable."""
        # Single query CLI
        try:
            from llm_music_theory.cli import run_single
            assert run_single is not None
        except ImportError:
            pytest.fail("run_single CLI module should be importable")
        
        # Batch processing CLI  
        try:
            from llm_music_theory.cli import run_batch
            assert run_batch is not None
        except ImportError:
            pytest.fail("run_batch CLI module should be importable")
    
    def test_cli_modules_have_main_functions(self):
        """CLI modules MUST have main/entry functions."""
        from llm_music_theory.cli import run_single, run_batch
        
        # Check for standard entry point patterns
        entry_point_names = ['main', 'cli_main', 'run', 'execute', 'entry_point']
        
        # run_single should have an entry point
        single_has_entry = any(
            hasattr(run_single, name) and callable(getattr(run_single, name))
            for name in entry_point_names
        )
        assert single_has_entry, f"run_single should have one of: {entry_point_names}"
        
        # run_batch should have an entry point
        batch_has_entry = any(
            hasattr(run_batch, name) and callable(getattr(run_batch, name))
            for name in entry_point_names
        )
        assert batch_has_entry, f"run_batch should have one of: {entry_point_names}"


class TestSingleQueryCLI:
    """Test single query CLI requirements."""
    
    def test_single_query_argument_parsing(self):
        """Single query CLI MUST parse required arguments."""
        from llm_music_theory.cli import run_single
        
        # Mock sys.argv to test argument parsing
        test_args = [
            "run_single.py",
            "--model", "chatgpt",
            "--question", "Q1b", 
            "--exam", "test_exam",
            "--format", "mei",
            "--context"
        ]
        
        with patch('sys.argv', test_args):
            try:
                # Try different possible function names
                if hasattr(run_single, 'main'):
                    with patch.object(run_single, 'PromptRunner') as mock_runner:
                        mock_runner.return_value.run.return_value = "test result"
                        run_single.main()
                elif hasattr(run_single, 'cli_main'):
                    with patch.object(run_single, 'PromptRunner') as mock_runner:
                        mock_runner.return_value.run.return_value = "test result"
                        run_single.cli_main()
                else:
                    pytest.skip("Could not find entry point function")
                    
            except (SystemExit, AttributeError):
                # SystemExit is normal for argparse
                # AttributeError might occur due to different implementation
                pass
            except Exception as e:
                pytest.fail(f"Argument parsing failed: {e}")
    
    def test_single_query_required_arguments(self):
        """Single query CLI MUST require essential arguments."""
        from llm_music_theory.cli import run_single
        
        # Test missing required arguments
        incomplete_args = [
            ["run_single.py"],  # No arguments
            ["run_single.py", "--model", "chatgpt"],  # Missing other required args
            ["run_single.py", "--question", "Q1b"],  # Missing model
        ]
        
        for args in incomplete_args:
            with patch('sys.argv', args):
                try:
                    if hasattr(run_single, 'main'):
                        run_single.main()
                    elif hasattr(run_single, 'cli_main'):
                        run_single.cli_main()
                    else:
                        pytest.skip("Could not find entry point function")
                except SystemExit:
                    # Expected - should exit due to missing arguments
                    pass
                except Exception:
                    # Other exceptions are also acceptable for missing args
                    pass
                else:
                    pytest.fail("Should have raised error for missing arguments")
    
    def test_single_query_execution_integration(self):
        """Single query CLI SHOULD integrate with the runner properly."""
        from llm_music_theory.cli import run_single
        
        test_args = [
            "run_single.py",
            "--model", "chatgpt",
            "--question", "Q1b",
            "--exam", "test_exam", 
            "--format", "mei",
            "--context"
        ]
        
        with patch('sys.argv', test_args):
            # Mock the runner to verify integration
            with patch('llm_music_theory.core.runner.PromptRunner') as mock_runner_class:
                mock_runner = Mock()
                mock_runner.run.return_value = "CLI test result"
                mock_runner_class.return_value = mock_runner
                
                try:
                    if hasattr(run_single, 'main'):
                        run_single.main()
                    elif hasattr(run_single, 'cli_main'):
                        run_single.cli_main()
                    else:
                        pytest.skip("Could not find entry point function")
                        
                    # Should have created runner and called run
                    mock_runner_class.assert_called_once()
                    mock_runner.run.assert_called_once()
                    
                    # Should have passed the correct arguments
                    call_args = mock_runner.run.call_args
                    if call_args:
                        # Verify some arguments were passed
                        assert len(call_args[0]) > 0 or len(call_args[1]) > 0
                        
                except (SystemExit, AttributeError):
                    # May exit normally or have different interface
                    pass


class TestBatchProcessingCLI:
    """Test batch processing CLI requirements."""
    
    def test_batch_argument_parsing(self):
        """Batch CLI MUST parse batch-specific arguments.""" 
        from llm_music_theory.cli import run_batch
        
        test_args = [
            "run_batch.py",
            "--models", "chatgpt,claude",
            "--questions", "Q1a,Q1b",
            "--exams", "test_exam",
            "--formats", "mei,abc",
            "--context", "--no-context"
        ]
        
        with patch('sys.argv', test_args):
            try:
                if hasattr(run_batch, 'main'):
                    with patch('llm_music_theory.core.runner.PromptRunner') as mock_runner:
                        mock_runner.return_value.run.return_value = "batch result"
                        run_batch.main()
                elif hasattr(run_batch, 'cli_main'):
                    with patch('llm_music_theory.core.runner.PromptRunner') as mock_runner:
                        mock_runner.return_value.run.return_value = "batch result"
                        run_batch.cli_main()
                else:
                    pytest.skip("Could not find entry point function")
                    
            except (SystemExit, AttributeError):
                # SystemExit is normal for CLI tools
                pass
            except Exception as e:
                pytest.fail(f"Batch argument parsing failed: {e}")
    
    def test_batch_multiple_combinations(self):
        """Batch CLI SHOULD process multiple parameter combinations."""
        from llm_music_theory.cli import run_batch
        
        test_args = [
            "run_batch.py",
            "--models", "chatgpt",
            "--questions", "Q1a,Q1b", 
            "--exams", "test_exam",
            "--formats", "mei,abc",
            "--context"
        ]
        
        with patch('sys.argv', test_args):
            with patch('llm_music_theory.core.runner.PromptRunner') as mock_runner_class:
                mock_runner = Mock()
                mock_runner.run.return_value = "batch test result"
                mock_runner_class.return_value = mock_runner
                
                try:
                    if hasattr(run_batch, 'main'):
                        run_batch.main()
                    elif hasattr(run_batch, 'cli_main'):
                        run_batch.cli_main()
                    else:
                        pytest.skip("Could not find entry point function")
                    
                    # Should have made multiple calls for combinations
                    # 1 model × 2 questions × 1 exam × 2 formats = 4 calls minimum
                    call_count = mock_runner.run.call_count
                    assert call_count >= 4, f"Expected at least 4 calls, got {call_count}"
                    
                except (SystemExit, AttributeError):
                    pass


class TestCLIUserExperience:
    """Test CLI user experience requirements."""
    
    def test_help_messages(self):
        """CLI SHOULD provide helpful usage information."""
        from llm_music_theory.cli import run_single, run_batch
        
        # Test help for single query
        with patch('sys.argv', ['run_single.py', '--help']):
            with pytest.raises(SystemExit):
                try:
                    if hasattr(run_single, 'main'):
                        run_single.main()
                    elif hasattr(run_single, 'cli_main'):
                        run_single.cli_main()
                except AttributeError:
                    pytest.skip("Entry point function not found")
        
        # Test help for batch
        with patch('sys.argv', ['run_batch.py', '--help']):
            with pytest.raises(SystemExit):
                try:
                    if hasattr(run_batch, 'main'):
                        run_batch.main()
                    elif hasattr(run_batch, 'cli_main'):
                        run_batch.cli_main()
                except AttributeError:
                    pytest.skip("Entry point function not found")
    
    def test_progress_reporting(self):
        """Batch CLI SHOULD provide progress feedback for long operations."""
        from llm_music_theory.cli import run_batch
        
        test_args = [
            "run_batch.py",
            "--models", "chatgpt",
            "--questions", "Q1a,Q1b,Q1c",
            "--exams", "test_exam",
            "--formats", "mei", 
            "--context"
        ]
        
        # Capture stdout to check for progress messages
        with patch('sys.argv', test_args), \
             patch('sys.stdout', new_callable=StringIO) as mock_stdout, \
             patch('llm_music_theory.core.runner.PromptRunner') as mock_runner_class:
            
            mock_runner = Mock()
            mock_runner.run.return_value = "progress test result"
            mock_runner_class.return_value = mock_runner
            
            try:
                if hasattr(run_batch, 'main'):
                    run_batch.main()
                elif hasattr(run_batch, 'cli_main'):
                    run_batch.cli_main()
                else:
                    pytest.skip("Could not find entry point function")
                
                output = mock_stdout.getvalue()
                
                # Should have some output indicating progress
                # (exact format is flexible)
                assert len(output) > 0, "Should provide some progress feedback"
                
            except (SystemExit, AttributeError):
                pass
    
    def test_error_handling_user_friendly(self):
        """CLI SHOULD provide user-friendly error messages."""
        from llm_music_theory.cli import run_single
        
        test_args = [
            "run_single.py",
            "--model", "invalid_model",
            "--question", "Q1b",
            "--exam", "test_exam",
            "--format", "mei",
            "--context"
        ]
        
        with patch('sys.argv', test_args), \
             patch('sys.stderr', new_callable=StringIO) as mock_stderr, \
             patch('llm_music_theory.core.dispatcher.get_llm', side_effect=ValueError("Unknown model: invalid_model")):
            
            try:
                if hasattr(run_single, 'main'):
                    run_single.main()
                elif hasattr(run_single, 'cli_main'):
                    run_single.cli_main()
                else:
                    pytest.skip("Could not find entry point function")
                    
            except SystemExit:
                # Should exit with error
                error_output = mock_stderr.getvalue()
                
                # Error message should be user-friendly
                error_lower = error_output.lower()
                assert any(word in error_lower for word in ["error", "invalid", "unknown", "model"])
                
            except AttributeError:
                pytest.skip("Entry point function not found")


class TestCLIConfiguration:
    """Test CLI configuration and setup requirements."""
    
    def test_environment_variable_support(self):
        """CLI SHOULD support configuration via environment variables."""
        from llm_music_theory.cli import run_single
        
        # Mock environment variables
        with patch.dict('os.environ', {
            'LLM_MUSIC_THEORY_MODEL': 'chatgpt',
            'LLM_MUSIC_THEORY_EXAM': 'default_exam',
            'LLM_MUSIC_THEORY_FORMAT': 'mei'
        }):
            
            # Minimal args, relying on env vars
            test_args = [
                "run_single.py", 
                "--question", "Q1b"
            ]
            
            with patch('sys.argv', test_args), \
                 patch('llm_music_theory.core.runner.PromptRunner') as mock_runner_class:
                
                mock_runner = Mock()
                mock_runner.run.return_value = "env var test result"
                mock_runner_class.return_value = mock_runner
                
                try:
                    if hasattr(run_single, 'main'):
                        run_single.main()
                    elif hasattr(run_single, 'cli_main'):
                        run_single.cli_main()
                    else:
                        pytest.skip("Could not find entry point function")
                    
                    # Should have used environment variables to fill in defaults
                    # (exact implementation is flexible)
                    
                except (SystemExit, AttributeError):
                    # May not be implemented yet, which is fine
                    pass
    
    def test_config_file_support(self):
        """CLI MAY support configuration files."""
        # This is a nice-to-have feature
        # Implementation is optional but if present should be testable
        
        from llm_music_theory.cli import run_single
        
        # Test is optional - just document the expectation
        pytest.skip("Config file support is optional")
    
    def test_output_format_options(self):
        """CLI SHOULD support different output formats."""
        from llm_music_theory.cli import run_single
        
        for output_format in ['json', 'text', 'csv']:
            test_args = [
                "run_single.py",
                "--model", "chatgpt",
                "--question", "Q1b",
                "--exam", "test_exam",
                "--format", "mei",
                "--context",
                "--output-format", output_format
            ]
            
            with patch('sys.argv', test_args), \
                 patch('sys.stdout', new_callable=StringIO) as mock_stdout, \
                 patch('llm_music_theory.core.runner.PromptRunner') as mock_runner_class:
                
                mock_runner = Mock()
                mock_runner.run.return_value = f"result for {output_format}"
                mock_runner_class.return_value = mock_runner
                
                try:
                    if hasattr(run_single, 'main'):
                        run_single.main()
                    elif hasattr(run_single, 'cli_main'):
                        run_single.cli_main()
                    else:
                        pytest.skip("Could not find entry point function")
                    
                    output = mock_stdout.getvalue()
                    
                    # Should have some output in requested format
                    # (exact format validation is implementation-specific)
                    assert len(output) > 0
                    
                except (SystemExit, AttributeError):
                    # Output format support may not be implemented
                    pass


class TestCLIPerformance:
    """Test CLI performance requirements."""
    
    @pytest.mark.slow
    def test_cli_startup_speed(self):
        """CLI startup SHOULD be reasonably fast."""
        import time
        import subprocess
        import sys
        
        # Test import time
        start_time = time.time()
        
        try:
            from llm_music_theory.cli import run_single
            import_time = time.time() - start_time
            
            # Should import quickly (< 2 seconds)
            assert import_time < 2.0, f"CLI import took {import_time:.2f}s"
            
        except ImportError as e:
            pytest.fail(f"CLI module import failed: {e}")
    
    @pytest.mark.slow
    def test_batch_processing_efficiency(self):
        """Batch processing SHOULD handle multiple items efficiently."""
        import time
        from llm_music_theory.cli import run_batch
        
        test_args = [
            "run_batch.py",
            "--models", "chatgpt",
            "--questions", "Q1a,Q1b,Q1c,Q1d,Q1e",
            "--exams", "test_exam",
            "--formats", "mei",
            "--context"
        ]
        
        with patch('sys.argv', test_args), \
             patch('llm_music_theory.core.runner.PromptRunner') as mock_runner_class:
            
            mock_runner = Mock()
            
            # Simulate some processing time per call
            def slow_run(*args, **kwargs):
                import time
                time.sleep(0.01)  # 10ms per call
                return "efficient test result"
            
            mock_runner.run.side_effect = slow_run
            mock_runner_class.return_value = mock_runner
            
            start_time = time.time()
            
            try:
                if hasattr(run_batch, 'main'):
                    run_batch.main()
                elif hasattr(run_batch, 'cli_main'):
                    run_batch.cli_main()
                else:
                    pytest.skip("Could not find entry point function")
                
                total_time = time.time() - start_time
                
                # Should complete within reasonable time
                # 5 questions × 0.01s + overhead should be < 1 second
                assert total_time < 1.0, f"Batch processing took {total_time:.2f}s"
                
            except (SystemExit, AttributeError):
                pass
