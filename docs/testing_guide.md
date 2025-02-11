# Testing Guide

This guide explains how we test our ConnectWise Project Reporting system. Even if you're not technical, understanding our testing approach helps ensure the system works reliably.

## What We Test

### 1. Data Models
These are like templates that ensure our data is correct. For example:
- A project must have a name
- Hours can't be negative
- Email addresses must be valid
- Dates must make sense (end date can't be before start date)

### 2. API Client
This is how we talk to ConnectWise. We test:
- Can we connect properly?
- Do we handle errors gracefully?
- Are we respecting rate limits?
- Is data being sent/received correctly?

### 3. Business Logic
These are our custom rules, like:
- Billable hours can't exceed total hours
- Project identifiers must follow certain formats
- Time entries must have valid start/end times

## How to Run Tests

### Basic Test Run
```bash
# From the project root directory
pytest

# For more detailed output
pytest -v

# To run specific tests
pytest tests/models/test_models.py
```

### Understanding Test Output
- ✅ PASSED: Test worked as expected
- ❌ FAILED: Something's wrong, check the error message
- ⚠️ WARNING: Not an error, but something to be aware of

## Test Examples

### 1. Testing a Member
```python
# This tests if we can create a valid member
member = Member(
    id=1,
    identifier="john.doe",
    email="john@example.com"
)

# This should fail (invalid email)
member = Member(
    id=1,
    identifier="john.doe",
    email="not-an-email"  # This will raise an error
)
```

### 2. Testing a Project
```python
# Valid project
project = Project(
    id=1,
    name="Website Redesign",
    estimated_hours=40.5
)

# Invalid project (negative hours)
project = Project(
    id=1,
    name="Website Redesign",
    estimated_hours=-10  # This will raise an error
)
```

## Common Issues and Solutions

### 1. Test Failures
If tests fail, check:
- Are environment variables set correctly?
- Is ConnectWise accessible?
- Are you using valid test data?

### 2. Warnings
- Pydantic warnings usually mean we're using older style code
- Connection warnings might indicate network issues
- Rate limit warnings mean we're making too many requests

## Adding New Tests

When adding new features:
1. Think about what could go wrong
2. Write tests for both valid and invalid cases
3. Test edge cases (empty values, maximum values, etc.)
4. Make sure error messages are helpful

## Best Practices

1. **Test First**: Write tests before implementing features
2. **Clear Names**: Use descriptive test names
3. **Good Data**: Use realistic test data
4. **Error Messages**: Make them helpful for debugging
5. **Documentation**: Keep this guide updated

## Getting Help

If you're stuck:
1. Check the error message carefully
2. Look at similar tests for examples
3. Ask for help in the team chat
4. Document any new issues you find 