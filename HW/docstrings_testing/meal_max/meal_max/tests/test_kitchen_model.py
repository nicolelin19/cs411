import pytest
from meal_max.models.kitchen_model import (Meal, 
                                                    create_meal, 
                                                    delete_meal, 
                                                    get_leaderboard, 
                                                    get_meal_by_id, 
                                                    get_meal_by_name, 
                                                    update_meal_stats)
import sqlite3
from contextlib import contextmanager
import re

def normalize_sql_whitespace(query):
    """
    Normalizes whitespace in an SQL query by replacing multiple spaces with a single space
    and trimming leading/trailing whitespace.
    """
    # Remove extra spaces and newlines, keeping a single space between keywords/clauses
    return re.sub(r'\s+', ' ', query).strip()

@pytest.fixture
def mock_db_cursor(mocker):
    """Mocking the database connection & cursor for the tests."""
    mock_conn = mocker.Mock()
    mock_cursor = mocker.Mock()

    # Mock the cursor
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.commit.return_value = None

    @contextmanager
    def mock_get_db_connection():
        yield mock_conn

    # Mock the `get_db_connection` function to return the mock connection
    mocker.patch("meal_max.models.kitchen_model.get_db_connection", mock_get_db_connection)

    return mock_cursor

######################################################
#
#    Tests for Meal 
#
######################################################

def test_meal_post_init_valid():
    """Test that a Meal instance is initialized with valid attributes."""
    meal = Meal(id=1, meal="Meal 1", cuisine="Cuisine 1", price=12.5, difficulty="MED")
    assert meal.price == 12.5
    assert meal.difficulty == "MED"

def test_meal_post_init_invalid_price():
    """Test ensuring that a ValueError is raised if a price is invalid."""
    with pytest.raises(ValueError, match="Price must be a positive value."):
        Meal(id=1, meal="Meal 1", cuisine="Cuisine 1", price=-5.0, difficulty="MED")

def test_meal_post_init_invalid_difficulty():
    """Test to ensure a ValueError is raised if a difficulty is invalid."""
    with pytest.raises(ValueError, match="Difficulty must be 'LOW', 'MED', or 'HIGH'."):
        Meal(id=1, meal="Meal 1", cuisine="Cuisine 1", price=10.0, difficulty="EASY")

######################################################
#
#    Tests for Create and Delete Meal Functions
#
######################################################

def test_create_meal(mock_db_cursor):
    """Test if a new meal is correctly created and added to the database."""
    create_meal("Meal 1", "Cuisine 1", 15.0, "MED")
    expected_query = normalize_sql_whitespace("""
                                              INSERT INTO meals (meal, cuisine, price, difficulty) 
                                              VALUES (?, ?, ?, ?)
                                              """)
    actual_query = normalize_sql_whitespace(mock_db_cursor.execute.call_args[0][0])

    # Assert that the SQL query was correct
    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    # Extract the arguments used in the SQL call (second element of call_args)
    actual_args = mock_db_cursor.execute.call_args[0][1]

    # Assert that the SQL query was executed with the correct arguments
    expected_args = ("Meal 1", "Cuisine 1", 15.0, "MED")
    assert actual_args == expected_args, f"The SQL query arguments did not match. Expected {expected_args}, got {actual_args}."

def test_create_meal_duplicate(mock_db_cursor):
    """Test raising a ValueError if a meal duplicate is created."""
    mock_db_cursor.execute.side_effect = sqlite3.IntegrityError
    with pytest.raises(ValueError, match=r"Meal with name 'Meal 1' already exists"):
        create_meal("Meal 1", "Cuisine", 15.0, "MED")


def test_delete_meal(mock_db_cursor):
    """Test setting a meal's status to 'deleted'."""
    mock_db_cursor.fetchone.return_value = (False,)
    delete_meal(1)
    mock_db_cursor.execute.assert_any_call("SELECT deleted FROM meals WHERE id = ?", (1,))
    mock_db_cursor.execute.assert_any_call("UPDATE meals SET deleted = TRUE WHERE id = ?", (1,))

def test_delete_non_existent_meal(mock_db_cursor):
    """Test that a ValueError is raised if a non-existent meal is deleted."""
    mock_db_cursor.fetchone.return_value = None
    with pytest.raises(ValueError, match="Meal with ID 999 not found"):
        delete_meal(999)

