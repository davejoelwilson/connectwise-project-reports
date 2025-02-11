import pytest
from datetime import datetime, timedelta
from pydantic import ValidationError
from connectwise.models import Member, Status, Project, TimeEntry, Ticket, Note

def test_member_validation():
    """Test Member model validation rules"""
    # Test valid data
    member = Member(
        id=1,
        identifier="john.doe",
        first_name="John",
        last_name="Doe",
        email="john@example.com"
    )
    assert member.id == 1
    assert member.identifier == "john.doe"
    
    # Test invalid id
    with pytest.raises(ValidationError) as exc:
        Member(id=-1, identifier="test")
    assert "Input should be greater than 0" in str(exc.value)
    
    # Test invalid identifier
    with pytest.raises(ValidationError) as exc:
        Member(id=1, identifier="invalid@user")
    assert "Identifier must contain only alphanumeric characters" in str(exc.value)
    
    # Test invalid email
    with pytest.raises(ValidationError) as exc:
        Member(id=1, identifier="test", email="invalid-email")
    assert "value is not a valid email address" in str(exc.value)
    
    # Test max length validations
    long_string = "a" * 51
    with pytest.raises(ValidationError) as exc:
        Member(id=1, identifier=long_string)
    assert "String should have at most 50 characters" in str(exc.value)

def test_status_validation():
    """Test Status model validation rules"""
    # Test valid data
    status = Status(id=1, name="Active")
    assert status.id == 1
    assert status.name == "Active"
    
    # Test invalid id
    with pytest.raises(ValidationError) as exc:
        Status(id=0, name="Test")
    assert "Input should be greater than 0" in str(exc.value)
    
    # Test empty name
    with pytest.raises(ValidationError) as exc:
        Status(id=1, name="")
    assert "String should have at least 1 character" in str(exc.value)
    
    # Test name too long
    with pytest.raises(ValidationError) as exc:
        Status(id=1, name="a" * 51)
    assert "String should have at most 50 characters" in str(exc.value)

def test_project_validation():
    """Test Project model validation rules"""
    now = datetime.now()
    
    # Test valid data
    project = Project(
        id=1,
        name="Test Project",
        status=Status(id=1, name="Active"),
        manager=Member(id=1, identifier="john.doe"),
        company_name="Test Company",
        estimated_hours=40.5,
        actual_hours=20.0,
        scheduled_start=now,
        scheduled_finish=now + timedelta(days=30),
        billing_method="FixedFee"
    )
    assert project.id == 1
    assert project.name == "Test Project"
    assert project.estimated_hours == 40.5
    
    # Test invalid dates
    with pytest.raises(ValidationError) as exc:
        Project(
            id=1,
            name="Test",
            scheduled_start=now,
            scheduled_finish=now - timedelta(days=1)
        )
    assert "Scheduled finish must be after scheduled start" in str(exc.value)
    
    # Test invalid billing method
    with pytest.raises(ValidationError) as exc:
        Project(id=1, name="Test", billing_method="Invalid")
    assert "Input should be 'FixedFee', 'TimeAndMaterials' or 'NotToExceed'" in str(exc.value)
    
    # Test negative hours
    with pytest.raises(ValidationError) as exc:
        Project(id=1, name="Test", estimated_hours=-1)
    assert "Input should be greater than or equal to 0" in str(exc.value) 