#!/usr/bin/env python3
"""
Enhancement Framework Validation Test Cases
==========================================

This script creates comprehensive test scenarios and compares enhanced vs standard scoring
to validate that the enhancement framework produces expected improvements.
"""

import subprocess

import pandas as pd

# Test case definitions
TEST_CASES = {
    "senior_executive_biotech": {
        "description": "Senior Executive in Biotech - Cross-functional leadership heavy",
        "data": [
            ("Essential", "Lead strategic planning for drug discovery pipeline", 4),
            ("Essential", "Manage cross-functional teams across chemistry and biology", 4),
            ("Essential", "Oversee partnerships and licensing agreements", 3),
            ("Important", "Communicate complex scientific findings to stakeholders", 5),
            ("Important", "Evaluate and prioritize therapeutic targets", 4),
            ("Important", "Direct platform development initiatives", 3),
            ("Desirable", "Expert knowledge of bioinformatics and computational biology", 2),
            ("Desirable", "Advanced understanding of regulatory pathways", 3),
            ("Implicit", "Present to board members and investors", 4),
            ("Implicit", "Collaborate with clinical development teams", 4)
        ],
        "enhancement_configs": [
            {"target_role_type": "executive", "target_role_level": "senior_executive", "years_experience": 20, "proven_strengths": None},
            {"target_role_type": "executive", "target_role_level": "c_suite", "years_experience": 25, "proven_strengths": ["cross-functional", "strategy"]},
            {"target_role_type": "executive", "target_role_level": "senior_executive", "years_experience": 15, "proven_strengths": ["bioinformatics", "drug-discovery"]}
        ]
    },

    "senior_ic_technical": {
        "description": "Senior IC Technical Role - Deep expertise focused",
        "data": [
            ("Essential", "Develop novel algorithms for data analysis", 5),
            ("Essential", "Implement advanced statistical modeling techniques", 4),
            ("Essential", "Optimize computational pipelines for performance", 4),
            ("Important", "Design and execute complex research experiments", 5),
            ("Important", "Analyze large-scale genomic datasets", 3),
            ("Important", "Publish research findings in peer-reviewed journals", 3),
            ("Desirable", "Mentor junior scientists and researchers", 2),
            ("Desirable", "Collaborate with external research institutions", 3),
            ("Implicit", "Present findings at scientific conferences", 3),
            ("Implicit", "Stay current with latest computational methods", 5)
        ],
        "enhancement_configs": [
            {"target_role_type": "ic", "target_role_level": "senior_ic", "years_experience": 15, "proven_strengths": None},
            {"target_role_type": "ic", "target_role_level": "senior_ic", "years_experience": 20, "proven_strengths": ["algorithms", "computational-biology"]},
            {"target_role_type": "executive", "target_role_level": "senior_ic", "years_experience": 15, "proven_strengths": None}  # Misaligned for comparison
        ]
    },

    "director_hybrid": {
        "description": "Director/VP Hybrid Role - Balance of leadership and technical",
        "data": [
            ("Essential", "Lead technical strategy and roadmap development", 4),
            ("Essential", "Manage team of senior scientists and engineers", 3),
            ("Essential", "Drive innovation in platform technologies", 4),
            ("Important", "Collaborate across multiple business functions", 5),
            ("Important", "Evaluate technical feasibility of new projects", 4),
            ("Important", "Represent technical capabilities to senior leadership", 3),
            ("Desirable", "Hands-on contribution to key technical projects", 2),
            ("Desirable", "Experience with technology transfer and licensing", 2),
            ("Implicit", "Translate business requirements into technical specifications", 4),
            ("Implicit", "Build relationships with key external partners", 3)
        ],
        "enhancement_configs": [
            {"target_role_type": "executive", "target_role_level": "director_vp", "years_experience": 18, "proven_strengths": None},
            {"target_role_type": "hybrid", "target_role_level": "director_vp", "years_experience": 18, "proven_strengths": ["technical-leadership", "cross-functional"]},
            {"target_role_type": "ic", "target_role_level": "director_vp", "years_experience": 18, "proven_strengths": None}  # Misaligned
        ]
    },

    "junior_executive_gaps": {
        "description": "Junior Executive with Core Gaps - Experience calibration test",
        "data": [
            ("Essential", "Lead strategic planning initiatives", 2),  # Core gap
            ("Essential", "Manage and develop team members", 1),       # Core gap
            ("Essential", "Drive business development opportunities", 3),
            ("Important", "Communicate with senior stakeholders", 2),
            ("Important", "Analyze market trends and opportunities", 4),
            ("Important", "Coordinate cross-functional projects", 3),
            ("Desirable", "Expert domain knowledge in therapeutics", 4),
            ("Desirable", "Advanced data analysis capabilities", 5),
            ("Implicit", "Present to executive leadership", 2),
            ("Implicit", "Build external partnerships", 2)
        ],
        "enhancement_configs": [
            {"target_role_type": "executive", "target_role_level": "senior_executive", "years_experience": 10, "proven_strengths": None},  # Junior - less penalty
            {"target_role_type": "executive", "target_role_level": "senior_executive", "years_experience": 25, "proven_strengths": None},  # Senior - more penalty
            {"target_role_type": "executive", "target_role_level": "director_vp", "years_experience": 10, "proven_strengths": ["domain-expertise"]}  # Lower level, proven strengths
        ]
    }
}

