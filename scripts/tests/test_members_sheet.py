"""Tests for publishing/create_members_sheet.py — data building and dedup."""

from unittest.mock import patch


def test_build_channel_data_basic(load_module):
    mod = load_module("publishing/create_members_sheet.py")
    # Populate MEMBER_DB for the test
    mod.MEMBER_DB.update({
        "alice@example.com": {
            "name": "Alice Smith",
            "slack": "@alice",
            "role": "PM",
            "department": "Product",
            "location": "Helsinki",
            "team_role": "lead",
        },
        "bob@example.com": {
            "name": "Bob Jones",
            "slack": "@bob",
            "role": "Dev",
            "department": "Engineering",
            "location": "Berlin",
            "team_role": "member",
        },
    })
    channels = {
        "proj-general": {
            "description": "Main channel",
            "members": ["alice@example.com", "bob@example.com"],
        }
    }
    result = mod.build_channel_data(channels)
    assert "proj-general" in result
    rows = result["proj-general"]["rows"]
    assert len(rows) == 2
    # Sorted by name
    assert rows[0]["name"] == "Alice Smith"
    assert rows[1]["name"] == "Bob Jones"
    assert result["proj-general"]["description"] == "Main channel"


def test_build_channel_data_unknown_member(load_module):
    mod = load_module("publishing/create_members_sheet.py")
    mod.MEMBER_DB.clear()
    channels = {
        "test": {"description": "", "members": ["unknown@example.com"]},
    }
    result = mod.build_channel_data(channels)
    rows = result["test"]["rows"]
    assert len(rows) == 1
    assert rows[0]["email"] == "unknown@example.com"
    assert rows[0]["name"] == ""
    assert rows[0]["team_role"] == "member"


def test_build_master_view_dedup(load_module):
    mod = load_module("publishing/create_members_sheet.py")
    mod.MEMBER_DB.update({
        "alice@example.com": {"name": "Alice", "slack": "@alice", "role": "PM",
                               "department": "Product", "location": "Helsinki", "team_role": "lead"},
    })
    channel_data = {
        "ch1": {
            "description": "",
            "rows": [{"email": "alice@example.com", "name": "Alice", "slack": "@alice",
                      "role": "PM", "department": "Product", "location": "Helsinki", "team_role": "lead"}],
        },
        "ch2": {
            "description": "",
            "rows": [{"email": "alice@example.com", "name": "Alice", "slack": "@alice",
                      "role": "PM", "department": "Product", "location": "Helsinki", "team_role": "lead"}],
        },
    }
    result = mod.build_master_view(channel_data)
    assert len(result) == 1
    assert "ch1" in result[0]["channels"]
    assert "ch2" in result[0]["channels"]
    assert result[0]["channels_str"] == "ch1, ch2"


def test_build_master_view_multiple_members(load_module):
    mod = load_module("publishing/create_members_sheet.py")
    mod.MEMBER_DB.clear()
    channel_data = {
        "ch1": {
            "description": "",
            "rows": [
                {"email": "a@x.com", "name": "Alice", "slack": "", "role": "", "department": "", "location": "", "team_role": "lead"},
                {"email": "b@x.com", "name": "Bob", "slack": "", "role": "", "department": "", "location": "", "team_role": "member"},
            ],
        },
    }
    result = mod.build_master_view(channel_data)
    assert len(result) == 2
    # Sorted by name
    assert result[0]["name"] == "Alice"
    assert result[1]["name"] == "Bob"
