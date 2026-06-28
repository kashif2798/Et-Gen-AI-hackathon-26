"""
Comprehensive Test Runner for ET Nexus Chatbot

Runs all tests from all phases and generates a summary report.
"""
import sys
from pathlib import Path
import time

# Add chatbot to path
sys.path.insert(0, str(Path(__file__).parent))


def run_test_suite(name: str, module_name: str):
    """Run a test suite and return results"""
    print(f"\n{'='*70}")
    print(f"Running {name}")
    print(f"{'='*70}\n")
    
    try:
        module = __import__(f"tests.{module_name}", fromlist=['run_all_tests'])
        
        if hasattr(module, 'run_all_tests'):
            start = time.time()
            success = module.run_all_tests()
            duration = time.time() - start
            
            return {
                'name': name,
                'success': success,
                'duration': duration,
                'error': None
            }
        else:
            return {
                'name': name,
                'success': False,
                'duration': 0,
                'error': 'No run_all_tests function found'
            }
    
    except Exception as e:
        return {
            'name': name,
            'success': False,
            'duration': 0,
            'error': str(e)
        }


def main():
    """Run all test suites"""
    print("=" * 70)
    print("ET NEXUS CHATBOT - COMPREHENSIVE TEST SUITE")
    print("=" * 70)
    print()
    print("Running all tests from Phases 1-5...")
    print()
    
    # Define test suites
    test_suites = [
        ("Phase 1: Q&A Processor", "test_qa_processor"),
        ("Phase 2: Vector Store Ingestion", "test_qa_ingest"),
        ("Phase 3: Chat Engine", "test_chat_engine"),
        ("Phase 4: API Layer", "test_api_simple"),
        ("Phase 5: Integration Tests", "test_integration"),
        ("Phase 5: Performance Tests", "test_performance"),
    ]
    
    results = []
    total_start = time.time()
    
    # Run each test suite
    for name, module in test_suites:
        result = run_test_suite(name, module)
        results.append(result)
    
    total_duration = time.time() - total_start
    
    # Print summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print()
    
    passed = sum(1 for r in results if r['success'])
    failed = sum(1 for r in results if not r['success'])
    
    for result in results:
        status = "✅ PASS" if result['success'] else "❌ FAIL"
        duration = f"{result['duration']:.2f}s" if result['duration'] > 0 else "N/A"
        
        print(f"{status} - {result['name']} ({duration})")
        
        if result['error']:
            print(f"         Error: {result['error']}")
    
    print()
    print("=" * 70)
    print(f"Total: {passed} passed, {failed} failed")
    print(f"Duration: {total_duration:.2f}s")
    print("=" * 70)
    
    if failed == 0:
        print("\n🎉 ALL TEST SUITES PASSED!")
        print("\nChatbot is ready for deployment!")
    else:
        print(f"\n⚠️  {failed} test suite(s) failed")
        print("Please review the errors above")
    
    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
