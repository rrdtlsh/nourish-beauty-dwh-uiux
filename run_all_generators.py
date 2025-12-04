"""
Run All Data Generators - Clean Output
"""
import subprocess
import sys

def run_generator(generator_name):
    """Run a single generator with clean output"""
    print(f"\n{'='*60}")
    print(f"🚀 Running: {generator_name}")
    print('='*60)
    
    result = subprocess.run(
        [sys.executable, '-m', generator_name],
        capture_output=False,  # Show output directly
        text=True
    )
    
    if result.returncode == 0:
        print(f"✅ {generator_name} completed successfully")
    else:
        print(f"❌ {generator_name} failed")
    
    return result.returncode == 0

if __name__ == "__main__":
    generators = [
        'etl.extract.generate_user_activity',
        'etl.extract.generate_usability_score',
        'etl.extract.generate_dashboard_usage',
        'etl.extract.generate_social_media',
        'etl.extract.generate_user_funnel'
    ]
    
    print("\n" + "="*60)
    print("🎯 STARTING ALL DATA GENERATORS")
    print("="*60)
    
    results = []
    for gen in generators:
        success = run_generator(gen)
        results.append((gen, success))
    
    print("\n" + "="*60)
    print("📊 SUMMARY")
    print("="*60)
    
    for gen, success in results:
        status = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"{status} - {gen.split('.')[-1]}")
    
    total_success = sum(1 for _, s in results if s)
    print(f"\n🎉 Completed: {total_success}/{len(generators)} generators")
    print("="*60 + "\n")
