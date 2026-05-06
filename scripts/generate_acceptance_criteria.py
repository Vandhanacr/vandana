#!/usr/bin/env python3
"""
Generate Gherkin-formatted acceptance criteria for Azure DevOps work items.
Uses Claude/Copilot to analyze user stories and create comprehensive test scenarios.
"""

import os
import sys
import json
from datetime import datetime
import anthropic
from azure.devops.connection import Connection
from azure.devops.v7_0.work_item_tracking.models import JsonPatchOperation
from msrest.authentication import BasicAuthentication


def get_ado_connection():
    """Create Azure DevOps API connection."""
    org = os.getenv("ADO_ORGANIZATION", "kantarware")
    pat = os.getenv("ADO_PAT")
    
    if not pat:
        raise ValueError("ADO_PAT environment variable not set")
    
    credentials = BasicAuthentication("", pat)
    connection = Connection(
        base_url=f"https://dev.azure.com/{org}",
        creds=credentials
    )
    return connection


def fetch_work_item(work_item_id: str):
    """Fetch work item from Azure DevOps."""
    connection = get_ado_connection()
    wit_client = connection.clients.get_work_item_tracking_client()
    project = os.getenv("ADO_PROJECT", "KM-Ecosystem")
    
    try:
        work_item = wit_client.get_work_item(
            id=int(work_item_id),
            project=project
        )
        return work_item
    except Exception as e:
        raise Exception(f"Failed to fetch work item {work_item_id}: {str(e)}")


def check_existing_criteria(work_item) -> bool:
    """Check if acceptance criteria already exists."""
    fields = work_item.fields
    criteria = fields.get("Microsoft.VSTS.Common.AcceptanceCriteria", "")
    return bool(criteria and criteria.strip())


def extract_context(work_item) -> dict:
    """Extract relevant context from work item."""
    fields = work_item.fields
    
    context = {
        "id": work_item.id,
        "title": fields.get("System.Title", ""),
        "description": fields.get("System.Description", ""),
        "state": fields.get("System.State", ""),
        "work_item_type": fields.get("System.WorkItemType", ""),
    }
    
    return context


def generate_gherkin_criteria(context: dict) -> str:
    """Generate Gherkin-formatted acceptance criteria using Copilot."""
    api_key = os.getenv("COPILOT_API_KEY")
    
    if not api_key:
        raise ValueError("COPILOT_API_KEY environment variable not set")
    
    client = anthropic.Anthropic(api_key=api_key)
    
    prompt = f"""
You are a QA expert specializing in test case generation. 
Analyze this work item and generate comprehensive Gherkin-formatted acceptance criteria.

Work Item ID: {context['id']}
Title: {context['title']}
Type: {context['work_item_type']}
Description: {context['description']}

Requirements:
1. Generate 5-8 Gherkin scenarios covering the main functionality
2. Include positive scenarios, edge cases, and error handling
3. Each scenario should be independent and testable
4. Use clear Given-When-Then format
5. Include all steps to reproduce if mentioned in description
6. Format as a Feature with multiple Scenarios
7. Make scenarios realistic and specific to the work item

Return ONLY the Gherkin content (no markdown formatting, no backticks):

Feature: [Title from work item]
  Scenario: [Specific scenario]
    Given [precondition]
    When [action]
    Then [expected result]
"""

    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=2048,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )
    
    return message.content[0].text.strip()


def update_work_item(work_item_id: str, acceptance_criteria: str) -> bool:
    """Update work item with generated acceptance criteria."""
    connection = get_ado_connection()
    wit_client = connection.clients.get_work_item_tracking_client()
    project = os.getenv("ADO_PROJECT", "KM-Ecosystem")
    
    patch_document = [
        JsonPatchOperation(
            op="add",
            path="/fields/Microsoft.VSTS.Common.AcceptanceCriteria",
            value=acceptance_criteria
        )
    ]
    
    try:
        updated_item = wit_client.update_work_item(
            document=patch_document,
            id=int(work_item_id),
            project=project
        )
        return updated_item is not None
    except Exception as e:
        print(f"Error updating work item: {str(e)}")
        return False


def save_results(result: dict, filename: str = "acceptance_criteria_result.json"):
    """Save results to JSON file."""
    with open(filename, 'w') as f:
        json.dump(result, f, indent=2)
    print(f"\n✅ Results saved to {filename}")


def main():
    """Main execution flow."""
    if len(sys.argv) < 2:
        print("❌ Usage: python generate_acceptance_criteria.py <WORK_ITEM_ID>")
        sys.exit(1)
    
    work_item_id = sys.argv[1]
    result = {
        "timestamp": datetime.now().isoformat(),
        "work_item_id": work_item_id,
        "status": "processing",
        "message": "",
        "generated_criteria": None,
        "updated": False
    }
    
    try:
        # Step 1: Fetch work item
        print(f"📦 Fetching work item #{work_item_id}...")
        work_item = fetch_work_item(work_item_id)
        print(f"   ✓ Title: {work_item.fields['System.Title']}")
        
        # Step 2: Check for existing criteria
        print(f"🔍 Checking for existing acceptance criteria...")
        if check_existing_criteria(work_item):
            result["status"] = "skipped"
            result["message"] = "Acceptance criteria already exists"
            print(f"   ⚠️  {result['message']}")
            save_results(result)
            return
        
        print(f"   ✓ No existing criteria found")
        
        # Step 3: Extract context
        print(f"📋 Extracting work item context...")
        context = extract_context(work_item)
        print(f"   ✓ Type: {context['work_item_type']}")
        print(f"   ✓ State: {context['state']}")
        
        # Step 4: Generate criteria with Copilot
        print(f"🤖 Generating Gherkin scenarios with Copilot...")
        generated_criteria = generate_gherkin_criteria(context)
        print(f"   ✓ Generated {len(generated_criteria)} characters")
        
        # Step 5: Update work item
        print(f"📤 Updating work item in Azure DevOps...")
        updated = update_work_item(work_item_id, generated_criteria)
        
        if updated:
            result["status"] = "success"
            result["message"] = "Acceptance criteria generated and updated successfully"
            result["generated_criteria"] = generated_criteria
            result["updated"] = True
            print(f"   ✓ Work item updated successfully")
        else:
            result["status"] = "error"
            result["message"] = "Failed to update work item"
            result["generated_criteria"] = generated_criteria
            print(f"   ❌ Failed to update work item")
        
        # Step 6: Display results
        print(f"\n{'='*70}")
        print(f"GENERATED ACCEPTANCE CRITERIA (Work Item #{work_item_id})")
        print(f"{'='*70}")
        print(generated_criteria)
        print(f"{'='*70}\n")
        
        # Step 7: Save results
        save_results(result)
        
    except Exception as e:
        result["status"] = "error"
        result["message"] = str(e)
        print(f"❌ Error: {result['message']}")
        save_results(result)
        sys.exit(1)


if __name__ == "__main__":
    main()
