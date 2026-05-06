# 📋 Azure DevOps Acceptance Criteria Generator

Generate Gherkin-formatted acceptance criteria for Azure DevOps user stories using GitHub Copilot.

## 🎯 Features

- **Fetch User Stories**: Retrieves work items by ID from Azure DevOps
- **Check Existing Criteria**: Skips update if criteria already exists
- **Generate with Copilot**: Uses Claude AI to create comprehensive Gherkin scenarios
- **Auto-Update ADO**: Updates the work item with generated criteria
- **GitHub Actions Integration**: Run via workflow or command-line

## 📋 Prerequisites

1. **Azure DevOps Account**
   - Organization: `kantarware`
   - Project: `KM-Ecosystem`
   - Personal Access Token (PAT) with "Work Items (read, write)" scope

2. **GitHub Copilot / Claude API**
   - API Key for Copilot or Claude

3. **Python 3.11+**

## 🚀 Setup

### 1. Get Azure DevOps PAT

1. Go to https://dev.azure.com/kantarware
2. Click your profile icon → **Personal access tokens**
3. Click **New Token**
4. Configure:
   - **Name**: `GitHub-Copilot-ADO`
   - **Organization**: `kantarware`
   - **Scopes**: Check "Work Items (read, write)"
   - **Expiration**: 1 year
5. Click **Create** and copy the token

### 2. Add GitHub Secrets

In your repository settings (`Settings` → `Secrets and variables` → `Actions`):

```
ADO_ORGANIZATION = kantarware
ADO_PROJECT = KM-Ecosystem
ADO_PAT = <Your Azure DevOps PAT>
COPILOT_API_KEY = <Your Claude/Copilot API Key>
```

### 3. Install Dependencies

```bash
pip install anthropic azure-devops azure-identity
```

## 💻 Usage

### Option A: Command Line (Local)

```bash
export ADO_ORGANIZATION=kantarware
export ADO_PROJECT=KM-Ecosystem
export ADO_PAT=your_pat_here
export COPILOT_API_KEY=your_api_key_here

python scripts/generate_acceptance_criteria.py 2516289
```

### Option B: GitHub Actions Workflow (Recommended)

1. **Go to**: `Actions` → `Generate ADO Acceptance Criteria`
2. **Click**: `Run workflow`
3. **Enter**: Work Item ID (e.g., `2516289`)
4. **View**: Results in workflow logs

### Option C: Trigger via Issue Comment

Comment on any issue:
```
/generate-criteria 2516289
```

The bot will generate and comment with results.

## 📊 Example Output

### Input Story (#2516289)
```
Title: Target Export is failing when expressions with Functions are added in the targets

Steps to Reproduce:
1. Login to the ecosystem with valid credentials
2. Navigate to the Target export
3. Select Survey (Eg: GB TGI) and click on OK
4. Add the targets:
   - All Men - DBSEXLME
   - All Women - DBSEXLWO
   - Average shoppers - MeanScoreNoZero(...)
```

### Generated Acceptance Criteria (Gherkin)
```gherkin
Feature: Target Export with Function Expressions

  Scenario: Export simple targets without functions
    Given I am logged into the ecosystem with valid credentials
    When I navigate to the Target export
    And I select Survey "GB TGI"
    And I click OK
    Then the export dialog opens successfully

  Scenario: Export simple text-based targets
    Given I am on the Target export page
    When I add target "All Men - DBSEXLME"
    And I add target "All Women - DBSEXLWO"
    And I click Export
    Then the targets should be exported successfully

  Scenario: Export targets with function expressions
    Given I am on the Target export page
    When I add target "Average shoppers - MeanScoreNoZero(DBSEXFS, 11111, DBSEXMS, 15000)"
    And I click Export
    Then the target with function expression should be processed correctly
    And the export should complete successfully

  Scenario: Handle complex function expressions with multiple parameters
    Given I am on the Target export page
    When I add target with function expression containing multiple parameters
    And I click Export
    Then the system should validate and process the function expression
    And the export should succeed

  Scenario: Handle invalid function expressions gracefully
    Given I am on the Target export page
    When I add target with invalid function expression "InvalidFunc(...)"
    And I click Export
    Then an error message should be displayed
    And the user should be prompted to correct the expression
    And the export process should not proceed
```

## 📁 File Structure

```
vandana/
├── .github/
│   └── workflows/
│       └── generate-acceptance-criteria.yml  # GitHub Action
├── scripts/
│   └── generate_acceptance_criteria.py       # Main script
└── ACCEPTANCE_CRITERIA_README.md             # This file
```

## 🔄 Workflow Details

The script follows this process:

```
1. Fetch Work Item (ADO API)
   ↓
2. Check for Existing Criteria
   ├─ If exists → Skip and report
   └─ If missing → Continue
   ↓
3. Extract Context
   ├─ Title
   ├─ Description
   └─ Reproduction Steps
   ↓
4. Generate with Copilot
   └─ Create Gherkin scenarios
   ↓
5. Update Work Item (ADO API)
   └─ Set Microsoft.VSTS.Common.AcceptanceCriteria field
   ↓
6. Report Results
   └─ Console + JSON output
```

## 📊 Supported Work Item Types

- User Stories
- Features
- Product Backlog Items (PBIs)
- Any custom work item type with acceptance criteria field

## ⚙️ Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `ADO_ORGANIZATION` | Azure DevOps org name | `kantarware` |
| `ADO_PROJECT` | ADO project name | `KM-Ecosystem` |
| `ADO_PAT` | Personal Access Token | `pat_***` |
| `COPILOT_API_KEY` | Claude/Copilot API key | `sk-***` |

## 🐛 Troubleshooting

### Error: "Invalid work item ID"
- Check the ID exists in your ADO project
- Verify ADO_PAT has correct permissions

### Error: "Acceptance criteria already exists"
- This is expected if the work item already has criteria
- No update will be made (safe operation)

### Error: "Could not authenticate with Copilot"
- Verify `COPILOT_API_KEY` is correct
- Check API key hasn't expired

### No output file generated
- Check GitHub Actions logs for detailed error messages
- Ensure all environment variables are set

## 🔐 Security Notes

- Never commit secrets or API keys
- Use GitHub Secrets for all credentials
- ADO PAT should have minimal required scopes
- Rotate secrets periodically

## 📈 Next Steps

1. **Process your story**:
   ```bash
   python scripts/generate_acceptance_criteria.py 2516289
   ```

2. **Review generated criteria** in ADO work item

3. **Refine if needed** - AI-generated criteria should be reviewed by QA

4. **Run automated tests** based on Gherkin scenarios

## 📞 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review GitHub Actions logs
3. Verify all environment variables are set correctly

---

**Created**: 2026-05-06  
**Compatible with**: Azure DevOps, GitHub Actions, Python 3.11+
