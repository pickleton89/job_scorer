# Job Scorer Enhancement Framework User Guide

## Overview

The Job Scorer Enhancement Framework transforms basic skill assessment into strategic career positioning for senior professionals. This guide provides comprehensive instructions for using the enhancement features to optimize your job application scoring.

## Quick Start

### Basic Enhancement Usage

```bash
# Enable enhancements with defaults (senior executive, 20 years experience)
python -m scoring.scoring_v2 your_skills.csv --enable-enhancements
```

This single flag activates all four enhancement modules with sensible defaults for most senior professionals.

### Compare Standard vs Enhanced

```bash
# Run standard scoring first
python -m scoring.scoring_v2 your_skills.csv

# Then run with enhancements to see the difference
python -m scoring.scoring_v2 your_skills.csv --enable-enhancements
```

## Enhancement Options Reference

### Core Enhancement Flag

| Flag | Description | Default |
|------|-------------|---------|
| `--enable-enhancements` | Activates all strategic positioning features | Disabled |

### Configuration Options

| Option | Choices | Default | Description |
|--------|---------|---------|-------------|
| `--target-role-type` | `executive`, `ic`, `hybrid` | `executive` | Role type for dual-track scoring |
| `--target-role-level` | `c_suite`, `senior_executive`, `director_vp`, `senior_ic` | `senior_executive` | Target position level |
| `--years-experience` | Integer (1-50) | `20` | Years of professional experience |
| `--proven-strengths` | Space-separated keywords | None | Cross-functional strength indicators |

## Role-Specific Configuration Guide

### 👔 Senior Executive Roles

**Best Configuration:**
```bash
python -m scoring.scoring_v2 skills.csv --enable-enhancements \
  --target-role-type executive \
  --target-role-level senior_executive \
  --years-experience 20 \
  --proven-strengths cross-functional strategy
```

**When to Use:**
- VP or SVP level positions
- 15-25 years experience
- Leading teams of 20+ people
- Cross-functional responsibilities

**What Gets Emphasized:**
- Strategic planning and vision
- Cross-functional team leadership
- Stakeholder communication
- Business development

### 🏢 C-Suite Positions

**Best Configuration:**
```bash
python -m scoring.scoring_v2 skills.csv --enable-enhancements \
  --target-role-type executive \
  --target-role-level c_suite \
  --years-experience 25 \
  --proven-strengths strategy partnerships fundraising
```

**When to Use:**
- CEO, COO, CTO, CSO positions
- 20+ years experience
- Board-level responsibilities
- Company-wide strategic impact

**What Gets Emphasized:**
- Strategic thinking (1.4x weight)
- Business acumen (1.3x weight)
- Cross-functional integration (1.2x weight)
- Technical literacy de-emphasized (0.8x weight)

### 🔬 Senior Individual Contributor

**Best Configuration:**
```bash
python -m scoring.scoring_v2 skills.csv --enable-enhancements \
  --target-role-type ic \
  --target-role-level senior_ic \
  --years-experience 15 \
  --proven-strengths algorithms computational-biology research
```

**When to Use:**
- Principal Scientist, Staff Engineer, Research Fellow
- 10-20 years experience
- Deep technical expertise required
- Limited management responsibilities

**What Gets Emphasized:**
- Domain expertise (1.4x weight)
- Technical literacy (1.3x weight)
- Hands-on skills (1.1x weight)
- Strategic thinking de-emphasized (0.8x weight)

### ⚖️ Director/VP Hybrid Roles

**Best Configuration:**
```bash
python -m scoring.scoring_v2 skills.csv --enable-enhancements \
  --target-role-type hybrid \
  --target-role-level director_vp \
  --years-experience 18 \
  --proven-strengths technical-leadership cross-functional
```

**When to Use:**
- Director of Engineering, VP of Research
- 12-20 years experience
- Balance of leadership and technical depth
- Managing technical teams

**What Gets Emphasized:**
- Cross-functional leadership (1.1x weight)
- Domain expertise (1.1x weight)
- Technical literacy (1.2x weight)
- Balanced approach to all skills