def create_csv_from_data(data: list[tuple[str, str, int]], filename: str) -> str:
    """Create a CSV file from test data."""
    df_data = {
        "Classification": [item[0] for item in data],
        "Requirement": [item[1] for item in data],
        "SelfScore": [item[2] for item in data]
    }
    df = pd.DataFrame(df_data)

    filepath = f"data/{filename}.csv"
    df.to_csv(filepath, index=False)
    return filepath

def run_scoring(csv_path: str, enhanced: bool = False, **kwargs) -> dict:
    """Run scoring and capture results."""
    cmd = ["uv", "run", "python", "-m", "scoring.scoring_v2", csv_path]

    if enhanced:
        cmd.append("--enable-enhancements")
        if kwargs.get("target_role_type"):
            cmd.extend(["--target-role-type", kwargs["target_role_type"]])
        if kwargs.get("target_role_level"):
            cmd.extend(["--target-role-level", kwargs["target_role_level"]])
        if kwargs.get("years_experience"):
            cmd.extend(["--years-experience", str(kwargs["years_experience"])])
        if kwargs.get("proven_strengths"):
            cmd.extend(["--proven-strengths"] + kwargs["proven_strengths"])

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=".")
        output = result.stdout

        # Parse key metrics from output
        lines = output.split('\n')
        metrics = {"error": None}

        for line in lines:
            if "Core gap present" in line:
                metrics["core_gap"] = "YES" in line
            elif "Actual points" in line and ":" in line:
                parts = line.split(":")[-1].strip().split("/")
                metrics["actual_points"] = float(parts[0].strip())
                metrics["max_points"] = float(parts[1].strip())
            elif "% Fit" in line and ":" in line:
                pct_str = line.split(":")[-1].strip().rstrip("%")
                metrics["pct_fit"] = float(pct_str)
            elif "Verdict" in line and ":" in line:
                metrics["verdict"] = line.split(":")[-1].strip()

        return metrics

    except Exception as e:
        return {"error": str(e)}