def test_delete_already_deleted_meal(mock_db_cursor):
    """Test that a ValueError is raised when deleting a meal that is already deleted."""
    mock_db_cursor.fetchone.return_value = (True,)
    with pytest.raises(ValueError, match="Meal with ID 1 has been deleted"):
        delete_meal(1)

######################################################
#
#    Tests for Get Leaderboard and Get Meal Functions
#
######################################################

def test_get_leaderboard(mock_db_cursor):
    """Test to retrieveg the sorted (by wins) leaderboard."""
    mock_db_cursor.fetchall.return_value = [
        (1, "Meal 1", "Cuisine 1", 10.0, "MED", 5, 3, 0.6)
    ]
    leaderboard = get_leaderboard()
    expected_leaderboard = [
        {'id': 1, 'meal': "Meal 1", 'cuisine': "Cuisine 1", 'price': 10.0, 'difficulty': "MED", 'battles': 5, 'wins': 3, 'win_pct': 60.0}
    ]
    assert leaderboard == expected_leaderboard

def test_get_meal_by_id(mock_db_cursor):
    """Test retrieving a meal by its ID."""
    mock_db_cursor.fetchone.return_value = (1, "Meal 1", "Cuisine 1", 12.0, "MED", False)
    meal = get_meal_by_id(1)
    assert meal == Meal(id=1, meal="Meal 1", cuisine="Cuisine 1", price=12.0, difficulty="MED")

def test_get_meal_by_id_not_found(mock_db_cursor):
    """Test that retrieving a non-existent meal by ID raises a ValueError."""
    mock_db_cursor.fetchone.return_value = None
    with pytest.raises(ValueError, match="Meal with ID 999 not found"):
        get_meal_by_id(999)

def test_get_meal_by_name(mock_db_cursor):
    """Test retrieving a meal by its name."""
    mock_db_cursor.fetchone.return_value = (1, "Meal 1", "Cuisine 1", 12.0, "MED", False)
    meal = get_meal_by_name("Meal 1")
    assert meal == Meal(id=1, meal="Meal 1", cuisine="Cuisine 1", price=12.0, difficulty="MED")

def test_get_meal_by_name_not_found(mock_db_cursor):
    """Test that retrieving a non-existent meal by name raises a ValueError."""
    mock_db_cursor.fetchone.return_value = None
    with pytest.raises(ValueError, match=r"Meal with name Meal 2347 not found"):
        get_meal_by_name("Meal 2347")


######################################################
#
#    Tests for Update_Meal_Stats
#
######################################################

def test_update_meal_stats_win(mock_db_cursor):
    """Test to verify that when a meal’s stats are updated 'win', the correct SQL query is executed"""
    mock_db_cursor.fetchone.return_value = (False,)
    update_meal_stats(1, 'win')
    mock_db_cursor.execute.assert_any_call("UPDATE meals SET battles = battles + 1, wins = wins + 1 WHERE id = ?", (1,))

def test_update_meal_stats_loss(mock_db_cursor):
    """Test to verify that when a meal’s stats are updated 'loss', the correct SQL query is executed"""
    mock_db_cursor.fetchone.return_value = (False,)
    update_meal_stats(1, 'loss')
    mock_db_cursor.execute.assert_any_call("UPDATE meals SET battles = battles + 1 WHERE id = ?", (1,))

def test_update_meal_stats_invalid_result(mock_db_cursor):
    """Test that an invalid result (value) raises a ValueError."""
    mock_db_cursor.fetchone.return_value = [False]
    with pytest.raises(ValueError, match=r"Invalid result: .*\. Expected 'win' or 'loss'\."):
        update_meal_stats(1, 1)
    with pytest.raises(ValueError, match=r"Invalid result: .*\. Expected 'win' or 'loss'\."):
        update_meal_stats(1, 'lost')

def test_update_meal_stats_deleted_meal(mock_db_cursor):
    """Test that updating stats for a meal that has been deleted raises a ValueError."""
    mock_db_cursor.fetchone.return_value = (True,)
    with pytest.raises(ValueError, match="Meal with ID 1 has been deleted"):
        update_meal_stats(1, 'win')