## Proven Strengths Guide

### What Are Proven Strengths?

Keywords that represent your demonstrated capabilities and experiences. When these appear in job requirements, you receive bonus multipliers.

### Effective Proven Strength Keywords

#### Cross-Functional Leadership
- `cross-functional`
- `multidisciplinary`
- `integration`
- `coordination`
- `collaboration`

#### Technical Domains
- `bioinformatics`
- `computational-biology`
- `algorithms`
- `machine-learning`
- `data-science`
- `platform-development`

#### Business Strategy
- `strategy`
- `partnerships`
- `licensing`
- `fundraising`
- `business-development`

#### Domain Expertise
- `drug-discovery`
- `therapeutics`
- `clinical`
- `regulatory`
- `chemistry`
- `biology`

### How to Choose Proven Strengths

1. **Review your resume**: What are your top 3-5 demonstrated capabilities?
2. **Match job requirements**: Look for keywords that appear in the job posting
3. **Be specific**: Use compound terms like "drug-discovery" rather than just "discovery"
4. **Limit to 3-5**: Quality over quantity - focus on your strongest areas

### Examples by Role Type

**Senior Executive:**
```bash
--proven-strengths cross-functional strategy partnerships
```

**Technical IC:**
```bash
--proven-strengths algorithms computational-biology machine-learning
```

**Biotech Professional:**
```bash
--proven-strengths drug-discovery bioinformatics clinical
```

**Business Development:**
```bash
--proven-strengths partnerships licensing fundraising
```

## Experience Level Calibration

### How It Works

The system adjusts expectations based on years of experience:

- **< 15 years**: No calibration penalties (standard scoring)
- **15+ years**: Higher baselines expected for leadership skills
- **20+ years**: Senior professional standards applied
- **25+ years**: Executive-level expectations

### Skill Category Baselines (15+ years)

| Skill Category | Minimum Expected Score |
|----------------|----------------------|
| Basic Technical | 3+ |
| Leadership | 4+ |
| Strategic Thinking | 4+ |
| Communication | 4+ |
| Domain Expertise | 4+ |

### What This Means

If you have 20+ years of experience but score a 3 in "Leadership skills," the system applies a 0.7x penalty because senior professionals are expected to have stronger leadership capabilities.

### Recommendations

1. **Be honest about your experience level** - the calibration helps set realistic expectations
2. **Focus on leadership gaps** if you're 15+ years and targeting executive roles
3. **Consider targeting IC roles** if you prefer to avoid leadership calibration
4. **Use proven strengths** to offset calibration penalties in weak areas

## Understanding Your Enhanced Results

### Reading the Output

When enhancements are enabled, you'll see:

```
ENHANCED STRATEGIC POSITIONING RESULTS
Role Type: Executive | Experience: 20y | Level: Senior Executive
Proven Strengths: cross-functional, bioinformatics
--------------------------------------------------
                     VERDICT                      
--------------------------------------------------

1. Core gap present : NO
2. Actual points    : 3.73 / 10.0
3. % Fit            : 37.0%
```

### Interpreting Score Changes

**Positive Changes (+2% to +7%):**
- Your profile aligns well with the target role
- Cross-functional requirements detected and rewarded
- Proven strengths matching job requirements
- Appropriate role-level calibration

**No Change (0%):**
- Balanced role with no specific advantages
- Requirements don't trigger enhancement bonuses
- May indicate you're targeting the right level

**Negative Changes (-1% to -4%):**
- Role type misalignment (e.g., IC applying to executive role)
- Below-baseline scores for your experience level
- May need to adjust target role or improve skills

### When to Adjust Your Configuration

**If your score decreases:**
1. Try different `--target-role-type` (executive → ic or vice versa)
2. Lower the `--target-role-level` (c_suite → senior_executive)
3. Adjust `--years-experience` if misconfigured
4. Remove or change `--proven-strengths` if not matching