def validate_test_case(test_name: str, test_data: dict) -> dict:
    """Validate a single test case with multiple enhancement configurations."""
    print(f"\n{'='*60}")
    print(f"VALIDATING: {test_name}")
    print(f"Description: {test_data['description']}")
    print('='*60)

    # Create CSV file for this test case
    csv_path = create_csv_from_data(test_data['data'], f"validation_{test_name}")

    results = {
        "test_name": test_name,
        "description": test_data['description'],
        "standard_scoring": None,
        "enhanced_configs": []
    }

    # Run standard scoring
    print("\n📊 STANDARD SCORING:")
    standard_result = run_scoring(csv_path, enhanced=False)
    results["standard_scoring"] = standard_result

    if standard_result.get("error"):
        print(f"❌ Error: {standard_result['error']}")
        return results

    print(f"   Core Gap: {'YES' if standard_result.get('core_gap') else 'NO'}")
    print(f"   % Fit: {standard_result.get('pct_fit', 'N/A'):.1f}%")
    print(f"   Points: {standard_result.get('actual_points', 'N/A'):.2f}/{standard_result.get('max_points', 'N/A'):.1f}")
    print(f"   Verdict: {standard_result.get('verdict', 'N/A')}")

    # Run each enhancement configuration
    for i, config in enumerate(test_data['enhancement_configs'], 1):
        print(f"\n🚀 ENHANCED CONFIG {i}:")
        print(f"   Role: {config['target_role_type']} | Level: {config['target_role_level']} | Experience: {config['years_experience']}y")
        if config['proven_strengths']:
            print(f"   Strengths: {', '.join(config['proven_strengths'])}")

        enhanced_result = run_scoring(csv_path, enhanced=True, **config)

        if enhanced_result.get("error"):
            print(f"❌ Error: {enhanced_result['error']}")
            continue

        enhanced_result['config'] = config
        results["enhanced_configs"].append(enhanced_result)

        # Calculate improvement
        std_pct = standard_result.get('pct_fit', 0)
        enh_pct = enhanced_result.get('pct_fit', 0)
        improvement = enh_pct - std_pct

        print(f"   Core Gap: {'YES' if enhanced_result.get('core_gap') else 'NO'}")
        print(f"   % Fit: {enh_pct:.1f}% ({improvement:+.1f}% vs standard)")
        print(f"   Points: {enhanced_result.get('actual_points', 'N/A'):.2f}/{enhanced_result.get('max_points', 'N/A'):.1f}")
        print(f"   Verdict: {enhanced_result.get('verdict', 'N/A')}")

        # Color-code the improvement
        if improvement > 0:
            print(f"   ✅ IMPROVEMENT: +{improvement:.1f} percentage points")
        elif improvement == 0:
            print("   ➖ NO CHANGE: Same as standard scoring")
        else:
            print(f"   ⚠️  DECREASE: {improvement:.1f} percentage points")

    return results

def main():
    """Run all validation test cases and generate report."""
    print("🎯 JOB SCORER ENHANCEMENT FRAMEWORK VALIDATION")
    print("=" * 60)
    print("Comparing enhanced vs standard scoring across multiple scenarios...")

    all_results = []

    # Run all test cases
    for test_name, test_data in TEST_CASES.items():
        result = validate_test_case(test_name, test_data)
        all_results.append(result)

    # Generate summary report
    print(f"\n{'='*60}")
    print("📋 VALIDATION SUMMARY REPORT")
    print('='*60)

    for result in all_results:
        if result["standard_scoring"] and not result["standard_scoring"].get("error"):
            print(f"\n🎯 {result['test_name'].upper().replace('_', ' ')}")
            std_pct = result["standard_scoring"].get("pct_fit", 0)
            print(f"   Standard: {std_pct:.1f}%")

            best_improvement = 0
            best_config = None

            for enhanced in result["enhanced_configs"]:
                if not enhanced.get("error"):
                    enh_pct = enhanced.get("pct_fit", 0)
                    improvement = enh_pct - std_pct
                    if improvement > best_improvement:
                        best_improvement = improvement
                        best_config = enhanced["config"]

            if best_config:
                print(f"   Best Enhanced: {std_pct + best_improvement:.1f}% (+{best_improvement:.1f}%)")
                print(f"   Best Config: {best_config['target_role_type']}/{best_config['target_role_level']}")
            else:
                print("   No successful enhanced configurations")

    print(f"\n{'='*60}")
    print("✅ VALIDATION COMPLETE")
    print("Check individual test results above for detailed analysis.")
    print('='*60)

if __name__ == "__main__":
    main()