**If your score doesn't improve much:**
1. Add relevant `--proven-strengths` keywords
2. Ensure role type matches the job requirements
3. Consider if enhancements are needed for this role

## Common Use Cases

### Case 1: Biotech Executive Transition

**Scenario**: Senior scientist (15 years) moving to executive role

**Configuration**:
```bash
--enable-enhancements \
--target-role-type executive \
--target-role-level director_vp \
--years-experience 15 \
--proven-strengths cross-functional drug-discovery
```

**Expected Improvement**: 3-5% for cross-functional requirements

### Case 2: Tech Company Senior IC

**Scenario**: Principal Engineer with deep technical expertise

**Configuration**:
```bash
--enable-enhancements \
--target-role-type ic \
--target-role-level senior_ic \
--years-experience 18 \
--proven-strengths algorithms platform-development
```

**Expected Improvement**: 2-3% for technical depth requirements

### Case 3: Consulting to Industry

**Scenario**: Experienced consultant moving to industry executive role

**Configuration**:
```bash
--enable-enhancements \
--target-role-type executive \
--target-role-level senior_executive \
--years-experience 22 \
--proven-strengths strategy cross-functional partnerships
```

**Expected Improvement**: 4-7% for strategic and cross-functional requirements

### Case 4: Academic to Industry

**Scenario**: Professor/researcher transitioning to industry

**Configuration**:
```bash
--enable-enhancements \
--target-role-type hybrid \
--target-role-level director_vp \
--years-experience 20 \
--proven-strengths research computational-biology
```

**Expected Improvement**: 2-4% with balanced approach

## Troubleshooting

### Q: My enhanced score is lower than standard score

**A**: This usually indicates role misalignment. Try:
1. Changing `--target-role-type` from executive to ic (or vice versa)
2. Lowering the `--target-role-level` 
3. Checking if your experience level triggers penalties you're not ready for

### Q: I'm not seeing much improvement

**A**: Consider:
1. Adding specific `--proven-strengths` that match the job requirements
2. Ensuring the job has cross-functional elements that trigger bonuses
3. Checking if the role is well-suited for enhancements (senior roles benefit most)

### Q: How do I know what proven strengths to use?

**A**: 
1. Review the job posting for recurring keywords
2. Look at your strongest demonstrated capabilities
3. Use compound terms that are specific to your domain
4. Test different combinations to see what provides the best improvement

### Q: Should I always use enhancements?

**A**: Use enhancements when:
- You have 15+ years experience
- Targeting senior/executive roles
- Job has cross-functional requirements
- You want strategic positioning beyond basic skill matching

Skip enhancements for:
- Junior roles (< 15 years experience)
- Purely technical roles with no leadership component
- When standard scoring already shows excellent fit

## Best Practices

1. **Start with standard scoring** to establish a baseline
2. **Use realistic configurations** that match your actual profile
3. **Experiment with proven strengths** to find the best keyword combinations
4. **Document your configuration** for consistent use across similar roles
5. **Validate improvements make sense** - large gains should align with genuine strengths
6. **Consider the target role carefully** - don't aim too high or too low for your experience

## Advanced Tips

### Maximizing Cross-Functional Bonuses

Look for job requirements containing multiple domains:
- "Collaborate with chemistry, biology, and clinical teams"
- "Bridge research findings with business strategy"
- "Integrate platform development with regulatory requirements"

These trigger the highest enhancement bonuses.

### Role Level Strategy

- **Aim slightly above your current level** for aspirational positioning
- **Use director_vp as a transition** between IC and senior executive
- **Try both c_suite and senior_executive** to see which fits better

### Keyword Strategy

- **Use hyphens in compound terms**: "drug-discovery" not "drug discovery"
- **Be domain-specific**: "computational-biology" not just "biology"
- **Match job posting language**: If they say "bioinformatics," use "bioinformatics"

This guide should help you leverage the enhancement framework effectively for strategic career positioning. For additional support, see the validation report in `docs/Enhancement_Framework_Validation_Report.md` for detailed performance analysis.